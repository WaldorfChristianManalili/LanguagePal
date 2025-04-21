from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging
from app.models.flashcard import Flashcard
from app.models.user import User
from app.models.category import Category
from app.models.lesson import Lesson
from app.models.flashcard_history import FlashcardHistory
from app.schemas.flashcard import FlashcardResponse
from app.database import get_db
from app.utils.openai import generate_flashcard
from app.utils.jwt import get_current_user

# Suppress SQLAlchemy logs
for logger_name in ['sqlalchemy', 'sqlalchemy.engine', 'sqlalchemy.orm', 'sqlalchemy.pool', 'sqlalchemy.dialects']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["flashcard"])

async def get_user(db: AsyncSession, user_id: int) -> User:
    """Fetch user by ID, raising 404 if not found."""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User not found for user_id: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def is_repeated_lesson(db: AsyncSession, user_id: int, lesson_id: int) -> bool:
    """Check if the user has previously completed this lesson."""
    result = await db.execute(
        select(FlashcardHistory).filter(
            FlashcardHistory.user_id == user_id,
            FlashcardHistory.lesson_id == lesson_id
        )
    )
    is_repeat = bool(result.scalars().first())
    logger.info(f"Lesson {lesson_id} for user {user_id} is_repeat: {is_repeat}")
    return is_repeat

async def get_used_flashcard_words(db: AsyncSession, user_id: int, lesson_id: int) -> set:
    """Get words of flashcards used by the user in the current lesson."""
    query = select(Flashcard.word).join(
        FlashcardHistory,
        FlashcardHistory.flashcard_id == Flashcard.id
    ).filter(
        FlashcardHistory.user_id == user_id,
        FlashcardHistory.lesson_id == lesson_id
    )
    result = await db.execute(query)
    used_words = set(result.scalars().all())
    logger.info(f"Used words for user {user_id}, lesson {lesson_id}: {used_words}")
    return used_words

async def get_valid_flashcard_data(category: Category, user_language: str, lesson_name: str, db: AsyncSession, user_id: int, lesson_id: int, word: str = None) -> dict:
    """Generate a valid flashcard, avoiding duplicates for new lessons."""
    used_words = await get_used_flashcard_words(db, user_id, lesson_id)
    try:
        logger.info(f"Generating flashcard for category {category.name}, lesson {lesson_name}, word: {word}")
        flashcard_data = await generate_flashcard(
            category=category.name,
            target_language=user_language,
            category_id=category.id,
            lesson_name=lesson_name,
            db=db,
            user_id=user_id,
            word=word
        )
        if "Error" in flashcard_data["word"]:
            logger.error(f"Flashcard generation returned error: {flashcard_data['word']}")
            raise HTTPException(status_code=500, detail="Failed to generate flashcard")
        if flashcard_data["word"] not in used_words or await is_repeated_lesson(db, user_id, lesson_id):
            logger.info(f"Generated valid flashcard: {flashcard_data['word']}")
            return flashcard_data
        logger.error(f"Generated flashcard {flashcard_data['word']} already used")
        raise HTTPException(status_code=500, detail="Failed to generate unique flashcard")
    except HTTPException as e:
        logger.error(f"Flashcard generation failed: {str(e.detail)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in flashcard generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate flashcard")

@router.get("/generate", response_model=FlashcardResponse)
async def get_flashcard(
    lesson_id: int,
    lesson_name: str,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a flashcard for the given lesson."""
    logger.info(f"Generating flashcard for lesson_id: {lesson_id}, lesson_name: {lesson_name}, user_id: {user_id}")
    try:
        user = await get_user(db, user_id)
        user_language = user.learning_language or "Japanese"

        # Fetch lesson and category
        result = await db.execute(select(Lesson).filter(Lesson.id == lesson_id))
        lesson = result.scalars().first()
        if not lesson:
            logger.error(f"Lesson not found for lesson_id: {lesson_id}")
            raise HTTPException(status_code=404, detail="Lesson not found")

        result = await db.execute(select(Category).filter(Category.id == lesson.category_id))
        category = result.scalars().first()
        if not category:
            logger.error(f"Category not found for lesson_id: {lesson_id}")
            raise HTTPException(status_code=404, detail="Category not found")

        # Generate flashcard
        flashcard_data = await get_valid_flashcard_data(category, user_language, lesson_name, db, user_id, lesson_id)
        flashcard_id = flashcard_data["flashcard_id"]
        if flashcard_id:  # Flashcard was saved by generate_flashcard
            history = FlashcardHistory(
                user_id=user_id,
                flashcard_id=flashcard_id,
                lesson_id=lesson_id
            )
            db.add(history)
            await db.commit()
        logger.info(f"Generated flashcard for lesson_id: {lesson_id}, word: {flashcard_data['word']}")
        return {
            "flashcard_id": flashcard_id,
            "word": flashcard_data["word"],
            "translation": flashcard_data["translation"],
            "type": flashcard_data["type"],
            "english_equivalents": flashcard_data["english_equivalents"],
            "definition": flashcard_data["definition"],
            "english_definition": flashcard_data["english_definition"],
            "example_sentence": flashcard_data["example_sentence"],
            "english_sentence": flashcard_data["english_sentence"],
            "category": category.name,
            "lesson_id": lesson_id,
            "options": flashcard_data["options"],
        }
    except HTTPException as e:
        logger.error(f"HTTP error in get_flashcard: {str(e.detail)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_flashcard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate flashcard")