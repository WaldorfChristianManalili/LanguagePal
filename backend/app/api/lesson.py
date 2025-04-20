from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.schemas.lesson import LessonResponse
from app.database import get_db
from app.services.auth_service import get_current_user
from app.utils.openai import generate_flashcard, generate_dialogue
from app.api.sentence import get_scrambled_sentence

router = APIRouter()

@router.get("/lesson/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    result = await db.execute(select(Progress).filter_by(user_id=user.id, category_id=lesson.category_id))
    progress = result.scalars().all()
    completed_activities = {p.activity_id for p in progress if p.completed}

    activities = []
    for i in range(3):
        for j in range(2):
            activity_id = f"flashcard-{i}-{j}"
            if activity_id not in completed_activities:
                flashcard = await generate_flashcard(lesson.category.name, user.learning_language, db)
                activities.append({
                    "id": activity_id,
                    "type": "flashcard",
                    "data": flashcard,
                    "completed": False
                })
        activity_id = f"sentence-{i}"
        if activity_id not in completed_activities:
            sentence = await get_scrambled_sentence(lesson.category.name, user.id, db)
            activities.append({
                "id": activity_id,
                "type": "sentence",
                "data": {
                    "sentence_id": sentence["sentence_id"],
                    "scrambled_words": sentence["scrambled_words"],
                    "original_sentence": sentence["original_sentence"],
                    "english_sentence": sentence["english_sentence"],
                    "hints": sentence["hints"],
                    "explanation": ""
                },
                "completed": False
            })
    activity_id = "dialogue"
    if activity_id not in completed_activities:
        dialogue = await generate_dialogue(lesson.category.name, user.learning_language)
        activities.append({
            "id": activity_id,
            "type": "dialogue",
            "data": dialogue,
            "completed": False
        })

    return {"activities": activities}

@router.post("/lesson/{lesson_id}/complete")
async def complete_activity(lesson_id: int, body: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    progress = Progress(
        user_id=user.id,
        category_id=lesson.category_id,
        activity_id=body["activityId"],
        type=body["activityId"].split("-")[0],
        completed=True,
        result=str(body["result"])
    )
    db.add(progress)
    await db.commit()
    return {"status": "success"}