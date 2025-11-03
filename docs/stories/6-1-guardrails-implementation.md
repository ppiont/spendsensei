# Story 6.1: Guardrails Implementation

Status: drafted

## Story

As a platform,
I want to enforce ethical guidelines and tone standards,
So that all recommendations are respectful and appropriate.

## Acceptance Criteria

1. Create `utils/guardrails.py` module
2. Define `SHAME_PATTERNS` list with regex patterns
3. Implement `check_tone(text)` function
4. Implement `check_consent(user_consent)` function
5. Define `DISCLAIMER` constant
6. Add tone checking to rationale generation
7. Add disclaimer to all recommendations
8. Test with edge cases
9. Verify catches shaming language
10. Confirm all recommendations include disclaimer

## Tasks / Subtasks

- [ ] Create utils/guardrails.py
- [ ] Define shame patterns
- [ ] Implement check_tone()
- [ ] Implement check_consent()
- [ ] Add disclaimer constant
- [ ] Integrate with generation pipeline

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
