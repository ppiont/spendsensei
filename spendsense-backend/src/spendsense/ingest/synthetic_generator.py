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

# Transaction category weights with detailed subcategories
# Format: (primary_category, detailed_category, weight)
CATEGORY_WEIGHTS = [
    ("FOOD_AND_DRINK", "RESTAURANTS", 0.15),
    ("FOOD_AND_DRINK", "GROCERIES", 0.10),
    ("GENERAL_MERCHANDISE", "SUPERSTORES", 0.12),
    ("GENERAL_MERCHANDISE", "ONLINE_MARKETPLACES", 0.08),
    ("TRANSPORTATION", "GAS", 0.08),
    ("TRANSPORTATION", "PUBLIC_TRANSPORTATION", 0.07),
    ("ENTERTAINMENT", "MOVIES_AND_MUSIC", 0.05),
    ("ENTERTAINMENT", "SPORTING_EVENTS_AMUSEMENT_PARKS_AND_MUSEUMS", 0.05),
    ("UTILITIES", "ELECTRIC", 0.05),
    ("UTILITIES", "INTERNET_AND_CABLE", 0.05),
    ("HEALTHCARE", "PRIMARY_CARE", 0.03),
    ("HEALTHCARE", "PHARMACIES", 0.02),
    ("INCOME", "INCOME", 0.15),
]

# Merchant entity IDs for recurring merchants (normalized)
MERCHANT_ENTITIES = [
    "starbucks_corp",
    "mcdonalds_corp",
    "whole_foods_market",
    "trader_joes",
    "shell_oil",
    "chevron_corp",
    "amazon_com",
    "walmart_inc",
    "target_corp",
    "netflix_inc",
    "spotify_ab",
    "apple_inc",
]

# Payment channel options
PAYMENT_CHANNELS = ["online", "in_store", "other"]


def generate_user() -> dict[str, Any]:
    """Generate a single synthetic user profile"""
    user_id = fake.uuid4()
    # Ensure unique email by incorporating uuid
    base_email = fake.email()
    username, domain = base_email.split('@')
    unique_email = f"{username}+{user_id[:8]}@{domain}"

    return {
        "id": user_id,
        "name": fake.name(),
        "email": unique_email,
        "consent": False,
        "created_at": fake.date_time_between(start_date="-2y").isoformat(),
    }


