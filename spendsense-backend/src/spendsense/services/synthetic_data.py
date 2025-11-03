"""Synthetic data generator for SpendSense using Faker"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import AsyncSessionLocal
from spendsense.models.user import User
from spendsense.models.account import Account
from spendsense.models.transaction import Transaction

# Initialize Faker with seed for deterministic output
fake = Faker()
Faker.seed(42)
random.seed(42)

# Transaction category weights
CATEGORY_WEIGHTS = [
    ("FOOD_AND_DRINK", 0.25),
    ("GENERAL_MERCHANDISE", 0.20),
    ("TRANSPORTATION", 0.15),
    ("ENTERTAINMENT", 0.10),
    ("UTILITIES", 0.10),
    ("HEALTHCARE", 0.05),
    ("INCOME", 0.15),
]


def generate_user() -> dict[str, Any]:
    """Generate a single synthetic user profile"""
    user_id = fake.uuid4()

    return {
        "id": user_id,
        "name": fake.name(),
        "email": fake.email(),
        "consent": False,
        "created_at": fake.date_time_between(start_date="-2y").isoformat(),
    }


def generate_accounts(user_id: str) -> list[dict[str, Any]]:
    """Generate 1-3 accounts for a user"""
    num_accounts = random.randint(1, 3)
    accounts = []

    # Define possible account types
    account_types = [
        ("depository", "checking"),
        ("depository", "savings"),
        ("credit", "credit_card"),
    ]

    for _ in range(num_accounts):
        account_type, subtype = random.choice(account_types)
        account_id = fake.uuid4()
        balance = random.randint(100, 50000) * 100  # in cents

        account = {
            "id": account_id,
            "user_id": user_id,
            "type": account_type,
            "subtype": subtype,
            "name": f"{fake.company()} {subtype.replace('_', ' ').title()}",
            "mask": fake.bothify(text="####"),
            "balance": balance,
            "currency": "USD",
        }

        # Add credit card specific fields
        if account_type == "credit":
            limit = random.randint(1000, 25000) * 100
            account["limit"] = limit
            account["apr"] = round(random.uniform(12.99, 29.99), 2)
            account["min_payment"] = int(balance * 0.02)  # 2% minimum payment
            account["is_overdue"] = False
        else:
            account["limit"] = None
            account["apr"] = None
            account["min_payment"] = None
            account["is_overdue"] = False

        accounts.append(account)

    return accounts


def generate_transactions(account: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate 20-100 transactions for an account"""
    num_transactions = random.randint(20, 100)
    transactions = []

    # Extract category names and weights
    categories = [cat for cat, _ in CATEGORY_WEIGHTS]
    weights = [weight for _, weight in CATEGORY_WEIGHTS]

    for _ in range(num_transactions):
        transaction_id = fake.uuid4()
        date = fake.date_time_between(start_date="-180d")
        category = random.choices(categories, weights=weights)[0]

        # Generate amount based on category
        if category == "INCOME":
            # Income is negative (credit to account)
            amount = -random.randint(2000, 6000) * 100
        else:
            # Expenses are positive (debit from account)
            amount = random.randint(5, 250) * 100

        # 5% of transactions are pending
        pending = random.random() < 0.05

        transaction = {
            "id": transaction_id,
            "account_id": account["id"],
            "date": date.isoformat(),
            "amount": amount,
            "merchant_name": fake.company(),
            "category": category,
            "pending": pending,
        }

        transactions.append(transaction)

    # Sort transactions by date (oldest first)
    transactions.sort(key=lambda t: t["date"])

    return transactions


def generate_dataset(num_users: int = 50) -> dict[str, list[dict[str, Any]]]:
    """Generate complete dataset with users, accounts, and transactions"""
    print(f"Generating dataset with {num_users} users...")

    all_users = []
    all_accounts = []
    all_transactions = []

    for i in range(num_users):
        # Generate user
        user = generate_user()
        all_users.append(user)

        # Generate accounts for user
        accounts = generate_accounts(user["id"])
        all_accounts.extend(accounts)

        # Generate transactions for each account
        for account in accounts:
            transactions = generate_transactions(account)
            all_transactions.extend(transactions)

        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{num_users} users...")

    dataset = {
        "users": all_users,
        "accounts": all_accounts,
        "transactions": all_transactions,
    }

    print(f"\nGeneration complete:")
    print(f"  - {len(all_users)} users")
    print(f"  - {len(all_accounts)} accounts")
    print(f"  - {len(all_transactions)} transactions")

    return dataset


def save_dataset(dataset: dict[str, Any], output_path: str = "data/users.json"):
    """Save dataset to JSON file"""
    output_file = Path(output_path)
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"\nDataset saved to: {output_path}")


async def load_data_from_json(db: AsyncSession, json_path: str = "data/users.json"):
    """Load synthetic data from JSON file into database"""
    print(f"Loading data from {json_path}...")

    # Read JSON file
    with open(json_path, "r") as f:
        dataset = json.load(f)

    try:
        # Create User instances
        users = []
        for user_data in dataset["users"]:
            user = User(
                id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
                consent=user_data["consent"],
                created_at=datetime.fromisoformat(user_data["created_at"]),
            )
            users.append(user)

        # Create Account instances
        accounts = []
        for account_data in dataset["accounts"]:
            account = Account(
                id=account_data["id"],
                user_id=account_data["user_id"],
                type=account_data["type"],
                subtype=account_data["subtype"],
                name=account_data["name"],
                mask=account_data["mask"],
                balance=account_data["balance"],
                limit=account_data.get("limit"),
                currency=account_data["currency"],
                apr=account_data.get("apr"),
                min_payment=account_data.get("min_payment"),
                is_overdue=account_data["is_overdue"],
            )
            accounts.append(account)

        # Create Transaction instances
        transactions = []
        for txn_data in dataset["transactions"]:
            transaction = Transaction(
                id=txn_data["id"],
                account_id=txn_data["account_id"],
                date=datetime.fromisoformat(txn_data["date"]),
                amount=txn_data["amount"],
                merchant_name=txn_data["merchant_name"],
                category=txn_data["category"],
                pending=txn_data["pending"],
            )
            transactions.append(transaction)

        # Batch insert all data
        db.add_all(users)
        db.add_all(accounts)
        db.add_all(transactions)

        await db.commit()

        print(f"\nLoaded into database:")
        print(f"  - {len(users)} users")
        print(f"  - {len(accounts)} accounts")
        print(f"  - {len(transactions)} transactions")

    except Exception as e:
        await db.rollback()
        print(f"Error loading data: {e}")
        raise


async def main_async(num_users: int = 50, load: bool = False):
    """Async main function for CLI"""
    # Generate dataset
    dataset = generate_dataset(num_users)
    save_dataset(dataset)

    # Optionally load into database
    if load:
        async with AsyncSessionLocal() as db:
            await load_data_from_json(db)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic financial data")
    parser.add_argument(
        "--num-users",
        type=int,
        default=50,
        help="Number of users to generate (default: 50)",
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load generated data into database",
    )

    args = parser.parse_args()

    # Run async main
    asyncio.run(main_async(num_users=args.num_users, load=args.load))


if __name__ == "__main__":
    main()
