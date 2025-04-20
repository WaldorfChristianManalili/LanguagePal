from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.category import Category
from app.models.lesson import Lesson
from app.seed_data import USERS, CATEGORIES
import logging

async def seed_categories(db: AsyncSession):
    """Seed the categories and lessons tables with sample data."""
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM categories"))
        existing_count = result.scalar()
        if existing_count > 0:
            logging.info(f"Found {existing_count} existing categories. Skipping seeding.")
            return
        for category_data in CATEGORIES:
            category = Category(
                name=category_data["name"],
                chapter=category_data.get("chapter", 1),
                difficulty=category_data.get("difficulty", "A1")
            )
            db.add(category)
            await db.commit()
            await db.refresh(category)
            for lesson_data in category_data.get("lessons", []):
                lesson = Lesson(
                    name=lesson_data["name"],
                    description=lesson_data["description"],
                    category_id=category.id
                )
                db.add(lesson)
        await db.commit()
        logging.info(f"Successfully seeded {len(CATEGORIES)} categories and their lessons.")
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

async def seed_database():
    """Run all seeding operations."""
    async with AsyncSessionLocal() as db:
        await seed_categories(db)
        await seed_users(db)