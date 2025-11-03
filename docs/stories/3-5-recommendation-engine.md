# Story 3.5: Recommendation Engine

Status: drafted

## Story

As a platform,
I want to combine persona assignment with content generation,
So that I can deliver complete personalized recommendations with rationales.

## Acceptance Criteria

1. Create `services/recommendations.py` module
2. Define `Recommendation` Pydantic model
3. Implement `generate_recommendations(db, user_id, generator, window_days)` async function
4. Process flow: assign_persona → generate_education → generate_rationale → build recommendations
5. Return list of recommendations with full traceability
6. Use dependency injection for generator
7. Add error handling
8. Support both 30d and 180d windows
9. Verify complete workflow
10. Test with synthetic users (<500ms target)

## Tasks / Subtasks

- [ ] Create services/recommendations.py
- [ ] Define Recommendation Pydantic model
- [ ] Implement generate_recommendations() async function
- [ ] Call assign_persona() for user
- [ ] Call generator.generate_education() for top 3 items
- [ ] For each item, call generator.generate_rationale()
- [ ] Build Recommendation objects
- [ ] Test complete pipeline

## Dev Notes

**Architecture:** Orchestrates persona + content + rationale. Complete explainability chain.

**New files:**
- src/spendsense/services/recommendations.py

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
