# backend/app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, get_db

# Create the FastAPI app
app = FastAPI(
    title="LanguagePal API",
    description="Backend API for LanguagePal, an interactive language learning chatbot."
)

# Async startup event to create tables
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Root endpoint (async)
@app.get("/")
async def read_root():
    return {"message": "Welcome to LanguagePal API!"}

# Test endpoint with async database dependency
@app.get("/test-db")
async def test_database(db: AsyncSession = Depends(get_db)):
    return {"message": "Async database connection successful!"}