"""Application configuration using Pydantic Settings"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables can be set in .env file or system environment.
    """

    # Database
    database_url: str = "sqlite+aiosqlite:///data/spendsense.db"

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",  # Vite dev server (default)
        "http://localhost:3000",  # Alternative frontend port
        "http://localhost:4173",  # Vite preview
    ]

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
