#!/usr/bin/env python3
"""
Database initialization script for Railway deployment.

This script:
1. Creates all database tables
2. Checks if data already exists
3. Optionally loads synthetic data if database is empty

Safe to run multiple times (idempotent).
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select, text
from spendsense.database import engine, Base, AsyncSessionLocal
from spendsense.models.user import User
from spendsense.models.account import Account
from spendsense.models.transaction import Transaction
from spendsense.models.content import Content
from spendsense.models.persona import Persona
from spendsense.models.operator_override import OperatorOverride


async def init_database():
    """Initialize database schema and optionally load data"""

    print("=" * 80)
    print("Railway Database Initialization")
    print("=" * 80)

    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Data directory exists: {data_dir.absolute()}")

    # Create tables
    print("\n📦 Creating database schema...")
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Enable WAL mode for better concurrency
        await conn.execute(text("PRAGMA journal_mode=WAL"))

    print("✅ Database schema created")

    # Check if database already has data
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

        if users:
            print(f"\n✅ Database already initialized with {len(users)} users")
            print("   Skipping synthetic data generation (database not empty)")
            return True

        print("\n⚠️  Database is empty - synthetic data generation required")
        print("   Run synthetic data generator script separately:")
        print("   uv run python scripts/init_and_load_data.py")

    print("\n" + "=" * 80)
    print("✅ Database initialization complete")
    print("=" * 80)

    return True


async def main():
    """Main entry point"""
    try:
        success = await init_database()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ ERROR: Database initialization failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
