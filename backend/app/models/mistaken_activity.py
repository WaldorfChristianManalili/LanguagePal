from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class MistakenActivity(Base):
    __tablename__ = "mistaken_activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    activity_id = Column(String, index=True)
    activity_type = Column(String)  # "flashcard" or "sentence"
    word = Column(String, nullable=True)  # For flashcard mistakes