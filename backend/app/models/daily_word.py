from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class DailyWord(Base):
    __tablename__ = "daily_words"
    
    id = Column(Integer, primary_key=True, index=True)
    original_word = Column(String, index=True, nullable=False)  # Word in English
    translated_word = Column(String, nullable=False)  # Word in target language
    definition = Column(String, nullable=False)
    example_sentence = Column(String, nullable=True)
    hint = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), index=True, nullable=False)  # Set to UTC midnight
    image_url = Column(String, nullable=True)
    
    # Relationships
    results = relationship("UserDailyWordResult", back_populates="daily_word")

class UserDailyWordResult(Base):
    __tablename__ = "user_daily_word_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    daily_word_id = Column(Integer, ForeignKey("daily_words.id"), nullable=False)
    guesses = Column(Integer, default=0)  # Number of guesses made (max 6)
    guesses_list = Column(String, nullable=True)  # Store guesses as JSON
    guessed_correctly = Column(Boolean, default=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="daily_word_results")
    daily_word = relationship("DailyWord", back_populates="results")