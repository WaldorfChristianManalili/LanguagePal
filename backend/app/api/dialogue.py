from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dialogue import Dialogue
from app.models.user import User
from app.models.category import Category
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.schemas.dialogue import DialogueResponse, ChatRequest, ChatResponse, TranslateResponse, SubmitDialogueRequest, SubmitDialogueResponse
from app.database import get_db
from app.utils.openai import generate_situation, chat_message, translate_message, evaluate_conversation
from app.utils.jwt import get_current_user
import json

router = APIRouter(tags=["dialogue"])

async def get_user(db: AsyncSession, user_id: int) -> User:
    """Fetch user by ID, raising 404 if not found."""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/generate", response_model=DialogueResponse)
async def generate_dialogue_situation(
    lesson_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate or retrieve a cached situation for the dialogue."""
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

    # Check for cached situation
    result = await db.execute(
        select(Dialogue).filter(
            Dialogue.category_id == lesson.category_id,
            Dialogue.lesson_id == lesson.id
        )
    )
    dialogue = result.scalars().first()

    # Generate new situation if none exists
    if not dialogue:
        situation = await generate_situation(category.name, lesson.name, user_language)
        dialogue = Dialogue(
            situation=situation["situation"],
            category_id=category.id,
            lesson_id=lesson.id
        )
        db.add(dialogue)
        await db.commit()
        await db.refresh(dialogue)

    # Start conversation
    initial_message = await chat_message(
        dialogue.situation,
        [],
        user_language,
        user_id
    )

    conversation = [initial_message]
    return {
        "dialogue_id": dialogue.id,
        "situation": dialogue.situation,
        "conversation": conversation,
        "category": category.name,
        "lesson_id": lesson_id
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle user message and return AI response."""
    user = await get_user(db, user_id)
    user_language = user.learning_language

    # Fetch dialogue
    result = await db.execute(select(Dialogue).filter(Dialogue.id == request.dialogue_id))
    dialogue = result.scalars().first()
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")

    # Parse conversation
    conversation = request.conversation
    if len([msg for msg in conversation if msg["speaker"] == "user"]) >= 3:
        raise HTTPException(status_code=400, detail="Maximum user messages reached")

    # Generate AI response
    ai_message = await chat_message(
        dialogue.situation,
        conversation,
        user_language,
        user_id
    )
    conversation.append(ai_message)

    # Check if conversation should end (6 messages total)
    is_complete = len(conversation) >= 6
    if is_complete:
        evaluation = await evaluate_conversation(conversation, user_language)
        result_data = {
            "is_correct": evaluation["satisfactory"],
            "feedback": evaluation["feedback"],
            "situation": dialogue.situation,
            "conversation": conversation
        }
        progress = Progress(
            user_id=user_id,
            category_id=dialogue.category_id,
            activity_id=f"dialogue-{dialogue.id}",
            type="dialogue",
            completed=True,
            result=json.dumps(result_data)
        )
        db.add(progress)
        await db.commit()

    return {
        "dialogue_id": dialogue.id,
        "conversation": conversation,
        "is_complete": is_complete
    }

@router.post("/translate", response_model=TranslateResponse)
async def translate(
    message: str,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Translate a message to English."""
    user = await get_user(db, user_id)
    translation = await translate_message(message, user.learning_language, "English")
    return {"translation": translation}

@router.post("/submit", response_model=SubmitDialogueResponse)
async def submit_dialogue(
    request: SubmitDialogueRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit final conversation for evaluation (if ended early)."""
    user = await get_user(db, user_id)
    user_language = user.learning_language

    # Fetch dialogue
    result = await db.execute(select(Dialogue).filter(Dialogue.id == request.dialogue_id))
    dialogue = result.scalars().first()
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")

    # Evaluate conversation
    evaluation = await evaluate_conversation(request.conversation, user_language)
    result_data = {
        "is_correct": evaluation["satisfactory"],
        "feedback": evaluation["feedback"],
        "situation": dialogue.situation,
        "conversation": request.conversation
    }
    progress = Progress(
        user_id=user_id,
        category_id=dialogue.category_id,
        activity_id=f"dialogue-{dialogue.id}",
        type="dialogue",
        completed=True,
        result=json.dumps(result_data)
    )
    db.add(progress)
    await db.commit()

    return {
        "is_correct": evaluation["satisfactory"],
        "feedback": evaluation["feedback"],
        "result_id": progress.id,
        "dialogue_id": dialogue.id
    }