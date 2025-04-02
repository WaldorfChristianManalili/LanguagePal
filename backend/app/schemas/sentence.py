from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class SentenceBase(BaseModel):
    text: str
    difficulty: DifficultyLevel
    category_id: int | None = None
    created_at: datetime
    last_used_at: datetime | None = None
    used_count: int = 0

class SentenceCreate(SentenceBase):
    pass

class Sentence(SentenceBase):
    id: int

    class Config:
        from_attributes = True

class UserSentenceResultBase(BaseModel):
    user_id: int
    sentence_id: int
    translated_sentence: str
    scrambled_order: str
    user_answer: str
    is_correct: bool = False
    feedback: str | None = None
    is_pinned: bool = False
    attempted_at: datetime

class UserSentenceResultCreate(UserSentenceResultBase):
    pass

class UserSentenceResult(UserSentenceResultBase):
    id: int

    class Config:
        from_attributes = True