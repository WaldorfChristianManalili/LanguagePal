import httpx
import os
import logging
from dotenv import load_dotenv
from functools import lru_cache
from time import sleep

load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=100)
async def get_image(query: str) -> str:
    """Fetch a medium-sized image URL from Pexels for the given query, with caching."""
    if not PEXELS_API_KEY:
        logger.error("Pexels API key not configured")
        return "https://placehold.co/600x400"
    
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}
    
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                if response.status_code == 429:
                    logger.warning(f"Pexels rate limit exceeded for query '{query}', retrying in {attempt + 1}s")
                    sleep(attempt + 1)
                    continue
                response.raise_for_status()
                data = response.json()
                photos = data.get("photos", [])
                if not photos:
                    logger.warning(f"No images found for query: {query}")
                    return "https://placehold.co/600x400"
                image_url = photos[0]["src"]["medium"]
                logger.info(f"Returning image URL for query '{query}': {image_url}")
                return image_url
            except (httpx.HTTPStatusError, httpx.RequestError, KeyError) as e:
                logger.error(f"Pexels API error for query '{query}': {str(e)}")
                return "https://placehold.co/600x400"