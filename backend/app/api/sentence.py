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

router = APIRouter(tags=["sentence"])

async def get_user(db: AsyncSession, user_id: int) -> User:
    """Fetch user by ID, raising 404 if not found."""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_translation(db: AsyncSession, sentence_id: int, language: str) -> SentenceTranslation:
    """Fetch or create translation for a sentence, handling race conditions."""
    # Fetch sentence
    result = await db.execute(select(Sentence).filter(Sentence.id == sentence_id))
    sentence = result.scalars().first()
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    # Check for existing translation
    result = await db.execute(
        select(SentenceTranslation).filter(
            SentenceTranslation.sentence_id == sentence_id,
            SentenceTranslation.language == language
        )
    )
    translation = result.scalars().first()
    if translation:
        return translation

    # Translate if not found
    translation_result = await translate_sentence(sentence.text, language)
    if not isinstance(translation_result, dict) or not all(key in translation_result for key in ["words", "sentence", "hints", "explanation"]):
        raise HTTPException(status_code=500, detail="Invalid translation response")
    if "error" in translation_result["sentence"].lower():
        raise HTTPException(status_code=500, detail="Translation service unavailable")

    translated_words = [word.strip() for word in translation_result["words"] if word.strip() not in [",", "，"]]
    translated_text = translation_result["sentence"].strip().rstrip(",").rstrip("，")
    hints = [hint["text"] for hint in translation_result["hints"] if isinstance(hint, dict) and "text" in hint]

    # Check again to avoid race conditions
    result = await db.execute(
        select(SentenceTranslation).filter(
            SentenceTranslation.sentence_id == sentence_id,
            SentenceTranslation.language == language
        )
    )
    translation = result.scalars().first()
    if not translation:
        translation = SentenceTranslation(
            sentence_id=sentence_id,
            language=language,
            translated_text=translated_text,
            translated_words=translated_words,
            hints=hints,
            explanation=translation_result["explanation"]
        )
        db.add(translation)
        await db.commit()
    return translation

@router.get("/scramble", response_model=SentenceResponse)
async def get_scrambled_sentence(
    category: str,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, user_id)
    user_language = user.learning_language

    # Fetch sentences for category
    result = await db.execute(
        select(Sentence).join(Sentence.category).filter(Category.name == category)
    )
    sentences = result.scalars().all()
    if not sentences:
        raise HTTPException(status_code=404, detail="No sentences available for this category")

    # Select least-used sentence
    sentence = min(sentences, key=lambda s: (s.used_count, s.last_used_at or datetime.min))

    # Get or create translation
    translation = await get_translation(db, sentence.id, user_language)
    shuffled_words = translation.translated_words.copy()
    shuffle(shuffled_words)

    # Update sentence usage
    sentence.used_count += 1
    sentence.last_used_at = datetime.utcnow()
    db.add(sentence)

    # Reset used_count if all sentences are heavily used
    if all(s.used_count > 10 for s in sentences):
        for s in sentences:
            s.used_count = 0
        db.add_all(sentences)

    await db.commit()

    return {
        "scrambled_words": shuffled_words,
        "original_sentence": translation.translated_text,
        "sentence_id": sentence.id,
        "english_sentence": sentence.text,
        "hints": [{"text": hint, "usefulness": max(3 - i, 1)} for i, hint in enumerate(translation.hints or [])]
    }

@router.post("/submit", response_model=SubmitSentenceResponse)
async def submit_sentence(
    request: SubmitSentenceRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    def normalize_text(text: str) -> str:
        """Normalize text by removing whitespace, punctuation, and converting to lowercase."""
        text = text.replace('\u3000', ' ').replace('\t', ' ').replace('\n', ' ').strip()
        text = text.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
        return ''.join(text.split()).lower()

    # Fetch user, sentence, and translation
    user = await get_user(db, user_id)
    result = await db.execute(select(Sentence).filter(Sentence.id == request.sentence_id))
    sentence = result.scalars().first()
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    translation = await get_translation(db, request.sentence_id, user.learning_language)

    # Normalize and compare
    user_answer_normalized = normalize_text(request.user_answer)
    translated_text_normalized = normalize_text(translation.translated_text)
    is_correct = user_answer_normalized == translated_text_normalized
    feedback = (
        "Correct! Well done." if is_correct
        else f"Incorrect. The correct sentence is: {translation.translated_text}"
    )

    # Update or create result
    result = await db.execute(
        select(UserSentenceResult).filter(
            UserSentenceResult.user_id == user_id,
            UserSentenceResult.sentence_id == request.sentence_id
        )
    )
    user_result = result.scalars().first()
    if user_result:
        user_result.user_answer = request.user_answer
        user_result.is_correct = is_correct
        user_result.feedback = feedback
        user_result.translated_sentence = translation.translated_text
        user_result.attempted_at = datetime.utcnow()
    else:
        user_result = UserSentenceResult(
            user_id=user_id,
            sentence_id=request.sentence_id,
            translated_sentence=translation.translated_text,
            user_answer=request.user_answer,
            is_correct=is_correct,
            feedback=feedback,
            is_pinned=False,
            attempted_at=datetime.utcnow()
        )
        db.add(user_result)

    await db.commit()
    await db.refresh(user_result)

    return {
        "is_correct": user_result.is_correct,
        "feedback": user_result.feedback,
        "translated_sentence": user_result.translated_sentence,
        "result_id": user_result.id,
        "is_pinned": user_result.is_pinned,
        "explanation": translation.explanation,
        "sentence_id": user_result.sentence_id,
        "user_answer": user_result.user_answer
    }

@router.patch("/result/{result_id}/pin")
async def toggle_pin(
    result_id: int,
    pin_data: PinRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch the specific result
    result = await db.execute(
        select(UserSentenceResult).filter(
            UserSentenceResult.id == result_id,
            UserSentenceResult.user_id == user_id
        )
    )
    sentence_result = result.scalars().first()
    if not sentence_result:
        raise HTTPException(status_code=404, detail="Result not found")

    # Fetch all results for the same sentence
    result = await db.execute(
        select(UserSentenceResult).filter(
            UserSentenceResult.sentence_id == sentence_result.sentence_id,
            UserSentenceResult.user_id == user_id
        )
    )
    all_results = result.scalars().all()

    # Update pin status
    for other_result in all_results:
        other_result.is_pinned = (other_result.id == result_id) and pin_data.is_pinned
    db.add_all(all_results)
    await db.commit()

    await db.refresh(sentence_result)
    return {"is_pinned": sentence_result.is_pinned}

@router.get("/results/pinned", response_model=List[SubmitSentenceResponse])
async def get_pinned_results(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, user_id)
    user_language = user.learning_language

    result = await db.execute(
        select(UserSentenceResult).filter(
            UserSentenceResult.user_id == user_id,
            UserSentenceResult.is_pinned
        )
    )
    pinned_results = result.scalars().all()

    responses = []
    for result in pinned_results:
        translation = await get_translation(db, result.sentence_id, user_language)
        responses.append(
            SubmitSentenceResponse(
                is_correct=result.is_correct,
                feedback=result.feedback,
                translated_sentence=result.translated_sentence,
                result_id=result.id,
                is_pinned=result.is_pinned,
                explanation=translation.explanation,
                sentence_id=result.sentence_id,
                user_answer=result.user_answer
            )
        )
    return responses