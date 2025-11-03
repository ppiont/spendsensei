# Story 4.4: Insights Endpoint

Status: drafted

## Story

As a developer,
I want an insights endpoint that returns personalized recommendations,
So that the frontend can display financial education.

## Acceptance Criteria

1. Create `routers/insights.py` module
2. Initialize TemplateGenerator as module-level singleton
3. Implement `GET /insights/{user_id}` endpoint with window parameter
4. Return RecommendationResponse with persona, confidence, recommendations
5. Add 404 error if user not found
6. Add 500 error with logging if generation fails
7. Register router with FastAPI app
8. Test with synthetic users
9. Verify response time <5 seconds
10. Check OpenAPI docs show window parameter options

## Tasks / Subtasks

- [ ] Create routers/insights.py
- [ ] Initialize TemplateGenerator singleton
- [ ] Implement GET /insights/{user_id}
- [ ] Call generate_recommendations() pipeline
- [ ] Add error handling
- [ ] Register router
- [ ] Test with synthetic users

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
