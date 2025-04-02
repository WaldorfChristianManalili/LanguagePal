from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.daily_word import DailyWord as DailyWordModel, UserDailyWordResult as UserDailyWordResultModel
from app.models.user import User as UserModel
from app.schemas.daily_word import DailyWord, UserDailyWordResult, UserDailyWordResultCreate
from app.database import get_db
from app.utils.openai import client as openai_client, translate_sentence  # Add translate_sentence import
from datetime import datetime, timezone

router = APIRouter()

@router.get("/daily_word", response_model=DailyWord)
async def get_daily_word(db: AsyncSession = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    word = (await db.execute(select(DailyWordModel).filter(DailyWordModel.date == today))).scalars().first()
    
    if not word:
        user = (await db.execute(select(UserModel).limit(1))).scalars().first()  # Assume first user for language
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Generate a {user.learning_language} word with definition and example sentence."}]
        )
        word_data = response.choices[0].message.content.split("\n")
        word = DailyWordModel(
            original_word=word_data[0],
            translated_word=await translate_sentence(word_data[0], "English"),  # Now defined
            definition=word_data[1],
            example_sentence=word_data[2],
            date=today
        )
        db.add(word)
        await db.commit()
        await db.refresh(word)
    return word

@router.post("/daily_word/submit", response_model=UserDailyWordResult)
async def submit_daily_word(result: UserDailyWordResultCreate, db: AsyncSession = Depends(get_db)):
    word = (await db.execute(select(DailyWordModel).filter(DailyWordModel.id == result.daily_word_id))).scalars().first()
    if not word:
        raise HTTPException(status_code=404, detail="Daily word not found")
    
    guesses = result.guesses + 1
    is_correct = result.guesses_list.split(",")[-1] == word.original_word and guesses <= 6
    db_result = UserDailyWordResultModel(**result.dict(), guesses=guesses, guessed_correctly=is_correct)
    db.add(db_result)
    await db.commit()
    await db.refresh(db_result)
    return db_result