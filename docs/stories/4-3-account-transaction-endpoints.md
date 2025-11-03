# Story 4.3: Account & Transaction Endpoints

Status: drafted

## Story

As a developer,
I want to retrieve user accounts and transactions via API,
So that the frontend can display financial data.

## Acceptance Criteria

1. Create `routers/accounts.py` module
2. Implement `GET /accounts/{user_id}` endpoint
3. Create `routers/transactions.py` module
4. Implement `GET /transactions/{user_id}` endpoint with pagination
5. Add 404 error if user not found
6. Register both routers with FastAPI app
7. Test with synthetic data
8. Verify pagination works
9. Confirm OpenAPI docs include query parameters
10. Check response time <100ms

## Tasks / Subtasks

- [ ] Create routers/accounts.py and transactions.py
- [ ] Implement GET /accounts/{user_id}
- [ ] Implement GET /transactions/{user_id} with limit/offset
- [ ] Add pagination support
- [ ] Register routers
- [ ] Test with synthetic data

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
