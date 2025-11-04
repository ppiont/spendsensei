"""Initialize database and load synthetic data"""

import asyncio
from spendsense.database import init_db
from spendsense.services.synthetic_data import main_async

async def main():
    """Create tables, generate synthetic data, and load into database"""
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!\n")

    print("Generating and loading synthetic data...")
    await main_async(num_users=50, load=True)
    print("\nComplete!")

if __name__ == "__main__":
    asyncio.run(main())
