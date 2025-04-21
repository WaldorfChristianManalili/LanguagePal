from fastapi import APIRouter, HTTPException
from app.utils.pexels import get_image

router = APIRouter(tags=["pexels"])

@router.get("/image")
async def fetch_pexels_image(query: str) -> dict:
    """Fetch a Pexels image URL for the given query."""
    try:
        image_url = await get_image(query)
        return {"image_url": image_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")