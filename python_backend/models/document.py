"""Document model for uploaded files"""

from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List
from datetime import datetime

class Document(SQLModel, table=True):
    """Uploaded documents for RAG"""
    __tablename__ = "documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    userId: int = Field(foreign_key="user.id", index=True)
    filename: str
    contentType: str
    extractedText: str
    vectorIds: List[str] = Field(default=[], sa_column=Column(JSON))  # ChromaDB vector IDs
    createdAt: datetime = Field(default_factory=datetime.utcnow)
