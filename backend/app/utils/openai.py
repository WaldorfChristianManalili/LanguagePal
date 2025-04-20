import os
import json
import re
from openai import AsyncOpenAI
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

async def generate_flashcard(category: str, target_language: str, db: AsyncSession = None) -> dict:
    if not client:
        return {
            "word": "hello",
            "definition": "A greeting",
            "example_sentence": "Hello, how are you?",
            "image": "https://via.placeholder.com/60"
        }
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are Language Pal, a friendly language tutor. Generate a flashcard for a vocabulary word in the category '{category}' for {target_language}. "
                        f"Return a JSON object with: "
                        f"- 'word': the vocabulary word or phrase in {target_language}. "
                        f"- 'definition': a concise English definition (max 5 words). "
                        f"- 'example_sentence': an example sentence using the word in {target_language}, with English translation in parentheses. "
                        f"- 'image': a placeholder URL for an image (e.g., 'https://via.placeholder.com/60'). "
                        f"Example: "
                        f"```json\n"
                        f"{{\n"
                        f"  \"word\": \"こんにちは\",\n"
                        f"  \"definition\": \"Hello greeting\",\n"
                        f"  \"example_sentence\": \"こんにちは、お元気ですか？ (Hello, how are you?)\",\n"
                        f"  \"image\": \"https://via.placeholder.com/60\"\n"
                        f"}}\n"
                        f"```"
                    )
                },
                {"role": "user", "content": f"Generate a flashcard for {category} in {target_language}."}
            ],
            max_tokens=200,
            temperature=0.5
        )
        raw_output = response.choices[0].message.content.strip()

        if raw_output.startswith("```json") and raw_output.endswith("```"):
            raw_output = raw_output[7:-3].strip()
        
        result = json.loads(raw_output)
        
        if not isinstance(result, dict) or not all(key in result for key in ["word", "definition", "example_sentence", "image"]):
            return {
                "word": "error",
                "definition": "Invalid response",
                "example_sentence": "Error occurred",
                "image": "https://via.placeholder.com/60"
            }
        
        flashcard_data = {
            "word": result["word"].strip(),
            "definition": result["definition"].strip(),
            "example_sentence": result["example_sentence"].strip(),
            "image": result["image"] or "https://via.placeholder.com/60"
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
                translation=flashcard_data["definition"],
                category_id=category_obj.id,
                used_count=1
            )
            db.add(flashcard)
            await db.commit()
            await db.refresh(flashcard)
            flashcard_data["flashcard_id"] = flashcard.id

        return flashcard_data
    except Exception as e:
        return {
            "word": f"Error: {str(e)}",
            "definition": "Translation error",
            "example_sentence": "Error occurred",
            "image": "https://via.placeholder.com/60"
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
        # Format conversation history
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
            model="gpt-4o-mini",
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
        # Format conversation for evaluation
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