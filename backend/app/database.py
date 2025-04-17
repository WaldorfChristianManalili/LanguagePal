from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db