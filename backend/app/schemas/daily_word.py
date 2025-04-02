from pydantic import BaseModel
from datetime import datetime

class DailyWordBase(BaseModel):
    original_word: str
    translated_word: str
    definition: str
    example_sentence: str | None = None
    hint: str | None = None
    date: datetime
    image_url: str | None = None

class DailyWordCreate(DailyWordBase):
    pass

class DailyWord(DailyWordBase):
    id: int

    class Config:
        from_attributes = True

class UserDailyWordResultBase(BaseModel):
    user_id: int
    daily_word_id: int
    guesses: int = 0
    guesses_list: str | None = None
    guessed_correctly: bool = False
    attempted_at: datetime

class UserDailyWordResultCreate(UserDailyWordResultBase):
    pass

class UserDailyWordResult(UserDailyWordResultBase):
    id: int

    class Config:
        from_attributes = True