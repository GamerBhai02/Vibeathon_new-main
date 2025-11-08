"""Flashcard model"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import date, datetime


class Flashcard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    front: str
    back: str
    userId: int = Field(foreign_key="user.id")
    topicId: Optional[int] = Field(default=None, foreign_key="topic.id")

    # SM-2 algorithm fields
    repetition: int = Field(default=0)
    easinessFactor: float = Field(default=2.5)
    interval: int = Field(default=1)  # In days
    nextReviewDate: date = Field(default_factory=lambda: datetime.utcnow().date())

    user: "User" = Relationship(back_populates="flashcards")
    topic: Optional["Topic"] = Relationship(back_populates="flashcards")
