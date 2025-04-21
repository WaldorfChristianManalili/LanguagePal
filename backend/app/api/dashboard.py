from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.category import Category
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.database import get_db
from app.utils.jwt import get_current_user
from typing import List
from pydantic import BaseModel

router = APIRouter(tags=["dashboard"])

class LessonResponse(BaseModel):
    id: str
    title: str
    subtitle: str
    completed: bool
    categoryId: str

    class Config:
        from_attributes = True

class ChapterResponse(BaseModel):
    id: str
    name: str
    difficulty: str
    progress: float
    lessons: List[LessonResponse]

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    chapters: List[ChapterResponse]

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    if not categories:
        return DashboardResponse(chapters=[])

    chapters_dict = {}
    for category in categories:
        chapter_id = category.chapter
        if chapter_id not in chapters_dict:
            chapters_dict[chapter_id] = []
        chapters_dict[chapter_id].append(category)

    chapters = []
    for chapter_id, chapter_categories in sorted(chapters_dict.items()):
        category_ids = [cat.id for cat in chapter_categories]
        result = await db.execute(select(Lesson).filter(Lesson.category_id.in_(category_ids)))
        lessons = result.scalars().all()

        result = await db.execute(
            select(Progress).filter(
                Progress.user_id == user_id,
                Progress.category_id.in_(category_ids),
                Progress.type == "lesson",
                Progress.completed == True
            )
        )
        progress_records = result.scalars().all()
        completed_lesson_ids = {p.activity_id.split("lesson-")[1] for p in progress_records if p.activity_id.startswith("lesson-")}

        total_lessons = len(lessons)
        completed_lessons = len(completed_lesson_ids)
        progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        lesson_responses = []
        for lesson in lessons:
            result = await db.execute(select(Category).filter(Category.id == lesson.category_id))
            category = result.scalars().first()
            lesson_responses.append(
                LessonResponse(
                    id=str(lesson.id),
                    title=lesson.name,
                    subtitle=lesson.description or "Learn key phrases",
                    completed=str(lesson.id) in completed_lesson_ids,
                    categoryId=str(lesson.category_id)
                )
            )

        chapter_name = chapter_categories[0].name
        chapter_difficulty = chapter_categories[0].difficulty

        chapters.append(
            ChapterResponse(
                id=str(chapter_id),
                name=f"Chapter {chapter_id}: {chapter_name}",
                difficulty=chapter_difficulty,
                progress=round(progress, 1),
                lessons=lesson_responses
            )
        )

    return DashboardResponse(chapters=chapters)