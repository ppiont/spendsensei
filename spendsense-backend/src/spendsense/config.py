"""Application configuration using Pydantic Settings"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_database_url() -> str:
    """
    Get default database URL based on environment.

    For Railway, uses /app/data directory (volume mount).
    For local development, uses relative data/ directory.
    """
    # Check for Railway environment
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        return "sqlite+aiosqlite:////app/data/spendsense.db"
    return "sqlite+aiosqlite:///data/spendsense.db"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables can be set in .env file or system environment.
    """

    # Database
    # Override with DATABASE_URL environment variable
    database_url: str = get_default_database_url()

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",  # Vite dev server (default)
        "http://localhost:3000",  # Alternative frontend port
        "http://localhost:4173",  # Vite preview
    ]
    # Additional CORS origins from environment variable (comma-separated)
    # Set RAILWAY_PUBLIC_DOMAIN or FRONTEND_URL for production
    cors_origins_extra: str = ""

    # API
    api_title: str = "SpendSense API"
    api_version: str = "0.1.0"
    api_description: str = "Financial behavior analysis platform"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
