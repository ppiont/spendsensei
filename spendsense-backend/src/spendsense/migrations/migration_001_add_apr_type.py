"""
Migration 001: Add apr_type field to accounts table

This migration adds the apr_type column to credit card accounts to distinguish
between different APR types: purchase, cash_advance, and penalty rates.
"""

import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_column_exists(db: AsyncSession, table: str, column: str) -> bool:
    """Check if a column exists in a table."""
    result = await db.execute(text(f"PRAGMA table_info({table})"))
    columns = {row[1] for row in result.fetchall()}
    return column in columns


async def migrate(db: AsyncSession) -> None:
    """
    Add apr_type column to accounts table.

    Sets default value of 'purchase' for existing credit card accounts.
    """
    try:
        # Check if column already exists
        if await check_column_exists(db, "accounts", "apr_type"):
            logger.info("Migration 001: apr_type column already exists, skipping")
            return

        logger.info("Migration 001: Adding apr_type column to accounts table...")

        # Add the column
        await db.execute(text(
            "ALTER TABLE accounts ADD COLUMN apr_type TEXT"
        ))

        # Set default value for existing credit cards
        await db.execute(text(
            "UPDATE accounts SET apr_type = 'purchase' WHERE subtype = 'credit_card' AND apr IS NOT NULL"
        ))

        await db.commit()

        logger.info("Migration 001: Successfully added apr_type column")
        logger.info("Migration 001: Set default 'purchase' for existing credit cards")

    except Exception as e:
        logger.error(f"Migration 001 failed: {e}")
        await db.rollback()
        raise


async def rollback(db: AsyncSession) -> None:
    """
    Rollback migration 001.

    Note: SQLite doesn't support DROP COLUMN in all versions.
    This is provided for reference but may not work on all SQLite versions.
    """
    logger.warning("Migration 001 rollback: SQLite may not support DROP COLUMN")
    try:
        await db.execute(text("ALTER TABLE accounts DROP COLUMN apr_type"))
        await db.commit()
        logger.info("Migration 001: Rolled back apr_type column")
    except Exception as e:
        logger.error(f"Migration 001 rollback failed: {e}")
        logger.warning("Manual database recreation may be required")
        raise
