from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Situation(Base):
    __tablename__ = "situations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    difficulty_level = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_free_chat = Column(Boolean, default=False)  # Flag for unlimited messages
    max_messages = Column(Integer, default=10)  # Default message limit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)  # Track when last used
    used_count = Column(Integer, default=0)  # Track how many times used
    
    # Relationships
    category = relationship("Category", back_populates="situations")
    dialogues = relationship("Dialogue", back_populates="situation")