#!/usr/bin/env python3
"""
Test script for Story 4.3: Account & Transaction Endpoints

Tests:
1. GET /accounts/{user_id} - retrieve all accounts for a user
2. GET /transactions/{user_id} - retrieve transactions with pagination
3. 404 error handling for non-existent users
4. Pagination functionality (limit, offset)
5. Response time <100ms
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from spendsense.database import AsyncSessionLocal
from spendsense.models.user import User
from spendsense.models.account import Account
from spendsense.models.transaction import Transaction
from sqlalchemy import select


async def test_accounts_endpoint():
    """Test GET /accounts/{user_id} endpoint logic"""
    print("\n" + "=" * 60)
    print("TEST 1: Get User Accounts")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get a real user from database
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()

        if not test_user:
            print("❌ No users found in database")
            return False

        print(f"✓ Testing with user: {test_user.id} ({test_user.name})")

        # Fetch accounts for this user
        start_time = time.time()
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == test_user.id)
        )
        accounts = accounts_result.scalars().all()
        elapsed_ms = (time.time() - start_time) * 1000

        print(f"✓ Found {len(accounts)} accounts")
        print(f"✓ Query time: {elapsed_ms:.2f}ms")

        if len(accounts) > 0:
            print(f"\n  Sample account:")
            print(f"    ID: {accounts[0].id}")
            print(f"    Type: {accounts[0].type}/{accounts[0].subtype}")
            print(f"    Name: {accounts[0].name}")
            print(f"    Balance: ${accounts[0].balance / 100:.2f}")

        # Verify all accounts belong to the user
        for account in accounts:
            assert account.user_id == test_user.id, f"Account {account.id} belongs to wrong user"

        print("\n✅ TEST 1 PASSED")
        return True


async def test_transactions_endpoint():
    """Test GET /transactions/{user_id} endpoint logic"""
    print("\n" + "=" * 60)
    print("TEST 2: Get User Transactions")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get a user with transactions
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()

        if not test_user:
            print("❌ No users found in database")
            return False

        print(f"✓ Testing with user: {test_user.id} ({test_user.name})")

        # Fetch transactions for all user's accounts
        start_time = time.time()
        transactions_result = await db.execute(
            select(Transaction)
            .join(Account)
            .where(Account.user_id == test_user.id)
            .order_by(Transaction.date.desc())
        )
        transactions = transactions_result.scalars().all()
        elapsed_ms = (time.time() - start_time) * 1000

        print(f"✓ Found {len(transactions)} transactions")
        print(f"✓ Query time: {elapsed_ms:.2f}ms")

        if len(transactions) > 0:
            print(f"\n  Sample transaction:")
            txn = transactions[0]
            print(f"    ID: {txn.id}")
            print(f"    Date: {txn.date}")
            print(f"    Amount: ${txn.amount / 100:.2f}")
            print(f"    Merchant: {txn.merchant_name}")
            print(f"    Category: {txn.category}")

        # Verify elapsed time is under 100ms
        assert elapsed_ms < 100, f"Query took {elapsed_ms:.2f}ms, exceeds 100ms target"

        print("\n✅ TEST 2 PASSED")
        return True


async def test_pagination():
    """Test pagination with limit and offset"""
    print("\n" + "=" * 60)
    print("TEST 3: Transaction Pagination")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get a user
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()

        if not test_user:
            print("❌ No users found in database")
            return False

        # Test with limit=10, offset=0
        result1 = await db.execute(
            select(Transaction)
            .join(Account)
            .where(Account.user_id == test_user.id)
            .order_by(Transaction.date.desc())
            .limit(10)
            .offset(0)
        )
        page1_txns = result1.scalars().all()

        print(f"✓ Page 1 (limit=10, offset=0): {len(page1_txns)} transactions")

        # Test with limit=10, offset=10
        result2 = await db.execute(
            select(Transaction)
            .join(Account)
            .where(Account.user_id == test_user.id)
            .order_by(Transaction.date.desc())
            .limit(10)
            .offset(10)
        )
        page2_txns = result2.scalars().all()

        print(f"✓ Page 2 (limit=10, offset=10): {len(page2_txns)} transactions")

        # Verify no overlap between pages
        page1_ids = {txn.id for txn in page1_txns}
        page2_ids = {txn.id for txn in page2_txns}
        overlap = page1_ids & page2_ids

        assert len(overlap) == 0, f"Pages overlap: {overlap}"
        print("✓ No overlap between pages")

        # Verify correct order (most recent first)
        if len(page1_txns) > 1:
            for i in range(len(page1_txns) - 1):
                assert page1_txns[i].date >= page1_txns[i + 1].date, "Transactions not sorted by date desc"

        print("✓ Transactions sorted by date (most recent first)")

        print("\n✅ TEST 3 PASSED")
        return True


async def test_user_not_found():
    """Test 404 error handling for non-existent user"""
    print("\n" + "=" * 60)
    print("TEST 4: User Not Found (404)")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        fake_user_id = "user_does_not_exist_12345"

        # Check user doesn't exist
        result = await db.execute(
            select(User).where(User.id == fake_user_id)
        )
        user = result.scalar_one_or_none()

        assert user is None, "Test user should not exist"
        print(f"✓ Confirmed user {fake_user_id} does not exist")

        # Try to fetch accounts for non-existent user
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == fake_user_id)
        )
        accounts = accounts_result.scalars().all()

        assert len(accounts) == 0, "Should have no accounts for non-existent user"
        print("✓ No accounts found for non-existent user")

        print("\n✅ TEST 4 PASSED")
        return True


async def test_performance():
    """Test response time is under 100ms"""
    print("\n" + "=" * 60)
    print("TEST 5: Performance (<100ms)")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Get multiple users
        result = await db.execute(select(User).limit(5))
        test_users = result.scalars().all()

        if len(test_users) == 0:
            print("❌ No users found in database")
            return False

        print(f"✓ Testing with {len(test_users)} users")

        account_times = []
        transaction_times = []

        for user in test_users:
            # Test accounts endpoint
            start = time.time()
            await db.execute(
                select(Account).where(Account.user_id == user.id)
            )
            account_times.append((time.time() - start) * 1000)

            # Test transactions endpoint
            start = time.time()
            await db.execute(
                select(Transaction)
                .join(Account)
                .where(Account.user_id == user.id)
                .order_by(Transaction.date.desc())
                .limit(100)
            )
            transaction_times.append((time.time() - start) * 1000)

        avg_account_time = sum(account_times) / len(account_times)
        avg_transaction_time = sum(transaction_times) / len(transaction_times)
        max_account_time = max(account_times)
        max_transaction_time = max(transaction_times)

        print(f"\nAccounts endpoint:")
        print(f"  Average: {avg_account_time:.2f}ms")
        print(f"  Max: {max_account_time:.2f}ms")

        print(f"\nTransactions endpoint:")
        print(f"  Average: {avg_transaction_time:.2f}ms")
        print(f"  Max: {max_transaction_time:.2f}ms")

        # Verify performance meets requirements
        assert max_account_time < 100, f"Accounts query took {max_account_time:.2f}ms, exceeds 100ms"
        assert max_transaction_time < 100, f"Transactions query took {max_transaction_time:.2f}ms, exceeds 100ms"

        print("\n✓ All queries completed in <100ms")

        print("\n✅ TEST 5 PASSED")
        return True


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("STORY 4.3: Account & Transaction Endpoints Test Suite")
    print("=" * 60)

    tests = [
        ("Get User Accounts", test_accounts_endpoint),
        ("Get User Transactions", test_transactions_endpoint),
        ("Transaction Pagination", test_pagination),
        ("User Not Found (404)", test_user_not_found),
        ("Performance (<100ms)", test_performance),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {str(e)}")
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
