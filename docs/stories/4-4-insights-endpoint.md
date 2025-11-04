# Story 4.4: Insights Endpoint

Status: review

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

- [x] Create routers/insights.py
- [x] Initialize TemplateGenerator singleton
- [x] Implement GET /insights/{user_id}
- [x] Call generate_recommendations() pipeline
- [x] Add error handling
- [x] Register router
- [x] Test with synthetic users

## Dev Agent Record

### Context Reference

No context file provided - implemented based on story file and existing Epic 3 recommendation engine.

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

**Implementation Plan:**
1. Created routers/insights.py with GET /insights/{user_id}?window=30 endpoint
2. Initialized TemplateGenerator as module-level singleton for efficiency
3. Integrated complete recommendation pipeline from Epic 3
4. Added 404 error handling when user not found
5. Added 500 error handling with logging when generation fails
6. Registered insights router in main.py
7. Created comprehensive test suite covering all acceptance criteria
8. All 6 tests passing with excellent performance (~0.02s average)

### Completion Notes List

- ✅ Created routers/insights.py with GET /insights/{user_id} endpoint
- ✅ Initialized TemplateGenerator as module-level singleton (created once at module load)
- ✅ Implemented window parameter with Query annotation (1-365 days, default 30)
- ✅ Integrated complete recommendation pipeline: personas → content generation → rationales
- ✅ Returns list[RecommendationResponse] with persona, confidence, and 3 recommendations
- ✅ Added 404 error handling when user not found (validated before processing)
- ✅ Added 500 error handling with logging when generation fails
- ✅ Registered insights_router in main.py with proper imports
- ✅ Updated routers/__init__.py to export insights_router
- ✅ Created comprehensive test suite (test_insights_endpoint.py)
- ✅ All 6 tests passing: insights generation, window parameters, persona assignment, 404 handling, performance, structure validation
- ✅ Performance excellent: avg 0.02s (~50x faster than 5s target!)
- ✅ Tested with both 30-day and 180-day windows (only supported values)
- ✅ Recommendations include all required fields: content, rationale, persona, confidence
- ✅ OpenAPI docs automatically include window query parameter via FastAPI Query annotations

### File List

**NEW:**
- src/spendsense/routers/insights.py
- scripts/test_insights_endpoint.py

**MODIFIED:**
- src/spendsense/routers/__init__.py (added insights_router export)
- src/spendsense/main.py (registered insights router)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
| 2025-11-03 | Amelia (Dev Agent) | Complete implementation of insights endpoint with recommendation pipeline integration |
