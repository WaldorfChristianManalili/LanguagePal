import os
import json
import re
from openai import AsyncOpenAI, OpenAIError
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.flashcard import Flashcard
from app.models.category import Category
from fastapi import HTTPException
import logging

# Suppress SQLAlchemy logs
for logger_name in ['sqlalchemy', 'sqlalchemy.engine', 'sqlalchemy.orm', 'sqlalchemy.pool', 'sqlalchemy.dialects']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key, max_retries=0) if api_key else None

async def translate_sentence(sentence: str, target_language: str) -> dict:
    # Unchanged, keeping your existing function
    if not client:
        return {
            "words": ["OpenAI API key not provided"],
            "sentence": "Translation disabled",
            "hints": [],
            "explanation": "Translation disabled"
        }
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are Language Pal, a friendly language tutor. Translate '{sentence}' to {target_language} and return a JSON object with: "
                        f"- 'words': array of words/phrases, excluding commas and punctuation (e.g., ['お元気', 'です', 'か']). "
                        f"- 'sentence': full translated sentence without commas. "
                        f"- 'hints': 3 short hints for arranging the sentence, focusing on structure or meaning (e.g., 'Starts with a greeting'). "
                        f"  Exclude punctuation hints (e.g., 'Ends with a question mark'). Format as [{{\"text\": string, \"usefulness\": number}}], with scores (3=high, 2=medium, 1=low). "
                        f"- 'explanation': explain why the translated sentence is structured this way, in a natural, engaging tone like teaching a curious student. "
                        f"  Use markdown bullet points (e.g., `- **こんにちは**: ...`) for each word/phrase. Focus on grammar, structure, and cultural context. "
                        f"  Do not explain punctuation (e.g., '?', '.', '¿'). "
                        f"Example: "
                        f"```json\n"
                        f"{{\n"
                        f"  \"words\": [\"コーヒー\", \"が\", \"必要\", \"です\"],\n"
                        f"  \"sentence\": \"コーヒー が 必要 です\",\n"
                        f"  \"hints\": [\n"
                        f"    {{\"text\": \"The sentence starts with the subject.\", \"usefulness\": 3}},\n"
                        f"    {{\"text\": \"必要 is not a verb, but a noun meaning necessity.\", \"usefulness\": 2}},\n"
                        f"    {{\"text\": \"The natural Japanese sentence structure is: [Subject] が [Description] です.\", \"usefulness\": 1}}\n"
                        f"  ],\n"
                        f"  \"explanation\": \"Explain why 'コーヒー が 必要 です' is structured this way.\"\n"
                        f"}}\n"
                        f"```"
                    )
                },
                {"role": "user", "content": sentence}
            ],
            max_tokens=600,
            temperature=0.5
        )
        raw_output = response.choices[0].message.content.strip()

        if raw_output.startswith("```json") and raw_output.endswith("```"):
            raw_output = raw_output[7:-3].strip()
        
        result = json.loads(raw_output)
        
        if isinstance(result, list):
            words = [word.strip() for word in result if word.strip() not in [",", "，"]]
            sentence = " ".join(words).strip()
            return {
                "words": words,
                "sentence": sentence,
                "hints": [],
                "explanation": "Invalid response format"
            }
        
        if not isinstance(result, dict) or not all(key in result for key in ["words", "sentence", "hints", "explanation"]):
            return {
                "words": ["Invalid response format"],
                "sentence": "Translation error",
                "hints": [],
                "explanation": "Translation error"
            }
        
        words = [word.strip() for word in result.get("words", []) if word.strip() not in [",", "，", "?", ".", "!", "¿", "¡"]]
        sentence = result.get("sentence", " ".join(words)).strip().rstrip(",").rstrip("，")
        hints = result.get("hints", [])
        
        parsed_hints = []
        for hint in hints:
            if isinstance(hint, dict) and "text" in hint and "usefulness" in hint:
                text = hint["text"]
                usefulness = hint["usefulness"]
                if isinstance(text, str) and isinstance(usefulness, (int, float)) and text.strip():
                    if not any(p in text.lower() for p in ["question mark", "comma", "punctuation"]):
                        parsed_hints.append({"text": text.strip(), "usefulness": int(usefulness)})
            
        parsed_hints.sort(key=lambda x: x["usefulness"], reverse=True)
        explanation = result.get("explanation", "")
        
        explanation = re.sub(r'^\d+\.\s+', '- ', explanation, flags=re.MULTILINE)
        explanation = re.sub(
            r'- \*\*[?.!¿¡]+\*\*:[^\n]*\n?',
            '',
            explanation,
            flags=re.MULTILINE
        ).strip()

        return {
            "words": words,
            "sentence": sentence,
            "hints": parsed_hints,
            "explanation": explanation
        }
    except json.JSONDecodeError:
        return {
            "words": ["Translation error: JSON decode error"],
            "sentence": "Translation error",
            "hints": [],
            "explanation": "Translation error"
        }
    except Exception as e:
        return {
            "words": [f"Translation error: {str(e)}"],
            "sentence": "Translation error",
            "hints": [],
            "explanation": "Translation error"
        }

