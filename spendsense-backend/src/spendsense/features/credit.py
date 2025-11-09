"""
Credit Utilization Analysis

Analyzes credit card utilization and identifies high-risk patterns.
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


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

    # Check for minimum-payment-only behavior
    has_minimum_payment_only = False
    for acc in credit_accounts:
        last_payment = acc.get("last_payment_amount", 0)
        min_payment = acc.get("min_payment", 0)

        # Allow 10% tolerance for rounding/fees
        # Check payment was made but was only minimum amount
        if min_payment > 0 and 0 < last_payment <= min_payment * 1.1:
            has_minimum_payment_only = True
            logger.warning(
                f"Account {acc.get('id')} appears to be minimum-payment-only: "
                f"last_payment=${last_payment/100:.2f}, min=${min_payment/100:.2f}"
            )
            break

    if has_minimum_payment_only:
        flags.append("minimum_payment_only")

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
