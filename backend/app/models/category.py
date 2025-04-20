from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    chapter = Column(Integer, default=1)
    difficulty = Column(String, default="A1")
    sentences = relationship("Sentence", back_populates="category")
    flashcards = relationship("Flashcard", back_populates="category")
    lessons = relationship("Lesson", back_populates="category")
    dialogues = relationship("Dialogue", back_populates="category")