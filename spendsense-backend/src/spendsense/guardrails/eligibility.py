"""
Eligibility Checking Guardrails

Validates that users meet requirements for recommended products and services.

Implemented checks:
- Income requirements (minimum income thresholds)
- Existing account filtering (avoid duplicate account types)
- Predatory product blocklist (payday loans, high-APR products)
- Credit score requirements (when available in future)
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def check_income_requirement(offer: Dict[str, Any], user_income: int) -> bool:
    """
    Check if user meets minimum income requirement for an offer.

    Args:
        offer: Partner offer with potential 'min_income' requirement
        user_income: User's annual income in cents

    Returns:
        True if user meets income requirement or no requirement exists
    """
    min_income = offer.get("min_income", 0)
    if min_income == 0:
        return True

    if user_income >= min_income:
        return True

    logger.info(f"User income ${user_income/100:.2f} below minimum ${min_income/100:.2f}")
    return False


def has_existing_account(user_accounts: List[Dict[str, Any]], account_type: str) -> bool:
    """
    Check if user already has an account of the specified type.

    Args:
        user_accounts: List of user's existing accounts
        account_type: Account type to check (e.g., "savings", "checking")

    Returns:
        True if user has an account of this type
    """
    for account in user_accounts:
        if account.get("subtype") == account_type:
            return True
    return False


def is_predatory_product(offer: Dict[str, Any]) -> bool:
    """
    Check if offer is a predatory financial product.

    Args:
        offer: Partner offer to evaluate

    Returns:
        True if product is predatory (should be blocked)

    Blocked products:
        - Payday loans, title loans, rent-to-own
        - Any product with APR > 36% (state cap threshold)
    """
    product_type = offer.get("type", "").lower()

    # Block known predatory products
    blocked_types = ["payday_loan", "title_loan", "rent_to_own"]
    if product_type in blocked_types:
        logger.warning(f"Blocked predatory product type: {product_type}")
        return True

    # Check for excessive fees/APR
    apr = offer.get("apr", 0.0)
    if apr > 36.0:  # Many states cap at 36% APR
        logger.warning(f"Blocked high-APR product: {apr}%")
        return True

    return False


def check_eligibility(offer: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
    """
    Comprehensive eligibility check for a partner offer.

    Runs all eligibility checks in sequence:
    1. Predatory product filtering (blocks high-risk products)
    2. Income requirement verification
    3. Existing account duplication prevention

    Args:
        offer: Partner offer to check eligibility for
        user_data: User's financial data including accounts, income, etc.

    Returns:
        True if user is eligible for this offer
    """
    # Check for predatory products first
    if is_predatory_product(offer):
        return False

    # Check income requirements
    user_income = user_data.get("annual_income", 0)
    if not check_income_requirement(offer, user_income):
        return False

    # Check for existing accounts (don't offer savings if they have one)
    user_accounts = user_data.get("accounts", [])
    offer_account_type = offer.get("account_type")
    if offer_account_type and has_existing_account(user_accounts, offer_account_type):
        logger.info(f"User already has {offer_account_type} account")
        return False

    # All checks passed
    return True
