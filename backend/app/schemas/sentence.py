from pydantic import BaseModel
from typing import List

class SentenceResponse(BaseModel):
    scrambled_words: List[str]
    original_sentence: str
    sentence_id: int

    class Config:
        from_attributes = True

class SubmitSentenceRequest(BaseModel):
    sentence_id: int
    constructed_sentence: str
    original_sentence: str

class SubmitSentenceResponse(BaseModel):
    is_correct: bool
    feedback: str
    correct_sentence: str
    result_id: int
    is_pinned: bool