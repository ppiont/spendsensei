#!/usr/bin/env python3
"""Test script for subscription detection functionality"""

import json
import sys
from pathlib import Path

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from spendsense.services.features import detect_subscriptions


def main():
    """Test subscription detection with synthetic data"""

    # Load synthetic data
    data_file = backend_root / "data" / "users.json"

    if not data_file.exists():
        print(f"Error: Data file not found at {data_file}")
        print("Please run the synthetic data generator first (Story 1.4)")
        return 1

    print(f"Loading data from: {data_file}")
    with open(data_file, "r") as f:
        users_data = json.load(f)

    users = users_data.get("users", [])
    all_accounts = users_data.get("accounts", [])
    all_transactions = users_data.get("transactions", [])

    if not users:
        print("Error: No users found in data file")
        return 1

    print(f"\nLoaded {len(users)} users, {len(all_accounts)} accounts, {len(all_transactions)} transactions")

    # Select first user and get their transactions
    selected_user = users[0]
    user_id = selected_user.get("id")

    # Get accounts for this user
    user_accounts = [acc for acc in all_accounts if acc.get("user_id") == user_id]
    user_account_ids = {acc.get("id") for acc in user_accounts}

    # Get transactions for this user's accounts
    transactions = [txn for txn in all_transactions if txn.get("account_id") in user_account_ids]

    if not transactions:
        print(f"Error: No transactions found for user {user_id}")
        return 1

    print(f"\nSelected user: {user_id}")
    print(f"User accounts: {len(user_accounts)}")
    print(f"Total transactions: {len(transactions)}")

    # Count unique merchants
    unique_merchants = set(txn.get("merchant_name") for txn in transactions if txn.get("merchant_name"))
    print(f"Unique merchants: {len(unique_merchants)}")

    # Test subscription detection
    print("\n" + "="*60)
    print("TESTING SUBSCRIPTION DETECTION")
    print("="*60)

    result = detect_subscriptions(transactions, 180)

    print(f"\n📊 RESULTS:")
    print(f"  Recurring merchants found: {result['count']}")
    print(f"  Monthly recurring spend: ${result['monthly_recurring_spend'] / 100:.2f}")
    print(f"  Percentage of total spending: {result['percentage_of_spending']:.2f}%")

    if result['recurring_merchants']:
        print(f"\n📋 RECURRING MERCHANTS:")
        for merchant in result['recurring_merchants']:
            print(f"  - {merchant['name']}")
            print(f"    Frequency: {merchant['frequency']}")
            print(f"    Average amount: ${merchant['avg_amount'] / 100:.2f}")
            print(f"    Transaction count: {merchant['count']}")
    else:
        print("\n⚠️  No recurring merchants detected")

    # Test edge cases
    print("\n" + "="*60)
    print("TESTING EDGE CASES")
    print("="*60)

    # Edge case 1: Empty transactions
    print("\n1. Empty transactions:")
    result = detect_subscriptions([], 180)
    print(f"   Count: {result['count']} (expected: 0)")
    print(f"   Status: {'✅ PASS' if result['count'] == 0 else '❌ FAIL'}")

    # Edge case 2: <3 transactions
    print("\n2. Less than 3 transactions:")
    result = detect_subscriptions(transactions[:2], 180)
    print(f"   Count: {result['count']} (expected: 0)")
    print(f"   Status: {'✅ PASS' if result['count'] == 0 else '❌ FAIL'}")

    # Edge case 3: Only income transactions
    income_txns = [
        {"amount": -500, "category": "INCOME", "merchant_name": "Employer", "date": "2024-01-01"},
        {"amount": -500, "category": "INCOME", "merchant_name": "Employer", "date": "2024-02-01"},
        {"amount": -500, "category": "INCOME", "merchant_name": "Employer", "date": "2024-03-01"},
    ]
    print("\n3. Only income transactions:")
    result = detect_subscriptions(income_txns, 180)
    print(f"   Count: {result['count']} (expected: 0)")
    print(f"   Status: {'✅ PASS' if result['count'] == 0 else '❌ FAIL'}")

    print("\n" + "="*60)
    print("✅ TESTING COMPLETE")
    print("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
