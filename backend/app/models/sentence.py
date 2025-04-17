from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Sentence(Base):
    __tablename__ = "sentences"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
    used_count = Column(Integer, default=0)
    
    # Add relationship
    category = relationship("Category", back_populates="sentences")

class SentenceTranslation(Base):
    __tablename__ = "sentence_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False)
    language = Column(String, nullable=False)
    translated_text = Column(String, nullable=False)
    translated_words = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSentenceResult(Base):
    __tablename__ = "user_sentence_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False)
    translated_sentence = Column(String, nullable=False)
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    feedback = Column(String, nullable=False)
    is_pinned = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    
    # Fixed relationship
    user = relationship("User", back_populates="sentence_results")