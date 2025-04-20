from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    learning_language: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    learning_language: str | None = None
    is_active: bool | None = None

class UserResponse(UserBase):
    id: int
    openai_thread_id: str | None = None
    is_active: bool = True
    created_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True

class User(UserBase):  # Internal use
    id: int
    hashed_password: str
    openai_thread_id: str | None = None
    is_active: bool = True
    created_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True