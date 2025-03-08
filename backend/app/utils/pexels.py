import requests
import os
from dotenv import load_dotenv

load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

async def get_image(query: str):
    if not PEXELS_API_KEY:
        return "https://placehold.co/600x400"  # Fallback image
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()["photos"][0]["src"]["medium"]