from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.models.user import User
from app.database import AsyncSession, get_db

router = APIRouter()

@router.get("/users/{username}")
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if not user:
        return {"message": "User not found"}
    return {"username": user.username, "language": user.chosen_language}