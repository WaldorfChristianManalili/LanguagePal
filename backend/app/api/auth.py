from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel
from app.schemas.user import UserResponse, UserCreate
from app.database import get_db
from app.utils.openai import client as openai_client
from app.utils.jwt import create_access_token, get_current_user
from passlib.context import CryptContext
from datetime import datetime

router = APIRouter(tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_user_by_username(db: AsyncSession, username: str) -> UserModel:
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_user_by_id(db: AsyncSession, user_id: int) -> UserModel:
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserModel).filter((UserModel.username == user.username) | (UserModel.email == user.email))
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    thread_id = None
    if openai_client:
        try:
            thread = await openai_client.threads.create()
            thread_id = thread.id
        except Exception:
            thread_id = None

    hashed_password = pwd_context.hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        learning_language=user.learning_language,
        openai_thread_id=thread_id,
        created_at=datetime.utcnow(),
        last_login=None
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, form_data.username)
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user.last_login = datetime.utcnow()
    db.add(user)
    await db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{username}", response_model=UserResponse)
async def get_user(
    username: str,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    payload = get_current_user(token)
    token_user_id = payload.get("sub")
    user = await get_user_by_username(db, username)

    if str(user.id) != token_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")

    return user

@router.get("/validate", response_model=UserResponse)
async def validate_token(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_user_by_id(db, user_id)