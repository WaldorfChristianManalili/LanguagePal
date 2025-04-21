import logging
import random
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.sentence import Sentence, SentenceTranslation
from app.models.user import User
from app.models.category import Category
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.models.flashcard import Flashcard
from app.schemas.sentence import SentenceResponse, SubmitSentenceRequest, SubmitSentenceResponse
from app.database import get_db
from app.utils.openai import translate_sentence
from app.utils.jwt import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["sentence"])

# Dependency to get the Request object
def get_request(request: Request) -> Request:
    """Dependency to provide the Request object."""
    return request

# Store used sentence IDs in a session-specific context
def get_session_state(request: Request = Depends(get_request)):
    """Get or initialize session state for tracking used sentences."""
    if not hasattr(request.state, "used_sentence_ids"):
        request.state.used_sentence_ids = []
    return request.state.used_sentence_ids

async def get_user(db: AsyncSession, user_id: int) -> User:
    """Fetch user by ID, raising 404 if not found."""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_translation(db: AsyncSession, sentence_id: int, language: str, flashcard_words: list[str] = None) -> SentenceTranslation:
    """Fetch or create translation for a sentence, handling race conditions."""
    result = await db.execute(select(Sentence).filter(Sentence.id == sentence_id))
    sentence = result.scalars().first()
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    result = await db.execute(
        select(SentenceTranslation).filter(
            SentenceTranslation.sentence_id == sentence_id,
            SentenceTranslation.language == language
        )
    )
    translation = result.scalars().first()
    if translation:
        return translation

    # Fetch category
    result = await db.execute(select(Category).filter(Category.id == sentence.category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Prepare prompt with explicit request for English translation
    sentence_prompt = (
        f"""
        Generate a simple sentence in {language} for the category '{category.name}' suitable for language learners.
        {"Use the words: " + ", ".join(flashcard_words) + "." if flashcard_words else "Choose appropriate words."}
        Provide the response in JSON format with the following structure:
        {{
            "words": ["word1", "word2", ...],
            "sentence": "Full sentence in {language}",
            "english_sentence": "English translation",
            "hints": [
                {{"text": "Hint text", "usefulness": number}},
                ...
            ],
            "explanation": "Detailed explanation including the English translation"
        }}
        """
    )
    translation_result = await translate_sentence(sentence_prompt, language)
    logger.info(f"Translation result for sentence_id {sentence_id}: {translation_result}")

    # Parse and validate result
    if not isinstance(translation_result, dict):
        logger.error(f"Invalid translation response: {translation_result}")
        raise HTTPException(status_code=500, detail="Invalid translation response")

    required_keys = ["words", "sentence", "english_sentence", "hints", "explanation"]
    missing_keys = [key for key in required_keys if key not in translation_result]
    if missing_keys:
        logger.error(f"Missing required keys in translation result: {missing_keys}")
        raise HTTPException(status_code=500, detail=f"Missing required keys: {missing_keys}")

    translated_words = [word.strip() for word in translation_result["words"] if word.strip() not in [",", "，"]]
    translated_text = translation_result["sentence"].strip().rstrip(",").rstrip("，")
    english_text = translation_result["english_sentence"].strip()

    # Validate sentence
    if len(translated_words) < 2:
        logger.error(f"Sentence too short: {translated_text}")
        raise HTTPException(status_code=500, detail="Generated sentence is too short")
    if all(word in ["こんにちは", "おはよう", "こんばんは"] for word in translated_words):
        logger.error(f"Invalid sentence, contains only greetings: {translated_text}")
        raise HTTPException(status_code=500, detail="Generated sentence is invalid")

    hints = [hint for hint in translation_result["hints"] if isinstance(hint, dict) and "text" in hint]
    explanation = translation_result["explanation"] or "No explanation available"

    # Update Sentence.text with English translation
    sentence.text = english_text
    db.add(sentence)

    result = await db.execute(
        select(SentenceTranslation).filter(
            SentenceTranslation.sentence_id == sentence_id,
            SentenceTranslation.language == language
        )
    )
    translation = result.scalars().first()
    if not translation:
        translation = SentenceTranslation(
            sentence_id=sentence_id,
            language=language,
            translated_text=translated_text,
            translated_words=json.dumps(translated_words),
            hints=json.dumps(hints),
            explanation=explanation
        )
        db.add(translation)
        await db.commit()
    return translation

async def get_scrambled_sentence(
    category_name: str,
    user_id: int,
    db: AsyncSession,
    lesson_id: int,
    flashcard_words: str = None,
    sentence_id: int = None,
    harder: bool = False,
    request: Request = None  # Make request optional
):
    """Generate a new scrambled sentence for the given category and user, unique within the lesson."""
    logger.info(f"Generating scrambled sentence for category: {category_name}, user: {user_id}, lesson_id: {lesson_id}, sentence_id: {sentence_id}, flashcard_words: {flashcard_words}, harder: {harder}")
    
    # Use a global dictionary for lesson-scoped session state
    global_session_state = getattr(get_scrambled_sentence, "_session_state", {})
    if not global_session_state:
        get_scrambled_sentence._session_state = global_session_state
    
    state_key = f"used_sentence_ids_{lesson_id}"
    if state_key not in global_session_state:
        global_session_state[state_key] = []
    session_state = global_session_state[state_key]
    
    user = await get_user(db, user_id)
    user_language = user.learning_language

    # Parse flashcard words
    flashcard_words_list = [word.strip() for word in flashcard_words.split(",")] if flashcard_words else []

    # Validate flashcard words
    if flashcard_words_list:
        for word in flashcard_words_list:
            result = await db.execute(select(Flashcard).filter(Flashcard.word == word))
            flashcard = result.scalars().first()
            if not flashcard:
                logger.error(f"Flashcard not found: {word}")
                raise HTTPException(status_code=404, detail=f"Flashcard not found: {word}")
            if ' ' in flashcard.word:
                logger.error(f"Flashcard word '{word}' is a phrase")
                raise HTTPException(status_code=400, detail=f"Flashcard word '{word}' is a phrase, expected single word")

    # Fetch category by name
    result = await db.execute(select(Category).filter(Category.name == category_name))
    category = result.scalars().first()
    if not category:
        logger.error(f"Category '{category_name}' not found")
        raise HTTPException(status_code=404, detail=f"Category '{category_name}' not found")

    # If sentence_id is provided, fetch from DB (e.g., for retries)
    if sentence_id:
        result = await db.execute(select(Sentence).filter_by(id=sentence_id))
        sentence = result.scalars().first()
        if not sentence:
            logger.error(f"Sentence with ID {sentence_id} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Sentence not found")
        
        translation = await get_translation(db, sentence.id, user_language, flashcard_words_list)
        shuffled_words = json.loads(translation.translated_words)
        random.shuffle(shuffled_words)
        response = {
            "sentence_id": sentence.id,
            "scrambled_words": shuffled_words,
            "original_sentence": translation.translated_text,
            "english_sentence": sentence.text,
            "hints": [{"text": hint["text"], "usefulness": hint["usefulness"]} for hint in json.loads(translation.hints or "[]")],
            "explanation": translation.explanation if translation.explanation else "No explanation available"
        }
        logger.info(f"Returning scrambled sentence for sentence_id {sentence_id}: {response}")
        return response

    # Generate a new sentence
    sentence_prompt = (
        f"""
        Generate a simple sentence in {user_language} for the category '{category_name}' suitable for language learners.
        {"Use the words: " + ", ".join(flashcard_words_list) + "." if flashcard_words_list else "Choose appropriate words."}
        {"Make it slightly more complex." if harder else "Keep it simple."}
        Ensure the sentence is unique, novel, and significantly different in structure and vocabulary from previously generated ones.
        Provide the response in JSON format with the following structure:
        {{
            "words": ["word1", "word2", ...],
            "sentence": "Full sentence in {user_language}",
            "english_sentence": "English translation",
            "hints": [
                {{"text": "Hint text", "usefulness": number}},
                ...
            ],
            "explanation": "Detailed explanation including the English translation"
        }}
        """
    )
    translation_result = await translate_sentence(sentence_prompt, user_language)
    logger.info(f"New sentence translation result: {translation_result}")

    # Parse and validate result
    if not isinstance(translation_result, dict):
        logger.error(f"Invalid translation result: {translation_result}")
        raise HTTPException(status_code=500, detail="Failed to generate valid translation")

    required_keys = ["words", "sentence", "english_sentence", "hints", "explanation"]
    missing_keys = [key for key in required_keys if key not in translation_result]
    if missing_keys:
        logger.error(f"Missing required keys in translation result: {missing_keys}")
        raise HTTPException(status_code=500, detail=f"Missing required keys: {missing_keys}")

    translated_text = translation_result["sentence"].strip()
    english_text = translation_result["english_sentence"].strip()
    translated_words = [word.strip() for word in translation_result["words"] if word.strip() not in [",", "，"]]
    hints = [hint for hint in translation_result["hints"] if isinstance(hint, dict) and "text" in hint]
    explanation = translation_result["explanation"] or "No explanation available"

    # Validate sentence
    if len(translated_words) < 2:
        logger.error(f"Sentence too short: {translated_text}")
        raise HTTPException(status_code=500, detail="Generated sentence is too short")
    if all(word in ["こんにちは", "おはよう", "こんばんは"] for word in translated_words):
        logger.error(f"Invalid sentence, contains only greetings: {translated_text}")
        raise HTTPException(status_code=500, detail="Generated sentence is invalid")

    # Check for duplicate sentence
    result = await db.execute(
        select(Sentence).filter(Sentence.text == english_text, Sentence.category_id == category.id)
    )
    sentence = result.scalars().first()
    if sentence and sentence.id not in session_state:
        logger.info(f"Sentence '{english_text}' already exists, using it")
    else:
        sentence = Sentence(
            text=english_text,
            category_id=category.id,
            used_count=0,
            last_used_at=None
        )
        db.add(sentence)
        await db.commit()
        await db.refresh(sentence)

    # Ensure the sentence hasn’t been used in this session
    if sentence.id in session_state:
        logger.warning(f"Sentence ID {sentence.id} already used in session, generating another")
        # Recursively call to generate a new sentence
        return await get_scrambled_sentence(
            category_name=category_name,
            user_id=user_id,
            db=db,
            lesson_id=lesson_id,
            flashcard_words=flashcard_words,
            harder=harder
        )

    # Add to session state
    session_state.append(sentence.id)
    logger.info(f"Added sentence ID {sentence.id} to session state: {session_state}")

    # Get or create translation
    translation = await get_translation(db, sentence.id, user_language, flashcard_words_list)
    shuffled_words = json.loads(translation.translated_words)
    random.shuffle(shuffled_words)

    # Update sentence usage
    sentence.used_count += 1
    sentence.last_used_at = datetime.utcnow()
    db.add(sentence)

    try:
        await db.commit()
    except Exception as e:
        logger.error(f"Database commit failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save sentence data")

    response = {
        "sentence_id": sentence.id,
        "scrambled_words": shuffled_words,
        "original_sentence": translation.translated_text,
        "english_sentence": sentence.text,
        "hints": [{"text": hint["text"], "usefulness": hint["usefulness"]} for hint in json.loads(translation.hints or "[]")],
        "explanation": translation.explanation if translation.explanation else "No explanation available"
    }
    logger.info(f"Returning scrambled sentence: {response}")
    return response

@router.get("/scramble", response_model=SentenceResponse)
async def get_scrambled_sentence_route(
    lesson_id: int,
    request: Request,  # Move the request parameter up
    flashcard_words: str = None,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """API endpoint to get a scrambled sentence for a lesson."""
    result = await db.execute(select(Lesson).filter(Lesson.id == lesson_id))
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    result = await db.execute(select(Category).filter(Category.id == lesson.category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return await get_scrambled_sentence(
        category_name=category.name,
        user_id=user_id,
        db=db,
        lesson_id=lesson_id,
        flashcard_words=flashcard_words,
        request=request
    )

@router.post("/submit", response_model=SubmitSentenceResponse)
async def submit_sentence(
    request: SubmitSentenceRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a user's sentence attempt and evaluate it."""
    def normalize_text(text: str) -> str:
        """Normalize text by removing whitespace, punctuation, and converting to lowercase."""
        text = text.replace('\u3000', ' ').replace('\t', ' ').replace('\n', ' ').strip()
        text = text.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
        return ''.join(text.split()).lower()

    user = await get_user(db, user_id)
    result = await db.execute(select(Sentence).filter(Sentence.id == request.sentence_id))
    sentence = result.scalars().first()
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    translation = await get_translation(db, request.sentence_id, user.learning_language)

    user_answer_normalized = normalize_text(request.user_answer)
    translated_text_normalized = normalize_text(translation.translated_text)
    is_correct = user_answer_normalized == translated_text_normalized
    feedback = (
        "Correct! Well done." if is_correct
        else f"Incorrect. The correct sentence is: {translation.translated_text}"
    )

    result_data = {
        "is_correct": is_correct,
        "feedback": feedback,
        "translated_sentence": translation.translated_text,
        "user_answer": request.user_answer,
        "explanation": translation.explanation,
        "sentence_id": request.sentence_id
    }
    progress = Progress(
        user_id=user_id,
        category_id=sentence.category_id,
        activity_id=f"sentence-{request.sentence_id}",
        type="sentence",
        completed=True,
        result=json.dumps(result_data)
    )
    db.add(progress)
    await db.commit()

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "translated_sentence": translation.translated_text,
        "result_id": progress.id,
        "is_pinned": False,
        "explanation": translation.explanation,
        "sentence_id": request.sentence_id,
        "user_answer": request.user_answer
    }