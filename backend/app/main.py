from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.database import engine, Base, get_db
from app.db_seed import seed_database
from app.api import auth, sentence, flashcard, dialogue, category, dashboard, pexels  # Add pexels
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Seeding database...")
    await seed_database()
    logging.info("Database initialization and seeding completed.")
    yield

app = FastAPI(
    title="LanguagePal API",
    description="Backend API for LanguagePal, an interactive language learning chatbot.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(category.router, prefix="/api/category", tags=["Category"])
app.include_router(sentence.router, prefix="/api/sentence", tags=["Sentence Construction"])
app.include_router(flashcard.router, prefix="/api/flashcard", tags=["Flashcard Vocabulary"])  # Changed to /api/flashcard
app.include_router(dialogue.router, prefix="/api/dialogue", tags=["Simulated Dialogues"])
app.include_router(dashboard.router, prefix="", tags=["Dashboard"])
app.include_router(pexels.router, prefix="/api/pexels", tags=["Pexels"])  # Added pexels

@app.get("/")
async def read_root():
    return {"message": "Welcome to LanguagePal API!"}

@app.get("/test-db")
async def test_database(db: AsyncSession = Depends(get_db)):
    return {"message": "Async database connection successful!"}

@app.get("/test-routes")
async def print_routes():
    routes = [route.path for route in app.routes]
    return {"routes": routes}