def generate_accounts(user_id: str) -> list[dict[str, Any]]:
    """Generate 3-5 accounts for a user with Plaid-compliant fields.

    Ensures each user has at minimum:
    - 1 checking account (for income transactions)
    - 1 credit card (for credit utilization signals)
    - 1 savings account (for savings signals)

    Plus 0-2 additional random accounts for variety.
    """
    accounts = []

    # Core account types that every user needs for signal detection
    core_account_types = [
        ("depository", "checking"),   # Required for income signals
        ("credit", "credit_card"),    # Required for credit signals
        ("depository", "savings"),    # Required for savings signals
    ]

    # Additional account types for variety
    extra_account_types = [
        ("loan", "mortgage"),
        ("loan", "student_loan"),
        ("depository", "money_market"),
    ]

    # Start with core accounts
    selected_types = list(core_account_types)

    # Add 0-2 extra account types
    num_extra = random.randint(0, 2)
    if num_extra > 0:
        selected_types.extend(random.sample(extra_account_types, min(num_extra, len(extra_account_types))))

    for account_type, subtype in selected_types:
        account_id = fake.uuid4()

        # Generate Plaid-compliant balance fields
        current = random.randint(100, 50000) * 100  # in cents
        available = current - random.randint(0, 500) * 100  # slightly less available

        account = {
            "id": account_id,
            "user_id": user_id,
            "type": account_type,
            "subtype": subtype,
            "name": f"{fake.company()} {subtype.replace('_', ' ').title()}",
            "mask": fake.bothify(text="####"),
            "current_balance": current,
            "available_balance": available,
            "currency": "USD",
            "holder_category": "personal",  # All personal accounts per requirements
        }

        # Add credit card specific fields
        if account_type == "credit":
            limit = random.randint(1000, 25000) * 100
            account["limit"] = limit
            account["apr"] = round(random.uniform(12.99, 29.99), 2)
            # APR types: purchase (70%), cash_advance (20%), penalty (10%)
            account["apr_type"] = random.choices(
                ["purchase", "cash_advance", "penalty"],
                weights=[0.7, 0.2, 0.1]
            )[0]
            account["min_payment"] = int(current * 0.02)  # 2% minimum payment
            account["is_overdue"] = False

            # Credit card payment tracking fields
            account["last_payment_amount"] = random.randint(50, 500) * 100
            account["last_payment_date"] = fake.date_time_between(start_date="-30d").isoformat()
            account["next_payment_due_date"] = fake.date_time_between(start_date="+1d", end_date="+30d").isoformat()
            account["last_statement_balance"] = random.randint(100, 2000) * 100
            account["last_statement_date"] = fake.date_time_between(start_date="-60d", end_date="-30d").isoformat()
            account["interest_rate"] = None
        elif account_type == "loan":
            # Loan-specific fields (mortgages and student loans)
            account["limit"] = None
            account["apr"] = None
            account["apr_type"] = None
            account["min_payment"] = None
            account["is_overdue"] = False
            account["last_payment_amount"] = None
            account["last_payment_date"] = None
            account["last_statement_balance"] = None
            account["last_statement_date"] = None

            if subtype == "mortgage":
                # Mortgage: $100k-$500k balance, 3-7% interest rate
                account["current_balance"] = random.randint(100000, 500000) * 100  # $100k-$500k in cents
                account["available_balance"] = None  # Loans don't have available balance
                account["interest_rate"] = round(random.uniform(0.03, 0.07), 4)  # 3-7%
                account["next_payment_due_date"] = fake.date_time_between(start_date="+1d", end_date="+30d").isoformat()
            elif subtype == "student_loan":
                # Student loan: $10k-$150k balance, 4-8% interest rate
                account["current_balance"] = random.randint(10000, 150000) * 100  # $10k-$150k in cents
                account["available_balance"] = None  # Loans don't have available balance
                account["interest_rate"] = round(random.uniform(0.04, 0.08), 4)  # 4-8%
                account["next_payment_due_date"] = fake.date_time_between(start_date="+1d", end_date="+30d").isoformat()
        else:
            # Depository accounts (checking, savings)
            account["limit"] = None
            account["apr"] = None
            account["apr_type"] = None
            account["min_payment"] = None
            account["is_overdue"] = False
            account["last_payment_amount"] = None
            account["last_payment_date"] = None
            account["next_payment_due_date"] = None
            account["last_statement_balance"] = None
            account["last_statement_date"] = None
            account["interest_rate"] = None

        accounts.append(account)

    return accounts


