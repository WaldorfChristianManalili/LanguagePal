from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.database import engine, Base, get_db
from app.api import auth, sentence, flashcard, daily_word, dialogue

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="LanguagePal API",
    description="Backend API for LanguagePal, an interactive language learning chatbot.",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(sentence.router, prefix="/sentence", tags=["Sentence Construction"])
app.include_router(flashcard.router, prefix="/flashcard", tags=["Flashcard Vocabulary"])
app.include_router(daily_word.router, prefix="/daily_word", tags=["Word of the Day"])
app.include_router(dialogue.router, prefix="/dialogue", tags=["Simulated Dialogues"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to LanguagePal API!"}

@app.get("/test-db")
async def test_database(db: AsyncSession = Depends(get_db)):
    return {"message": "Async database connection successful!"}