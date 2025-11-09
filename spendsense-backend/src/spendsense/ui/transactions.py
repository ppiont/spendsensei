"""Transaction retrieval endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.account import Account
from spendsense.models.transaction import Transaction
from spendsense.models.user import User
from spendsense.schemas.transaction import TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/{user_id}", response_model=list[TransactionResponse])
async def get_user_transactions(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve transactions for a user with pagination.

    Args:
        user_id: User ID to fetch transactions for
        limit: Maximum number of transactions to return (1-1000)
        offset: Number of transactions to skip for pagination
        db: Database session

    Returns:
        list[TransactionResponse]: List of user's transactions

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 500 if database error occurs
    """
    try:
        # Check if user exists
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        # Fetch transactions for all user's accounts with pagination
        # Join with accounts table to filter by user_id
        transactions_result = await db.execute(
            select(Transaction)
            .join(Account)
            .where(Account.user_id == user_id)
            .order_by(Transaction.date.desc())  # Most recent first
            .limit(limit)
            .offset(offset)
        )
        transactions = transactions_result.scalars().all()

        # Convert to response schemas
        return [TransactionResponse.from_orm(txn) for txn in transactions]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch transactions: {str(e)}"
        )
