from pydantic import BaseModel

class FlashcardResponse(BaseModel):
    flashcard_id: int
    word: str
    translation: str
    category: str
    lesson_id: int

class SubmitFlashcardRequest(BaseModel):
    flashcard_id: int
    user_answer: str

class SubmitFlashcardResponse(BaseModel):
    is_correct: bool
    feedback: str
    translation: str
    result_id: int
    flashcard_id: int
    user_answer: str