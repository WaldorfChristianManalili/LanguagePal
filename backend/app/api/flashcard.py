from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.flashcard import Flashcard
from app.models.user import User
from app.models.category import Category
from app.models.lesson import Lesson
from app.models.flashcard_history import FlashcardHistory
from app.schemas.flashcard import FlashcardResponse
from app.database import get_db
from app.utils.openai import generate_flashcard
from app.utils.jwt import get_current_user

router = APIRouter(tags=["flashcard"])

async def get_user(db: AsyncSession, user_id: int) -> User:
    """Fetch user by ID, raising 404 if not found."""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
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
    return bool(result.scalars().first())

async def get_used_flashcard_words(db: AsyncSession, user_id: int, lesson_id: int) -> set:
    """Get words of flashcards previously used by the user, excluding the current lesson if repeated."""
    query = select(Flashcard.word).join(
        FlashcardHistory,
        FlashcardHistory.flashcard_id == Flashcard.id
    ).filter(FlashcardHistory.user_id == user_id)
    
    if await is_repeated_lesson(db, user_id, lesson_id):
        query = query.filter(FlashcardHistory.lesson_id != lesson_id)
    
    result = await db.execute(query)
    return {word for word in result.scalars().all()}

async def get_valid_flashcard_data(category: Category, user_language: str, db: AsyncSession, user_id: int, lesson_id: int, word: str = None) -> dict:
    """Generate or fetch a valid flashcard, avoiding duplicates for new lessons."""
    used_words = await get_used_flashcard_words(db, user_id, lesson_id)
    max_attempts = 3
    for _ in range(max_attempts):
        flashcard_data = await generate_flashcard(category.name, user_language, db, word)
        if "Error" in flashcard_data["word"]:
            continue
        if flashcard_data["word"] not in used_words or await is_repeated_lesson(db, user_id, lesson_id):
            return flashcard_data
    # Try a cached flashcard
    result = await db.execute(
        select(Flashcard)
        .filter(Flashcard.category_id == category.id)
        .filter(~Flashcard.word.in_(used_words) | (Flashcard.word == word))
        .order_by(Flashcard.used_count.asc())
        .limit(1)
    )
    cached = result.scalars().first()
    if cached:
        return {
            "flashcard_id": cached.id,
            "word": cached.word,
            "translation": cached.translation,
            "type": cached.type or "noun",
            "english_equivalents": cached.english_equivalents or [cached.translation],
            "definition": cached.definition or "A word",
            "english_definition": cached.english_definition or "A word",
            "example_sentence": cached.example_sentence or f"{cached.word} example.",
            "english_sentence": cached.english_sentence or f"{cached.translation} example.",
            "options": [
                {"id": "1", "option_text": cached.translation},
                {"id": "2", "option_text": "incorrect1"},
                {"id": "3", "option_text": "incorrect2"},
                {"id": "4", "option_text": "incorrect3"}
            ]
        }
    raise HTTPException(status_code=500, detail="Failed to generate valid flashcard")

@router.get("/generate", response_model=FlashcardResponse)
async def get_flashcard(
    lesson_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate or retrieve a cached flashcard for the given lesson."""
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

    # Check if lesson is repeated
    is_repeat = await is_repeated_lesson(db, user_id, lesson_id)

    # Fetch cached flashcards
    used_words = await get_used_flashcard_words(db, user_id, lesson_id) if not is_repeat else set()
    result = await db.execute(
        select(Flashcard)
        .filter(Flashcard.category_id == lesson.category_id)
        .filter(~Flashcard.word.in_(used_words) if not is_repeat else True)
    )
    flashcards = result.scalars().all()

    # Generate new flashcard if none exist or for variety
    if not flashcards or not is_repeat:
        flashcard_data = await get_valid_flashcard_data(category, user_language, db, user_id, lesson_id)
        flashcard_id = flashcard_data["flashcard_id"]
        if flashcard_id:  # Flashcard was saved by generate_flashcard
            history = FlashcardHistory(
                user_id=user_id,
                flashcard_id=flashcard_id,
                lesson_id=lesson_id
            )
            db.add(history)
            await db.commit()
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

    # Select least-used flashcard for repeated lessons
    flashcard = min(flashcards, key=lambda f: (f.used_count, f.last_used_at or datetime.min))
    flashcard.used_count += 1
    flashcard.last_used_at = datetime.utcnow()
    db.add(flashcard)

    # Record history
    history = FlashcardHistory(
        user_id=user_id,
        flashcard_id=flashcard.id,
        lesson_id=lesson_id
    )
    db.add(history)

    # Reset used_count if all flashcards are heavily used
    if all(f.used_count > 10 for f in flashcards):
        for f in flashcards:
            f.used_count = 0
        db.add_all(flashcards)

    await db.commit()

    # Generate additional data for cached flashcard
    flashcard_data = await get_valid_flashcard_data(category, user_language, db, user_id, lesson_id, word=flashcard.word)
    return {
        "flashcard_id": flashcard.id,
        "word": flashcard.word,
        "translation": flashcard.translation,
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