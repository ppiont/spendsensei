"""
Persona Assignment Logic

Assigns financial personas to users based on their behavioral signals.
Personas are assigned in priority order (most urgent first) with confidence scoring.

Personas:
- high_utilization: Credit card usage ≥50% OR interest charges OR overdue
- variable_income: Median pay gap >45 days AND buffer <1 month
- debt_consolidator: Multiple cards with moderate utilization, paying interest
- subscription_heavy: ≥3 subscriptions AND (monthly spend ≥$50 OR ≥10% of total)
- savings_builder: Growth rate ≥2% OR monthly inflow ≥$200, AND utilization <30%
- balanced: Default fallback if no other persona matches
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from spendsense.features import BehaviorSignals, compute_signals
from spendsense.personas.types import PERSONA_PRIORITY, CONFIDENCE_SCORES
from spendsense.models.persona import Persona

logger = logging.getLogger(__name__)


def calculate_high_utilization_confidence(signals: BehaviorSignals) -> float:
    """
    Calculate confidence for high utilization persona based on signal strength.

    Confidence scoring:
    - Base score from utilization level (0.65-0.90)
    - Boosts for warning flags (+0.05-0.10 each)
    - Capped at 0.98 maximum

    Args:
        signals: BehaviorSignals object with credit data

    Returns:
        Confidence score 0.0-0.98 (0.0 if no match)
    """
    credit = signals.credit

    # Check if credit data exists
    if not credit:
        return 0.0

    confidence = 0.0

    # Primary signal: Utilization level
    utilization = credit.get("overall_utilization", 0.0)
    if utilization >= 90.0:
        confidence = 0.90  # Critical level
        logger.info(f"High utilization: critical at {utilization:.1f}%")
    elif utilization >= 80.0:
        confidence = 0.85  # Very high
        logger.info(f"High utilization: very high at {utilization:.1f}%")
    elif utilization >= 70.0:
        confidence = 0.80  # High
        logger.info(f"High utilization: high at {utilization:.1f}%")
    elif utilization >= 50.0:
        confidence = 0.70  # Moderate concern
        logger.info(f"High utilization: moderate at {utilization:.1f}%")
    else:
        confidence = 0.0  # Below threshold

    # Boost confidence for additional warning flags
    flags = credit.get("flags", [])

    if "overdue" in flags:
        confidence = min(confidence + 0.10, 0.98)  # Urgent signal
        logger.info("High utilization boost: overdue payment detected")

    if "interest_charges" in flags:
        confidence = min(confidence + 0.05, 0.98)
        logger.info("High utilization boost: interest charges detected")

    if "minimum_payment_only" in flags:
        confidence = min(confidence + 0.05, 0.98)
        logger.info("High utilization boost: minimum payment only")

    # Ensure minimum confidence if we have any match
    if confidence > 0:
        confidence = max(confidence, 0.65)

    return min(confidence, 0.98)


def calculate_variable_income_confidence(signals: BehaviorSignals) -> float:
    """
    Calculate confidence for variable income persona based on signal strength.

    Confidence scoring:
    - Base score from pay gap irregularity (0.75-0.90)
    - Adjusted based on buffer tightness
    - Higher scores for more irregular income + lower buffer

    Args:
        signals: BehaviorSignals object with income data

    Returns:
        Confidence score 0.0-0.95 (0.0 if no match)
    """
    income = signals.income

    # Check if income data exists
    if not income:
        return 0.0

    # Check median pay gap (must be >45 days)
    median_gap_days = income.get("median_gap_days", 0)
    if median_gap_days <= 45:
        return 0.0

    # Base confidence from irregularity level
    if median_gap_days >= 90:
        confidence = 0.90  # Very irregular (quarterly or worse)
        logger.info(f"Variable income: very irregular, gap {median_gap_days} days")
    elif median_gap_days >= 60:
        confidence = 0.85  # Irregular (bi-monthly)
        logger.info(f"Variable income: irregular, gap {median_gap_days} days")
    else:  # 45-60 days
        confidence = 0.75  # Moderately irregular
        logger.info(f"Variable income: moderately irregular, gap {median_gap_days} days")

    # Adjust based on buffer tightness (must be <1 month)
    buffer_months = income.get("buffer_months", 0.0)
    if buffer_months >= 1.0:
        return 0.0  # Has sufficient buffer, not a match

    # Boost confidence for very low buffer
    if buffer_months < 0.25:
        confidence = min(confidence + 0.10, 0.95)  # Critical buffer
        logger.info(f"Variable income boost: critical buffer at {buffer_months:.2f} months")
    elif buffer_months < 0.5:
        confidence = min(confidence + 0.05, 0.95)  # Low buffer
        logger.info(f"Variable income boost: low buffer at {buffer_months:.2f} months")

    # Ensure minimum confidence for matches
    confidence = max(confidence, 0.70)

    return min(confidence, 0.95)


def calculate_subscription_heavy_confidence(signals: BehaviorSignals) -> float:
    """
    Calculate confidence for subscription heavy persona based on signal strength.

    Confidence scoring:
    - Base score from subscription count (0.70-0.85)
    - Boost for high monthly spend or high percentage
    - Higher scores for more subscriptions + higher impact

    Args:
        signals: BehaviorSignals object with subscription data

    Returns:
        Confidence score 0.0-0.90 (0.0 if no match)
    """
    subscriptions = signals.subscriptions

    # Check if subscription data exists
    if not subscriptions:
        return 0.0

    # Check subscription count (must be ≥3)
    count = subscriptions.get("count", 0)
    if count < 3:
        return 0.0

    # Base confidence from subscription count
    if count >= 7:
        confidence = 0.85  # Very subscription heavy
        logger.info(f"Subscription heavy: {count} subscriptions")
    elif count >= 5:
        confidence = 0.80  # Many subscriptions
        logger.info(f"Subscription heavy: {count} subscriptions")
    else:  # 3-4
        confidence = 0.70  # Moderate subscriptions
        logger.info(f"Subscription heavy: {count} subscriptions")

    # Check monthly recurring spend and percentage
    monthly_spend = subscriptions.get("monthly_recurring_spend", 0)
    percentage = subscriptions.get("percentage_of_spending", 0.0)

    # Must meet one of the spend criteria
    if monthly_spend < 5000 and percentage < 10.0:  # $50 = 5000 cents
        return 0.0  # Count alone isn't enough

    # Boost for high monthly spend
    if monthly_spend >= 20000:  # $200+
        confidence = min(confidence + 0.08, 0.90)
        logger.info(f"Subscription boost: high monthly spend ${monthly_spend/100:.2f}")
    elif monthly_spend >= 10000:  # $100+
        confidence = min(confidence + 0.05, 0.90)

    # Boost for high percentage of total spend
    if percentage >= 20.0:
        confidence = min(confidence + 0.05, 0.90)
        logger.info(f"Subscription boost: high percentage {percentage:.1f}%")

    return min(confidence, 0.90)


def calculate_savings_builder_confidence(signals: BehaviorSignals) -> float:
    """
    Calculate confidence for savings builder persona based on signal strength.

    Confidence scoring:
    - Base score from growth rate or inflow (0.70-0.85)
    - Bonus for both growth AND inflow
    - Reduced if credit utilization is approaching 30%
    - Assumes low credit utilization (<30%)

    Args:
        signals: BehaviorSignals object with savings and credit data

    Returns:
        Confidence score 0.0-0.88 (0.0 if no match)
    """
    savings = signals.savings
    credit = signals.credit

    # Check if savings data exists
    if not savings:
        return 0.0

    # Check savings growth and inflow
    growth_rate = savings.get("growth_rate", 0.0)
    monthly_inflow = savings.get("monthly_inflow", 0)

    # Must meet at least one savings criterion
    if growth_rate < 2.0 and monthly_inflow < 20000:  # $200 = 20000 cents
        return 0.0

    # Check credit utilization (must be <30%)
    if credit:
        utilization = credit.get("overall_utilization", 0.0)
        if utilization >= 30.0:
            return 0.0  # Not a match if high utilization

    # Base confidence from savings behavior
    if growth_rate >= 5.0:
        confidence = 0.85  # Excellent growth
        logger.info(f"Savings builder: excellent growth at {growth_rate:.1f}%")
    elif growth_rate >= 3.0:
        confidence = 0.80  # Strong growth
        logger.info(f"Savings builder: strong growth at {growth_rate:.1f}%")
    elif growth_rate >= 2.0:
        confidence = 0.75  # Moderate growth
        logger.info(f"Savings builder: moderate growth at {growth_rate:.1f}%")
    else:
        confidence = 0.70  # Meeting threshold via inflow only
        logger.info(f"Savings builder: via inflow ${monthly_inflow/100:.2f}/mo")

    # Boost for high monthly inflow
    if monthly_inflow >= 50000:  # $500+
        confidence = min(confidence + 0.05, 0.88)
        logger.info(f"Savings builder boost: high inflow ${monthly_inflow/100:.2f}/mo")
    elif monthly_inflow >= 30000:  # $300+
        confidence = min(confidence + 0.03, 0.88)

    # Small reduction if utilization is close to threshold
    if credit and credit.get("overall_utilization", 0.0) >= 20.0:
        confidence = max(confidence - 0.05, 0.65)

    return min(confidence, 0.88)


def calculate_debt_consolidator_confidence(signals: BehaviorSignals) -> float:
    """
    Calculate confidence for debt consolidator persona based on signal strength.

    Confidence scoring:
    - Base score from utilization and interest charges (0.75-0.88)
    - Boost for multiple cards and higher interest
    - Requires regular income for consolidation viability

    Args:
        signals: BehaviorSignals object with credit and income data

    Returns:
        Confidence score 0.0-0.92 (0.0 if no match)
    """
    credit = signals.credit
    income = signals.income

    # Must have credit data
    if not credit:
        return 0.0

    # Check utilization is moderate (30-70%)
    utilization = credit.get("overall_utilization", 0.0)
    if utilization < 30.0 or utilization >= 70.0:
        return 0.0

    # Must have 2+ cards with balances
    per_card = credit.get("per_card", [])
    cards_with_balance = [c for c in per_card if c.get("balance", 0) > 0]
    if len(cards_with_balance) < 2:
        return 0.0

    # Must be paying interest (consolidation opportunity)
    monthly_interest = credit.get("monthly_interest", 0)
    if monthly_interest <= 0:
        return 0.0

    # Check NOT overdue (responsible borrower)
    flags = credit.get("flags", [])
    if "overdue" in flags:
        return 0.0

    # Should have regular income (ability to consolidate)
    if income:
        frequency = income.get("frequency", "unknown")
        if frequency == "unknown":
            return 0.0
    else:
        return 0.0  # Need income data for consolidation

    # Base confidence from utilization level
    if utilization >= 60.0:
        confidence = 0.88  # Higher urgency
        logger.info(f"Debt consolidator: high utilization at {utilization:.1f}%")
    elif utilization >= 50.0:
        confidence = 0.85  # Moderate urgency
        logger.info(f"Debt consolidator: moderate utilization at {utilization:.1f}%")
    else:  # 30-50%
        confidence = 0.75  # Lower urgency but opportunity exists
        logger.info(f"Debt consolidator: opportunity at {utilization:.1f}%")

    # Boost for multiple cards (more complex to manage)
    if len(cards_with_balance) >= 4:
        confidence = min(confidence + 0.05, 0.92)
        logger.info(f"Debt consolidator boost: {len(cards_with_balance)} cards")
    elif len(cards_with_balance) >= 3:
        confidence = min(confidence + 0.03, 0.92)

    # Boost for high interest charges (more savings potential)
    if monthly_interest >= 20000:  # $200/mo
        confidence = min(confidence + 0.05, 0.92)
        logger.info(f"Debt consolidator boost: high interest ${monthly_interest/100:.2f}/mo")
    elif monthly_interest >= 10000:  # $100/mo
        confidence = min(confidence + 0.03, 0.92)

    logger.info(
        f"Debt consolidator: {len(cards_with_balance)} cards, "
        f"{utilization:.1f}% utilization, ${monthly_interest/100:.2f}/mo interest, "
        f"confidence {confidence:.2f}"
    )

    return min(confidence, 0.92)


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

    # Check personas in priority order, using first with confidence > 0
    # Each function returns a confidence score (0.0-1.0)
    confidence = calculate_high_utilization_confidence(signals)
    if confidence > 0:
        persona_type = "high_utilization"
    else:
        confidence = calculate_variable_income_confidence(signals)
        if confidence > 0:
            persona_type = "variable_income"
        else:
            confidence = calculate_debt_consolidator_confidence(signals)
            if confidence > 0:
                persona_type = "debt_consolidator"
            else:
                confidence = calculate_subscription_heavy_confidence(signals)
                if confidence > 0:
                    persona_type = "subscription_heavy"
                else:
                    confidence = calculate_savings_builder_confidence(signals)
                    if confidence > 0:
                        persona_type = "savings_builder"
                    else:
                        # Default to balanced with base confidence
                        persona_type = "balanced"
                        confidence = 0.60

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
