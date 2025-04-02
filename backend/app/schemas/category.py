from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True  # Enables ORM mode for SQLAlchemy compatibility