async def generate_flashcard(
    category: str,
    target_language: str,
    category_id: int,
    lesson_name: str,
    db: AsyncSession,
    user_id: int,
    word: str = None,
    harder: bool = False,
    max_retries: int = 5,
    is_new_lesson: bool = False
) -> dict:
    if not client:
        logger.error("No OpenAI client available")
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # Check for cached flashcard
    if word:
        result = await db.execute(
            select(Flashcard).filter(
                Flashcard.word == word,
                Flashcard.user_id == user_id,
                Flashcard.category_id == category_id
            )
        )
        cached_flashcard = result.scalars().first()
        if cached_flashcard:
            if ' ' in cached_flashcard.word or len(cached_flashcard.word.split()) > 1:
                logger.error(f"Cached flashcard word '{cached_flashcard.word}' is a phrase")
                raise HTTPException(status_code=500, detail="Cached flashcard contains a phrase")
            logger.info(f"Using cached flashcard: {word}, user: {user_id}, lesson: {lesson_name}")
            return {
                "flashcard_id": cached_flashcard.id,
                "word": cached_flashcard.word,
                "translation": cached_flashcard.translation,
                "type": cached_flashcard.type,
                "english_equivalents": json.loads(cached_flashcard.english_equivalents),
                "definition": cached_flashcard.definition,
                "english_definition": cached_flashcard.english_definition,
                "example_sentence": cached_flashcard.example_sentence,
                "english_sentence": cached_flashcard.english_sentence,
                "options": json.loads(cached_flashcard.options) if cached_flashcard.options else [
                    {"id": "1", "option_text": cached_flashcard.translation},
                    {"id": "2", "option_text": "age"},
                    {"id": "3", "option_text": "job"},
                    {"id": "4", "option_text": "city"}
                ]
            }

    # Fetch user's existing flashcards to avoid duplicates
    result = await db.execute(
        select(Flashcard.word).filter(
            Flashcard.user_id == user_id,
            Flashcard.category_id == category_id
        )
    )
    excluded_words = [row[0] for row in result.fetchall()]
    logger.info(f"Excluded words for user {user_id}, category {category_id}: {excluded_words}")

    # Track words generated during retries
    failed_words = set()

    attempts = 0
    while attempts < max_retries:
        try:
            logger.info(f"Generating flashcard: category={category}, lesson={lesson_name}, target_language={target_language}, harder={harder}, attempt={attempts + 1}")
            
            # Simplified prompt
            word_instruction = f"Use the word: {word}." if word else (
                f"Choose a single word for the lesson '{lesson_name}' (e.g., 名前 for 'Saying your name')."
            )
            difficulty_instruction = (
                "Choose a less common word (A2 level)." if harder else
                "Choose a basic word (A1 level)."
            )
            excluded_instruction = (
                f"Absolutely avoid these words: {', '.join(excluded_words + list(failed_words))}."
                if (excluded_words or failed_words) else ""
            )
            new_lesson_instruction = (
                "Ensure the word is unique for this user." if is_new_lesson else ""
            )
            
            prompt = (
                f"Generate a flashcard for a single word in {target_language} for the category '{category}' and lesson '{lesson_name}'. "
                f"{word_instruction} {difficulty_instruction} {excluded_instruction} {new_lesson_instruction} "
                f"The word must be a single kanji or kana term, not a phrase. "
                f"Return a JSON object with: "
                f"- 'word': the word (e.g., '名前'). "
                f"- 'translation': English translation. "
                f"- 'type': part of speech (noun, verb, etc.). "
                f"- 'english_equivalents': list of English synonyms. "
                f"- 'definition': short definition in {target_language}. "
                f"- 'english_definition': short English definition. "
                f"- 'example_sentence': simple sentence in {target_language}. "
                f"- 'english_sentence': English translation of the sentence. "
                f"- 'options': 4 multiple-choice options (1 correct, 3 incorrect, related to '{category}'). "
                f"Example: "
                f"```json\n"
                f"{{\n"
                f"  \"word\": \"名前\",\n"
                f"  \"translation\": \"name\",\n"
                f"  \"type\": \"noun\",\n"
                f"  \"english_equivalents\": [\"name\", \"title\"],\n"
                f"  \"definition\": \"人を識別する語\",\n"
                f"  \"english_definition\": \"Word identifying a person\",\n"
                f"  \"example_sentence\": \"私の名前は田中です。\",\n"
                f"  \"english_sentence\": \"My name is Tanaka.\",\n"
                f"  \"options\": [\n"
                f"    {{\"id\": \"1\", \"option_text\": \"name\"}},\n"
                f"    {{\"id\": \"2\", \"option_text\": \"age\"}},\n"
                f"    {{\"id\": \"3\", \"option_text\": \"job\"}},\n"
                f"    {{\"id\": \"4\", \"option_text\": \"city\"}}\n"
                f"  ]\n"
                f"}}\n"
                f"```"
            )
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Generate a flashcard for {category} and lesson {lesson_name}."}
                ],
                max_tokens=300,
                temperature=0.5
            )
            raw_output = response.choices[0].message.content.strip()

            if raw_output.startswith("```json") and raw_output.endswith("```"):
                raw_output = raw_output[7:-3].strip()
            
            result = json.loads(raw_output)
            
            if not isinstance(result, dict) or not all(
                key in result
                for key in [
                    "word",
                    "translation",
                    "type",
                    "english_equivalents",
                    "definition",
                    "english_definition",
                    "example_sentence",
                    "english_sentence",
                    "options"
                ]
            ):
                logger.error(f"Invalid flashcard format: {raw_output}")
                raise ValueError("Invalid flashcard response format")

            word = result["word"].strip()
            if ' ' in word or len(word.split()) > 1:
                logger.error(f"Generated word '{word}' is a phrase")
                raise ValueError("Flashcard word must be a single word")

            if word in excluded_words or word in failed_words:
                logger.warning(f"Generated word '{word}' already used by user {user_id}, retrying")
                failed_words.add(word)
                attempts += 1
                continue

            flashcard_data = {
                "word": word,
                "translation": result["translation"].strip(),
                "type": result["type"].strip(),
                "english_equivalents": result["english_equivalents"],
                "definition": result["definition"].strip(),
                "english_definition": result["english_definition"].strip(),
                "example_sentence": result["example_sentence"].strip(),
                "english_sentence": result["english_sentence"].strip(),
                "options": [
                    {"id": opt["id"], "option_text": opt["option_text"].strip()}
                    for opt in result["options"]
                ]
            }

            result = await db.execute(
                select(Category).filter(Category.name == category)
            )
            category_obj = result.scalars().first()
            if not category_obj:
                logger.error(f"Category not found: {category}")
                raise HTTPException(status_code=404, detail="Category not found")
            
            flashcard = Flashcard(
                word=flashcard_data["word"],
                translation=flashcard_data["translation"],
                type=flashcard_data["type"],
                english_equivalents=json.dumps(flashcard_data["english_equivalents"]),
                definition=flashcard_data["definition"],
                english_definition=flashcard_data["english_definition"],
                example_sentence=flashcard_data["example_sentence"],
                english_sentence=flashcard_data["english_sentence"],
                category_id=category_obj.id,
                user_id=user_id,
                used_count=1,
                options=json.dumps(flashcard_data["options"])
            )
            db.add(flashcard)
            await db.commit()
            await db.refresh(flashcard)
            flashcard_data["flashcard_id"] = flashcard.id
            flashcard_data["english_equivalents"] = json.loads(flashcard.english_equivalents)
            flashcard_data["options"] = json.loads(flashcard.options)

            logger.info(f"Generated flashcard: {flashcard_data['word']} for lesson: {lesson_name}")
            return flashcard_data
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Flashcard attempt {attempts + 1} failed: {str(e)}")
            attempts += 1
            if attempts >= max_retries:
                if is_new_lesson:
                    fallback_words = {
                        "Saying your name": ["君", "姓"],
                        "Greetings": ["挨拶", "元気"],
                        "Introducing Yourself": ["趣味", "年齢"],
                        "Developing Fluency": ["会話", "流暢"]
                    }.get(lesson_name, ["単語"])
                    for fallback_word in fallback_words:
                        if fallback_word not in excluded_words and fallback_word not in failed_words:
                            logger.info(f"Using fallback word: {fallback_word}")
                            return await generate_flashcard(
                                category=category,
                                target_language=target_language,
                                category_id=category_id,
                                lesson_name=lesson_name,
                                db=db,
                                user_id=user_id,
                                word=fallback_word,
                                harder=harder,
                                max_retries=1,
                                is_new_lesson=is_new_lesson
                            )
                raise HTTPException(status_code=500, detail="Failed to generate valid flashcard")
        except OpenAIError as e:
            logger.error(f"OpenAI error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate flashcard")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate flashcard")

    raise HTTPException(status_code=500, detail="Failed to generate unique flashcard after retries")

