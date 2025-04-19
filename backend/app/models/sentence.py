from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Sentence(Base):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)  # English sentence
    category_id = Column(Integer, ForeignKey("categories.id"))
    used_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)

    category = relationship("Category", back_populates="sentences")
    translations = relationship("SentenceTranslation", back_populates="sentence")

class SentenceTranslation(Base):
    __tablename__ = "sentence_translations"

    id = Column(Integer, primary_key=True, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False)
    language = Column(String, nullable=False)
    translated_text = Column(String, nullable=False)
    translated_words = Column(ARRAY(String), nullable=False)
    explanation = Column(String, nullable=True)
    hints = Column(ARRAY(String), nullable=True)

    sentence = relationship("Sentence", back_populates="translations")

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

    user = relationship("User", back_populates="sentence_results")
    sentence = relationship("Sentence")