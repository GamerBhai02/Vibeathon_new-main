"""User model"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

    topics: List["Topic"] = Relationship(back_populates="user")
    flashcards: List["Flashcard"] = Relationship(back_populates="user")
