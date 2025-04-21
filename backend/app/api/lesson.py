from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from app.models.lesson import Lesson
from app.models.user import User
from app.models.category import Category
from app.models.progress import Progress
from app.models.mistaken_activity import MistakenActivity
from app.models.flashcard import Flashcard
from app.schemas.lesson import LessonResponse
from app.database import get_db
from app.utils.openai import generate_flashcard
from app.api.sentence import get_scrambled_sentence
from app.utils.jwt import get_current_user
from app.utils.pexels import get_image
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["lesson"])

async def get_flashcard_data(flashcard: Flashcard) -> dict:
    """Helper to format flashcard data with Pexels image."""
    pexels_image_url = "https://placehold.co/600x400"  # Default fallback
    try:
        pexels_image_url = await get_image(flashcard.word)
    except Exception as e:
        logger.warning(f"Failed to get image for word '{flashcard.word}': {str(e)}")
        # Keep the default fallback URL
    
    return {
        "flashcard_id": flashcard.id,
        "word": flashcard.word,
        "translation": flashcard.translation,
        "type": flashcard.type,
        "english_equivalents": json.loads(flashcard.english_equivalents),
        "definition": flashcard.definition,
        "english_definition": flashcard.english_definition,
        "example_sentence": flashcard.example_sentence,
        "english_sentence": flashcard.english_sentence,
        "options": json.loads(flashcard.options) if flashcard.options else [
            {"id": "1", "option_text": flashcard.translation},
            {"id": "2", "option_text": "age"},
            {"id": "3", "option_text": "job"},
            {"id": "4", "option_text": "city"}
        ],
        "pexels_image_url": pexels_image_url
    }

