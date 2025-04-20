from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.flashcard import Flashcard
from app.models.user import User
from app.models.category import Category
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.schemas.flashcard import FlashcardResponse, SubmitFlashcardRequest, SubmitFlashcardResponse
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

    # Fetch cached flashcards
    result = await db.execute(
        select(Flashcard).filter(Flashcard.category_id == lesson.category_id)
    )
    flashcards = result.scalars().all()

    # Generate new flashcard if none exist
    if not flashcards:
        flashcard_data = await generate_flashcard(category.name, user_language, db)
        return {
            "flashcard_id": flashcard_data.get("flashcard_id", 0),
            "word": flashcard_data["word"],
            "translation": flashcard_data["translation"],
            "category": category.name,
            "lesson_id": lesson_id
        }

    # Select least-used flashcard
    flashcard = min(flashcards, key=lambda f: (f.used_count, f.last_used_at or datetime.min))
    flashcard.used_count += 1
    flashcard.last_used_at = datetime.utcnow()
    db.add(flashcard)

    # Reset used_count if all flashcards are heavily used
    if all(f.used_count > 10 for f in flashcards):
        for f in flashcards:
            f.used_count = 0
        db.add_all(flashcards)

    await db.commit()

    return {
        "flashcard_id": flashcard.id,
        "word": flashcard.word,
        "translation": flashcard.translation,
        "category": category.name,
        "lesson_id": lesson_id
    }

@router.post("/submit", response_model=SubmitFlashcardResponse)
async def submit_flashcard(
    request: SubmitFlashcardRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a flashcard answer and store the result in progress."""
    user = await get_user(db, user_id)

    # Fetch flashcard
    result = await db.execute(select(Flashcard).filter(Flashcard.id == request.flashcard_id))
    flashcard = result.scalars().first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # Evaluate answer
    is_correct = request.user_answer.strip().lower() == flashcard.translation.strip().lower()
    feedback = (
        "Correct! Well done." if is_correct
        else f"Incorrect. The correct translation is: {flashcard.translation}"
    )

    # Store result in progress
    result_data = {
        "is_correct": is_correct,
        "feedback": feedback,
        "word": flashcard.word,
        "translation": flashcard.translation,
        "user_answer": request.user_answer,
        "flashcard_id": flashcard.id
    }
    progress = Progress(
        user_id=user_id,
        category_id=flashcard.category_id,
        activity_id=f"flashcard-{request.flashcard_id}",
        type="flashcard",
        completed=True,
        result=str(result_data)
    )
    db.add(progress)
    await db.commit()

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "translation": flashcard.translation,
        "result_id": progress.id,
        "flashcard_id": flashcard.id,
        "user_answer": request.user_answer
    }