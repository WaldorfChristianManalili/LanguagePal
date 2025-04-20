from pydantic import BaseModel
from typing import List

class LessonSchema(BaseModel):
    id: int
    title: str
    subtitle: str | None
    image: str
    completed: bool
    categoryId: int

class DashboardResponse(BaseModel):
    id: int
    name: str
    difficulty: str
    progress: float
    lessons: List[LessonSchema]