import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key, max_retries=0) if api_key else None

async def translate_sentence(sentence: str, target_language: str) -> dict:
    if not client:
        logger.error("OpenAI API key not provided - translation disabled")
        return {"words": ["OpenAI API key not provided"], "sentence": "Translation disabled"}
    
    try:
        logger.debug(f"Translating '{sentence}' to {target_language}")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Translate the sentence to {target_language}. "
                        f"Return a JSON object with: "
                        f"'words': array of words/phrases and punctuation (e.g., 'お元気', 'です', 'か', '?'), "
                        f"excluding commas (',' or '，'). "
                        f"'sentence': full sentence without commas. "
                        f"Example: {{ \"words\": [\"こんにちは\", \"お元気\", \"です\", \"か\", \"?\"], \"sentence\": \"こんにちは お元気 です か ?\" }}"
                    )
                },
                {"role": "user", "content": sentence}
            ],
            max_tokens=100,
            temperature=0.3
        )
        raw_output = response.choices[0].message.content.strip()
        logger.debug(f"Raw model response: {raw_output}")

        # Parse JSON
        result = json.loads(raw_output)
        
        # Handle list result
        if isinstance(result, list):
            logger.warning(f"Received list instead of dict: {result}")
            words = [word.strip() for word in result if word.strip() not in [",", "，"]]
            sentence = " ".join(words).strip()
            return {"words": words, "sentence": sentence}
        
        # Validate dictionary
        if not isinstance(result, dict) or "words" not in result or "sentence" not in result:
            logger.error(f"Invalid result format: {result}")
            return {"words": ["Invalid response format"], "sentence": "Translation error"}
        
        # Filter commas
        words = [word.strip() for word in result.get("words", []) if word.strip() not in [",", "，"]]
        sentence = result.get("sentence", " ".join(words)).strip().rstrip(",").rstrip("，")
        
        logger.debug(f"Parsed translated words: {words}, sentence: {sentence}")
        return {"words": words, "sentence": sentence}
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {str(e)}, raw_output: {raw_output}")
        return {"words": [f"Translation error: {str(e)}"], "sentence": "Translation error"}
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {"words": [f"Translation error: {str(e)}"], "sentence": "Translation error"}