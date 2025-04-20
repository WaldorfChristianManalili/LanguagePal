from pydantic import BaseModel
from typing import List, Dict

class SentenceResponse(BaseModel):
    scrambled_words: List[str]
    original_sentence: str
    sentence_id: int
    english_sentence: str
    hints: List[Dict[str, str | int]]

class SubmitSentenceRequest(BaseModel):
    sentence_id: int
    user_answer: str

class SubmitSentenceResponse(BaseModel):
    is_correct: bool
    feedback: str
    translated_sentence: str
    result_id: int
    explanation: str
    sentence_id: int
    user_answer: str