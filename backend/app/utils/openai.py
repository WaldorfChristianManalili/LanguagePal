from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

async def translate_sentence(sentence: str, target_language: str):
    if not client:
        return "OpenAI API key not provided - translation disabled"
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Translate '{sentence}' to {target_language}"}]
    )
    return response.choices[0].message.content