async def generate_situation(category: str, lesson: str, target_language: str) -> dict:
    if not client:
        return {
            "situation": f"Practice {lesson} in a {category} context."
        }
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are Language Pal, a friendly language tutor. Generate a brief situation for practicing the lesson '{lesson}' in the category '{category}' in {target_language}. "
                        f"Return a JSON object with: "
                        f"- 'situation': a short description of the context (e.g., 'You’re greeting a new colleague'). "
                        f"Keep it simple, relevant to the lesson and category, and suitable for a short conversation. "
                        f"Example: "
                        f"```json\n"
                        f"{{\n"
                        f"  \"situation\": \"You’re greeting a new colleague\"\n"
                        f"}}\n"
                        f"```"
                    )
                },
                {"role": "user", "content": f"Generate a situation for {lesson} in {category}."}
            ],
            max_tokens=100,
            temperature=0.5
        )
        raw_output = response.choices[0].message.content.strip()

        if raw_output.startswith("```json") and raw_output.endswith("```"):
            raw_output = raw_output[7:-3].strip()
        
        result = json.loads(raw_output)
        
        if not isinstance(result, dict) or "situation" not in result:
            return {
                "situation": "Error occurred"
            }
        
        return {
            "situation": result["situation"].strip()
        }
    except Exception as e:
        return {
            "situation": f"Error: {str(e)}"
        }

