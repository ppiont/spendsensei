"""Database configuration and session management for SpendSense"""

from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

from spendsense.config import settings

# Database connection string from config (supports environment variable overrides)
DATABASE_URL = settings.database_url

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Set to False in production
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create declarative base for ORM models
Base = declarative_base()


async def get_db():
    """FastAPI dependency for database sessions"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database: create tables and enable WAL mode"""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    async with engine.begin() as conn:
        # Import all models to ensure they're registered with Base.metadata

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Enable WAL mode for concurrent reads
        await conn.execute(text("PRAGMA journal_mode=WAL"))
