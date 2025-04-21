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

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key, max_retries=0) if api_key else None

async def translate_sentence(sentence: str, target_language: str) -> dict:
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

async def generate_flashcard(category: str, target_language: str, db: AsyncSession = None, word: str = None) -> dict:
    if not client:
        if db:
            # Try cached flashcard
            result = await db.execute(
                select(Flashcard).filter(Flashcard.category_id == 1).order_by(Flashcard.used_count.asc()).limit(1)
            )
            cached = result.scalars().first()
            if cached:
                return {
                    "flashcard_id": cached.id,
                    "word": cached.word,
                    "translation": cached.translation,
                    "type": cached.type or "noun",
                    "english_equivalents": cached.english_equivalents or [cached.translation],
                    "definition": cached.definition or "A word",
                    "english_definition": cached.english_definition or "A word",
                    "example_sentence": cached.example_sentence or f"{cached.word} example.",
                    "english_sentence": cached.english_sentence or f"{cached.translation} example.",
                    "options": [
                        {"id": "1", "option_text": cached.translation},
                        {"id": "2", "option_text": "incorrect1"},
                        {"id": "3", "option_text": "incorrect2"},
                        {"id": "4", "option_text": "incorrect3"}
                    ]
                }
        # Generic fallback
        return {
            "flashcard_id": 0,
            "word": "word",
            "translation": "word",
            "type": "noun",
            "english_equivalents": ["word"],
            "definition": "A vocabulary item",
            "english_definition": "A vocabulary item",
            "example_sentence": f"A simple {target_language} word.",
            "english_sentence": "A simple word.",
            "options": [
                {"id": "1", "option_text": "word"},
                {"id": "2", "option_text": "incorrect1"},
                {"id": "3", "option_text": "incorrect2"},
                {"id": "4", "option_text": "incorrect3"}
            ]
        }
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are Language Pal, a friendly language tutor. Generate a flashcard for a vocabulary word in the category '{category}' for {target_language}. "
                        f"{'Use the word: ' + word + '.' if word else 'Choose a relevant word.'} "
                        f"Return a JSON object with: "
                        f"- 'word': the vocabulary word or phrase in {target_language}. "
                        f"- 'translation': the primary English translation. "
                        f"- 'type': part of speech (e.g., noun, verb, adjective, interjection). "
                        f"- 'english_equivalents': list of English synonyms or equivalent words/phrases (include the translation). "
                        f"- 'definition': a concise definition in {target_language} (max 10 words). "
                        f"- 'english_definition': a concise English definition (max 10 words). "
                        f"- 'example_sentence': a simple example sentence in {target_language}. "
                        f"- 'english_sentence': the English translation of the example sentence. "
                        f"- 'options': 4 multiple-choice options for the translation (1 correct, 3 incorrect), each with 'id' (string) and 'option_text'. "
                        f"Example: "
                        f"```json\n"
                        f"{{\n"
                        f"  \"word\": \"casa\",\n"
                        f"  \"translation\": \"house\",\n"
                        f"  \"type\": \"noun\",\n"
                        f"  \"english_equivalents\": [\"house\", \"home\"],\n"
                        f"  \"definition\": \"Lugar donde las personas viven\",\n"
                        f"  \"english_definition\": \"Place where people live\",\n"
                        f"  \"example_sentence\": \"Vivo en una casa grande.\",\n"
                        f"  \"english_sentence\": \"I live in a large house.\",\n"
                        f"  \"options\": [\n"
                        f"    {{\"id\": \"1\", \"option_text\": \"house\"}},\n"
                        f"    {{\"id\": \"2\", \"option_text\": \"car\"}},\n"
                        f"    {{\"id\": \"3\", \"option_text\": \"tree\"}},\n"
                        f"    {{\"id\": \"4\", \"option_text\": \"book\"}}\n"
                        f"  ]\n"
                        f"}}\n"
                        f"```"
                    )
                },
                {"role": "user", "content": f"Generate a flashcard for {category} in {target_language}."}
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
            raise ValueError("Invalid flashcard response format")

        flashcard_data = {
            "word": result["word"].strip(),
            "translation": result["translation"].strip(),
            "type": result["type"].strip(),
            "english_equivalents": [eq.strip() for eq in result["english_equivalents"]],
            "definition": result["definition"].strip(),
            "english_definition": result["english_definition"].strip(),
            "example_sentence": result["example_sentence"].strip(),
            "english_sentence": result["english_sentence"].strip(),
            "options": [
                {"id": opt["id"], "option_text": opt["option_text"].strip()}
                for opt in result["options"]
            ]
        }

        if db:
            result = await db.execute(
                select(Category).filter(Category.name == category)
            )
            category_obj = result.scalars().first()
            if not category_obj:
                raise HTTPException(status_code=404, detail="Category not found")
            
            flashcard = Flashcard(
                word=flashcard_data["word"],
                translation=flashcard_data["translation"],
                type=flashcard_data["type"],
                english_equivalents=flashcard_data["english_equivalents"],
                definition=flashcard_data["definition"],
                english_definition=flashcard_data["english_definition"],
                example_sentence=flashcard_data["example_sentence"],
                english_sentence=flashcard_data["english_sentence"],
                category_id=category_obj.id,
                used_count=1
            )
            db.add(flashcard)
            await db.commit()
            await db.refresh(flashcard)
            flashcard_data["flashcard_id"] = flashcard.id

        return flashcard_data
    except (OpenAIError, ValueError, json.JSONDecodeError) as e:
        if db:
            # Try cached flashcard
            result = await db.execute(
                select(Flashcard).filter(Flashcard.category_id == 1).order_by(Flashcard.used_count.asc()).limit(1)
            )
            cached = result.scalars().first()
            if cached:
                return {
                    "flashcard_id": cached.id,
                    "word": cached.word,
                    "translation": cached.translation,
                    "type": cached.type or "noun",
                    "english_equivalents": cached.english_equivalents or [cached.translation],
                    "definition": cached.definition or "A word",
                    "english_definition": cached.english_definition or "A word",
                    "example_sentence": cached.example_sentence or f"{cached.word} example.",
                    "english_sentence": cached.english_sentence or f"{cached.translation} example.",
                    "options": [
                        {"id": "1", "option_text": cached.translation},
                        {"id": "2", "option_text": "incorrect1"},
                        {"id": "3", "option_text": "incorrect2"},
                        {"id": "4", "option_text": "incorrect3"}
                    ]
                }
        # Generic fallback
        return {
            "flashcard_id": 0,
            "word": "word",
            "translation": "word",
            "type": "noun",
            "english_equivalents": ["word"],
            "definition": "A vocabulary item",
            "english_definition": "A vocabulary item",
            "example_sentence": f"A simple {target_language} word.",
            "english_sentence": "A simple word.",
            "options": [
                {"id": "1", "option_text": "word"},
                {"id": "2", "option_text": "incorrect1"},
                {"id": "3", "option_text": "incorrect2"},
                {"id": "4", "option_text": "incorrect3"}
            ]
        }

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
            model="gmt-4o-mini",
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