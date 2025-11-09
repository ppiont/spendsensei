"""Test suite for user and consent operations

Converted from scripts/test_user_endpoints.py to pytest format.
Tests user creation, consent updates, and database operations.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from spendsense.models.user import User


@pytest.mark.api
@pytest.mark.integration
class TestUserOperations:
    """Test user CRUD operations and consent management"""

    async def test_create_user(self, db: AsyncSession):
        """Test creating a new user in the database"""
        # Create user
        user = User(
            id="test-user-create-001",
            name="Test User",
            email="test@example.com",
            consent=False,
            created_at=datetime.now(timezone.utc)
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Verify user was created
        assert user.id == "test-user-create-001"
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.consent is False
        assert user.created_at is not None

    async def test_find_user(self, db: AsyncSession):
        """Test finding an existing user in the database"""
        # Create test user
        user = User(
            id="test-user-find-001",
            name="Find Me",
            email="findme@example.com",
            consent=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        await db.commit()

        # Find user
        result = await db.execute(
            select(User).where(User.id == "test-user-find-001")
        )
        found_user = result.scalar_one_or_none()

        # Verify user was found
        assert found_user is not None
        assert found_user.id == "test-user-find-001"
        assert found_user.email == "findme@example.com"
        assert found_user.consent is True

    async def test_update_consent(self, db: AsyncSession):
        """Test updating user consent status"""
        # Create user without consent
        user = User(
            id="test-user-consent-001",
            name="Consent User",
            email="consent@example.com",
            consent=False,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Update consent to True
        user.consent = True
        await db.commit()
        await db.refresh(user)

        # Verify consent was updated
        assert user.consent is True

    async def test_consent_persistence(self, db: AsyncSession):
        """Test that consent updates persist correctly"""
        # Create user
        user = User(
            id="test-user-persist-001",
            name="Persist User",
            email="persist@example.com",
            consent=False,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        await db.commit()

        # Update consent
        user.consent = True
        await db.commit()

        # Re-query user from database
        result = await db.execute(
            select(User).where(User.id == "test-user-persist-001")
        )
        verified_user = result.scalar_one_or_none()

        # Verify consent persisted
        assert verified_user is not None
        assert verified_user.consent is True

    async def test_user_not_found(self, db: AsyncSession):
        """Test that querying for nonexistent user returns None"""
        result = await db.execute(
            select(User).where(User.id == "nonexistent-user-12345")
        )
        not_found = result.scalar_one_or_none()

        # Verify None returned for nonexistent user
        assert not_found is None


@pytest.mark.api
@pytest.mark.unit
class TestUserModel:
    """Test User model validation and behavior"""

    async def test_user_with_test_fixture(self, test_user: User):
        """Test using the test_user fixture"""
        assert test_user.id == "test-user-001"
        assert test_user.name == "Test User"
        assert test_user.consent is True

    async def test_user_without_consent_fixture(self, test_user_no_consent: User):
        """Test using the test_user_no_consent fixture"""
        assert test_user_no_consent.id == "test-user-no-consent"
        assert test_user_no_consent.consent is False

    async def test_multiple_users_fixture(self, multiple_test_users: list):
        """Test using the multiple_test_users fixture"""
        assert len(multiple_test_users) == 3
        assert all(user.consent is True for user in multiple_test_users)
        assert multiple_test_users[0].id == "test-user-001"
