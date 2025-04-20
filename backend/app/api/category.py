from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.category import Category
from app.models.lesson import Lesson
from app.schemas.category import CategoryResponse
from app.database import get_db

router = APIRouter(tags=["category"])

@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    return [
        {
            "id": category.id,
            "name": category.name,
            "chapter": category.chapter,
            "difficulty": category.difficulty,
            "lessons": [
                {"id": lesson.id, "name": lesson.name, "description": lesson.description}
                for lesson in category.lessons
            ]
        }
        for category in categories
    ]