from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.flashcard import Word as WordModel, FlashcardSession as FlashcardSessionModel, FlashcardResult as FlashcardResultModel
from app.models.user import User as UserModel
from app.schemas.flashcard import Word, FlashcardSession, FlashcardSessionCreate, FlashcardResult, FlashcardResultCreate
from app.database import get_db
from app.utils.openai import client as openai_client, translate_sentence
from app.utils.pexels import get_image
from typing import List

router = APIRouter()

@router.post("/flashcard/session", response_model=FlashcardSession)
async def start_flashcard_session(session: FlashcardSessionCreate, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(UserModel).filter(UserModel.id == session.user_id))).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_session = FlashcardSessionModel(**session.dict())
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    # Generate 10 words
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Generate 10 {user.learning_language} words related to {session.category_id} with definitions."}]
    )
    words_data = response.choices[0].message.content.split("\n")[:10]
    
    for word_data in words_data:
        word, definition = word_data.split(" - ", 1)
        image_url = await get_image(word)
        db_word = WordModel(
            original_word=word,
            translated_word=await translate_sentence(word, "English"),  # Now properly defined
            definition=definition,
            image_url=image_url,
            category_id=session.category_id,
            created_by_ai=True
        )
        db.add(db_word)
    await db.commit()
    return db_session

@router.post("/flashcard/result", response_model=FlashcardResult)
async def submit_flashcard_result(result: FlashcardResultCreate, db: AsyncSession = Depends(get_db)):
    db_result = FlashcardResultModel(**result.dict())
    db.add(db_result)
    
    # Limit to 200 results, remove oldest unpinned
    results = (await db.execute(select(FlashcardResultModel).filter(FlashcardResultModel.session_id == result.session_id).order_by(FlashcardResultModel.created_at))).scalars().all()
    if len(results) > 200:
        for old_result in results[:-200]:
            if not old_result.is_pinned:
                await db.delete(old_result)
    
    await db.commit()
    await db.refresh(db_result)
    return db_result

@router.get("/flashcard/session/{session_id}", response_model=List[Word])
async def get_flashcard_words(session_id: int, db: AsyncSession = Depends(get_db)):
    session = (await db.execute(select(FlashcardSessionModel).filter(FlashcardSessionModel.id == session_id))).scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    words = (await db.execute(select(WordModel).filter(WordModel.category_id == session.category_id))).scalars().all()[:10]
    return words