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
import logging  # Add logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Registering user: username={user.username}, email={user.email}")
    
    # Check if username or email already exists
    existing_user = await db.execute(
        select(UserModel).filter((UserModel.username == user.username) | (UserModel.email == user.email))
    )
    existing = existing_user.scalars().first()
    logger.debug(f"Existing user check result: {existing}")
    
    if existing:
        logger.warning(f"User already exists: {existing.username}")
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    
    # Create OpenAI thread for the user
    if openai_client:
        try:
            thread = await openai_client.threads.create()
            thread_id = thread.id
            logger.debug(f"OpenAI thread created: {thread_id}")
        except Exception as e:
            logger.error(f"OpenAI thread creation failed: {str(e)}")
            thread_id = None  # Fallback
    else:
        logger.warning("OpenAI client not initialized, skipping thread creation.")
        thread_id = None
    
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
    logger.debug(f"User registered successfully: {db_user.username}")
    return db_user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Verify user credentials
    result = await db.execute(select(UserModel).filter(UserModel.username == form_data.username))
    user = result.scalars().first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token with user.id
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{username}", response_model=User)
async def get_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    logger.debug(f"Received token: {token}")
    
    # Verify token and get current user
    try:
        payload = get_current_user(token)
    except HTTPException as e:
        logger.error(f"Error decoding token: {str(e.detail)}")
        raise e

    logger.debug(f"Decoded payload: {payload}")
    token_username = payload.get("sub")
    if token_username != username:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    
    # Fetch user from database
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user