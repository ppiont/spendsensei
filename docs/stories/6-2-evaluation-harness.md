# Story 6.2: Evaluation Harness

Status: drafted

## Story

As a developer,
I want to measure system performance against PRD requirements,
So that I can verify quality and identify issues.

## Acceptance Criteria

1. Create evaluation script `scripts/evaluate.py`
2. Measure Coverage (% users with persona + ≥3 signals)
3. Measure Explainability (% recommendations with rationales)
4. Measure Latency (average recommendation generation time)
5. Measure Auditability (% with complete decision trace)
6. Run evaluation against all synthetic users
7. Generate metrics JSON file
8. Calculate summary statistics
9. Print results to console
10. Verify meets targets: 100% coverage, 100% explainability, <5s latency

## Tasks / Subtasks

- [ ] Create scripts/evaluate.py
- [ ] Implement coverage measurement
- [ ] Implement explainability measurement
- [ ] Implement latency measurement
- [ ] Run against all users
- [ ] Generate metrics report

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
