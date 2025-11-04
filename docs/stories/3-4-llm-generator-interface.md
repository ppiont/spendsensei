# Story 3.4: LLM Generator Interface

Status: done

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

- [x] Create generators/llm.py
- [x] Extend ContentGenerator base class
- [x] Add init with provider parameter
- [x] Implement stubs with NotImplementedError
- [x] Add comprehensive docstrings
- [x] Document future integration points

## Dev Notes

**Architecture:** Stub only - enables future AI without code refactoring. Same interface as TemplateGenerator.

**New files:**
- src/spendsense/generators/__init__.py
- src/spendsense/generators/base.py (created for Story 3.3 dependency)
- src/spendsense/generators/llm.py

## Dev Agent Record

### Implementation Summary

Successfully implemented LLMGenerator stub interface with comprehensive documentation for future AI integration:

1. Created generators module structure with __init__.py
2. Implemented base.py with ContentGenerator abstract class and Pydantic models (EducationItem, Rationale)
3. Implemented llm.py with LLMGenerator class extending ContentGenerator
4. Added __init__(provider, model) supporting "anthropic" and "openai" providers
5. Implemented generate_education() and generate_rationale() stubs with NotImplementedError
6. Added extensive docstrings covering:
   - API initialization examples for both Anthropic and OpenAI
   - Structured output implementation patterns
   - Guardrails integration examples
   - Expected input/output formats
   - Data validation requirements
7. Included PROMPT_TEMPLATES section as placeholder for future prompts
8. Documented swapping instructions in module docstring
9. Added comprehensive integration checklist covering API keys, testing, monitoring, and cost management
10. Verified class structure matches base.py interface exactly

All acceptance criteria met. The stub implementation enables future LLM integration without requiring code refactoring.

### Context Reference

- Story 3.3 (Template Generator) - created base.py as dependency
- ContentGenerator abstract interface matches future TemplateGenerator

### Agent Model Used

claude-sonnet-4-5-20250929

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
| 2025-11-03 | Dev Agent (claude-sonnet-4-5) | Implementation complete - LLMGenerator stub with comprehensive integration docs |
