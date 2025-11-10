"""
Signal Computation Orchestrator

Coordinates all behavioral signal detection functions to produce complete user profiles.
"""

from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import logging

from spendsense.features.types import BehaviorSignals
from spendsense.features.income import analyze_income
from spendsense.features.savings import analyze_savings
from spendsense.features.credit import analyze_credit
from spendsense.features.subscriptions import detect_subscriptions

logger = logging.getLogger(__name__)


async def compute_signals(db: AsyncSession, user_id: str, window_days: int) -> BehaviorSignals:
    """
    Compute all behavioral signals for a user within a time window.

    This is the orchestration layer that queries the database for user accounts
    and transactions, then calls all signal detection functions to populate a
    complete BehaviorSignals object.

    Args:
        db: Async SQLAlchemy database session
        user_id: User identifier
        window_days: Number of days to analyze (e.g., 30, 180)

    Returns:
        BehaviorSignals object with all fields populated

    Raises:
        HTTPException(404): If user has no accounts
        HTTPException(500): If database query fails

    Performance:
        Target: <200ms per user with indexed queries
    """
    try:
        # Import models locally to avoid circular imports
        from spendsense.models.account import Account
        from spendsense.models.transaction import Transaction

        # Calculate cutoff date for time window
        cutoff_date = datetime.now() - timedelta(days=window_days)

        logger.info(f"Computing signals for user {user_id}, window: {window_days} days, cutoff: {cutoff_date}")

        # Query user's accounts
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == user_id)
        )
        accounts = accounts_result.scalars().all()

        # Edge case: User has no accounts
        if not accounts:
            logger.warning(f"User {user_id} has no accounts")
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found or has no accounts"
            )

        logger.info(f"Found {len(accounts)} accounts for user {user_id}")

        # Query transactions within time window (with indexed join)
        txns_result = await db.execute(
            select(Transaction)
            .join(Account)
            .where(
                Account.user_id == user_id,
                Transaction.date >= cutoff_date
            )
            .order_by(Transaction.date)  # Order for better cache locality
        )
        transactions = txns_result.scalars().all()

        logger.info(f"Found {len(transactions)} transactions for user {user_id} within window")

        # Convert ORM objects to dictionaries for signal functions
        accounts_dicts = [
            {
                "id": acc.id,
                "type": acc.type,
                "subtype": acc.subtype,
                "balance": acc.current_balance,
                "limit": acc.limit,
                "apr": acc.apr,
                "is_overdue": acc.is_overdue,
                "last_payment_amount": acc.last_payment_amount,
                "min_payment": acc.min_payment
            }
            for acc in accounts
        ]

        transactions_dicts = [
            {
                "id": txn.id,
                "account_id": txn.account_id,
                "date": txn.date,
                "amount": txn.amount,
                "merchant_name": txn.merchant_name,
                "merchant_entity_id": txn.merchant_entity_id,
                "personal_finance_category_primary": txn.personal_finance_category_primary,
                "personal_finance_category_detailed": txn.personal_finance_category_detailed
            }
            for txn in transactions
        ]

        # Call all signal detection functions
        logger.debug(f"Calling signal detection functions for user {user_id}")

        subscriptions_data = detect_subscriptions(transactions_dicts, window_days)
        savings_data = analyze_savings(accounts_dicts, transactions_dicts, window_days)
        credit_data = analyze_credit(accounts_dicts, transactions_dicts)
        income_data = analyze_income(transactions_dicts, window_days)

        # Populate BehaviorSignals object
        signals = BehaviorSignals(
            subscriptions=subscriptions_data,
            savings=savings_data,
            credit=credit_data,
            income=income_data
        )

        logger.info(f"Successfully computed signals for user {user_id}")

        return signals

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log and wrap unexpected errors
        logger.error(f"Error computing signals for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute signals: {str(e)}"
        )
