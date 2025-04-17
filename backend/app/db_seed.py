from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import AsyncSessionLocal
from app.models.sentence import Sentence
from app.models.user import User
from app.models.category import Category
from passlib.context import CryptContext
import logging

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin"),
        "learning_language": "Japanese",
        "openai_thread_id": None,
        "is_active": True,
    },
]

CATEGORIES = [
    {"name": "Greetings"},
    {"name": "Travel"},
    {"name": "Daily Life"},
]

SENTENCES = [
    {"text": "Hello, how are you?", "category_name": "Greetings"},
    {"text": "Where is the airport?", "category_name": "Travel"},
    {"text": "I need a coffee.", "category_name": "Daily Life"},
    {"text": "Good morning!", "category_name": "Greetings"},
    {"text": "Can you help me?", "category_name": "Travel"},
    {"text": "What time is it?", "category_name": "Daily Life"},
]

async def seed_categories(db: AsyncSession):
    """Seed the categories table with sample data."""
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM categories"))
        existing_count = result.scalar()
        if existing_count > 0:
            logging.info(f"Found {existing_count} existing categories. Skipping seeding.")
            return
        for category_data in CATEGORIES:
            category = Category(name=category_data["name"])
            db.add(category)
        await db.commit()
        logging.info(f"Successfully seeded {len(CATEGORIES)} categories.")
    except Exception as e:
        await db.rollback()
        logging.error(f"Error seeding categories: {str(e)}")
        raise

async def seed_users(db: AsyncSession):
    """Seed the users table with sample data."""
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        existing_count = result.scalar()
        if existing_count > 0:
            logging.info(f"Found {existing_count} existing users. Skipping seeding.")
            return
        for user_data in USERS:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=user_data["hashed_password"],
                learning_language=user_data["learning_language"],
                openai_thread_id=user_data["openai_thread_id"],
                is_active=user_data["is_active"],
            )
            db.add(user)
        await db.commit()
        logging.info(f"Successfully seeded {len(USERS)} users.")
    except Exception as e:
        await db.rollback()
        logging.error(f"Error seeding users: {str(e)}")
        raise

async def seed_sentences(db: AsyncSession):
    """Seed the sentences table with sample data."""
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM sentences"))
        existing_count = result.scalar()
        if existing_count > 0:
            logging.info(f"Found {existing_count} existing sentences. Skipping seeding.")
            return
        # Fetch category IDs
        result = await db.execute(text("SELECT id, name FROM categories"))
        categories = {row[1]: row[0] for row in result.fetchall()}
        
        for sentence_data in SENTENCES:
            category_id = categories.get(sentence_data["category_name"])
            if not category_id:
                logging.error(f"Category {sentence_data['category_name']} not found.")
                continue
            sentence = Sentence(
                text=sentence_data["text"],
                category_id=category_id,
                used_count=0,
            )
            db.add(sentence)
        await db.commit()
        logging.info(f"Successfully seeded {len(SENTENCES)} sentences.")
    except Exception as e:
        await db.rollback()
        logging.error(f"Error seeding sentences: {str(e)}")
        raise

async def seed_database():
    """Run all seeding operations."""
    async with AsyncSessionLocal() as db:
        await seed_categories(db)
        await seed_users(db)
        await seed_sentences(db)