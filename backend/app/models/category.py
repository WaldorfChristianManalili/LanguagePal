from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    # Relationships - used to organize different types of content
    sentences = relationship("Sentence", back_populates="category")
    words = relationship("Word", back_populates="category")
    situations = relationship("Situation", back_populates="category")
    flashcard_sessions = relationship("FlashcardSession", back_populates="category")