async def chat_message(situation: str, conversation: list, target_language: str, user_id: int) -> dict:
    if not client:
        return {
            "speaker": "AI",
            "text": "Hello!"
        }
    
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are Language Pal, a friendly language tutor. You’re engaging in a conversation in {target_language} based on the situation: '{situation}'. "
                    f"Respond as a native speaker in a simple, natural way, appropriate for the lesson context. "
                    f"Keep responses short (1-2 sentences). If this is the 3rd AI message (conversation length ≥ 5), politely end the conversation. "
                    f"Return a JSON object with: "
                    f"- 'speaker': 'AI' "
                    f"- 'text': the response in {target_language} "
                    f"Example: "
                    f"```json\n"
                    f"{{\n"
                    f"  \"speaker\": \"AI\",\n"
                    f"  \"text\": \"こんにちは！はじめまして！\"\n"
                    f"}}\n"
                    f"```"
                )
            }
        ]
        for msg in conversation:
            role = "user" if msg["speaker"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["text"]})

        response = await client.chat.completions.create(
            model="gpt-4o-mini", # Fixed typo: 'gmt-4o-mini' to 'gpt-4o-mini'
            messages=messages,
            max_tokens=100,
            temperature=0.5
        )
        raw_output = response.choices[0].message.content.strip()

        if raw_output.startswith("```json") and raw_output.endswith("```"):
            raw_output = raw_output[7:-3].strip()
        
        result = json.loads(raw_output)
        
        if not isinstance(result, dict) or not all(key in result for key in ["speaker", "text"]):
            return {
                "speaker": "AI",
                "text": "Error occurred"
            }
        
        return {
            "speaker": result["speaker"].strip(),
            "text": result["text"].strip()
        }
    except Exception as e:
        return {
            "speaker": "AI",
            "text": f"Error: {str(e)}"
        }

