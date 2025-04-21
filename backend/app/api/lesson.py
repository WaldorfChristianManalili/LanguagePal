import json
from fastapi import APIRouter, Depends, HTTPException
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["lesson"])  # Fixed: Added tags for consistency with sentence.py

async def get_flashcard_data(flashcard: Flashcard) -> dict:
    """Helper to format flashcard data with Pexels image."""
    try:
        pexels_image_url = await get_image(flashcard.word)
    except HTTPException:
        pexels_image_url = "https://placehold.co/600x400"  # Fallback image
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
        "pexels_image_url": pexels_image_url or "https://placehold.co/600x400"  # Fallback image
    }
    
@router.get("/{lesson_id}/initial", response_model=LessonResponse)
async def get_initial_lesson(lesson_id: int, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    logger.info(f"Received request for initial lesson {lesson_id} by user {user_id}")
    
    # Fetch the lesson
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found in database")
        raise HTTPException(status_code=404, detail="Lesson not found")
    logger.info(f"Found lesson: {lesson.name}, category_id: {lesson.category_id}")

    # Fetch the user
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User with ID {user_id} not found in database")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Found user: {user.email}, learning_language: {user.learning_language}")

    # Fetch category
    result = await db.execute(select(Category).filter_by(id=lesson.category_id))
    category = result.scalars().first()
    if not category:
        logger.error(f"Category with ID {lesson.category_id} not found in database")
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
        # For checkpoints, return the first mistaken flashcard or a new harder flashcard
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
                    break  # Return only the first flashcard
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
        # Fetch cached flashcards for revisited lessons
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

        # Return the first flashcard
        activity_id = "flashcard-0-0"
        if activity_id not in completed_activities:
            flashcard_data = None
            if not is_new_lesson and cached_flashcards:
                flashcard_data = await get_flashcard_data(cached_flashcards[0])
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

    logger.info(f"Returning initial activity for lesson {lesson_id}")
    return {"activities": activities}

