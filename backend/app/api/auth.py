from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate
from app.database import get_db
from app.utils.openai import client as openai_client
from app.utils.jwt import create_access_token, get_current_user
from passlib.context import CryptContext

router = APIRouter(tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_user_by_username(db: AsyncSession, username: str) -> UserModel:
    """Fetch user by username, raising 404 if not found."""
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_user_by_id(db: AsyncSession, user_id: int) -> UserModel:
    """Fetch user by ID, raising 404 if not found."""
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if username or email already exists
    result = await db.execute(
        select(UserModel).filter((UserModel.username == user.username) | (UserModel.email == user.email))
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Create OpenAI thread for the user
    thread_id = None
    if openai_client:
        try:
            thread = await openai_client.threads.create()
            thread_id = thread.id
        except Exception:
            thread_id = None  # Fallback

    # Hash password and create user
    hashed_password = pwd_context.hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        learning_language=user.learning_language,
        openai_thread_id=thread_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Verify user credentials
    user = await get_user_by_username(db, form_data.username)
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate JWT token with user.id
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{username}", response_model=User)
async def get_user(
    username: str,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # Verify token and get current user
    payload = get_current_user(token)
    token_user_id = payload.get("sub")
    user = await get_user_by_username(db, username)

    # Ensure the token's user matches the requested username
    if str(user.id) != token_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")

    return user

@router.get("/validate", response_model=User)
async def validate_token(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch and return user
    return await get_user_by_id(db, user_id)