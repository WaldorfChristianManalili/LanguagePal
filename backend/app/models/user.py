from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    learning_language = Column(String, nullable=False)  # e.g., "Japanese", "Spanish"
    openai_thread_id = Column(String, nullable=True)  # User's own OpenAI thread
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sentence_results = relationship("UserSentenceResult", back_populates="user")
    flashcard_sessions = relationship("FlashcardSession", back_populates="user")
    daily_word_results = relationship("UserDailyWordResult", back_populates="user")
    dialogues = relationship("Dialogue", back_populates="user")