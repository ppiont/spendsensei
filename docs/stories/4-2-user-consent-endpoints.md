# Story 4.2: User & Consent Endpoints

Status: review

## Story

As a developer,
I want user creation and consent management endpoints,
So that the frontend can register users and track consent.

## Acceptance Criteria

1. Create `routers/users.py` module
2. Implement `POST /users` endpoint - create new user
3. Implement `POST /consent` endpoint - update consent
4. Add HTTPException for user not found (404)
5. Add Pydantic validation for email format
6. Use async database session from get_db()
7. Register router with FastAPI app
8. Test endpoints manually
9. Verify OpenAPI docs generated
10. Confirm consent field updates in database

## Tasks / Subtasks

- [x] Create routers/users.py
- [x] Implement POST /users endpoint
- [x] Implement POST /consent endpoint
- [x] Add error handling
- [x] Register router in main.py
- [x] Test with curl/Postman

## Dev Agent Record

### Context Reference

No context file provided - implemented based on story file and existing code patterns.

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

**Implementation Plan:**
1. Created routers directory structure
2. Implemented users router with POST /users and POST /consent endpoints
3. Added proper error handling (404 for not found, 500 for errors)
4. Used async database sessions with get_db() dependency
5. Email validation handled by Pydantic EmailStr in UserCreate schema
6. Registered router in main.py
7. Created test script to verify database operations
8. Verified OpenAPI docs generation

### Completion Notes List

- ✅ Created routers/__init__.py and routers/users.py
- ✅ Implemented POST /users endpoint with UUID generation and timestamp
- ✅ Implemented POST /users/consent endpoint for updating consent status
- ✅ Added HTTPException 404 when user not found
- ✅ Added HTTPException 500 for database errors with rollback
- ✅ Email validation works via Pydantic EmailStr type in UserCreate schema
- ✅ Used async database sessions from get_db() dependency
- ✅ Registered users_router in main.py with prefix="/users"
- ✅ Created test_user_endpoints.py - all 7 tests passing
- ✅ Verified OpenAPI docs available at /docs with both endpoints
- ✅ Confirmed consent field updates persist to database

### File List

**NEW:**
- src/spendsense/routers/__init__.py
- src/spendsense/routers/users.py
- scripts/test_user_endpoints.py

**MODIFIED:**
- src/spendsense/main.py (registered users_router)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
| 2025-11-03 | Amelia (Dev Agent) | Complete implementation of user and consent endpoints |
