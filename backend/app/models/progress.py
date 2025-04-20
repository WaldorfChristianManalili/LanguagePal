from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    activity_id = Column(String)
    type = Column(String)
    completed = Column(Boolean, default=False)
    result = Column(String)
    user = relationship("User", back_populates="progress")
    category = relationship("Category")