@router.get("/{lesson_id}/initial", response_model=LessonResponse)
async def get_initial_lesson(lesson_id: int, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    logger.info(f"Received request for initial lesson {lesson_id} by user {user_id}")
    
    # Fetch the lesson
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found")
        raise HTTPException(status_code=404, detail="Lesson not found")
    logger.info(f"Found lesson: {lesson.name}, category_id: {lesson.category_id}")

    # Fetch the user
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Found user: {user.email}, learning_language: {user.learning_language}")

    # Fetch category
    result = await db.execute(select(Category).filter_by(id=lesson.category_id))
    category = result.scalars().first()
    if not category:
        logger.error(f"Category with ID {lesson.category_id} not found")
        raise HTTPException(status_code=404, detail="Category not found")
    logger.info(f"Found category: {category.name}")

    # Fetch progress
    result = await db.execute(select(Progress).filter_by(user_id=user_id, category_id=lesson.category_id))
    progress = result.scalars().all()
    completed_activities = {p.activity_id for p in progress if p.completed}
    logger.info(f"Completed activities for user {user_id}: {completed_activities}")

    # Determine if the lesson is new
    is_new_lesson = not any(p for p in progress if p.activity_id.startswith("flashcard") or p.activity_id.startswith("sentence"))
    logger.info(f"Lesson {lesson_id} is {'new' if is_new_lesson else 'revisited'} for user {user_id}")

    activities = []
    if lesson.name.lower() == "checkpoint":
        result = await db.execute(
            select(MistakenActivity).filter_by(user_id=user_id, category_id=lesson.category_id)
        )
        mistaken_activities = result.scalars().all()
        if mistaken_activities:
            for ma in mistaken_activities:
                if ma.activity_type == "flashcard":
                    flashcard_data = await generate_flashcard(
                        category=category.name,
                        target_language=user.learning_language,
                        category_id=lesson.category_id,
                        lesson_name=lesson.name,
                        db=db,
                        user_id=user_id,
                        word=ma.word,
                        is_new_lesson=False
                    )
                    try:
                        flashcard_data["pexels_image_url"] = await get_image(flashcard_data["word"])
                    except HTTPException:
                        flashcard_data["pexels_image_url"] = "https://placehold.co/600x400"
                    activities.append({
                        "id": f"review-{ma.activity_id}",
                        "type": "flashcard",
                        "data": flashcard_data,
                        "completed": False
                    })
                    break
        else:
            flashcard_data = await generate_flashcard(
                category=category.name,
                target_language=user.learning_language,
                category_id=lesson.category_id,
                lesson_name=lesson.name,
                db=db,
                user_id=user_id,
                harder=True,
                is_new_lesson=False
            )
            try:
                flashcard_data["pexels_image_url"] = await get_image(flashcard_data["word"])
            except HTTPException:
                flashcard_data["pexels_image_url"] = "https://placehold.co/600x400"
            activities.append({
                "id": "new-flashcard-0",
                "type": "flashcard",
                "data": flashcard_data,
                "completed": False
            })
    else:
        cached_flashcards = []
        if not is_new_lesson:
            result = await db.execute(
                select(Flashcard).filter(
                    Flashcard.user_id == user_id,
                    Flashcard.category_id == lesson.category_id
                )
            )
            cached_flashcards = result.scalars().all()
            logger.info(f"Found {len(cached_flashcards)} cached flashcards for user {user_id}, category {lesson.category_id}")

        # Load first set: flashcard-0-0, flashcard-0-1, sentence-0
        for i in range(2):
            activity_id = f"flashcard-0-{i}"
            if activity_id not in completed_activities:
                flashcard_data = None
                if not is_new_lesson and i < len(cached_flashcards):
                    flashcard_data = await get_flashcard_data(cached_flashcards[i])
                    logger.info(f"Using cached flashcard: {flashcard_data['word']} for {activity_id}")
                else:
                    logger.info(f"Generating flashcard for {activity_id}")
                    flashcard_data = await generate_flashcard(
                        category=category.name,
                        target_language=user.learning_language,
                        category_id=lesson.category_id,
                        lesson_name=lesson.name,
                        db=db,
                        user_id=user_id,
                        is_new_lesson=is_new_lesson
                    )
                    try:
                        flashcard_data["pexels_image_url"] = await get_image(flashcard_data["word"])
                    except HTTPException:
                        flashcard_data["pexels_image_url"] = "https://placehold.co/600x400"
                activities.append({
                    "id": activity_id,
                    "type": "flashcard",
                    "data": flashcard_data,
                    "completed": False
                })

        activity_id = "sentence-0"
        if activity_id not in completed_activities:
            flashcard_words = ",".join(fc["data"]["word"] for fc in activities if fc["type"] == "flashcard")
            try:
                sentence = await get_scrambled_sentence(
                    category_name=category.name, 
                    user_id=user_id, 
                    db=db, 
                    lesson_id=lesson_id,
                    flashcard_words=flashcard_words
                )
                logger.info(f"Generated sentence for {activity_id}: {sentence}")
                activities.append({
                    "id": activity_id,
                    "type": "sentence",
                    "data": {
                        "sentence_id": sentence["sentence_id"],
                        "scrambled_words": sentence["scrambled_words"],
                        "original_sentence": sentence["original_sentence"],
                        "english_sentence": sentence["english_sentence"],
                        "hints": sentence["hints"],
                        "explanation": sentence.get("explanation", "No explanation provided")
                    },
                    "completed": False
                })
            except HTTPException as e:
                logger.error(f"Failed to generate sentence for {activity_id}: {str(e)}")
                # Fallback: Skip sentence but continue with flashcards
                logger.warning(f"Skipping sentence-0 due to error, proceeding with flashcards only")

    logger.info(f"Returning initial activities for lesson {lesson_id}: {[a['id'] for a in activities]}")
    return {"activities": activities}

@router.get("/{lesson_id}/next", response_model=LessonResponse)
async def get_next_activity(
    lesson_id: int,
    current_activity_id: str = Query(default=None, description="The ID of the last completed activity"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Received request for next activity after {current_activity_id} in lesson {lesson_id} by user {user_id}")

    # Fetch the lesson
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found")
        raise HTTPException(status_code=404, detail="Lesson not found")
    logger.info(f"Found lesson: {lesson.name}, category_id: {lesson.category_id}")

    # Fetch the user
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Found user: {user.email}, learning_language: {user.learning_language}")

    # Fetch category
    result = await db.execute(select(Category).filter_by(id=lesson.category_id))
    category = result.scalars().first()
    if not category:
        logger.error(f"Category with ID {lesson.category_id} not found")
        raise HTTPException(status_code=404, detail="Category not found")
    logger.info(f"Found category: {category.name}")

    # Fetch progress
    result = await db.execute(select(Progress).filter_by(user_id=user_id, category_id=lesson.category_id))
    progress = result.scalars().all()
    completed_activities = {p.activity_id for p in progress if p.completed}
    logger.info(f"Completed activities for user {user_id}: {completed_activities}")

    # Determine if the lesson is new
    is_new_lesson = not any(p for p in progress if p.activity_id.startswith("flashcard") or p.activity_id.startswith("sentence"))
    logger.info(f"Lesson {lesson_id} is {'new' if is_new_lesson else 'revisited'} for user {user_id}")

    activities = []
    if lesson.name.lower() == "checkpoint":
        result = await db.execute(
            select(MistakenActivity).filter_by(user_id=user_id, category_id=lesson.category_id)
        )
        mistaken_activities = result.scalars().all()
        checkpoint_activities = [(f"review-{ma.activity_id}", ma.activity_type, ma.word) for ma in mistaken_activities]
        if not mistaken_activities:
            checkpoint_activities = [
                ("new-flashcard-0", "flashcard", None),
                ("new-flashcard-1", "flashcard", None),
                ("new-sentence-0", "sentence", None)
            ]

        current_index = next((i for i, (aid, _, _) in enumerate(checkpoint_activities) if aid == current_activity_id), -1)
        if current_index == -1 or current_index + 1 >= len(checkpoint_activities):
            logger.info(f"No more checkpoint activities after {current_activity_id}")
            return {"activities": []}

        next_activity_id, next_activity_type, next_word = checkpoint_activities[current_index + 1]
        if next_activity_id in completed_activities:
            logger.info(f"Next activity {next_activity_id} already completed")
            return {"activities": []}

        if next_activity_type == "flashcard":
            flashcard_data = await generate_flashcard(
                category=category.name,
                target_language=user.learning_language,
                category_id=lesson.category_id,
                lesson_name=lesson.name,
                db=db,
                user_id=user_id,
                word=next_word,
                harder=not next_word,
                is_new_lesson=False
            )
            try:
                flashcard_data["pexels_image_url"] = await get_image(flashcard_data["word"])
            except Exception as e:
                logger.warning(f"Failed to get image for word '{flashcard_data['word']}': {str(e)}")
                flashcard_data["pexels_image_url"] = "https://placehold.co/600x400"
            activities.append({
                "id": next_activity_id,
                "type": "flashcard",
                "data": flashcard_data,
                "completed": False
            })
        else:
            try:
                sentence = await get_scrambled_sentence(
                    category_name=category.name, 
                    user_id=user_id, 
                    db=db, 
                    lesson_id=lesson_id,  # Added lesson_id parameter
                    harder=True
                )
                logger.info(f"Checkpoint next sentence response: {sentence}")
                activities.append({
                    "id": next_activity_id,
                    "type": "sentence",
                    "data": {
                        "sentence_id": sentence["sentence_id"],
                        "scrambled_words": sentence["scrambled_words"],
                        "original_sentence": sentence["original_sentence"],
                        "english_sentence": sentence["english_sentence"],
                        "hints": sentence["hints"],
                        "explanation": sentence.get("explanation", "No explanation provided")
                    },
                    "completed": False
                })
            except HTTPException as e:
                logger.error(f"Failed to generate sentence for {next_activity_id}: {str(e)}")
                return {"activities": []}
    else:
        lesson_activities = []
        cached_flashcards = []
        if not is_new_lesson:
            result = await db.execute(
                select(Flashcard).filter(
                    Flashcard.user_id == user_id,
                    Flashcard.category_id == lesson.category_id
                )
            )
            cached_flashcards = result.scalars().all()
            logger.info(f"Found {len(cached_flashcards)} cached flashcards for user {user_id}, category {lesson.category_id}")

        for i in range(3):
            for j in range(2):
                lesson_activities.append((f"flashcard-{i}-{j}", "flashcard", None))
            lesson_activities.append((f"sentence-{i}", "sentence", None))

        current_index = next((i for i, (aid, _, _) in enumerate(lesson_activities) if aid == current_activity_id), -1)
        if current_index == -1:
            logger.error(f"Invalid current_activity_id: {current_activity_id}")
            raise HTTPException(status_code=400, detail=f"Invalid current activity ID: {current_activity_id}")
        if current_index + 1 >= len(lesson_activities):
            logger.info(f"No more activities after {current_activity_id}")
            return {"activities": []}

        next_activity_id, next_activity_type, _ = lesson_activities[current_index + 1]
        if next_activity_id in completed_activities:
            logger.info(f"Next activity {next_activity_id} already completed")
            return {"activities": []}

        if next_activity_type == "flashcard":
            flashcard_data = None
            set_index, flashcard_in_set = map(int, next_activity_id.split('-')[1:])
            flashcard_position = set_index * 2 + flashcard_in_set
            if not is_new_lesson and flashcard_position < len(cached_flashcards):
                flashcard_data = await get_flashcard_data(cached_flashcards[flashcard_position])
                logger.info(f"Using cached flashcard: {flashcard_data['word']} for {next_activity_id}")
            else:
                logger.info(f"Generating flashcard for {next_activity_id}")
                flashcard_data = await generate_flashcard(
                    category=category.name,
                    target_language=user.learning_language,
                    category_id=lesson.category_id,
                    lesson_name=lesson.name,
                    db=db,
                    user_id=user_id,
                    is_new_lesson=is_new_lesson
                )
                try:
                    flashcard_data["pexels_image_url"] = await get_image(flashcard_data["word"])
                except Exception as e:
                    logger.warning(f"Failed to get image for word '{flashcard_data['word']}': {str(e)}")
                    flashcard_data["pexels_image_url"] = "https://placehold.co/600x400"
            activities.append({
                "id": next_activity_id,
                "type": "flashcard",
                "data": flashcard_data,
                "completed": False
            })
        else:
            set_index = int(next_activity_id.split('-')[1])
            flashcard_words = ",".join(
                [fc.word for fc in cached_flashcards[set_index*2:(set_index+1)*2]]
            ) if cached_flashcards and set_index*2 < len(cached_flashcards) else ""
            
            # Retry sentence generation up to 2 times
            sentence = None
            for attempt in range(2):
                try:
                    sentence = await get_scrambled_sentence(
                        category_name=category.name, 
                        user_id=user_id, 
                        db=db,
                        lesson_id=lesson_id,  # Added lesson_id parameter
                        flashcard_words=flashcard_words if attempt == 0 else None,
                        harder=False
                    )
                    logger.info(f"Generated sentence for {next_activity_id}: {sentence}")
                    break
                except HTTPException as e:
                    logger.warning(f"Sentence generation attempt {attempt + 1} failed for {next_activity_id}: {str(e)}")
            
            if sentence:
                activities.append({
                    "id": next_activity_id,
                    "type": "sentence",
                    "data": {
                        "sentence_id": sentence["sentence_id"],
                        "scrambled_words": sentence["scrambled_words"],
                        "original_sentence": sentence["original_sentence"],
                        "english_sentence": sentence["english_sentence"],
                        "hints": sentence["hints"],
                        "explanation": sentence.get("explanation", "No explanation provided")
                    },
                    "completed": False
                })
            else:
                logger.error(f"All sentence generation attempts failed for {next_activity_id}")
                # Fallback: Generate a flashcard
                flashcard_data = await generate_flashcard(
                    category=category.name,
                    target_language=user.learning_language,
                    category_id=lesson.category_id,
                    lesson_name=lesson.name,
                    db=db,
                    user_id=user_id,
                    is_new_lesson=is_new_lesson
                )
                try:
                    flashcard_data["pexels_image_url"] = await get_image(flashcard_data["word"])
                except Exception as e:
                    logger.warning(f"Failed to get image for word '{flashcard_data['word']}': {str(e)}")
                    flashcard_data["pexels_image_url"] = "https://placehold.co/600x400"
                activities.append({
                    "id": next_activity_id,
                    "type": "flashcard",
                    "data": flashcard_data,
                    "completed": False
                })
                logger.info(f"Fallback to flashcard for {next_activity_id}")

    logger.info(f"Returning next activity {next_activity_id} for lesson {lesson_id}")
    return {"activities": activities}

@router.post("/{lesson_id}/complete")
async def complete_activity(lesson_id: int, body: dict, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    logger.info(f"Completing activity for lesson {lesson_id}, user {user_id}")
    
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found")
        raise HTTPException(status_code=404, detail="Lesson not found")

    progress = Progress(
        user_id=user_id,
        category_id=lesson.category_id,
        activity_id=body["activityId"],
        type=body["activityId"].split("-")[0],
        completed=True,
        result=str(body["result"])
    )
    db.add(progress)
    await db.commit()
    logger.info(f"Activity {body['activityId']} completed for lesson {lesson_id}")
    return {"status": "success"}

@router.post("/{lesson_id}/mistake")
async def report_mistake(lesson_id: int, body: dict, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    logger.info(f"Reporting mistake for lesson {lesson_id}, user {user_id}, activity {body['activity_id']}")
    
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found")
        raise HTTPException(status_code=404, detail="Lesson not found")

    mistake = MistakenActivity(
        user_id=user_id,
        lesson_id=lesson_id,
        category_id=lesson.category_id,
        activity_id=body["activity_id"],
        activity_type=body["activity_type"],
        word=body.get("word")
    )
    db.add(mistake)
    await db.commit()
    logger.info(f"Mistake reported for activity {body['activity_id']}")
    return {"status": "success"}