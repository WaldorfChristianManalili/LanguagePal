from pydantic import BaseModel
from datetime import datetime

class SituationBase(BaseModel):
    title: str
    description: str
    difficulty_level: str
    category_id: int | None = None
    is_free_chat: bool = False
    max_messages: int = 10
    created_at: datetime
    last_used_at: datetime | None = None
    used_count: int = 0

class SituationCreate(SituationBase):
    pass

class Situation(SituationBase):
    id: int

    class Config:
        from_attributes = True