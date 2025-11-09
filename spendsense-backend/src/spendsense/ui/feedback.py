"""Feedback management endpoints"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.database import get_db
from spendsense.models.feedback import Feedback
from spendsense.models.user import User
from spendsense.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit user feedback on a recommendation or offer.

    This endpoint allows users to provide feedback on education content
    and partner offers, helping improve recommendation quality.

    Args:
        feedback_data: Feedback submission data
        db: Database session

    Returns:
        FeedbackResponse: Created feedback with generated ID

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 500 if database error occurs
    """
    try:
        # Verify user exists
        result = await db.execute(
            select(User).where(User.id == feedback_data.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {feedback_data.user_id} not found"
            )

        # Generate UUID for feedback
        feedback_id = f"fb_{uuid.uuid4().hex[:12]}"

        # Create feedback instance
        new_feedback = Feedback(
            id=feedback_id,
            user_id=feedback_data.user_id,
            recommendation_id=feedback_data.recommendation_id,
            recommendation_type=feedback_data.recommendation_type,
            feedback_type=feedback_data.feedback_type,
            comment=feedback_data.comment,
            created_at=datetime.now(timezone.utc)
        )

        # Add to database
        db.add(new_feedback)
        await db.commit()
        await db.refresh(new_feedback)

        # Return response
        return FeedbackResponse.from_orm(new_feedback)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create feedback: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=list[FeedbackResponse])
async def get_user_feedback(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all feedback submitted by a user.

    Args:
        user_id: User ID to get feedback for
        db: Database session

    Returns:
        list[FeedbackResponse]: List of feedback ordered by most recent

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 500 if database error occurs
    """
    try:
        # Verify user exists
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        # Get all feedback for user
        feedback_result = await db.execute(
            select(Feedback)
            .where(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
        )
        feedback_items = feedback_result.scalars().all()

        # Return response
        return [FeedbackResponse.from_orm(item) for item in feedback_items]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch feedback: {str(e)}"
        )
