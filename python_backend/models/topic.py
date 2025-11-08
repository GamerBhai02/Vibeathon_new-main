"""Topic model"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from ..enums import  TopicStatus


class Topic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    summary: Optional[str] = None
    status: TopicStatus = Field(default=TopicStatus.PENDING)
    userId: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="topics")
    flashcards: List["Flashcard"] = Relationship(back_populates="topic")
    quizzes: List["Quiz"] = Relationship(back_populates="topic")
