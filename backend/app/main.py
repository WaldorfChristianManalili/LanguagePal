# backend/app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.database import engine, Base, get_db
from app.api import auth, sentence, flashcard, daily_word, dialogue  # Import API routers

# Lifespan event to handle startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Nothing to do here for now

# Create the FastAPI app with lifespan
app = FastAPI(
    title="LanguagePal API",
    description="Backend API for LanguagePal, an interactive language learning chatbot.",
    lifespan=lifespan
)

# Include API routers with prefixes and tags
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(sentence.router, prefix="/sentence", tags=["Sentence Construction"])
app.include_router(flashcard.router, prefix="/flashcard", tags=["Flashcard Vocabulary"])
app.include_router(daily_word.router, prefix="/daily_word", tags=["Word of the Day"])
app.include_router(dialogue.router, prefix="/dialogue", tags=["Simulated Dialogues"])

# Root endpoint (async)
@app.get("/")
async def read_root():
    return {"message": "Welcome to LanguagePal API!"}

# Test endpoint with async database dependency
@app.get("/test-db")
async def test_database(db: AsyncSession = Depends(get_db)):
    return {"message": "Async database connection successful!"}