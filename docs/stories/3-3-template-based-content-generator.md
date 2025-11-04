# Story 3.3: Template-Based Content Generator

Status: complete

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

- [x] Create generators/base.py with abstract ContentGenerator
- [x] Define Pydantic models (EducationItem, Rationale)
- [x] Create generators/template.py with TemplateGenerator
- [x] Implement generate_education() - load YAML, filter, score
- [x] Implement generate_rationale() - format templates with data
- [x] Test with synthetic users

## Dev Notes

**Architecture:** Abstract base class enables future LLM swap. Template strings use .format() syntax.

**New files:**
- src/spendsense/generators/base.py
- src/spendsense/generators/template.py

## Dev Agent Record

### Implementation Summary

Successfully implemented template-based content generator with abstract base class and concrete TemplateGenerator implementation.

**Files Created:**
- `/src/spendsense/generators/base.py` - Abstract ContentGenerator class with EducationItem and Rationale Pydantic models
- `/src/spendsense/generators/template.py` - TemplateGenerator implementation with catalog loading and relevance scoring
- `/src/spendsense/generators/__init__.py` - Module exports
- `/scripts/test_template_generator.py` - Comprehensive test suite for all personas
- `/scripts/demo_template_integration.py` - Integration demo showing API usage

**Key Features:**
1. **Abstract Base Class**: Defines interface for future LLM-based generators
2. **Pydantic Models**: Type-safe EducationItem and Rationale models with validation
3. **YAML Catalog Loading**: Loads content from data/content_catalog.yaml with caching
4. **Signal Tag Extraction**: Converts BehaviorSignals into specific signal tags (e.g., 'high_utilization_80')
5. **Relevance Scoring**: Base 0.5 for persona match + 0.1 per signal match (capped at 1.0)
6. **Education Generation**: Filters, scores, and returns top N relevant content items
7. **Rationale Generation**: Creates explainable text with concrete data points per persona

**Relevance Algorithm:**
- Base score: 0.5 if persona matches
- Signal bonus: +0.1 per matching signal tag (max +0.5)
- Final score capped at 1.0
- Items sorted by relevance (highest first)

**Test Results:**
All 6 test scenarios passed:
- High Utilization: 3 items (0.70 relevance), rationale includes utilization %, balance, and flags
- Variable Income: 3 items (0.60-0.70), rationale includes median gap and buffer months
- Subscription Heavy: 3 items (0.60), rationale includes count and monthly spend
- Savings Builder: 3 items (0.60-0.70), rationale includes growth rate and inflow
- Balanced: 3 items (0.60-0.70), rationale adapts to available signals
- Relevance scoring verified correct sorting and range

**Rationale Examples Include Concrete Data:**
- Credit utilization: "85.0%", "$8,500.00 of your $10,000.00 total credit limit"
- Income: "median gap of 60 days", "$4,500.00 average payment", "0.8 months buffer"
- Subscriptions: "8 active recurring subscriptions totaling $150.00", "15.0% of spending"
- Savings: "growing at 5.0%", "$500.00 monthly inflow"

All acceptance criteria met and verified through automated testing.

### Context Reference

Dependencies successfully integrated:
- Story 3.1 (Persona Assignment) - Uses persona_type for filtering
- Story 3.2 (Content Catalog) - Loads from data/content_catalog.yaml
- BehaviorSignals from features.py - Extracts signal tags for scoring

### Agent Model Used

claude-sonnet-4-5-20250929

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
| 2025-11-03 | Claude (Dev Agent) | Complete implementation with tests |
