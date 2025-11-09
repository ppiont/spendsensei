# SpendSense Testing Guide

## Overview

This directory contains the automated test suite for SpendSense backend. Tests use pytest with async support via pytest-asyncio.

## Test Infrastructure

### Files
- `pytest.ini` - Pytest configuration (markers, asyncio mode, logging)
- `conftest.py` - Shared fixtures for database, users, accounts, transactions
- `__init__.py` - Test suite documentation

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api_users.py

# Run tests by marker
pytest -m unit          # Fast unit tests
pytest -m integration   # Integration tests (database)
pytest -m api           # API endpoint tests
pytest -m signals       # Signal detection tests

# Run with verbose output
pytest -v

# Run with coverage (if pytest-cov installed)
pytest --cov=spendsense --cov-report=html

# Run in parallel (if pytest-xdist installed)
pytest -n auto
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Fast unit tests, no external dependencies
- `@pytest.mark.integration` - Database or file system integration
- `@pytest.mark.api` - FastAPI route testing
- `@pytest.mark.slow` - Long-running operations
- `@pytest.mark.signals` - Behavioral signal detection
- `@pytest.mark.personas` - Persona assignment
- `@pytest.mark.recommendations` - Recommendation engine
- `@pytest.mark.guardrails` - Content safety and compliance

## Available Fixtures

### Database Fixtures
- `db` - Database session with automatic rollback
- `clean_db` - Completely clean database (all tables cleared)

### User Fixtures
- `test_user` - User with consent (id="test-user-001")
- `test_user_no_consent` - User without consent
- `multiple_test_users` - List of 3 users

### Account Fixtures
- `test_checking_account` - Checking account ($5,000 balance)
- `test_credit_card` - Credit card (85% utilization)
- `test_accounts` - List of checking + credit card

### Transaction Fixtures
- `test_transactions` - 5 sample transactions (income, subscriptions, expenses)

### Test Data Helpers
- `sample_user_data` - Dict with user financial data
- `sample_partner_offer` - Dict with partner offer details

## Migration from Manual Scripts to Pytest

### Status: 1 of 16 tests converted ✅

**Converted:**
- ✅ `test_user_endpoints.py` → `tests/test_api_users.py`

**Remaining to convert:**
- `test_account_transaction_endpoints.py` → `tests/test_api_accounts.py`
- `test_schemas.py` → `tests/test_models_schemas.py`
- `test_guardrails.py` → `tests/test_guardrails_consent.py`
- `test_credit_analysis.py` → `tests/test_signals_credit.py`
- `test_guardrails_blocking.py` → `tests/test_guardrails_blocking.py`
- `test_insights_endpoint.py` → `tests/test_api_insights.py`
- `test_insights_with_guardrails.py` → `tests/test_api_insights_guardrails.py`
- `test_income_analysis.py` → `tests/test_signals_income.py`
- `test_persona_assignment.py` → `tests/test_personas_assignment.py`
- `test_recommendation_engine.py` → `tests/test_recommendations_engine.py`
- `test_persona_matching.py` → `tests/test_personas_matching.py`
- `test_subscription_detection.py` → `tests/test_signals_subscriptions.py`
- `test_signal_computation.py` → `tests/test_signals_computation.py`
- `test_savings_analysis.py` → `tests/test_signals_savings.py`
- `test_template_generator.py` → `tests/test_recommendations_generator.py`

### Conversion Pattern

#### Before (Manual Script)
```python
# scripts/test_user_endpoints.py
import asyncio
import sys
from spendsense.database import AsyncSessionLocal

async def test_endpoints():
    async with AsyncSessionLocal() as db:
        # Test 1
        print("Test 1...")
        assert condition, "Failure message"

        # Test 2
        print("Test 2...")
        if not condition:
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_endpoints())
```

#### After (Pytest Format)
```python
# tests/test_api_users.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.api
@pytest.mark.integration
class TestUserOperations:
    """Organized test class"""

    async def test_case_1(self, db: AsyncSession):
        """Test description"""
        # Arrange
        user = create_user()

        # Act
        db.add(user)
        await db.commit()

        # Assert
        assert user.id is not None

    async def test_case_2(self, test_user):
        """Use fixtures instead of manual setup"""
        assert test_user.consent is True
```

### Key Differences

1. **No manual async main** - pytest-asyncio handles async automatically
2. **Use fixtures** - `db`, `test_user`, etc. instead of manual setup
3. **Separate test functions** - One logical test per function
4. **Use assertions** - No sys.exit(1), pytest handles failures
5. **Add markers** - `@pytest.mark.api`, `@pytest.mark.unit`, etc.
6. **Organize in classes** - Group related tests together
7. **No cleanup needed** - Fixtures auto-rollback database changes

### Template for Conversion

```python
"""Test suite for [feature name]

Converted from scripts/test_[original].py to pytest format.
Tests [what this module tests].
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
# Import what you need

@pytest.mark.[category]  # e.g., @pytest.mark.signals
@pytest.mark.integration
class Test[FeatureName]:
    """Test [feature] functionality"""

    async def test_[specific_case](self, db: AsyncSession):
        """Test [specific behavior]"""
        # Arrange - set up test data

        # Act - perform the operation

        # Assert - verify results
        assert expected == actual

    async def test_with_fixture(self, test_user):
        """Test using fixtures"""
        # Use pre-configured test data
        assert test_user.consent is True
```

## Best Practices

1. **Test Organization**
   - Group related tests in classes
   - Use descriptive class and function names
   - One assertion concept per test

2. **Fixture Usage**
   - Use fixtures instead of manual setup
   - Create new fixtures in conftest.py for common patterns
   - Keep fixtures simple and focused

3. **Async Testing**
   - All async functions automatically handled
   - Use `async def test_*` for async tests
   - Database fixtures are async-safe

4. **Markers**
   - Always add appropriate markers
   - Helps with selective test execution
   - Documents test type and purpose

5. **Assertions**
   - Use clear assertion messages when helpful
   - Test one thing per test function
   - Use pytest's rich assertion introspection

## Example: Converting a Signal Test

### Before
```python
# scripts/test_credit_analysis.py
async def main():
    async with AsyncSessionLocal() as db:
        signals = await analyze_credit(db, user_id)
        if signals.credit["overall_utilization"] > 0.3:
            print("✅ High utilization detected")
        else:
            print("❌ Failed")
            sys.exit(1)
```

### After
```python
# tests/test_signals_credit.py
@pytest.mark.signals
@pytest.mark.integration
class TestCreditSignals:

    async def test_high_utilization_detection(
        self, db, test_user, test_credit_card
    ):
        """Test detection of high credit utilization"""
        from spendsense.features.credit import analyze_credit

        signals = await analyze_credit(db, test_user.id, window_days=30)

        assert signals.credit is not None
        assert signals.credit["overall_utilization"] > 0.3
        assert "high_utilization" in signals.credit
```

## Converting Remaining Tests

To convert the remaining 15 manual tests:

1. **Copy** the manual test from `scripts/`
2. **Create** new file in `tests/` following naming convention
3. **Split** monolithic test into separate functions
4. **Replace** manual setup with fixtures
5. **Add** appropriate markers
6. **Remove** print statements and sys.exit()
7. **Group** in classes by feature area
8. **Run** `pytest tests/[new_file].py -v` to verify

## Future Enhancements

- Add pytest-cov for coverage reporting
- Add pytest-xdist for parallel execution
- Add pytest-timeout for hanging tests
- Integrate with CI/CD pipeline
- Add mutation testing with mutmut
- Add property-based testing with hypothesis
