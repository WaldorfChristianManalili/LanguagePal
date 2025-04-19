import os
import json
import re
from openai import AsyncOpenAI
from dotenv import load_dotenv

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

        # Strip markdown code block if present
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
                    # Only exclude hints explicitly mentioning punctuation terms
                    if not any(p in text.lower() for p in ["question mark", "comma", "punctuation"]):
                        parsed_hints.append({"text": text.strip(), "usefulness": int(usefulness)})
            
        parsed_hints.sort(key=lambda x: x["usefulness"], reverse=True)
        explanation = result.get("explanation", "")
        
        # Convert numbered lists to bullet points
        explanation = re.sub(r'^\d+\.\s+', '- ', explanation, flags=re.MULTILINE)
        # Remove punctuation explanations
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