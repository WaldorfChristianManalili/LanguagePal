from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.category import Category
from app.database import get_db

router = APIRouter(tags=["Category"])

@router.get("", response_model=List[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category.name))
    categories = result.scalars().all()
    return categories