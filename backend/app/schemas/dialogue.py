from pydantic import BaseModel
from datetime import datetime

class DialogueBase(BaseModel):
    user_id: int
    situation_id: int
    openai_thread_id: str
    started_at: datetime
    completed_at: datetime | None = None
    evaluation_score: float | None = None
    evaluation_feedback: str | None = None
    message_count: int = 0

class DialogueCreate(DialogueBase):
    pass

class Dialogue(DialogueBase):
    id: int

    class Config:
        from_attributes = True

class DialogueMessageBase(BaseModel):
    dialogue_id: int
    is_user: bool = True
    content: str
    translation: str | None = None
    created_at: datetime

class DialogueMessageCreate(DialogueMessageBase):
    pass

class DialogueMessage(DialogueMessageBase):
    id: int

    class Config:
        from_attributes = True