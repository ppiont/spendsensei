"""Database configuration and session management for SpendSense"""

import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text, select

from spendsense.config import settings

logger = logging.getLogger(__name__)

# Database connection string from config (supports environment variable overrides)
DATABASE_URL = settings.database_url

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Disable SQL logging in production
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
    """Initialize database: create tables, enable WAL mode, and load demo data if empty"""
    import os

    # Create data directory if it doesn't exist
    # Use /app/data for Railway, relative data/ for local
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        data_dir = Path("/app/data")
    else:
        data_dir = Path("data")
    data_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"Using data directory: {data_dir.absolute()}")

    async with engine.begin() as conn:
        # Import all models to ensure they're registered with Base.metadata
        # This must happen BEFORE create_all is called
        from spendsense.models.user import User  # noqa: F401
        from spendsense.models.account import Account  # noqa: F401
        from spendsense.models.transaction import Transaction  # noqa: F401
        from spendsense.models.persona import Persona  # noqa: F401
        from spendsense.models.content import Content  # noqa: F401
        from spendsense.models.feedback import Feedback  # noqa: F401
        from spendsense.models.operator_override import OperatorOverride  # noqa: F401

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Enable WAL mode for concurrent reads
        await conn.execute(text("PRAGMA journal_mode=WAL"))

    # Check if database is empty and load demo data
    # Import User model at this scope for query
    from spendsense.models.user import User
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        if not users:
            logger.info("Database is empty - generating 50 demo users...")
            try:
                # Import synthetic data generator
                from spendsense.ingest.synthetic_generator import (
                    generate_dataset,
                    save_dataset,
                    load_data_from_json,
                )

                logger.info("Step 1/2: Generating synthetic data...")
                dataset = generate_dataset(num_users=50)
                save_dataset(dataset)

                logger.info("Step 2/2: Loading data into database...")
                await load_data_from_json(session)

                # Verify data loaded
                result = await session.execute(select(User))
                loaded_users = result.scalars().all()
                logger.info(f"Successfully loaded {len(loaded_users)} demo users")
            except Exception as e:
                logger.error(f"Failed to load demo data: {e}")
                raise
        else:
            logger.info(f"Database already contains {len(users)} users")
