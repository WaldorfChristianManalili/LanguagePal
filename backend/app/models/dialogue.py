from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Dialogue(Base):
    __tablename__ = "dialogues"
    id = Column(Integer, primary_key=True, index=True)
    situation = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    category = relationship("Category", back_populates="dialogues")
    lesson = relationship("Lesson")