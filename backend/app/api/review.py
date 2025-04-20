from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.progress import Progress
from app.models.user import User
from app.schemas.progress import ProgressResponse
from app.database import get_db
from app.utils.jwt import get_current_user

router = APIRouter(tags=["review"])

@router.get("/review", response_model=list[ProgressResponse])
async def get_review(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Progress).filter(
            Progress.user_id == user.id,
            Progress.completed == True,
            Progress.result.contains('"is_correct": false')
        )
    )
    progress_entries = result.scalars().all()
    return [
        {
            "id": entry.id,
            "category_id": entry.category_id,
            "activity_id": entry.activity_id,
            "type": entry.type,
            "completed": entry.completed,
            "result": entry.result
        }
        for entry in progress_entries
    ]