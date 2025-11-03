# Story 3.3: Template-Based Content Generator

Status: drafted

## Story

As a platform,
I want to generate personalized recommendations from template-based content,
So that I can deliver explainable insights without requiring AI APIs.

## Acceptance Criteria

1. Create `generators/base.py` with abstract `ContentGenerator` class
2. Define `EducationItem` Pydantic model
3. Define `Rationale` Pydantic model
4. Define abstract methods: `generate_education()` and `generate_rationale()`
5. Create `generators/template.py` with `TemplateGenerator` implementation
6. Implement `generate_education()` - load catalog, filter, score, return top 3
7. Implement `generate_rationale()` - template strings with signal data
8. Create `_calculate_relevance()` helper
9. Verify rationales include concrete data points
10. Test with synthetic users

## Tasks / Subtasks

- [ ] Create generators/base.py with abstract ContentGenerator
- [ ] Define Pydantic models (EducationItem, Rationale)
- [ ] Create generators/template.py with TemplateGenerator
- [ ] Implement generate_education() - load YAML, filter, score
- [ ] Implement generate_rationale() - format templates with data
- [ ] Test with synthetic users

## Dev Notes

**Architecture:** Abstract base class enables future LLM swap. Template strings use .format() syntax.

**New files:**
- src/spendsense/generators/base.py
- src/spendsense/generators/template.py

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
