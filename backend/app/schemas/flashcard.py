from pydantic import BaseModel
from typing import List, Dict

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
    category: str
    lesson_id: int
    options: List[Dict[str, str]]