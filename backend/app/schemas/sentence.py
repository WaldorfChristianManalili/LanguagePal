from pydantic import BaseModel, Field
from typing import List, Optional

class Hint(BaseModel):
    text: str
    usefulness: int

class PinRequest(BaseModel):
    is_pinned: bool
    sentence_id: Optional[int] = None
    
class SentenceResponse(BaseModel):
    scrambled_words: List[str]
    original_sentence: str
    sentence_id: int
    english_sentence: str
    hints: List[Hint]

class SubmitSentenceRequest(BaseModel):
    sentence_id: int
    user_answer: str
    original_sentence: str

class SubmitSentenceResponse(BaseModel):
    is_correct: bool
    feedback: str
    translated_sentence: str
    result_id: int = Field(..., alias="id")  # Map 'id' from UserSentenceResult
    explanation: str 
    sentence_id: int
    user_answer: str

    class Config:
        from_attributes = True
        populate_by_name = True 