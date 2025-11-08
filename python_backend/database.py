"""Database connection and session management."""

from sqlmodel import create_engine, Session
from .config import settings

# Use DATABASE_URL from settings
DATABASE_URL = settings.DATABASE_URL

# The connect_args is for SQLite only - remove for PostgreSQL
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def get_session():
    """Provides a database session."""
    with Session(engine) as session:
        yield session