@router.get("/{lesson_id}/remaining", response_model=LessonResponse)
async def get_remaining_lesson(lesson_id: int, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    logger.info(f"Received request for remaining lesson {lesson_id} by user {user_id}")
    
    # Fetch the lesson
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found in database")
        raise HTTPException(status_code=404, detail="Lesson not found")
    logger.info(f"Found lesson: {lesson.name}, category_id: {lesson.category_id}")

    # Fetch the user
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User with ID {user_id} not found in database")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Found user: {user.email}, learning_language: {user.learning_language}")

    # Fetch category
    result = await db.execute(select(Category).filter_by(id=lesson.category_id))
    category = result.scalars().first()
    if not category:
        logger.error(f"Category with ID {lesson.category_id} not found in database")
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
        # Handle review for checkpoint
        result = await db.execute(
            select(MistakenActivity).filter_by(user_id=user_id, category_id=lesson.category_id)
        )
        mistaken_activities = result.scalars().all()
        if mistaken_activities:
            for ma in mistaken_activities:
                if ma.activity_type == "flashcard" and ma.activity_id != "flashcard-0":  # Skip the first flashcard
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
                elif ma.activity_type == "sentence":
                    sentence = await get_scrambled_sentence(category.name, user_id, db, sentence_id=ma.activity_id)
                    logger.info(f"Checkpoint remaining sentence response: {sentence}")
                    activities.append({
                        "id": f"review-{ma.activity_id}",
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
            # Generate remaining harder questions
            for i in range(1, 2):  # Only the second flashcard
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
                    "id": f"new-flashcard-{i}",
                    "type": "flashcard",
                    "data": flashcard_data,
                    "completed": False
                })
            try:
                sentence = await get_scrambled_sentence(category.name, user_id, db, harder=True)
                logger.info(f"Checkpoint new remaining sentence response: {sentence}")
                activities.append({
                    "id": "new-sentence-0",
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
                logger.error(f"Failed to generate checkpoint sentence: {str(e)}")
                # Skip sentence to avoid blocking
    else:
        # Fetch cached flashcards for revisited lessons
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

        # Regular lesson: 3 sets of 2 flashcards + 1 sentence, excluding the first flashcard
        flashcard_index = 1 if cached_flashcards else 0
        for i in range(3):
            for j in range(2):
                activity_id = f"flashcard-{i}-{j}"
                if activity_id == "flashcard-0-0":  # Skip the first flashcard
                    continue
                if activity_id not in completed_activities:
                    flashcard_data = None
                    if not is_new_lesson and flashcard_index < len(cached_flashcards):
                        flashcard_data = await get_flashcard_data(cached_flashcards[flashcard_index])
                        logger.info(f"Using cached flashcard: {flashcard_data['word']} for {activity_id}")
                        flashcard_index += 1
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
            activity_id = f"sentence-{i}"
            if activity_id not in completed_activities:
                logger.info(f"Generating sentence for {activity_id}")
                flashcard_words = ",".join(
                    [act["data"]["word"] for act in activities if act["type"] == "flashcard" and act["id"].startswith(f"flashcard-{i}")]
                )
                try:
                    sentence = await get_scrambled_sentence(category.name, user_id, db, flashcard_words=flashcard_words)
                    logger.info(f"Remaining lesson sentence response: {sentence}")
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
                    continue

    logger.info(f"Returning {len(activities)} remaining activities for lesson {lesson_id}")
    return {"activities": activities}

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: int, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    logger.info(f"Received request for lesson {lesson_id} by user {user_id}")
    
    # Fetch the lesson
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found in database")
        raise HTTPException(status_code=404, detail="Lesson not found")
    logger.info(f"Found lesson: {lesson.name}, category_id: {lesson.category_id}")

    # Fetch the user
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        logger.error(f"User with ID {user_id} not found in database")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Found user: {user.email}, learning_language: {user.learning_language}")

    # Fetch category
    result = await db.execute(select(Category).filter_by(id=lesson.category_id))
    category = result.scalars().first()
    if not category:
        logger.error(f"Category with ID {lesson.category_id} not found in database")
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
        # Handle review for checkpoint
        result = await db.execute(
            select(MistakenActivity).filter_by(user_id=user_id, category_id=lesson.category_id)
        )
        mistaken_activities = result.scalars().all()
        if mistaken_activities:
            for ma in mistaken_activities:
                if ma.activity_type == "flashcard":
                    flashcard = await generate_flashcard(
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
                        flashcard["pexels_image_url"] = await get_image(flashcard["word"])
                    except HTTPException:
                        flashcard["pexels_image_url"] = "https://placehold.co/600x400"
                    activities.append({
                        "id": f"review-{ma.activity_id}",
                        "type": "flashcard",
                        "data": flashcard,
                        "completed": False
                    })
                elif ma.activity_type == "sentence":
                    sentence = await get_scrambled_sentence(category.name, user_id, db, sentence_id=ma.activity_id)
                    logger.info(f"Checkpoint sentence response: {sentence}")
                    activities.append({
                        "id": f"review-{ma.activity_id}",
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
            # Generate new, harder questions
            for i in range(2):
                flashcard = await generate_flashcard(
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
                    flashcard["pexels_image_url"] = await get_image(flashcard["word"])
                except HTTPException:
                    flashcard["pexels_image_url"] = "https://placehold.co/600x400"
                activities.append({
                    "id": f"new-flashcard-{i}",
                    "type": "flashcard",
                    "data": flashcard,
                    "completed": False
                })
            try:
                sentence = await get_scrambled_sentence(category.name, user_id, db, harder=True)
                logger.info(f"Checkpoint new sentence response: {sentence}")
                activities.append({
                    "id": "new-sentence-0",
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
                logger.error(f"Failed to generate checkpoint sentence: {str(e)}")
                # Skip sentence to avoid blocking
    else:
        # Fetch cached flashcards for revisited lessons
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

        # Regular lesson: 3 sets of 2 flashcards + 1 sentence
        flashcard_index = 0
        for i in range(3):
            for j in range(2):
                activity_id = f"flashcard-{i}-{j}"
                if activity_id not in completed_activities:
                    if not is_new_lesson and flashcard_index < len(cached_flashcards):
                        flashcard_data = await get_flashcard_data(cached_flashcards[flashcard_index])
                        logger.info(f"Using cached flashcard: {flashcard_data['word']} for {activity_id}")
                        flashcard_index += 1
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
                            flashcard["pexels_image_url"] = await get_image(flashcard["word"])
                        except HTTPException:
                            flashcard["pexels_image_url"] = "https://placehold.co/600x400"
                    activities.append({
                        "id": activity_id,
                        "type": "flashcard",
                        "data": flashcard_data,
                        "completed": False
                    })
            activity_id = f"sentence-{i}"
            if activity_id not in completed_activities:
                logger.info(f"Generating sentence for {activity_id}")
                flashcard_words = ",".join(
                    [act["data"]["word"] for act in activities if act["type"] == "flashcard" and act["id"].startswith(f"flashcard-{i}")]
                )
                try:
                    sentence = await get_scrambled_sentence(category.name, user_id, db, flashcard_words=flashcard_words)
                    logger.info(f"Regular lesson sentence response: {sentence}")
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
                    continue

    logger.info(f"Returning {len(activities)} activities for lesson {lesson_id}")
    return {"activities": activities}

@router.post("/{lesson_id}/complete")
async def complete_activity(lesson_id: int, body: dict, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    logger.info(f"Completing activity for lesson {lesson_id}, user {user_id}")
    
    # Fetch the lesson
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found in database")
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Save progress
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
    
    # Fetch the lesson
    result = await db.execute(select(Lesson).filter_by(id=lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        logger.error(f"Lesson with ID {lesson_id} not found in database")
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Save mistake
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