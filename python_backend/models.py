"""SQLModel database models"""
from sqlmodel import Field, SQLModel, JSON, Column
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


def generate_id():
    return str(uuid.uuid4())


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(default_factory=generate_id, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class Topic(SQLModel, table=True):
    __tablename__ = "topics"
    
    id: str = Field(default_factory=generate_id, primary_key=True)
    userId: str = Field(foreign_key="users.id", index=True)
    name: str
    importanceScore: int
    masteryScore: int
    summary: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class StudyPlan(SQLModel, table=True):
    __tablename__ = "study_plans"
    
    id: str = Field(default_factory=generate_id, primary_key=True)
    userId: str = Field(foreign_key="users.id", index=True)
    startDate: str
    endDate: str
    examType: str
    blocks: List[Dict[str, Any]] = Field(sa_column=Column(JSON))
    weeklyGoal: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class PracticeQuestion(SQLModel, table=True):
    __tablename__ = "practice_questions"
    
    id: str = Field(default_factory=generate_id, primary_key=True)
    userId: str = Field(foreign_key="users.id", index=True)
    topicId: str = Field(foreign_key="topics.id", index=True)
    question: str
    hint: str
    steps: List[str] = Field(sa_column=Column(JSON))
    fullSolution: str
    rubric: str
    difficulty: str
    citations: List[str] = Field(sa_column=Column(JSON))
    confidence: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class MockExam(SQLModel, table=True):
    __tablename__ = "mock_exams"
    
    id: str = Field(default_factory=generate_id, primary_key=True)
    userId: str = Field(foreign_key="users.id", index=True)
    type: str
    title: str
    duration: int
    totalMarks: int
    questions: List[Dict[str, Any]] = Field(sa_column=Column(JSON))
    instructions: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class Attempt(SQLModel, table=True):
    __tablename__ = "attempts"
    
    id: str = Field(default_factory=generate_id, primary_key=True)
    userId: str = Field(foreign_key="users.id", index=True)
    mockId: str = Field(foreign_key="mock_exams.id", index=True)
    score: int
    timeTakenSec: int
    answers: List[Dict[str, Any]] = Field(sa_column=Column(JSON))
    topicBreakdown: Dict[str, Any] = Field(sa_column=Column(JSON))
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class Flashcard(SQLModel, table=True):
    __tablename__ = "flashcards"
    
    id: str = Field(default_factory=generate_id, primary_key=True)
    userId: str = Field(foreign_key="users.id", index=True)
    topicId: str = Field(foreign_key="topics.id", index=True)
    front: str
    back: str
    nextReviewAt: str
    easinessFactor: float = Field(default=2.5)
    interval: int = Field(default=1)
    repetitions: int = Field(default=0)
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    """Uploaded documents for RAG"""
    __tablename__ = "documents"
    
    id: str = Field(default_factory=generate_id, primary_key=True)
    userId: str = Field(foreign_key="users.id", index=True)
    filename: str
    contentType: str
    extractedText: str
    vectorIds: List[str] = Field(sa_column=Column(JSON))  # FAISS vector IDs
    createdAt: datetime = Field(default_factory=datetime.utcnow)
