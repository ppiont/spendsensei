"""Account retrieval endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.account import Account
from spendsense.models.user import User
from spendsense.schemas.account import AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/{user_id}", response_model=list[AccountResponse])
async def get_user_accounts(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all accounts for a user.

    Args:
        user_id: User ID to fetch accounts for
        db: Database session

    Returns:
        list[AccountResponse]: List of user's accounts

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

        # Fetch all accounts for the user
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == user_id)
        )
        accounts = accounts_result.scalars().all()

        # Convert to response schemas
        return [AccountResponse.from_orm(account) for account in accounts]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch accounts: {str(e)}"
        )
