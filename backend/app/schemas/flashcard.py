from pydantic import BaseModel
from datetime import datetime

class WordBase(BaseModel):
    original_word: str
    translated_word: str
    definition: str
    example_sentence: str | None = None
    image_url: str | None = None
    category_id: int
    created_at: datetime
    created_by_ai: bool = True

class WordCreate(WordBase):
    pass

class Word(WordBase):
    id: int

    class Config:
        from_attributes = True

class FlashcardSessionBase(BaseModel):
    user_id: int
    category_id: int
    started_at: datetime
    completed_at: datetime | None = None

class FlashcardSessionCreate(FlashcardSessionBase):
    pass

class FlashcardSession(FlashcardSessionBase):
    id: int

    class Config:
        from_attributes = True

class FlashcardResultBase(BaseModel):
    session_id: int
    word_id: int
    is_correct: bool = False
    user_response: str | None = None
    is_pinned: bool = False
    created_at: datetime

class FlashcardResultCreate(FlashcardResultBase):
    pass

class FlashcardResult(FlashcardResultBase):
    id: int

    class Config:
        from_attributes = True