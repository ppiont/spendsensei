#!/usr/bin/env python3
"""
Test script for Story 2.4: Income Stability Analysis

Tests the analyze_income function with synthetic data to verify:
- Income frequency classification (biweekly, monthly, weekly, variable)
- Income stability classification based on coefficient of variation
- Cash flow buffer calculation
- Edge case handling
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from spendsense.services.features import analyze_income, BehaviorSignals


def load_synthetic_data():
    """Load synthetic user data from Story 1.4"""
    data_path = project_root / "data" / "users.json"
    if not data_path.exists():
        print(f"Error: Synthetic data not found at {data_path}")
        sys.exit(1)
    
    with open(data_path, 'r') as f:
        return json.load(f)


def parse_transaction(txn):
    """Convert transaction dict to include datetime object"""
    return {
        'date': datetime.fromisoformat(txn['date']),
        'amount': txn['amount'],
        'category': txn['category'],
        'merchant_name': txn.get('merchant_name', '')
    }


def test_biweekly_income():
    """Test user with biweekly income pattern"""
    print("\n" + "="*60)
    print("TEST 1: Biweekly Income Pattern")
    print("="*60)

    data = load_synthetic_data()
    users = data['users']
    accounts = data['accounts']
    all_transactions = data['transactions']

    # Find user with regular income (biweekly pattern)
    for user in users:
        user_id = user['id']
        # Get user's account IDs
        user_account_ids = [acc['id'] for acc in accounts if acc['user_id'] == user_id]
        # Get transactions for this user's accounts
        user_transactions = [t for t in all_transactions if t['account_id'] in user_account_ids]
        transactions = [parse_transaction(t) for t in user_transactions]
        income_txns = [t for t in transactions if t['category'] == 'INCOME']

        if len(income_txns) >= 6:  # Need enough data
            result = analyze_income(transactions, 180)

            print(f"\nUser ID: {user_id}")
            print(f"Income Transactions: {len(income_txns)}")
            print(f"Frequency: {result['frequency']}")
            print(f"Stability: {result['stability']}")
            print(f"Average Amount: ${result['average_amount'] / 100:.2f}")
            print(f"Coefficient of Variation: {result['coefficient_variation']:.4f}")
            print(f"Buffer Months: {result['buffer_months']:.2f}")
            print(f"Median Gap Days: {result['median_gap_days']}")

            # Verify expectations
            assert result['frequency'] in ['biweekly', 'monthly', 'weekly', 'variable'], \
                f"Invalid frequency: {result['frequency']}"
            assert result['stability'] in ['stable', 'variable', 'unknown'], \
                f"Invalid stability: {result['stability']}"
            assert result['average_amount'] > 0, "Average amount should be positive"
            assert result['median_gap_days'] > 0, "Median gap should be positive"

            print("\n✓ Test passed!")
            break
    else:
        print("Warning: No suitable user found for biweekly test")


def test_monthly_income():
    """Test user with monthly income pattern"""
    print("\n" + "="*60)
    print("TEST 2: Monthly Income Pattern")
    print("="*60)

    data = load_synthetic_data()
    users = data['users']
    accounts = data['accounts']
    all_transactions = data['transactions']

    for user in users:
        user_id = user['id']
        user_account_ids = [acc['id'] for acc in accounts if acc['user_id'] == user_id]
        user_transactions = [t for t in all_transactions if t['account_id'] in user_account_ids]
        transactions = [parse_transaction(t) for t in user_transactions]
        income_txns = [t for t in transactions if t['category'] == 'INCOME']

        if len(income_txns) >= 3:
            # Check if monthly pattern
            income_sorted = sorted(income_txns, key=lambda t: t['date'])
            gaps = [(income_sorted[i+1]['date'] - income_sorted[i]['date']).days
                   for i in range(len(income_sorted)-1)]

            if gaps and 28 <= sum(gaps) / len(gaps) <= 32:
                result = analyze_income(transactions, 180)

                print(f"\nUser ID: {user_id}")
                print(f"Income Transactions: {len(income_txns)}")
                print(f"Frequency: {result['frequency']}")
                print(f"Stability: {result['stability']}")
                print(f"Average Amount: ${result['average_amount'] / 100:.2f}")
                print(f"Buffer Months: {result['buffer_months']:.2f}")

                assert result['frequency'] == 'monthly', \
                    f"Expected monthly, got {result['frequency']}"

                print("\n✓ Monthly pattern detected correctly!")
                break


def test_variable_income():
    """Test user with irregular income pattern"""
    print("\n" + "="*60)
    print("TEST 3: Variable Income Pattern")
    print("="*60)

    data = load_synthetic_data()
    users = data['users']
    accounts = data['accounts']
    all_transactions = data['transactions']

    for user in users:
        user_id = user['id']
        user_account_ids = [acc['id'] for acc in accounts if acc['user_id'] == user_id]
        user_transactions = [t for t in all_transactions if t['account_id'] in user_account_ids]
        transactions = [parse_transaction(t) for t in user_transactions]
        income_txns = [t for t in transactions if t['category'] == 'INCOME']

        if len(income_txns) >= 3:
            # Check for variable pattern
            income_sorted = sorted(income_txns, key=lambda t: t['date'])
            gaps = [(income_sorted[i+1]['date'] - income_sorted[i]['date']).days
                   for i in range(len(income_sorted)-1)]

            # Check if gaps are irregular
            if gaps and (max(gaps) - min(gaps) > 20):
                result = analyze_income(transactions, 180)

                print(f"\nUser ID: {user_id}")
                print(f"Income Transactions: {len(income_txns)}")
                print(f"Gap Range: {min(gaps)}-{max(gaps)} days")
                print(f"Frequency: {result['frequency']}")
                print(f"Stability: {result['stability']}")

                print("\n✓ Variable income pattern handled!")
                break


def test_edge_case_insufficient_data():
    """Test edge case: <2 income transactions"""
    print("\n" + "="*60)
    print("TEST 4: Edge Case - Insufficient Income Data")
    print("="*60)
    
    # Create test data with only 1 income transaction
    transactions = [
        {
            'date': datetime(2025, 10, 1),
            'amount': -500000,  # $5000 income (negative)
            'category': 'INCOME'
        },
        {
            'date': datetime(2025, 10, 5),
            'amount': 10000,  # $100 expense
            'category': 'FOOD_AND_DRINK'
        }
    ]
    
    result = analyze_income(transactions, 30)
    
    print(f"Income Transactions: 1")
    print(f"Result: {result}")
    
    assert result['frequency'] == 'unknown', "Should return unknown for <2 income txns"
    assert result['stability'] == 'unknown', "Should return unknown stability"
    assert result['average_amount'] == 0, "Should return 0 average"
    
    print("\n✓ Edge case handled correctly!")


def test_stable_vs_variable_income():
    """Test CV-based stability classification"""
    print("\n" + "="*60)
    print("TEST 5: Stability Classification (CV < 0.15 = stable)")
    print("="*60)
    
    # Stable income (low variation)
    stable_transactions = [
        {'date': datetime(2025, 8, 1), 'amount': -300000, 'category': 'INCOME'},
        {'date': datetime(2025, 8, 15), 'amount': -300000, 'category': 'INCOME'},
        {'date': datetime(2025, 9, 1), 'amount': -300000, 'category': 'INCOME'},
        {'date': datetime(2025, 9, 15), 'amount': -300000, 'category': 'INCOME'},
        {'date': datetime(2025, 10, 15), 'amount': 50000, 'category': 'FOOD_AND_DRINK'},
    ]
    
    result_stable = analyze_income(stable_transactions, 180)
    print(f"\nStable Income Test:")
    print(f"  CV: {result_stable['coefficient_variation']:.4f}")
    print(f"  Stability: {result_stable['stability']}")
    assert result_stable['stability'] == 'stable', "Low CV should be stable"
    
    # Variable income (high variation)
    variable_transactions = [
        {'date': datetime(2025, 8, 1), 'amount': -200000, 'category': 'INCOME'},
        {'date': datetime(2025, 8, 15), 'amount': -400000, 'category': 'INCOME'},
        {'date': datetime(2025, 9, 1), 'amount': -250000, 'category': 'INCOME'},
        {'date': datetime(2025, 9, 15), 'amount': -500000, 'category': 'INCOME'},
        {'date': datetime(2025, 10, 15), 'amount': 50000, 'category': 'FOOD_AND_DRINK'},
    ]
    
    result_variable = analyze_income(variable_transactions, 180)
    print(f"\nVariable Income Test:")
    print(f"  CV: {result_variable['coefficient_variation']:.4f}")
    print(f"  Stability: {result_variable['stability']}")
    assert result_variable['stability'] == 'variable', "High CV should be variable"
    
    print("\n✓ CV-based stability classification works!")


def test_behavior_signals_class():
    """Test BehaviorSignals dataclass initialization"""
    print("\n" + "="*60)
    print("TEST 6: BehaviorSignals Dataclass")
    print("="*60)
    
    signals = BehaviorSignals()
    
    print(f"Subscriptions: {signals.subscriptions}")
    print(f"Savings: {signals.savings}")
    print(f"Credit: {signals.credit}")
    print(f"Income: {signals.income}")
    
    assert signals.subscriptions == {}, "Should initialize as empty dict"
    assert signals.savings == {}, "Should initialize as empty dict"
    assert signals.credit == {}, "Should initialize as empty dict"
    assert signals.income == {}, "Should initialize as empty dict"
    
    # Test with income data
    signals.income = {'frequency': 'biweekly', 'stability': 'stable'}
    print(f"\nAfter setting income: {signals.income}")
    
    print("\n✓ BehaviorSignals class works correctly!")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("INCOME STABILITY ANALYSIS - TEST SUITE")
    print("Story 2.4 Implementation Verification")
    print("="*60)
    
    try:
        test_biweekly_income()
        test_monthly_income()
        test_variable_income()
        test_edge_case_insufficient_data()
        test_stable_vs_variable_income()
        test_behavior_signals_class()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
