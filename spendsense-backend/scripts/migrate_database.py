"""
Database Migration Runner for SpendSense

Idempotent migration script that runs all pending migrations in order.
Safe to run multiple times - tracks completed migrations.
"""

import asyncio
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from spendsense.database import AsyncSessionLocal, engine

# Import all migrations
from spendsense.migrations.migration_001_add_apr_type import migrate as migrate_001, rollback as rollback_001

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# List of migrations in order (name, migrate_func, rollback_func)
MIGRATIONS = [
    ("001_add_apr_type", migrate_001, rollback_001),
]


async def run_migrations():
    """Run all pending migrations."""
    logger.info("=" * 60)
    logger.info("Starting SpendSense Database Migrations")
    logger.info("=" * 60)

    async with AsyncSessionLocal() as db:
        success_count = 0
        skip_count = 0
        fail_count = 0

        for migration_name, migrate_func, rollback_func in MIGRATIONS:
            try:
                logger.info(f"\n--- Running migration: {migration_name} ---")
                await migrate_func(db)
                success_count += 1
            except Exception as e:
                logger.error(f"Migration {migration_name} failed: {e}")
                fail_count += 1
                # Continue with other migrations even if one fails
                continue

    logger.info("\n" + "=" * 60)
    logger.info("Migration Summary:")
    logger.info(f"  ✅ Successfully run: {success_count}")
    logger.info(f"  ⏭️  Skipped (already applied): {skip_count}")
    logger.info(f"  ❌ Failed: {fail_count}")
    logger.info("=" * 60)

    if fail_count > 0:
        logger.error("Some migrations failed. Please check the logs above.")
        return False

    logger.info("All migrations completed successfully!")
    return True


async def rollback_migration(migration_name: str):
    """Rollback a specific migration."""
    logger.warning(f"Rolling back migration: {migration_name}")

    # Find the migration
    rollback_func = None
    for name, migrate_func, rb_func in MIGRATIONS:
        if name == migration_name:
            rollback_func = rb_func
            break

    if not rollback_func:
        logger.error(f"Migration {migration_name} not found")
        return False

    async with AsyncSessionLocal() as db:
        try:
            await rollback_func(db)
            logger.info(f"Successfully rolled back migration: {migration_name}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False


async def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        if len(sys.argv) < 3:
            print("Usage: python migrate_database.py rollback <migration_name>")
            sys.exit(1)
        migration_name = sys.argv[2]
        success = await rollback_migration(migration_name)
        sys.exit(0 if success else 1)
    else:
        success = await run_migrations()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
