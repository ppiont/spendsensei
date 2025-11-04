"""User management endpoints"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.user import User
from spendsense.schemas.user import UserCreate, UserResponse

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
