from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.sentence import Sentence, UserSentenceResult, SentenceTranslation
from app.models.user import User
from app.models.category import Category
from app.schemas.sentence import PinRequest, SentenceResponse, SubmitSentenceRequest, SubmitSentenceResponse
from app.database import get_db
from app.utils.openai import translate_sentence
from app.utils.jwt import get_current_user
from random import shuffle
from typing import List
import logging

router = APIRouter(tags=["sentence"])
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.get("/scramble", response_model=SentenceResponse)
async def get_scrambled_sentence(
    category: str,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"Fetching sentence for category: {category}, user_id: {user_id}")
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    user_language = user.learning_language
    logger.debug(f"User language: {user_language}")

    result = await db.execute(
        select(Sentence).join(Sentence.category).filter(Category.name == category)
    )
    sentences = result.scalars().all()

    if not sentences:
        logger.error(f"No sentences found for category: {category}")
        raise HTTPException(status_code=404, detail="No sentences available for this category")

    sentence = min(sentences, key=lambda s: (s.used_count, s.last_used_at or datetime.min))
    logger.debug(f"Selected sentence: {sentence.text}, id: {sentence.id}")

    result = await db.execute(
        select(SentenceTranslation).filter(
            SentenceTranslation.sentence_id == sentence.id,
            SentenceTranslation.language == user_language
        )
    )
    translation = result.scalars().first()
    if translation:
        translated_words = translation.translated_words
        translated_text = translation.translated_text
        hints = [
            {"text": hint, "usefulness": max(3 - i, 1)}
            for i, hint in enumerate(translation.hints or [])
        ]
        logger.debug(f"Using cached translation: {translated_text}, hints: {hints}")
    else:
        logger.debug(f"Translating '{sentence.text}' to {user_language}")
        translation_result = await translate_sentence(sentence.text, user_language)
        
        logger.debug(f"Translation result: {translation_result}")
        if not isinstance(translation_result, dict) or not all(key in translation_result for key in ["words", "sentence", "hints", "explanation"]):
            logger.error(f"Invalid translation result format: {translation_result}")
            raise HTTPException(status_code=500, detail="Invalid translation response")
        
        translated_words = [word.strip() for word in translation_result["words"] if word.strip() not in [",", "，"]]
        translated_text = translation_result["sentence"].strip().rstrip(",").rstrip("，")
        hints = translation_result["hints"] or []
        if not hints:
            logger.warning(f"No hints provided by translation: {translation_result}")
        hint_texts = [hint["text"] for hint in hints if isinstance(hint, dict) and "text" in hint]
        explanation = translation_result["explanation"]
        if "error" in translated_text.lower():
            logger.error("Translation service unavailable")
            raise HTTPException(status_code=500, detail="Translation service unavailable")
        
        new_translation = SentenceTranslation(
            sentence_id=sentence.id,
            language=user_language,
            translated_text=translated_text,
            translated_words=translated_words,
            hints=hint_texts,  # Store hint texts
            explanation=explanation
        )
        db.add(new_translation)
        await db.commit()
        logger.debug(f"Cached translation: {translated_text}, hints: {hints}, explanation: {explanation}")

    shuffled_words = translated_words.copy()
    shuffle(shuffled_words)

    sentence.used_count += 1
    sentence.last_used_at = datetime.utcnow()
    db.add(sentence)
    await db.commit()

    if all(s.used_count > 10 for s in sentences):
        logger.debug("Resetting used_count for all sentences")
        for s in sentences:
            s.used_count = 0
        db.add_all(sentences)
        await db.commit()

    logger.debug(f"Returning scrambled sentence: {shuffled_words}, hints: {hints}")
    return {
        "scrambled_words": shuffled_words,
        "original_sentence": translated_text,
        "sentence_id": sentence.id,
        "english_sentence": sentence.text,
        "hints": hints
    }

