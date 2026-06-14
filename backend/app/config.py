"""
KisanAI Backend Configuration
Adapted for local development (SQLite, no Docker required).
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "KisanAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # Database — SQLite for local dev (no Docker needed)
    DATABASE_URL: str = "sqlite+aiosqlite:///./kisanai.db"

    # Redis (optional — gracefully degrades)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Local file storage (replaces MinIO for local dev)
    UPLOAD_DIR: str = str(Path(__file__).parent.parent.parent / "data" / "uploads")

    # ML
    MODEL_DIR: str = str(Path(__file__).parent.parent.parent / "models")
    KNOWLEDGE_BASE_DIR: str = str(Path(__file__).parent.parent.parent / "data" / "knowledge_base")
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/jpg"]

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"]

    # Fine-tuning
    MIN_SUBMISSIONS_FOR_FINETUNE: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
