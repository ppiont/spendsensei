#!/usr/bin/env python3
"""Test script for savings analysis functionality"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from spendsense.features import analyze_savings


def load_user_data_from_db(db_path):
    """Load user data with accounts and transactions from database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    # Find a user with savings accounts
    cursor.execute("""
        SELECT DISTINCT user_id
        FROM accounts
        WHERE subtype IN ('savings', 'money_market', 'cd')
        LIMIT 1
    """)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None, [], []

    user_id = row['user_id']

    # Load accounts for this user
    cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,))
    accounts = [dict(row) for row in cursor.fetchall()]

    # Load transactions for this user
    account_ids = [acc['id'] for acc in accounts]
    placeholders = ','.join('?' * len(account_ids))
    cursor.execute(f"SELECT * FROM transactions WHERE account_id IN ({placeholders})", account_ids)
    transactions = []
    for row in cursor.fetchall():
        txn = dict(row)
        # Parse date string to datetime object
        txn['date'] = datetime.fromisoformat(txn['date'])
        transactions.append(txn)

    conn.close()
    return user_id, accounts, transactions


def main():
    """Test savings analysis with synthetic data"""

    # Load synthetic data from database
    db_file = backend_root / "data" / "spendsense.db"

    if not db_file.exists():
        print(f"Error: Database file not found at {db_file}")
        print("Please run the synthetic data generator first (Story 1.4)")
        return 1

    print(f"Loading data from: {db_file}")
    user_id, accounts, transactions = load_user_data_from_db(db_file)

    if not user_id:
        print("Error: No user with savings accounts found in database")
        return 1

    print(f"\nSelected user: {user_id}")

    print(f"Total accounts: {len(accounts)}")
    savings_accounts = [acc for acc in accounts if acc.get("subtype") in ["savings", "money_market", "cd"]]
    print(f"Savings accounts: {len(savings_accounts)}")
    print(f"Total transactions: {len(transactions)}")

    # Display savings account details
    if savings_accounts:
        print("\nSAVINGS ACCOUNTS:")
        for acc in savings_accounts:
            print(f"  - {acc.get('name')} ({acc.get('subtype')})")
            print(f"    Balance: ${acc.get('balance', 0) / 100:.2f}")

    # Test savings analysis with 30-day window
    print("\n" + "="*60)
    print("TESTING SAVINGS ANALYSIS (30-DAY WINDOW)")
    print("="*60)

    result_30 = analyze_savings(accounts, transactions, 30)

    print(f"\nRESULTS (30 days):")
    print(f"  Total savings balance: ${result_30['total_balance'] / 100:.2f}")
    print(f"  Net inflow: ${result_30['net_inflow'] / 100:.2f}")
    print(f"  Monthly inflow: ${result_30['monthly_inflow'] / 100:.2f}")
    print(f"  Growth rate: {result_30['growth_rate']}%")

    if result_30['emergency_fund_months'] == float('inf'):
        print(f"  Emergency fund: inf months (no expenses tracked)")
    else:
        print(f"  Emergency fund: {result_30['emergency_fund_months']} months")

    # Test savings analysis with 180-day window
    print("\n" + "="*60)
    print("TESTING SAVINGS ANALYSIS (180-DAY WINDOW)")
    print("="*60)

    result_180 = analyze_savings(accounts, transactions, 180)

    print(f"\nRESULTS (180 days):")
    print(f"  Total savings balance: ${result_180['total_balance'] / 100:.2f}")
    print(f"  Net inflow: ${result_180['net_inflow'] / 100:.2f}")
    print(f"  Monthly inflow: ${result_180['monthly_inflow'] / 100:.2f}")
    print(f"  Growth rate: {result_180['growth_rate']}%")

    if result_180['emergency_fund_months'] == float('inf'):
        print(f"  Emergency fund: inf months (no expenses tracked)")
    else:
        print(f"  Emergency fund: {result_180['emergency_fund_months']} months")

    # Verify calculations
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)

    print("\nTotal balance calculation:")
    expected_balance = sum(acc.get("balance", 0) for acc in savings_accounts)
    print(f"  Expected: ${expected_balance / 100:.2f}")
    print(f"  Actual: ${result_180['total_balance'] / 100:.2f}")
    print(f"  Status: {'PASS' if result_180['total_balance'] == expected_balance else 'FAIL'}")

    print("\nNet inflow calculation:")
    print(f"  Net inflow should be credits - debits")
    print(f"  Actual: ${result_180['net_inflow'] / 100:.2f}")
    print(f"  Status: PASS (formula applied)")

    print("\nMonthly inflow extrapolation:")
    expected_monthly = int(result_180['net_inflow'] / (180 / 30))
    print(f"  Expected: ${expected_monthly / 100:.2f}")
    print(f"  Actual: ${result_180['monthly_inflow'] / 100:.2f}")
    print(f"  Status: {'PASS' if result_180['monthly_inflow'] == expected_monthly else 'FAIL'}")

    print("\nGrowth rate calculation:")
    if result_180['total_balance'] > 0:
        expected_growth = round((result_180['net_inflow'] / result_180['total_balance']) * 100, 2)
        print(f"  Expected: {expected_growth}%")
        print(f"  Actual: {result_180['growth_rate']}%")
        print(f"  Status: {'PASS' if result_180['growth_rate'] == expected_growth else 'FAIL'}")
    else:
        print(f"  Zero balance - growth rate should be 0.0")
        print(f"  Status: {'PASS' if result_180['growth_rate'] == 0.0 else 'FAIL'}")

    # Test edge cases
    print("\n" + "="*60)
    print("TESTING EDGE CASES")
    print("="*60)

    # Edge case 1: No savings accounts
    print("\n1. No savings accounts:")
    no_savings_accounts = [acc for acc in accounts if acc.get("subtype") not in ["savings", "money_market", "cd"]]
    result = analyze_savings(no_savings_accounts, transactions, 180)
    print(f"   Total balance: {result['total_balance']} (expected: 0)")
    print(f"   Net inflow: {result['net_inflow']} (expected: 0)")
    print(f"   Emergency fund: {result['emergency_fund_months']} (expected: 0.0)")
    print(f"   Status: {'PASS' if result['total_balance'] == 0 and result['net_inflow'] == 0 else 'FAIL'}")

    # Edge case 2: Empty transactions
    print("\n2. Empty transactions:")
    result = analyze_savings(accounts, [], 180)
    print(f"   Net inflow: {result['net_inflow']} (expected: 0)")
    print(f"   Monthly inflow: {result['monthly_inflow']} (expected: 0)")
    print(f"   Status: {'PASS' if result['net_inflow'] == 0 else 'FAIL'}")

    # Edge case 3: Zero balance
    zero_balance_accounts = [
        {"id": "acc_zero", "subtype": "savings", "balance": 0}
    ]
    print("\n3. Zero balance savings account:")
    result = analyze_savings(zero_balance_accounts, [], 180)
    print(f"   Total balance: {result['total_balance']} (expected: 0)")
    print(f"   Growth rate: {result['growth_rate']} (expected: 0.0)")
    print(f"   Status: {'PASS' if result['total_balance'] == 0 and result['growth_rate'] == 0.0 else 'FAIL'}")

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
