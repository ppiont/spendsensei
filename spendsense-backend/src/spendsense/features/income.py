"""
Income Stability Analysis

Analyzes income patterns to determine frequency, stability, and cash flow buffer.
"""

from typing import List, Dict
import statistics


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
