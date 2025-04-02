from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, func  # Add func import
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sentence import Sentence as SentenceModel, UserSentenceResult as UserSentenceResultModel, DifficultyLevel
from app.models.user import User as UserModel
from app.schemas.sentence import Sentence, UserSentenceResult, UserSentenceResultCreate
from app.database import get_db
from app.utils.openai import translate_sentence
from random import choice, shuffle

router = APIRouter()

@router.get("/sentence/{difficulty}", response_model=Sentence)
async def get_sentence(difficulty: DifficultyLevel, user_id: int, db: AsyncSession = Depends(get_db)):
    # Fetch user's language
    user = (await db.execute(select(UserModel).filter(UserModel.id == user_id))).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get unused sentences for the difficulty level
    result = await db.execute(
        select(SentenceModel).filter(
            SentenceModel.difficulty == difficulty,
            SentenceModel.used_count == 0
        )
    )
    sentences = result.scalars().all()
    
    if not sentences:
        # Reset all sentences if none are unused
        await db.execute(update(SentenceModel).values(used_count=0))
        await db.commit()
        result = await db.execute(select(SentenceModel).filter(SentenceModel.difficulty == difficulty))
        sentences = result.scalars().all()
    
    sentence = choice(sentences)
    translated = await translate_sentence(sentence.text, user.learning_language)
    
    # Scramble the sentence
    words = sentence.text.split()
    shuffle(words)
    scrambled = " ".join(words)
    
    # Mark as used
    sentence.used_count += 1
    sentence.last_used_at = func.now()
    await db.commit()
    await db.refresh(sentence)
    
    return {**sentence.__dict__, "translated": translated, "scrambled": scrambled}

@router.post("/sentence/submit", response_model=UserSentenceResult)
async def submit_sentence(result: UserSentenceResultCreate, db: AsyncSession = Depends(get_db)):
    # Verify sentence exists
    sentence = (await db.execute(select(SentenceModel).filter(SentenceModel.id == result.sentence_id))).scalars().first()
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")
    
    # Check correctness
    is_correct = result.user_answer.strip() == sentence.text.strip()
    feedback = await translate_sentence(
        f"The correct answer is '{sentence.text}'. Your answer was {'correct' if is_correct else 'incorrect'}.",
        (await db.execute(select(UserModel).filter(UserModel.id == result.user_id))).scalars().first().learning_language
    ) if is_correct else "Try again with proper word order."
    
    # Save result
    db_result = UserSentenceResultModel(**result.dict(), is_correct=is_correct, feedback=feedback)
    db.add(db_result)
    
    # Limit to 200 results, remove oldest unpinned
    results = (await db.execute(select(UserSentenceResultModel).filter(UserSentenceResultModel.user_id == result.user_id).order_by(UserSentenceResultModel.attempted_at))).scalars().all()
    if len(results) > 200:
        for old_result in results[:-200]:
            if not old_result.is_pinned:
                await db.delete(old_result)
    
    await db.commit()
    await db.refresh(db_result)
    return db_result