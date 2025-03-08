from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Dialogue(Base):
    __tablename__ = "dialogues"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    situation_id = Column(Integer, ForeignKey("situations.id"), nullable=False)
    openai_thread_id = Column(String, nullable=False)  # OpenAI thread for this dialogue
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    evaluation_score = Column(Float, nullable=True)  # AI evaluation score (0-10)
    evaluation_feedback = Column(Text, nullable=True)  # Detailed feedback
    message_count = Column(Integer, default=0)  # Count of messages in dialogue
    
    # Relationships
    user = relationship("User", back_populates="dialogues")
    situation = relationship("Situation", back_populates="dialogues")
    messages = relationship("DialogueMessage", back_populates="dialogue")

class DialogueMessage(Base):
    __tablename__ = "dialogue_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    dialogue_id = Column(Integer, ForeignKey("dialogues.id"), nullable=False)
    is_user = Column(Boolean, default=True)  # True if user sent message, False if AI
    content = Column(Text, nullable=False)  # In target language
    translation = Column(Text, nullable=True)  # Translation if requested
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dialogue = relationship("Dialogue", back_populates="messages")