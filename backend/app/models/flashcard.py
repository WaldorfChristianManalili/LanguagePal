from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import json

class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    type = Column(String, nullable=False)
    english_equivalents = Column(String, nullable=False)  # JSON-encoded list
    definition = Column(String, nullable=False)
    english_definition = Column(String, nullable=False)
    example_sentence = Column(String, nullable=False)
    english_sentence = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    used_count = Column(Integer, default=0)
    options = Column(String, nullable=True)  # JSON-encoded list of options
    category = relationship("Category", back_populates="flashcards")
    user = relationship("User", back_populates="flashcards")

    def to_dict(self):
        return {
            "flashcard_id": self.id,
            "word": self.word,
            "translation": self.translation,
            "type": self.type,
            "english_equivalents": json.loads(self.english_equivalents),
            "definition": self.definition,
            "english_definition": self.english_definition,
            "example_sentence": self.example_sentence,
            "english_sentence": self.english_sentence,
            "options": json.loads(self.options) if self.options else []
        }