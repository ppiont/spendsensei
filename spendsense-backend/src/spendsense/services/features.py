"""
Behavioral Signal Detection Module

This module provides functions to compute behavioral signals from user
financial data, including income stability, subscription detection,
savings patterns, and credit utilization.

All functions accept lists/dicts for flexibility (not ORM objects).
Amounts are in cents (positive = debit/expense, negative = credit/income).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics


@dataclass
class BehaviorSignals:
    """
    Container for all computed behavioral signals for a user.

    Each field contains a dictionary with signal-specific data structure.
    Fields are initialized as empty dicts and populated by analysis functions.
    """
    subscriptions: dict = None  # Story 2.1: Subscription detection
    savings: dict = None        # Story 2.2: Savings analysis
    credit: dict = None         # Story 2.3: Credit utilization
    income: dict = None         # Story 2.4: Income stability

    def __post_init__(self):
        """Initialize all fields as empty dicts if None"""
        if self.subscriptions is None:
            self.subscriptions = {}
        if self.savings is None:
            self.savings = {}
        if self.credit is None:
            self.credit = {}
        if self.income is None:
            self.income = {}


def analyze_income(transactions: List[Dict], window_days: int) -> Dict:
    """
    Analyze income stability and frequency patterns.

    Args:
        transactions: List of transaction dicts with keys:
            - date: datetime object
            - amount: int (cents, negative for INCOME)
            - category: str
        window_days: Number of days to analyze (e.g., 180)

    Returns:
        Dictionary with income analysis:
        {
            "frequency": str,              # "biweekly", "monthly", "weekly", "variable", "unknown"
            "stability": str,              # "stable", "variable", "unknown"
            "average_amount": int,         # Average income in cents
            "coefficient_variation": float, # CV ratio (stdev/mean)
            "buffer_months": float,        # Cash flow buffer in months
            "median_gap_days": int         # Median days between income
        }

    Edge cases:
        - <2 income transactions: returns "unknown" for frequency/stability
        - Zero income: returns zeros and "unknown"
        - Insufficient data for stdev: returns "unknown" stability
    """
    # Filter INCOME transactions only
    income_txns = [t for t in transactions if t.get('category') == 'INCOME']

    # Edge case: insufficient income transactions
    if len(income_txns) < 2:
        return {
            "frequency": "unknown",
            "stability": "unknown",
            "average_amount": 0,
            "coefficient_variation": 0.0,
            "buffer_months": 0.0,
            "median_gap_days": 0
        }

    # Sort by date ascending
    income_txns_sorted = sorted(income_txns, key=lambda t: t['date'])

    # Extract amounts (take absolute value since INCOME is negative)
    amounts = [abs(t['amount']) for t in income_txns_sorted]

    # Edge case: zero income amounts
    if sum(amounts) == 0:
        return {
            "frequency": "unknown",
            "stability": "unknown",
            "average_amount": 0,
            "coefficient_variation": 0.0,
            "buffer_months": 0.0,
            "median_gap_days": 0
        }

    # Calculate gaps between consecutive income transactions (in days)
    gaps = []
    for i in range(len(income_txns_sorted) - 1):
        date1 = income_txns_sorted[i]['date']
        date2 = income_txns_sorted[i + 1]['date']
        gap_days = (date2 - date1).days
        gaps.append(gap_days)

    # Calculate median gap
    median_gap = int(statistics.median(gaps)) if gaps else 0

    # Classify income frequency based on median gap
    if 13 <= median_gap <= 16:
        frequency = "biweekly"
    elif 28 <= median_gap <= 32:
        frequency = "monthly"
    elif 6 <= median_gap <= 8:
        frequency = "weekly"
    else:
        frequency = "variable"

    # Calculate income statistics
    average_amount = int(statistics.mean(amounts))

    # Calculate coefficient of variation
    if len(amounts) >= 2:
        try:
            std_dev = statistics.stdev(amounts)
            cv = std_dev / average_amount if average_amount > 0 else 0.0
        except statistics.StatisticsError:
            # Insufficient data for stdev
            cv = 0.0
            stability = "unknown"
        else:
            # Classify stability based on CV threshold
            stability = "stable" if cv < 0.15 else "variable"
    else:
        cv = 0.0
        stability = "unknown"

    # Calculate cash flow buffer
    # Total income (absolute value of INCOME transactions)
    total_income = sum(amounts)

    # Total expenses (all positive transaction amounts, exclude INCOME)
    expense_txns = [t for t in transactions if t.get('category') != 'INCOME' and t['amount'] > 0]
    total_expenses = sum(t['amount'] for t in expense_txns)

    # Calculate net cash flow
    net_cash_flow = total_income - total_expenses

    # Calculate monthly expenses
    monthly_expenses = total_expenses / (window_days / 30) if window_days > 0 else 0

    # Buffer in months (can be negative if spending exceeds income)
    if monthly_expenses > 0:
        buffer_months = net_cash_flow / monthly_expenses
    else:
        buffer_months = 0.0

    # Build return structure
    return {
        "frequency": frequency,
        "stability": stability,
        "average_amount": average_amount,
        "coefficient_variation": round(cv, 4),  # Round to 4 decimal places
        "buffer_months": round(buffer_months, 2),  # Round to 2 decimal places
        "median_gap_days": median_gap
    }


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

    # Task 3: Calculate monthly expenses from non-savings accounts
    # Exclude INCOME category, sum all debits
    monthly_expenses = 0
    total_debits = sum(
        txn["amount"]
        for txn in non_savings_transactions
        if txn["amount"] > 0 and txn.get("category") != "INCOME"
    )
    monthly_expenses = int(total_debits / (window_days / 30)) if window_days > 0 else 0

    # Task 4: Calculate emergency fund and growth rate
    # Emergency fund coverage (months of expenses)
    if monthly_expenses > 0:
        emergency_fund_months = round(total_savings_balance / monthly_expenses, 2)
    elif total_savings_balance > 0:
        # Has savings but no expenses tracked - return infinity indicator
        emergency_fund_months = float('inf')
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


def analyze_credit(accounts: List[Dict], transactions: List[Dict]) -> Dict:
    """
    Analyze credit card utilization and identify high-risk patterns.

    Args:
        accounts: List of account dictionaries with fields:
            - id (str): Unique account identifier
            - type (str): Account type (e.g., "credit", "checking", "savings")
            - balance (int): Current balance in cents
            - limit (int): Credit limit in cents (for credit accounts)
            - apr (float): Annual Percentage Rate (for credit accounts)
            - is_overdue (bool): Whether account has overdue payments
        transactions: List of transaction dictionaries (currently unused but accepted for consistency)

    Returns:
        Dictionary containing credit analysis:
        {
            "overall_utilization": float,     # Percentage (0-100)
            "total_balance": int,             # Total balance across all cards in cents
            "total_limit": int,               # Total credit limit in cents
            "monthly_interest": int,          # Estimated monthly interest in cents
            "flags": list,                    # Warning flags (e.g., "high_utilization_80")
            "per_card": [                     # Individual card details
                {
                    "account_id": str,
                    "utilization": float,
                    "balance": int,
                    "limit": int
                }
            ]
        }
    """
    # Filter to credit accounts only
    credit_accounts = [acc for acc in accounts if acc.get("type") == "credit"]

    # Handle edge case: no credit accounts
    if not credit_accounts:
        return {
            "overall_utilization": 0.0,
            "total_balance": 0,
            "total_limit": 0,
            "monthly_interest": 0,
            "flags": [],
            "per_card": []
        }

    # Calculate totals
    total_balance = sum(acc.get("balance", 0) for acc in credit_accounts)
    total_limit = sum(acc.get("limit", 0) for acc in credit_accounts)

    # Handle edge case: zero total limit
    if total_limit == 0:
        overall_utilization = 0.0
    else:
        overall_utilization = (total_balance / total_limit) * 100

    # Calculate per-card breakdown
    per_card = []
    for acc in credit_accounts:
        card_balance = acc.get("balance", 0)
        card_limit = acc.get("limit", 0)

        # Calculate card-specific utilization
        if card_limit == 0:
            card_utilization = 0.0
        else:
            card_utilization = (card_balance / card_limit) * 100

        per_card.append({
            "account_id": acc.get("id", ""),
            "utilization": round(card_utilization, 2),
            "balance": card_balance,
            "limit": card_limit
        })

    # Calculate monthly interest charges
    monthly_interest = 0
    for acc in credit_accounts:
        balance = acc.get("balance", 0)
        apr = acc.get("apr", 0.0)  # Default to 0 if missing

        # Monthly interest = (balance * APR / 100) / 12
        card_monthly_interest = (balance * apr / 100) / 12
        monthly_interest += card_monthly_interest

    # Round to nearest cent
    monthly_interest = int(round(monthly_interest))

    # Generate flags
    flags = []

    # Check for overdue accounts
    has_overdue = any(acc.get("is_overdue", False) for acc in credit_accounts)
    if has_overdue:
        flags.append("overdue")

    # Add interest charges flag
    if monthly_interest > 0:
        flags.append("interest_charges")

    # Add utilization flags (only one, highest threshold met)
    if overall_utilization >= 80:
        flags.append("high_utilization_80")
    elif overall_utilization >= 50:
        flags.append("high_utilization_50")
    elif overall_utilization >= 30:
        flags.append("moderate_utilization_30")

    return {
        "overall_utilization": round(overall_utilization, 2),
        "total_balance": total_balance,
        "total_limit": total_limit,
        "monthly_interest": monthly_interest,
        "flags": flags,
        "per_card": per_card
    }


def detect_subscriptions(transactions: List[Dict[str, Any]], window_days: int) -> Dict[str, Any]:
    """
    Detect recurring subscription merchants from transaction patterns.

    Args:
        transactions: List of transaction dicts with keys: date, amount, merchant_name, category
        window_days: Number of days to analyze (e.g., 180 for 6 months)

    Returns:
        Dictionary with subscription detection results:
        {
            "recurring_merchants": [
                {"name": str, "frequency": str, "avg_amount": int, "count": int}
            ],
            "count": int,
            "monthly_recurring_spend": int,
            "percentage_of_spending": float
        }
    """
    from collections import defaultdict

    # Edge case: Not enough transactions
    if len(transactions) < 3:
        return {
            "recurring_merchants": [],
            "count": 0,
            "monthly_recurring_spend": 0,
            "percentage_of_spending": 0.0,
        }

    # Filter to debit transactions only (amount > 0) and exclude INCOME category
    debit_transactions = [
        txn
        for txn in transactions
        if txn.get("amount", 0) > 0 and txn.get("category") != "INCOME"
    ]

    # Edge case: No debit transactions
    if not debit_transactions:
        return {
            "recurring_merchants": [],
            "count": 0,
            "monthly_recurring_spend": 0,
            "percentage_of_spending": 0.0,
        }

    # Calculate total spending for percentage calculation
    total_spend = sum(txn.get("amount", 0) for txn in debit_transactions)

    # Edge case: Zero total spend
    if total_spend == 0:
        return {
            "recurring_merchants": [],
            "count": 0,
            "monthly_recurring_spend": 0,
            "percentage_of_spending": 0.0,
        }

    # Group transactions by merchant_name
    merchant_transactions = defaultdict(list)
    for txn in debit_transactions:
        merchant_name = txn.get("merchant_name")
        if merchant_name:  # Skip transactions without merchant_name
            merchant_transactions[merchant_name].append(txn)

    # Identify recurring merchants (≥3 occurrences)
    recurring_merchants = []
    total_recurring_spend = 0

    for merchant_name, merchant_txns in merchant_transactions.items():
        if len(merchant_txns) < 3:
            continue

        # Sort transactions by date
        sorted_txns = sorted(
            merchant_txns,
            key=lambda t: t.get("date") if isinstance(t.get("date"), datetime) else datetime.fromisoformat(t.get("date"))
        )

        # Calculate gaps between consecutive transactions (in days)
        gaps = []
        for i in range(len(sorted_txns) - 1):
            date1 = sorted_txns[i].get("date")
            date2 = sorted_txns[i + 1].get("date")

            # Handle both datetime objects and ISO strings
            if isinstance(date1, str):
                date1 = datetime.fromisoformat(date1)
            if isinstance(date2, str):
                date2 = datetime.fromisoformat(date2)

            gap_days = (date2 - date1).days
            gaps.append(gap_days)

        # Calculate average gap
        avg_gap = sum(gaps) / len(gaps) if gaps else 0

        # Classify cadence based on average gap
        frequency = None
        if 28 <= avg_gap <= 35:
            frequency = "monthly"
        elif 6 <= avg_gap <= 8:
            frequency = "weekly"
        # else: irregular pattern, not classified as subscription

        # Only include if cadence is classified (monthly or weekly)
        if frequency:
            # Calculate average transaction amount
            avg_amount = sum(txn.get("amount", 0) for txn in sorted_txns) // len(sorted_txns)

            # Calculate monthly recurring spend estimate
            if frequency == "monthly":
                monthly_spend = avg_amount
            else:  # weekly
                monthly_spend = int(avg_amount * 4.33)  # 4.33 weeks per month

            total_recurring_spend += monthly_spend

            recurring_merchants.append({
                "name": merchant_name,
                "frequency": frequency,
                "avg_amount": avg_amount,
                "count": len(sorted_txns),
            })

    # Calculate percentage of total spending
    percentage_of_spending = (
        (total_recurring_spend / total_spend) * 100 if total_spend > 0 else 0.0
    )

    return {
        "recurring_merchants": recurring_merchants,
        "count": len(recurring_merchants),
        "monthly_recurring_spend": total_recurring_spend,
        "percentage_of_spending": round(percentage_of_spending, 2),
    }
