# Story 3.4: LLM Generator Interface

Status: drafted

## Story

As a platform,
I want an LLM generator interface for future AI integration,
So that I can optionally swap template-based content for AI-generated content.

## Acceptance Criteria

1. Create `generators/llm.py` with `LLMGenerator` class
2. Extend `ContentGenerator` abstract base class
3. Add `__init__(provider, model)` with provider options
4. Implement method signatures with NotImplementedError
5. Document in docstrings how to add AI integration
6. Add comments for API initialization
7. Include placeholder for prompt templates
8. Document swapping instructions
9. Verify class structure matches base.py
10. Stub only - no actual implementation

## Tasks / Subtasks

- [ ] Create generators/llm.py
- [ ] Extend ContentGenerator base class
- [ ] Add init with provider parameter
- [ ] Implement stubs with NotImplementedError
- [ ] Add comprehensive docstrings
- [ ] Document future integration points

## Dev Notes

**Architecture:** Stub only - enables future AI without code refactoring. Same interface as TemplateGenerator.

**New files:**
- src/spendsense/generators/llm.py

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
