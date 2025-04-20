from pydantic import BaseModel

class ProgressResponse(BaseModel):
    id: int
    category_id: int
    activity_id: str
    type: str
    completed: bool
    result: str