from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, func  # Add func import
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dialogue import Dialogue as DialogueModel, DialogueMessage as DialogueMessageModel
from app.models.situation import Situation as SituationModel
from app.models.user import User as UserModel
from app.schemas.dialogue import Dialogue, DialogueMessage, DialogueMessageCreate
from app.database import get_db
from app.utils.openai import client as openai_client, translate_sentence  # Add translate_sentence import
from random import choice

router = APIRouter()

@router.post("/dialogue/start", response_model=Dialogue)
async def start_dialogue(user_id: int, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(UserModel).filter(UserModel.id == user_id))).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get unused situations
    result = await db.execute(select(SituationModel).filter(SituationModel.used_count == 0))
    situations = result.scalars().all()
    
    if not situations:
        await db.execute(update(SituationModel).values(used_count=0))
        await db.commit()
        result = await db.execute(select(SituationModel))
        situations = result.scalars().all()
    
    situation = choice(situations)
    thread = await openai_client.threads.create()
    db_dialogue = DialogueModel(
        user_id=user_id,
        situation_id=situation.id,
        openai_thread_id=thread.id
    )
    db.add(db_dialogue)
    
    situation.used_count += 1
    situation.last_used_at = func.now()  # Now defined
    await db.commit()
    await db.refresh(db_dialogue)
    return db_dialogue

@router.post("/dialogue/message", response_model=DialogueMessage)
async def send_message(message: DialogueMessageCreate, db: AsyncSession = Depends(get_db)):
    dialogue = (await db.execute(select(DialogueModel).filter(DialogueModel.id == message.dialogue_id))).scalars().first()
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    
    situation = (await db.execute(select(SituationModel).filter(SituationModel.id == dialogue.situation_id))).scalars().first()
    user = (await db.execute(select(UserModel).filter(UserModel.id == dialogue.user_id))).scalars().first()
    
    db_message = DialogueMessageModel(**message.dict())
    db.add(db_message)
    dialogue.message_count += 1
    
    if dialogue.message_count >= (situation.max_messages if not situation.is_free_chat else float('inf')):
        evaluation = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Evaluate this {user.learning_language} conversation: {message.content}"}]
        )
        dialogue.evaluation_score = float(evaluation.choices[0].message.content.split()[0])
        dialogue.evaluation_feedback = evaluation.choices[0].message.content
        dialogue.completed_at = func.now()  # Now defined
    else:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Respond in {user.learning_language} to: {message.content}"}]
        )
        ai_message = DialogueMessageModel(
            dialogue_id=message.dialogue_id,
            is_user=False,
            content=response.choices[0].message.content
        )
        db.add(ai_message)
        dialogue.message_count += 1
    
    await db.commit()
    await db.refresh(db_message)
    return db_message

@router.get("/dialogue/translate/{message_id}", response_model=str)
async def translate_message(message_id: int, db: AsyncSession = Depends(get_db)):
    message = (await db.execute(select(DialogueMessageModel).filter(DialogueMessageModel.id == message_id))).scalars().first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    translation = await translate_sentence(message.content, "English")  # Now defined
    message.translation = translation
    await db.commit()
    return translation