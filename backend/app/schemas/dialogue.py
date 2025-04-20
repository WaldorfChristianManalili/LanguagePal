from pydantic import BaseModel
from typing import List, Dict

class DialogueResponse(BaseModel):
    dialogue_id: int
    situation: str
    conversation: List[Dict[str, str]]
    category: str
    lesson_id: int

class ChatRequest(BaseModel):
    dialogue_id: int
    conversation: List[Dict[str, str]]

class ChatResponse(BaseModel):
    dialogue_id: int
    conversation: List[Dict[str, str]]
    is_complete: bool

class TranslateResponse(BaseModel):
    translation: str

class SubmitDialogueRequest(BaseModel):
    dialogue_id: int
    conversation: List[Dict[str, str]]

class SubmitDialogueResponse(BaseModel):
    is_correct: bool
    feedback: str
    result_id: int
    dialogue_id: int