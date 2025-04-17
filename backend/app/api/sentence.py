from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.sentence import Sentence, SentenceTranslation, UserSentenceResult
from app.models.user import User
from app.models.category import Category
from app.schemas.sentence import SentenceResponse, SubmitSentenceRequest, SubmitSentenceResponse
from app.database import get_db
from app.utils.openai import translate_sentence
from app.utils.jwt import get_current_user
from random import shuffle
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
        logger.debug(f"Using cached translation: {translated_text}")
    else:
        logger.debug(f"Translating '{sentence.text}' to {user_language}")
        translation_result = await translate_sentence(sentence.text, user_language)
        
        logger.debug(f"Translation result: {translation_result}")
        if not isinstance(translation_result, dict) or "words" not in translation_result or "sentence" not in translation_result:
            logger.error(f"Invalid translation result format: {translation_result}")
            raise HTTPException(status_code=500, detail="Invalid translation response")
        
        translated_words = [word.strip() for word in translation_result["words"] if word.strip() not in [",", "，"]]
        translated_text = translation_result["sentence"].strip().rstrip(",").rstrip("，")
        if "error" in translated_text.lower():
            logger.error("Translation service unavailable")
            raise HTTPException(status_code=500, detail="Translation service unavailable")
        
        new_translation = SentenceTranslation(
            sentence_id=sentence.id,
            language=user_language,
            translated_text=translated_text,
            translated_words=translated_words
        )
        db.add(new_translation)
        await db.commit()
        logger.debug(f"Cached translation: {translated_text}")

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

    logger.debug(f"Returning scrambled sentence: {shuffled_words}")
    return {
        "scrambled_words": shuffled_words,
        "original_sentence": translated_text,
        "sentence_id": sentence.id,
    }

@router.post("/submit", response_model=SubmitSentenceResponse)
async def submit_sentence(
    request: SubmitSentenceRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.debug(f"Submitting sentence: {request.constructed_sentence}, user_id: {user_id}, original: {request.original_sentence}")
    
    result = await db.execute(select(Sentence).filter(Sentence.id == request.sentence_id))
    sentence = result.scalars().first()
    if not sentence:
        logger.error(f"Sentence not found: {request.sentence_id}")
        raise HTTPException(status_code=404, detail="Sentence not found")

    # Normalize by removing spaces, commas, and extra punctuation
    constructed_sentence = request.constructed_sentence.strip().replace(" ", "").replace(",", "").replace("，", "")
    original_sentence = request.original_sentence.strip().replace(" ", "").replace(",", "").replace("，", "")
    
    is_correct = constructed_sentence.lower() == original_sentence.lower()
    feedback = "Correct!" if is_correct else f"Incorrect. The correct sentence is: {request.original_sentence}"

    result = UserSentenceResult(
        user_id=user_id,
        sentence_id=request.sentence_id,
        translated_sentence=original_sentence,
        user_answer=constructed_sentence,
        is_correct=is_correct,
        feedback=feedback,
        is_pinned=False,
        attempted_at=datetime.utcnow(),
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)

    logger.debug(f"Submission result: is_correct={is_correct}, result_id={result.id}, normalized: {constructed_sentence} vs {original_sentence}")
    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "correct_sentence": original_sentence if not is_correct else "",
        "result_id": result.id,
        "is_pinned": result.is_pinned,
    }