@router.post("/submit", response_model=SubmitSentenceResponse)
async def submit_sentence(
    request: SubmitSentenceRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"Submitting sentence: user_answer='{request.user_answer}', original='{request.original_sentence}', sentence_id={request.sentence_id}")
    
    # Fetch the sentence
    query = select(Sentence).where(Sentence.id == request.sentence_id)
    result = await db.execute(query)
    sentence = result.scalar_one_or_none()
    if not sentence:
        logger.error(f"Sentence not found for ID: {request.sentence_id}")
        raise HTTPException(status_code=404, detail="Sentence not found")

    # Fetch the translation
    query = select(SentenceTranslation).where(
        SentenceTranslation.sentence_id == request.sentence_id
    )
    result = await db.execute(query)
    translation = result.scalar_one_or_none()
    if not translation:
        logger.error(f"Translation not found for sentence ID: {request.sentence_id}")
        raise HTTPException(status_code=404, detail="Translation not found")

    # Fetch user to determine language
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    is_japanese = user.learning_language == 'Japanese'

    # Normalize user answer and translated text
    def normalize_text(text: str, is_japanese: bool = False) -> str:
        # Replace full-width spaces and other whitespace with regular space
        text = text.replace('\u3000', ' ').replace('\t', ' ').replace('\n', ' ')
        # Remove punctuation and normalize spaces
        text = text.strip().replace(',', '').replace('.', '').replace('!', '').replace('?', '')
        if is_japanese:
            # Remove all spaces for Japanese text
            text = ''.join(text.split())
        else:
            # Preserve single spaces for other languages
            text = ' '.join(text.split())
        return text.lower()  # Lowercase for consistency (no effect on Japanese)

    user_answer_normalized = normalize_text(request.user_answer, is_japanese)
    translated_text_normalized = normalize_text(translation.translated_text, is_japanese)
    
    # Log raw bytes and normalized strings for debugging
    logger.debug(f"User answer raw: '{request.user_answer}', bytes: {[ord(c) for c in request.user_answer]}")
    logger.debug(f"Translated text raw: '{translation.translated_text}', bytes: {[ord(c) for c in translation.translated_text]}")
    logger.debug(f"Comparison: user_answer_normalized='{user_answer_normalized}', translated_text_normalized='{translated_text_normalized}', is_correct={user_answer_normalized == translated_text_normalized}")
    
    # Check if the user's answer is correct
    is_correct = user_answer_normalized == translated_text_normalized
    feedback = (
        "Correct! Well done."
        if is_correct
        else f"Incorrect. The correct sentence is: {translation.translated_text}"
    )

    # Save the result
    result = UserSentenceResult(
        user_id=user_id,
        sentence_id=request.sentence_id,
        translated_sentence=translation.translated_text,
        user_answer=request.user_answer,
        is_correct=is_correct,
        feedback=feedback,
        is_pinned=False
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)

    # Construct response manually for logging
    response_dict = {
        "is_correct": result.is_correct,
        "feedback": result.feedback,
        "translated_sentence": result.translated_sentence,
        "result_id": result.id,
        "is_pinned": result.is_pinned,
        "explanation": translation.explanation,
        "sentence_id": result.sentence_id,
        "user_answer": result.user_answer
    }
    logger.debug(f"Submit response: {response_dict}")
    
    return SubmitSentenceResponse(
        is_correct=result.is_correct,
        feedback=result.feedback,
        translated_sentence=result.translated_sentence,
        result_id=result.id,
        explanation=translation.explanation,
        sentence_id=result.sentence_id,
        user_answer=result.user_answer
    )

@router.patch("/result/{result_id}/pin")
async def toggle_pin(
    result_id: int,
    pin_data: PinRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"toggle_pin: Received request: result_id={result_id}, payload={pin_data}")
    query = select(UserSentenceResult).where(
        UserSentenceResult.id == result_id,
        UserSentenceResult.user_id == user_id
    )
    result = await db.execute(query)
    sentence_result = result.scalar_one_or_none()
    if not sentence_result:
        logger.error(f"toggle_pin: Result not found for result_id={result_id}")
        raise HTTPException(status_code=404, detail="Result not found")

    sentence_id = sentence_result.sentence_id
    if not sentence_id:
        logger.error(f"toggle_pin: No sentence_id for result_id={result_id}")
        raise HTTPException(status_code=400, detail="sentence_id required")

    # Fetch all results for this sentence_id
    all_results_query = select(UserSentenceResult).where(
        UserSentenceResult.sentence_id == sentence_id,
        UserSentenceResult.user_id == user_id
    )
    all_results = await db.execute(all_results_query)
    all_results = all_results.scalars().all()

    if pin_data.is_pinned:
        # Unpin all other results, pin this one
        for other_result in all_results:
            if other_result.id != result_id:
                other_result.is_pinned = False
                logger.debug(f"toggle_pin: Unpinned result_id={other_result.id}")
        sentence_result.is_pinned = True
    else:
        # Unpin all results for this sentence
        for other_result in all_results:
            other_result.is_pinned = False
            logger.debug(f"toggle_pin: Unpinned result_id={other_result.id}")

    await db.commit()
    await db.refresh(sentence_result)
    logger.debug(f"toggle_pin: result_id={result_id}, sentence_id={sentence_id}, is_pinned={sentence_result.is_pinned}")
    return {"is_pinned": sentence_result.is_pinned}

@router.get("/results/pinned", response_model=List[SubmitSentenceResponse])
async def get_pinned_results(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(UserSentenceResult).where(
        UserSentenceResult.user_id == user_id,
        UserSentenceResult.is_pinned
    )
    result = await db.execute(query)
    pinned_results = result.scalars().all()
    responses = []
    for r in pinned_results:
        query = select(SentenceTranslation).where(
            SentenceTranslation.sentence_id == r.sentence_id
        )
        translation_result = await db.execute(query)
        translation = translation_result.scalar_one_or_none()
        if not translation:
            logger.error(f"Translation not found for sentence_id: {r.sentence_id}")
            continue
        responses.append(
            SubmitSentenceResponse(
                is_correct=r.is_correct,
                feedback=r.feedback,
                translated_sentence=r.translated_sentence,
                result_id=r.id,
                is_pinned=r.is_pinned,
                explanation=translation.explanation,
                sentence_id=r.sentence_id,
                user_answer=r.user_answer
            )
        )
    print(f"Pinned results returned: {len(responses)}")
    return responses