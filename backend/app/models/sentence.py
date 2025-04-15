from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.category import Category

class DifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Sentence(Base):
    __tablename__ = "sentences"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)  # Original sentence in English
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)  # Track when last used
    used_count = Column(Integer, default=0)  # Track how many times used
    
    # Relationships
    category = relationship(Category, back_populates="sentences")
    results = relationship("UserSentenceResult", back_populates="sentence")

class UserSentenceResult(Base):
    __tablename__ = "user_sentence_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False)
    translated_sentence = Column(String, nullable=False)  # Sentence translated to user's language
    scrambled_order = Column(String, nullable=False)  # How it was scrambled
    user_answer = Column(String, nullable=False)  # User's attempted order
    is_correct = Column(Boolean, default=False)
    feedback = Column(Text, nullable=True)  # AI-generated feedback
    is_pinned = Column(Boolean, default=False)  # For saving results
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sentence_results")
    sentence = relationship("Sentence", back_populates="results")