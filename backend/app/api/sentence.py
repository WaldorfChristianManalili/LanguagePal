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

    # Check for existing translation
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
        
        if not isinstance(translation_result, dict) or not all(key in translation_result for key in ["words", "sentence", "hints", "explanation"]):
            logger.error(f"Invalid translation result format: {translation_result}")
            raise HTTPException(status_code=500, detail="Invalid translation response")
        
        translated_words = [word.strip() for word in translation_result["words"] if word.strip() not in [",", "，"]]
        translated_text = translation_result["sentence"].strip().rstrip(",").rstrip("，")
        hints = translation_result["hints"] or []
        hint_texts = [hint["text"] for hint in hints if isinstance(hint, dict) and "text" in hint]
        explanation = translation_result["explanation"]
        if "error" in translated_text.lower():
            logger.error("Translation service unavailable")
            raise HTTPException(status_code=500, detail="Translation service unavailable")
        
        # Check again before inserting to avoid race conditions
        result = await db.execute(
            select(SentenceTranslation).filter(
                SentenceTranslation.sentence_id == sentence.id,
                SentenceTranslation.language == user_language
            )
        )
        translation = result.scalars().first()
        if not translation:
            new_translation = SentenceTranslation(
                sentence_id=sentence.id,
                language=user_language,
                translated_text=translated_text,
                translated_words=translated_words,
                hints=hint_texts,
                explanation=explanation
            )
            db.add(new_translation)
            await db.commit()
            translation = new_translation
            logger.debug(f"Cached translation: {translated_text}, hints: {hints}, explanation: {explanation}")
        else:
            logger.debug(f"Translation already exists: {translation.translated_text}")
            translated_words = translation.translated_words
            translated_text = translation.translated_text
            hints = [
                {"text": hint, "usefulness": max(3 - i, 1)}
                for i, hint in enumerate(translation.hints or [])
            ]

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
    
    # Fetch user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    user_language = user.learning_language
    logger.debug(f"User language: {user_language}")

    # Fetch sentence
    query = select(Sentence).where(Sentence.id == request.sentence_id)
    result = await db.execute(query)
    sentence = result.scalar_one_or_none()
    if not sentence:
        logger.error(f"Sentence not found for ID: {request.sentence_id}")
        raise HTTPException(status_code=404, detail="Sentence not found")

    # Fetch translation
    query = select(SentenceTranslation).where(
        SentenceTranslation.sentence_id == request.sentence_id,
        SentenceTranslation.language == user_language
    )
    result = await db.execute(query)
    translation = result.scalar_one_or_none()
    if not translation:
        logger.error(f"Translation not found for sentence ID: {request.sentence_id}, language: {user_language}")
        raise HTTPException(status_code=404, detail="Translation not found for this language")

    # Normalize user answer and translated text
    is_japanese = user_language == 'Japanese'
    def normalize_text(text: str, is_japanese: bool = False) -> str:
        text = text.replace('\u3000', ' ').replace('\t', ' ').replace('\n', ' ')
        text = text.strip().replace(',', '').replace('.', '').replace('!', '').replace('?','')
        if is_japanese:
            text = ''.join(text.split())
        else:
            text = ' '.join(text.split())
        return text.lower()

    user_answer_normalized = normalize_text(request.user_answer, is_japanese)
    translated_text_normalized = normalize_text(translation.translated_text, is_japanese)
    
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

    # Check for existing submission
    existing_result = await db.execute(
        select(UserSentenceResult).where(
            UserSentenceResult.user_id == user_id,
            UserSentenceResult.sentence_id == request.sentence_id
        )
    )
    result = existing_result.scalars().first()
    if result:
        # Update existing result
        logger.debug(f"Updating existing UserSentenceResult: user_id={user_id}, sentence_id={request.sentence_id}")
        result.user_answer = request.user_answer
        result.is_correct = is_correct
        result.feedback = feedback
        result.translated_sentence = translation.translated_text
        result.attempted_at = datetime.utcnow()
        # Preserve is_pinned state
    else:
        # Create new result
        logger.debug(f"Creating new UserSentenceResult: user_id={user_id}, sentence_id={request.sentence_id}")
        result = UserSentenceResult(
            user_id=user_id,
            sentence_id=request.sentence_id,
            translated_sentence=translation.translated_text,
            user_answer=request.user_answer,
            is_correct=is_correct,
            feedback=feedback,
            is_pinned=False,
            attempted_at=datetime.utcnow()
        )
        db.add(result)

    await db.commit()
    await db.refresh(result)

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
    
    return SubmitSentenceResponse(**response_dict)

@router.patch("/result/{result_id}/pin")
async def toggle_pin(
    result_id: int,
    pin_data: PinRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(UserSentenceResult).where(
        UserSentenceResult.id == result_id,
        UserSentenceResult.user_id == user_id
    )
    result = await db.execute(query)
    sentence_result = result.scalar_one()  # Expect exactly one result
    if not sentence_result:
        raise HTTPException(status_code=404, detail="Result not found")

    sentence_id = sentence_result.sentence_id
    if not sentence_id:
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
        sentence_result.is_pinned = True
    else:
        # Unpin all results for this sentence
        for other_result in all_results:
            other_result.is_pinned = False

    await db.commit()
    await db.refresh(sentence_result)
    return {"is_pinned": sentence_result.is_pinned}

@router.get("/results/pinned", response_model=List[SubmitSentenceResponse])
async def get_pinned_results(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Fetch user to get learning_language
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_language = user.learning_language

    query = select(UserSentenceResult).where(
        UserSentenceResult.user_id == user_id,
        UserSentenceResult.is_pinned
    )
    result = await db.execute(query)
    pinned_results = result.scalars().all()
    responses = []
    for r in pinned_results:
        query = select(SentenceTranslation).where(
            SentenceTranslation.sentence_id == r.sentence_id,
            SentenceTranslation.language == user_language
        )
        translation_result = await db.execute(query)
        translation = translation_result.scalar_one_or_none()
        if not translation:
            logger.warning(f"Translation not found for sentence_id: {r.sentence_id}, language: {user_language}")
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
    logger.debug(f"Pinned results returned: {len(responses)}")
    return responses