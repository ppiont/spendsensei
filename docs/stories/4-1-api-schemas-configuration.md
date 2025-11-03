# Story 4.1: API Schemas & Configuration

Status: drafted

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

- [ ] Create schemas directory with all model files
- [ ] Define Pydantic models matching database schema
- [ ] Create config.py with Settings class
- [ ] Add CORS middleware to main.py
- [ ] Add global exception handler
- [ ] Test schema validation

## Dev Notes

**New files:**
- src/spendsense/schemas/*.py
- src/spendsense/config.py

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
