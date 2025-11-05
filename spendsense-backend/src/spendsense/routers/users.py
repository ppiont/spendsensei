"""User management endpoints"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.user import User
from spendsense.models.account import Account
from spendsense.schemas.user import UserCreate, UserResponse, ProfileResponse, AccountSummary, PersonaSummary
from spendsense.services.personas import assign_persona
from spendsense.services.features import compute_signals

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users.

    Args:
        db: Database session

    Returns:
        list[UserResponse]: List of all users ordered by name

    Raises:
        HTTPException: 500 if database error occurs
    """
    try:
        # Get all users ordered by name
        result = await db.execute(
            select(User).order_by(User.name)
        )
        users = result.scalars().all()

        # Return response
        return [UserResponse.from_orm(user) for user in users]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.

    Args:
        user_data: User creation data (name, email)
        db: Database session

    Returns:
        UserResponse: Created user with generated ID and timestamp

    Raises:
        HTTPException: 500 if database error occurs
    """
    try:
        # Generate UUID for new user
        user_id = str(uuid.uuid4())

        # Create new user instance
        new_user = User(
            id=user_id,
            name=user_data.name,
            email=user_data.email,
            consent=False,  # Default to no consent
            created_at=datetime.now(timezone.utc)
        )

        # Add to database
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Return response
        return UserResponse.from_orm(new_user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/consent", response_model=UserResponse)
async def update_consent(
    user_id: str,
    consent: bool,
    db: AsyncSession = Depends(get_db)
):
    """
    Update user consent status.

    Args:
        user_id: User ID to update
        consent: New consent value (true/false)
        db: Database session

    Returns:
        UserResponse: Updated user data

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 500 if database error occurs
    """
    try:
        # Find user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        # Update consent
        user.consent = consent
        await db.commit()
        await db.refresh(user)

        # Return response
        return UserResponse.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update consent: {str(e)}"
        )


@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive user profile including account summary and persona.

    Args:
        user_id: User ID to retrieve profile for
        db: Database session

    Returns:
        ProfileResponse: User info, account summary, and persona assignment

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 500 if database error occurs
    """
    try:
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        # Get accounts for summary
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == user_id)
        )
        accounts = accounts_result.scalars().all()

        # Calculate account summary
        total_balance = 0
        total_available = 0
        depository_count = 0
        credit_count = 0

        for account in accounts:
            total_balance += account.current_balance
            total_available += account.available_balance or account.current_balance

            if account.type == "depository":
                depository_count += 1
            elif account.type == "credit":
                credit_count += 1

        account_summary = AccountSummary(
            total_accounts=len(accounts),
            depository_accounts=depository_count,
            credit_accounts=credit_count,
            total_balance_cents=total_balance,
            total_available_cents=total_available
        )

        # Get persona assignment (if user has transactions)
        persona_summary = None
        try:
            # Compute signals and assign persona
            signals = await compute_signals(db=db, user_id=user_id, window_days=30)
            persona_type, confidence = assign_persona(signals)

            persona_summary = PersonaSummary(
                persona_type=persona_type,
                confidence=confidence,
                assigned_at=datetime.now(timezone.utc).isoformat() + "Z"
            )
        except Exception:
            # If persona assignment fails (e.g., no transactions), leave as None
            pass

        # Build profile response
        return ProfileResponse(
            user=UserResponse.from_orm(user),
            accounts=account_summary,
            persona=persona_summary
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user profile: {str(e)}"
        )
