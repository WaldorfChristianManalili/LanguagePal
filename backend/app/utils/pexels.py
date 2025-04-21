import httpx
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

async def get_image(query: str) -> str:
    """Fetch a medium-sized image URL from Pexels for the given query."""
    if not PEXELS_API_KEY:
        return "https://placehold.co/600x400"  # Fallback image
    
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()  # Raise for non-2xx status codes
            data = response.json()
            photos = data.get("photos", [])
            if not photos:
                return "https://placehold.co/600x400"  # Fallback if no photos
            return photos[0]["src"]["medium"]
        except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
            raise HTTPException(status_code=500, detail=f"Pexels API error: {str(e)}")