async def translate_message(message: str, from_language: str, to_language: str) -> str:
    if not client:
        return "Translation disabled"
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are Language Pal, a friendly language tutor. Translate the message '{message}' from {from_language} to {to_language}. "
                        f"Return only the translated text as a string."
                    )
                },
                {"role": "user", "content": message}
            ],
            max_tokens=100,
            temperature=0.5
        )
        translation = response.choices[0].message.content.strip()
        return translation
    except Exception as e:
        return f"Error: {str(e)}"

async def evaluate_conversation(conversation: list, target_language: str) -> dict:
    if not client:
        return {
            "satisfactory": False,
            "feedback": "Evaluation disabled"
        }
    
    try:
        conversation_text = "\n".join([f"{msg['speaker']}: {msg['text']}" for msg in conversation])
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are Language Pal, a friendly language tutor. Evaluate the following conversation in {target_language} for language accuracy, relevance, and engagement. "
                        f"Return a JSON object with: "
                        f"- 'satisfactory': boolean (true if the user’s responses are accurate, relevant, and non-empty; false otherwise) "
                        f"- 'feedback': a short, encouraging explanation (2-3 sentences) for the user, highlighting strengths or suggesting improvements "
                        f"Consider grammar, vocabulary, and context appropriateness. Be positive and constructive. "
                        f"Example: "
                        f"```json\n"
                        f"{{\n"
                        f"  \"satisfactory\": true,\n"
                        f"  \"feedback\": \"Great job using polite greetings! Try adding more details next time to keep the conversation flowing.\"\n"
                        f"}}\n"
                        f"```"
                    )
                },
                {"role": "user", "content": conversation_text}
            ],
            max_tokens=200,
            temperature=0.5
        )
        raw_output = response.choices[0].message.content.strip()

        if raw_output.startswith("```json") and raw_output.endswith("```"):
            raw_output = raw_output[7:-3].strip()
        
        result = json.loads(raw_output)
        
        if not isinstance(result, dict) or not all(key in result for key in ["satisfactory", "feedback"]):
            return {
                "satisfactory": False,
                "feedback": "Invalid evaluation format"
            }
        
        return {
            "satisfactory": result["satisfactory"],
            "feedback": result["feedback"].strip()
        }
    except Exception as e:
        return {
            "satisfactory": False,
            "feedback": f"Error: {str(e)}"
        }