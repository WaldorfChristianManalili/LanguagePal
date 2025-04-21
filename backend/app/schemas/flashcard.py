from pydantic import BaseModel
from typing import List, Optional

class FlashcardResponse(BaseModel):
    flashcard_id: int
    word: str
    translation: str
    type: str
    english_equivalents: List[str]
    definition: str
    english_definition: str
    example_sentence: str
    english_sentence: str
    category_id: int
    user_id: int
    used_count: int
    options: Optional[List[str]] = []

    class Config:
        from_attributes = True
