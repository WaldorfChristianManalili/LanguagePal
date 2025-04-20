from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    used_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    category = relationship("Category", back_populates="flashcards")