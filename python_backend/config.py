"""Application configuration"""
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./agentverse.db"
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24 * 7  # 7 days
    
    # AI Model APIs
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyB7leC6LVpjdkSlUzpSkW9zVjl1oO4R5gw")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # External services
    JUDGE0_API_KEY: str = os.getenv("JUDGE0_API_KEY", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
    # Application
    FAISS_INDEX_PATH: str = "./faiss_index"
    UPLOAD_DIR: str = "/tmp/uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
