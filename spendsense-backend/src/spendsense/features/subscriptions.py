"""
Subscription Detection

Detects recurring subscription merchants from transaction patterns.
"""

from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any


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
    # Need to compare apples-to-apples: window total vs window total
    # total_recurring_spend is monthly, so multiply by months in window
    total_recurring_in_window = total_recurring_spend * (window_days / 30)
    percentage_of_spending = (
        (total_recurring_in_window / total_spend) * 100 if total_spend > 0 else 0.0
    )

    return {
        "recurring_merchants": recurring_merchants,
        "count": len(recurring_merchants),
        "monthly_recurring_spend": total_recurring_spend,
        "percentage_of_spending": round(percentage_of_spending, 2),
    }
