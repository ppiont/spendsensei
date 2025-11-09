"""
Persona Assignment Logic Module

This module provides functions to assign financial personas to users based on
their behavioral signals. Personas are assigned in priority order (most urgent first)
with confidence scoring.

Personas:
- high_utilization: Credit card usage ≥50% OR interest charges OR overdue
- variable_income: Median pay gap >45 days AND buffer <1 month
- subscription_heavy: ≥3 subscriptions AND (monthly spend ≥$50 OR ≥10% of total)
- savings_builder: Growth rate ≥2% OR monthly inflow ≥$200, AND utilization <30%
- balanced: Default fallback if no other persona matches
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from spendsense.features import BehaviorSignals, compute_signals
from spendsense.models.persona import Persona

# Set up logging
logger = logging.getLogger(__name__)

# Persona priority order (most urgent/important first)
PERSONA_PRIORITY = [
    "high_utilization",    # Most urgent: >70% utilization OR overdue OR min-payment-only
    "variable_income",     # Cash flow risk: irregular income + low buffer
    "debt_consolidator",   # Opportunity: multiple cards with moderate utilization
    "subscription_heavy",  # Cost optimization: high recurring spend
    "savings_builder",     # Building wealth: positive savings trajectory
    "balanced"             # Default fallback
]

# Confidence scores for each persona type
CONFIDENCE_SCORES = {
    "high_utilization": 0.95,
    "variable_income": 0.90,
    "debt_consolidator": 0.88,
    "subscription_heavy": 0.85,
    "savings_builder": 0.80,
    "balanced": 0.60
}


def matches_high_utilization(signals: BehaviorSignals) -> bool:
    """
    Check if user matches high utilization persona.

    Criteria:
    - Overall credit utilization ≥50% OR
    - Has interest charges OR
    - Has overdue accounts OR
    - Making minimum payments only

    Args:
        signals: BehaviorSignals object with credit data

    Returns:
        True if user matches high utilization criteria
    """
    credit = signals.credit

    # Check if credit data exists
    if not credit:
        return False

    # Check utilization threshold
    utilization = credit.get("overall_utilization", 0.0)
    if utilization >= 50.0:
        logger.info("High utilization match: utilization >= 50%")
        return True

    # Check flags for interest charges, overdue, or minimum payment only
    flags = credit.get("flags", [])
    if "interest_charges" in flags:
        logger.info("High utilization match: interest charges detected")
        return True

    if "overdue" in flags:
        logger.info("High utilization match: overdue payments detected")
        return True

    if "minimum_payment_only" in flags:
        logger.info("High utilization match: minimum payment only behavior detected")
        return True

    return False


def matches_variable_income(signals: BehaviorSignals) -> bool:
    """
    Check if user matches variable income persona.

    Criteria:
    - Median pay gap >45 days AND
    - Cash flow buffer <1 month

    Args:
        signals: BehaviorSignals object with income data

    Returns:
        True if user matches variable income criteria
    """
    income = signals.income

    # Check if income data exists
    if not income:
        return False

    # Check median pay gap
    median_gap_days = income.get("median_gap_days", 0)
    if median_gap_days <= 45:
        return False

    # Check cash flow buffer
    buffer_months = income.get("buffer_months", 0.0)
    if buffer_months >= 1.0:
        return False

    return True


def matches_subscription_heavy(signals: BehaviorSignals) -> bool:
    """
    Check if user matches subscription heavy persona.

    Criteria:
    - ≥3 active subscriptions AND
    - (Monthly recurring spend ≥$50 OR ≥10% of total spending)

    Args:
        signals: BehaviorSignals object with subscription data

    Returns:
        True if user matches subscription heavy criteria
    """
    subscriptions = signals.subscriptions

    # Check if subscription data exists
    if not subscriptions:
        return False

    # Check subscription count
    count = subscriptions.get("count", 0)
    if count < 3:
        return False

    # Check monthly recurring spend ($50 = 5000 cents)
    monthly_spend = subscriptions.get("monthly_recurring_spend", 0)
    if monthly_spend >= 5000:
        return True

    # Check percentage of total spending
    percentage = subscriptions.get("percentage_of_spending", 0.0)
    if percentage >= 10.0:
        return True

    return False


def matches_savings_builder(signals: BehaviorSignals) -> bool:
    """
    Check if user matches savings builder persona.

    Criteria:
    - (Savings growth rate ≥2% OR monthly inflow ≥$200) AND
    - Credit utilization <30%

    Args:
        signals: BehaviorSignals object with savings and credit data

    Returns:
        True if user matches savings builder criteria
    """
    savings = signals.savings
    credit = signals.credit

    # Check if savings data exists
    if not savings:
        return False

    # Check savings growth or inflow
    growth_rate = savings.get("growth_rate", 0.0)
    monthly_inflow = savings.get("monthly_inflow", 0)

    savings_criteria_met = growth_rate >= 2.0 or monthly_inflow >= 20000  # $200 = 20000 cents

    if not savings_criteria_met:
        return False

    # Check credit utilization (must be low)
    if credit:
        utilization = credit.get("overall_utilization", 0.0)
        if utilization >= 30.0:
            return False

    return True


def matches_debt_consolidator(signals: BehaviorSignals) -> bool:
    """
    Check if user matches debt consolidator persona.

    Criteria:
    - Has 2+ credit cards with balances
    - Overall utilization 30-70% (significant but not urgent)
    - No overdue payments (responsible borrower)
    - Has regular income (can afford consolidation)
    - Paying interest charges

    Rationale:
    - Represents prime consolidation candidates
    - Not in crisis but paying unnecessary interest
    - Good credit score, qualifies for balance transfer offers

    Primary Focus:
    - Balance transfer strategies
    - Debt consolidation loans
    - Interest savings calculators

    Args:
        signals: BehaviorSignals object with credit and income data

    Returns:
        True if user matches debt consolidator criteria
    """
    credit = signals.credit
    income = signals.income

    # Must have credit data
    if not credit:
        return False

    # Check utilization is moderate (30-70%)
    utilization = credit.get("overall_utilization", 0.0)
    if utilization < 30.0 or utilization >= 70.0:
        return False

    # Must have 2+ cards with balances
    per_card = credit.get("per_card", [])
    cards_with_balance = [c for c in per_card if c.get("balance", 0) > 0]
    if len(cards_with_balance) < 2:
        return False

    # Must be paying interest (consolidation opportunity)
    monthly_interest = credit.get("monthly_interest", 0)
    if monthly_interest <= 0:
        return False

    # Check NOT overdue (responsible borrower)
    flags = credit.get("flags", [])
    if "overdue" in flags:
        return False

    # Should have regular income (ability to consolidate)
    if income:
        frequency = income.get("frequency", "unknown")
        if frequency == "unknown":
            return False

    logger.info(
        f"Debt consolidator match: {len(cards_with_balance)} cards, "
        f"{utilization:.1f}% utilization, ${monthly_interest/100:.2f}/mo interest"
    )

    return True


async def assign_persona(
    db: AsyncSession,
    user_id: str,
    window_days: int
) -> Dict[str, Any]:
    """
    Assign a financial persona to a user based on behavioral signals.

    Personas are checked in priority order (most urgent first). The first
    matching persona is assigned with its confidence score. If no persona
    matches, defaults to "balanced".

    Args:
        db: Async SQLAlchemy database session
        user_id: User identifier
        window_days: Number of days to analyze (e.g., 30, 180)

    Returns:
        Dictionary containing:
        {
            "persona_type": str,        # Assigned persona type
            "confidence": float,         # Confidence score (0.60-0.95)
            "signals": BehaviorSignals, # All computed signals
            "assigned_at": datetime     # Timestamp of assignment
        }

    Side Effects:
        - Saves persona assignment to database (personas table)

    Raises:
        HTTPException: If user not found or database error
    """
    logger.info(f"Assigning persona for user {user_id}, window: {window_days} days")

    # Compute all behavioral signals
    signals = await compute_signals(db, user_id, window_days)

    # Check personas in priority order
    persona_type = None

    if matches_high_utilization(signals):
        persona_type = "high_utilization"
    elif matches_variable_income(signals):
        persona_type = "variable_income"
    elif matches_debt_consolidator(signals):
        persona_type = "debt_consolidator"
    elif matches_subscription_heavy(signals):
        persona_type = "subscription_heavy"
    elif matches_savings_builder(signals):
        persona_type = "savings_builder"
    else:
        persona_type = "balanced"

    # Get confidence score for assigned persona
    confidence = CONFIDENCE_SCORES.get(persona_type, 0.60)

    # Format window string (e.g., "30d", "180d")
    window_str = f"{window_days}d"

    # Create timestamp
    assigned_at = datetime.now()

    logger.info(f"Assigned persona '{persona_type}' to user {user_id} with confidence {confidence}")

    # Save to database
    persona = Persona(
        user_id=user_id,
        window=window_str,
        persona_type=persona_type,
        confidence=confidence,
        assigned_at=assigned_at
    )

    db.add(persona)
    await db.commit()
    await db.refresh(persona)

    logger.info(f"Saved persona assignment to database: {persona}")

    # Return persona data
    return {
        "persona_type": persona_type,
        "confidence": confidence,
        "signals": signals,
        "assigned_at": assigned_at
    }
