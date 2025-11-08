"""Database setup and session management"""
from sqlmodel import SQLModel, Session, create_engine

# Force SQLite (ignore environment DATABASE_URL)
DATABASE_URL = "sqlite:///./agentverse.db"

# Create SQLite engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session dependency"""
    with Session(engine) as session:
        yield session
