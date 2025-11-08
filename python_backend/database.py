"""Database connection and session management."""

from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# The connect_args is for SQLite only
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def get_session():
    """Provides a database session."""
    with Session(engine) as session:
        yield session
