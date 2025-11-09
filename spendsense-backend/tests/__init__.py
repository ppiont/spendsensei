"""SpendSense Test Suite

This package contains all automated tests for the SpendSense backend.

Test Organization:
- test_api_*.py: API endpoint tests (FastAPI routes)
- test_signals_*.py: Behavioral signal detection tests
- test_personas_*.py: Persona assignment tests
- test_recommendations_*.py: Recommendation engine tests
- test_guardrails_*.py: Content safety and compliance tests
- test_models_*.py: Database model tests

Running Tests:
    # Run all tests
    pytest

    # Run specific test file
    pytest tests/test_api_users.py

    # Run tests by marker
    pytest -m unit
    pytest -m integration
    pytest -m api

    # Run with coverage
    pytest --cov=spendsense --cov-report=html

    # Run in parallel (requires pytest-xdist)
    pytest -n auto
"""
