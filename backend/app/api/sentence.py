from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.sentence import Sentence, SentenceTranslation
from app.models.user import User
from app.models.category import Category
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.schemas.sentence import SentenceResponse, SubmitSentenceRequest, SubmitSentenceResponse
from app.database import get_db
from app.utils.openai import translate_sentence
from app.utils.jwt import get_current_user
from random import shuffle

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
    result = await db.execute(select(Sentence).filter(Sentence.id == sentence_id))
    sentence = result.scalars().first()
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    result = await db.execute(
        select(SentenceTranslation).filter(
            SentenceTranslation.sentence_id == sentence_id,
            SentenceTranslation.language == language
        )
    )
    translation = result.scalars().first()
    if translation:
        return translation

    translation_result = await translate_sentence(f"A simple sentence about {sentence.category.name}", language)
    if not isinstance(translation_result, dict) or not all(key in translation_result for key in ["words", "sentence", "hints", "explanation"]):
        raise HTTPException(status_code=500, detail="Invalid translation response")
    if "error" in translation_result["sentence"].lower():
        raise HTTPException(status_code=500, detail="Translation service unavailable")

    translated_words = [word.strip() for word in translation_result["words"] if word.strip() not in [",", "，"]]
    translated_text = translation_result["sentence"].strip().rstrip(",").rstrip("，")
    hints = [hint["text"] for hint in translation_result["hints"] if isinstance(hint, dict) and "text" in hint]

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
    lesson_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, user_id)
    user_language = user.learning_language

    # Fetch lesson and category
    result = await db.execute(select(Lesson).filter(Lesson.id == lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    result = await db.execute(select(Category).filter(Category.id == lesson.category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Fetch sentences for category
    result = await db.execute(
        select(Sentence).filter(Sentence.category_id == category.id)
    )
    sentences = result.scalars().all()

    # Generate new sentence if none exist
    if not sentences:
        translation_result = await translate_sentence(f"A simple sentence about {category.name}", user_language)
        if "error" in translation_result["sentence"].lower():
            raise HTTPException(status_code=500, detail="Failed to generate sentence")
        
        sentence = Sentence(
            text=translation_result["sentence"],
            category_id=category.id,
            used_count=0,
            last_used_at=None
        )
        db.add(sentence)
        await db.commit()
        await db.refresh(sentence)
        sentences = [sentence]

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

    # Store result in progress
    result_data = {
        "is_correct": is_correct,
        "feedback": feedback,
        "translated_sentence": translation.translated_text,
        "user_answer": request.user_answer,
        "explanation": translation.explanation,
        "sentence_id": request.sentence_id
    }
    progress = Progress(
        user_id=user_id,
        category_id=sentence.category_id,
        activity_id=f"sentence-{request.sentence_id}",
        type="sentence",
        completed=True,
        result=str(result_data)
    )
    db.add(progress)
    await db.commit()

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "translated_sentence": translation.translated_text,
        "result_id": progress.id,
        "is_pinned": False,
        "explanation": translation.explanation,
        "sentence_id": request.sentence_id,
        "user_answer": request.user_answer
    }