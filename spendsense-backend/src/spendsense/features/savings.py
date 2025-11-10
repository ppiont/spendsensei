"""
Savings Analysis

Analyzes net savings inflow and emergency fund coverage.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any


def analyze_savings(accounts: List[Dict[str, Any]], transactions: List[Dict[str, Any]], window_days: int) -> Dict[str, Any]:
    """
    Analyze net savings inflow and emergency fund coverage.

    Identifies savings accounts, calculates net inflow (deposits - withdrawals),
    estimates monthly savings rate, and calculates emergency fund coverage in
    months of expenses.

    Args:
        accounts: List of account dicts with keys: id, subtype, balance
        transactions: List of transaction dicts with keys: account_id, date, amount, category
        window_days: Number of days to analyze (e.g., 30, 90, 180)

    Returns:
        Dictionary with savings analysis:
        {
            "total_balance": int,           # Total savings balance in cents
            "net_inflow": int,              # Net inflow in cents (credits - debits)
            "monthly_inflow": int,          # Estimated monthly rate in cents
            "growth_rate": float,           # Percentage (e.g., 2.5 for 2.5%)
            "emergency_fund_months": float  # Months of expenses covered
        }

    Note:
        - Transaction amounts are in cents
        - Positive amount = debit (money out)
        - Negative amount = credit (money in)
        - Savings account subtypes: "savings", "money_market", "cd"
    """
    # Task 1: Filter savings accounts
    savings_subtypes = {"savings", "money_market", "cd"}
    savings_accounts = [acc for acc in accounts if acc.get("subtype") in savings_subtypes]

    # Calculate total savings balance
    total_savings_balance = sum(acc.get("balance", 0) for acc in savings_accounts)

    # Store savings account IDs for transaction filtering
    savings_account_ids = {acc["id"] for acc in savings_accounts}

    # Edge case: No savings accounts
    if not savings_accounts:
        return {
            "total_balance": 0,
            "net_inflow": 0,
            "monthly_inflow": 0,
            "growth_rate": 0.0,
            "emergency_fund_months": 0.0
        }

    # Task 2: Calculate net savings inflow
    # Filter transactions within window
    cutoff_date = datetime.now() - timedelta(days=window_days)

    savings_transactions = []
    non_savings_transactions = []

    for txn in transactions:
        # Parse transaction date (handle both datetime objects and ISO strings)
        txn_date = txn.get("date")
        if isinstance(txn_date, str):
            txn_date = datetime.fromisoformat(txn_date.replace('Z', '+00:00'))

        if txn_date < cutoff_date:
            continue

        # Separate savings vs non-savings transactions
        if txn["account_id"] in savings_account_ids:
            savings_transactions.append(txn)
        else:
            non_savings_transactions.append(txn)

    # Calculate net inflow for savings accounts
    # Credits (negative amounts) = money IN, Debits (positive amounts) = money OUT
    credits = sum(abs(txn["amount"]) for txn in savings_transactions if txn["amount"] < 0)
    debits = sum(txn["amount"] for txn in savings_transactions if txn["amount"] > 0)
    net_inflow = credits - debits

    # Estimate monthly inflow rate
    monthly_inflow = int(net_inflow / (window_days / 30)) if window_days > 0 else 0

    # Task 3: Calculate monthly expenses from ALL transactions
    # Note: Use all transactions (not just non-savings) because users may spend from savings accounts
    # Exclude INCOME category, sum all debits
    monthly_expenses = 0
    total_debits = sum(
        txn["amount"]
        for txn in transactions  # Changed from non_savings_transactions
        if txn["amount"] > 0 and txn.get("personal_finance_category_primary") != "INCOME"
    )
    monthly_expenses = int(total_debits / (window_days / 30)) if window_days > 0 else 0

    # Task 4: Calculate emergency fund and growth rate
    # Emergency fund coverage (months of expenses)
    if monthly_expenses > 0:
        emergency_fund_months = round(total_savings_balance / monthly_expenses, 2)
    elif total_savings_balance > 0:
        # Has savings but no expenses tracked - use large but finite number
        # Cannot use float('inf') as it breaks JSON serialization
        emergency_fund_months = 999.0
    else:
        emergency_fund_months = 0.0

    # Growth rate (percentage)
    if total_savings_balance > 0:
        growth_rate = round((net_inflow / total_savings_balance) * 100, 2)
    else:
        growth_rate = 0.0

    # Task 5: Return structured data
    return {
        "total_balance": total_savings_balance,
        "net_inflow": net_inflow,
        "monthly_inflow": monthly_inflow,
        "growth_rate": growth_rate,
        "emergency_fund_months": emergency_fund_months
    }
