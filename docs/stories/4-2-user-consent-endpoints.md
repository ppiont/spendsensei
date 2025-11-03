# Story 4.2: User & Consent Endpoints

Status: drafted

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

- [ ] Create routers/users.py
- [ ] Implement POST /users endpoint
- [ ] Implement POST /consent endpoint
- [ ] Add error handling
- [ ] Register router in main.py
- [ ] Test with curl/Postman

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
