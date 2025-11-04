# Story 4.1: API Schemas & Configuration

Status: review

## Story

As a developer,
I want Pydantic schemas and API configuration,
So that I have type-safe request/response models and proper CORS setup.

## Acceptance Criteria

1. Create `schemas/user.py` with UserCreate, UserResponse models
2. Create `schemas/account.py` with AccountResponse model
3. Create `schemas/transaction.py` with TransactionResponse model
4. Create `schemas/insight.py` with RecommendationResponse model
5. All response models use snake_case field names
6. Dates serialized as ISO 8601 strings
7. Currency amounts as integers (cents)
8. Create `config.py` with Pydantic Settings
9. Update `main.py` with CORS middleware
10. Add global exception handler
11. Verify schemas validate correctly

## Tasks / Subtasks

- [x] Create schemas directory with all model files
- [x] Define Pydantic models matching database schema
- [x] Create config.py with Settings class
- [x] Add CORS middleware to main.py
- [x] Add global exception handler
- [x] Test schema validation

## Dev Notes

**New files:**
- src/spendsense/schemas/*.py
- src/spendsense/config.py

## Dev Agent Record

### Context Reference

No context file provided - implemented based on story file and existing models.

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

**Implementation Plan:**
1. Created schemas directory structure
2. Implemented all Pydantic schemas with proper validation
3. Created config.py with Pydantic Settings
4. Updated main.py with CORS middleware and global exception handler
5. Added pydantic-settings dependency
6. Created comprehensive test suite
7. Verified all acceptance criteria

### Completion Notes List

- ✅ Created schemas directory with __init__.py
- ✅ Implemented UserCreate and UserResponse schemas with email validation
- ✅ Implemented AccountResponse schema for depository and credit accounts
- ✅ Implemented TransactionResponse schema with proper amount handling
- ✅ Implemented RecommendationResponse, EducationItemResponse, and RationaleResponse schemas
- ✅ All schemas use snake_case field names as required
- ✅ Dates serialized as ISO 8601 strings (with Z suffix)
- ✅ Currency amounts stored as integers (cents) with proper validation
- ✅ Created config.py with Pydantic Settings loading from environment
- ✅ Added CORS middleware to main.py allowing localhost:5173, :3000, and :4173
- ✅ Added global exception handler logging errors and returning generic 500 responses
- ✅ Added pydantic-settings==2.11.0 dependency to pyproject.toml
- ✅ Created comprehensive test suite (test_schemas.py) - all 8 tests passing
- ✅ Verified app imports successfully with all configurations loaded

### File List

**NEW:**
- src/spendsense/schemas/__init__.py
- src/spendsense/schemas/user.py
- src/spendsense/schemas/account.py
- src/spendsense/schemas/transaction.py
- src/spendsense/schemas/insight.py
- src/spendsense/config.py
- scripts/test_schemas.py

**MODIFIED:**
- src/spendsense/main.py (added CORS middleware, global exception handler, logging)
- pyproject.toml (added pydantic-settings dependency)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
| 2025-11-03 | Amelia (Dev Agent) | Complete implementation of all schemas, config, CORS, and exception handling |
