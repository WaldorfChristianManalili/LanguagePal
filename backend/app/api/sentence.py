import logging
import random
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.sentence import Sentence, SentenceTranslation
from app.models.user import User
from app.models.category import Category
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.models.flashcard import Flashcard
from app.schemas.sentence import SentenceResponse, SubmitSentenceRequest, SubmitSentenceResponse
from app.database import get_db
from app.utils.openai import translate_sentence
from app.utils.jwt import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["sentence"])

async def get_user(db: AsyncSession, user_id: int) -> User:
    """Fetch user by ID, raising 404 if not found."""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_translation(db: AsyncSession, sentence_id: int, language: str, flashcard_words: list[str] = None) -> SentenceTranslation:
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

    # Use flashcard words if provided, otherwise fetch category
    result = await db.execute(select(Category).filter(Category.id == sentence.category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    sentence_prompt = (
        f"A simple sentence using the words {', '.join(flashcard_words)}" if flashcard_words
        else f"A simple, grammatically correct sentence about {category.name}"
    )
    translation_result = await translate_sentence(sentence_prompt, language)
    logger.info(f"Translation result for sentence_id {sentence_id}: {translation_result}")

    if not isinstance(translation_result, dict) or not all(key in translation_result for key in ["words", "sentence", "hints", "explanation"]):
        logger.error(f"Invalid translation response: {translation_result}")
        raise HTTPException(status_code=500, detail="Invalid translation response")
    if "error" in translation_result["sentence"].lower():
        logger.error(f"Translation service error: {translation_result['sentence']}")
        raise HTTPException(status_code=500, detail="Translation service unavailable")

    translated_words = [word.strip() for word in translation_result["words"] if word.strip() not in [",", "，"]]
    translated_text = translation_result["sentence"].strip().rstrip(",").rstrip("，")
    
    # Validate sentence: Ensure it has at least 2 words and is not just greetings
    if len(translated_words) < 2:
        logger.error(f"Sentence too short: {translated_text}")
        raise HTTPException(status_code=500, detail="Generated sentence is too short")
    if all(word in ["こんにちは", "おはよう", "こんばんは"] for word in translated_words):
        logger.error(f"Invalid sentence, contains only greetings: {translated_text}")
        raise HTTPException(status_code=500, detail="Generated sentence is invalid")

    hints = [hint for hint in translation_result["hints"] if isinstance(hint, dict) and "text" in hint]
    explanation = translation_result["explanation"] or "No explanation available"

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
            translated_words=json.dumps(translated_words),
            hints=json.dumps(hints),
            explanation=explanation
        )
        db.add(translation)
        await db.commit()
    return translation

async def get_scrambled_sentence(
    category_name: str,
    user_id: int,
    db: AsyncSession,
    flashcard_words: str = None,
    sentence_id: int = None,
    harder: bool = False
):
    """Generate a scrambled sentence for the given category and user."""
    logger.info(f"Generating scrambled sentence for category: {category_name}, user: {user_id}, sentence_id: {sentence_id}, flashcard_words: {flashcard_words}, harder: {harder}")
    user = await get_user(db, user_id)
    user_language = user.learning_language

    # Parse flashcard words
    flashcard_words_list = [word.strip() for word in flashcard_words.split(",")] if flashcard_words else []

    # Validate flashcard words
    if flashcard_words_list:
        for word in flashcard_words_list:
            result = await db.execute(select(Flashcard).filter(Flashcard.word == word))
            flashcard = result.scalars().first()
            if not flashcard:
                logger.error(f"Flashcard not found: {word}")
                raise HTTPException(status_code=404, detail=f"Flashcard not found: {word}")
            if ' ' in flashcard.word:
                logger.error(f"Flashcard word '{word}' is a phrase")
                raise HTTPException(status_code=400, detail=f"Flashcard word '{word}' is a phrase, expected single word")

    # Fetch category by name
    result = await db.execute(select(Category).filter(Category.name == category_name))
    category = result.scalars().first()
    if not category:
        logger.error(f"Category '{category_name}' not found")
        raise HTTPException(status_code=404, detail=f"Category '{category_name}' not found")

    # If sentence_id is provided, fetch from DB
    if sentence_id:
        result = await db.execute(select(Sentence).filter_by(id=sentence_id))
        sentence = result.scalars().first()
        if not sentence:
            logger.error(f"Sentence with ID {sentence_id} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Sentence not found")
        
        translation = await get_translation(db, sentence.id, user_language, flashcard_words_list)
        shuffled_words = json.loads(translation.translated_words)
        random.shuffle(shuffled_words)
        response = {
            "sentence_id": sentence.id,
            "scrambled_words": shuffled_words,
            "original_sentence": translation.translated_text,  # Japanese sentence
            "english_sentence": sentence.text,  # English sentence (source)
            "hints": [{"text": hint["text"], "usefulness": hint["usefulness"]} for hint in json.loads(translation.hints or "[]")],
            "explanation": translation.explanation if translation.explanation else "No explanation available"
        }
        logger.info(f"Returning scrambled sentence for sentence_id {sentence_id}: {response}")
        return response

    # Fetch sentences for category
    result = await db.execute(
        select(Sentence).filter(Sentence.category_id == category.id)
    )
    sentences = result.scalars().all()

    # Generate new sentence if none exist
    if not sentences:
        sentence_prompt = (
            f"A simple sentence using the words {', '.join(flashcard_words_list)}" if flashcard_words_list
            else f"A simple, grammatically correct sentence about {category_name}"
        )
        if harder:
            sentence_prompt = f"A more complex sentence about {category_name}, incorporating {', '.join(flashcard_words_list)} if provided"
        
        translation_result = await translate_sentence(sentence_prompt, user_language)
        logger.info(f"New sentence translation result: {translation_result}")

        if "error" in translation_result["sentence"].lower():
            logger.error(f"Failed to generate sentence: {translation_result['sentence']}")
            raise HTTPException(status_code=500, detail="Failed to generate sentence")
        
        # Validate translation
        translated_text = translation_result.get("translated_text", "").strip()
        source_text = translation_result.get("sentence", "").strip()
        if not translated_text or not source_text:
            logger.error(f"Invalid translation result: {translation_result}")
            raise HTTPException(status_code=500, detail="Failed to generate valid translation")

        sentence = Sentence(
            text=source_text,  # Store source (English) sentence
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
    translation = await get_translation(db, sentence.id, user_language, flashcard_words_list)
    shuffled_words = json.loads(translation.translated_words)
    random.shuffle(shuffled_words)

    # Update sentence usage
    sentence.used_count += 1
    sentence.last_used_at = datetime.utcnow()
    db.add(sentence)

    # Reset used_count if all sentences are heavily used
    if all(s.used_count > 10 for s in sentences):
        for s in sentences:
            s.used_count = 0
        db.add_all(sentences)

    try:
        await db.commit()
    except Exception as e:
        logger.error(f"Database commit failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save sentence data")

    response = {
        "sentence_id": sentence.id,
        "scrambled_words": shuffled_words,
        "original_sentence": translation.translated_text,  # Japanese sentence
        "english_sentence": sentence.text,  # English sentence (source)
        "hints": [{"text": hint["text"], "usefulness": hint["usefulness"]} for hint in json.loads(translation.hints or "[]")],
        "explanation": translation.explanation if translation.explanation else "No explanation available"
    }
    logger.info(f"Returning scrambled sentence: {response}")
    return response

@router.get("/scramble", response_model=SentenceResponse)
async def get_scrambled_sentence_route(
    lesson_id: int,
    flashcard_words: str = None,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """API endpoint to get a scrambled sentence for a lesson."""
    result = await db.execute(select(Lesson).filter(Lesson.id == lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    result = await db.execute(select(Category).filter(Category.id == lesson.category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return await get_scrambled_sentence(category.name, user_id, db, flashcard_words)

@router.post("/submit", response_model=SubmitSentenceResponse)
async def submit_sentence(
    request: SubmitSentenceRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a user's sentence attempt and evaluate it."""
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
        result=json.dumps(result_data)
    )
    db.add(progress)
    await db.commit()

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "Translated_sentence": translation.translated_text,
        "result_id": progress.id,
        "is_pinned": False,
        "explanation": translation.explanation,
        "sentence_id": request.sentence_id,
        "user_answer": request.user_answer
    }