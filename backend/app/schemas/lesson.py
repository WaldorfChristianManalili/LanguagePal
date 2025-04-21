from pydantic import BaseModel
from typing import List, Any

class Activity(BaseModel):
    id: str
    type: str
    data: Any
    completed: bool

class LessonResponse(BaseModel):
    activities: List[Activity]