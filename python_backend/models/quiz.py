"""Quiz and QuizQuestion models"""

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from ..enums import QuizDifficulty, QuizType


class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    difficulty: QuizDifficulty
    quizType: QuizType
    userId: int = Field(foreign_key="user.id")
    topicId: int = Field(foreign_key="topic.id")

    topic: "Topic" = Relationship(back_populates="quizzes")
    questions: List["QuizQuestion"] = Relationship(back_populates="quiz")


class QuizQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_text: str
    quizId: int = Field(foreign_key="quiz.id")

    quiz: Quiz = Relationship(back_populates="questions")
