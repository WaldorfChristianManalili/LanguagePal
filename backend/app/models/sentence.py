from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Sentence(Base):
    __tablename__ = "sentences"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    used_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    category = relationship("Category", back_populates="sentences")
    translations = relationship("SentenceTranslation", back_populates="sentence")

class SentenceTranslation(Base):
    __tablename__ = "sentence_translations"
    id = Column(Integer, primary_key=True, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id"))
    language = Column(String, nullable=False)
    translated_text = Column(String, nullable=False)
    translated_words = Column(String, nullable=False)  # JSON-encoded list
    hints = Column(String, nullable=True)  # JSON-encoded list
    explanation = Column(String, nullable=True)
    sentence = relationship("Sentence", back_populates="translations")