def generate_transactions(account: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate 40-100 transactions for an account with Plaid-compliant fields.

    Ensures realistic patterns for signal detection:
    - Multiple recurring subscriptions (3+ transactions from same merchant)
    - Regular income deposits if checking account
    - Mixed spending patterns
    """
    num_transactions = random.randint(40, 100)
    transactions = []

    # Extract category data and weights
    category_data = [(primary, detailed, weight) for primary, detailed, weight in CATEGORY_WEIGHTS]
    weights = [weight for _, _, weight in category_data]

    # Select 2-4 recurring merchants for this account (subscriptions)
    num_recurring = random.randint(2, 4)
    account_recurring_merchants = random.sample(MERCHANT_ENTITIES, num_recurring)

    # Generate subscription transactions first (ensures 3+ per merchant)
    for merchant_id in account_recurring_merchants:
        # Generate 3-6 recurring transactions for each subscription
        num_subscription_txns = random.randint(3, 6)
        subscription_amount = random.randint(10, 100) * 100  # $10-$100

        for i in range(num_subscription_txns):
            # Space transactions about 30 days apart for monthly pattern
            days_ago = 180 - (i * 30) - random.randint(-3, 3)
            if days_ago < 0:
                days_ago = random.randint(0, 30)

            transaction = {
                "id": fake.uuid4(),
                "account_id": account["id"],
                "date": fake.date_time_between(start_date=f"-{days_ago}d", end_date=f"-{max(0, days_ago-5)}d").isoformat(),
                "amount": subscription_amount + random.randint(-100, 100),  # Small variance
                "merchant_name": merchant_id.replace("_", " ").title(),
                "merchant_entity_id": merchant_id,
                "personal_finance_category_primary": "GENERAL_MERCHANDISE",
                "personal_finance_category_detailed": "ONLINE_MARKETPLACES",
                "payment_channel": "online",
                "pending": False,
            }
            transactions.append(transaction)

    # Generate remaining transactions randomly
    remaining = num_transactions - len(transactions)
    for _ in range(remaining):
        transaction_id = fake.uuid4()
        date = fake.date_time_between(start_date="-180d")

        # Select category
        primary, detailed, _ = random.choices(category_data, weights=weights)[0]

        # Generate amount based on primary category
        if primary == "INCOME":
            # Income is negative (credit to account)
            amount = -random.randint(2000, 6000) * 100
            merchant_name = fake.company()
            merchant_entity_id = None  # Income typically doesn't have merchant entities
        else:
            # Expenses are positive (debit from account)
            amount = random.randint(5, 250) * 100
            merchant_name = fake.company()
            # Additional 20% chance of recurring merchant (besides subscriptions above)
            merchant_entity_id = random.choice(MERCHANT_ENTITIES) if random.random() < 0.2 else None

        # 5% of transactions are pending
        pending = random.random() < 0.05

        # Generate payment channel based on category
        if primary in ["UTILITIES", "INCOME"]:
            payment_channel = "other"
        elif detailed in ["ONLINE_MARKETPLACES", "INTERNET_AND_CABLE"]:
            payment_channel = "online"
        else:
            payment_channel = random.choice(PAYMENT_CHANNELS)

        transaction = {
            "id": transaction_id,
            "account_id": account["id"],
            "date": date.isoformat(),
            "amount": amount,
            "merchant_name": merchant_name,
            "merchant_entity_id": merchant_entity_id,
            "personal_finance_category_primary": primary,
            "personal_finance_category_detailed": detailed,
            "payment_channel": payment_channel,
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

    print("\nGeneration complete:")
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
                current_balance=account_data["current_balance"],
                available_balance=account_data.get("available_balance"),
                limit=account_data.get("limit"),
                currency=account_data["currency"],
                holder_category=account_data["holder_category"],
                apr=account_data.get("apr"),
                apr_type=account_data.get("apr_type"),
                min_payment=account_data.get("min_payment"),
                is_overdue=account_data["is_overdue"],
                last_payment_amount=account_data.get("last_payment_amount"),
                last_payment_date=datetime.fromisoformat(account_data["last_payment_date"]) if account_data.get("last_payment_date") else None,
                next_payment_due_date=datetime.fromisoformat(account_data["next_payment_due_date"]) if account_data.get("next_payment_due_date") else None,
                last_statement_balance=account_data.get("last_statement_balance"),
                last_statement_date=datetime.fromisoformat(account_data["last_statement_date"]) if account_data.get("last_statement_date") else None,
                interest_rate=account_data.get("interest_rate"),
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
                merchant_name=txn_data.get("merchant_name"),
                merchant_entity_id=txn_data.get("merchant_entity_id"),
                personal_finance_category_primary=txn_data["personal_finance_category_primary"],
                personal_finance_category_detailed=txn_data.get("personal_finance_category_detailed"),
                payment_channel=txn_data.get("payment_channel"),
                pending=txn_data["pending"],
            )
            transactions.append(transaction)

        # Batch insert all data
        db.add_all(users)
        db.add_all(accounts)
        db.add_all(transactions)

        await db.commit()

        print("\nLoaded into database:")
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
