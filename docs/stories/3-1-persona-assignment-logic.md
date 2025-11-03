# Story 3.1: Persona Assignment Logic

Status: drafted

## Story

As a platform,
I want to assign financial personas based on behavioral signals,
So that users receive education tailored to their financial situation.

## Acceptance Criteria

1. Create `services/personas.py` module
2. Define `PERSONA_PRIORITY` list with order: high_utilization, variable_income, subscription_heavy, savings_builder, balanced
3. Implement `assign_persona(db, user_id, window_days)` async function
4. Create matching functions for each persona:
   - `matches_high_utilization()`: utilization ≥50% OR interest charges OR overdue
   - `matches_variable_income()`: median pay gap >45 days AND buffer <1 month
   - `matches_subscription_heavy()`: ≥3 subscriptions AND (monthly spend ≥$50 OR ≥10% of total)
   - `matches_savings_builder()`: growth rate ≥2% OR monthly inflow ≥$200, AND utilization <30%
5. Check personas in priority order (highest urgency first)
6. Return matched persona type, confidence score, and signals
7. Default to "balanced" persona if no matches
8. Confidence scores: high_utilization=0.95, variable_income=0.90, subscription_heavy=0.85, savings_builder=0.80, balanced=0.60
9. Save persona assignment to database (personas table)
10. Verify with synthetic data (should classify diverse users correctly)

## Tasks / Subtasks

- [ ] **Task 1: Create personas module with priority list** (AC: #1, #2)
  - [ ] Create `src/spendsense/services/personas.py`
  - [ ] Define PERSONA_PRIORITY constant:
    ```python
    PERSONA_PRIORITY = [
        "high_utilization",
        "variable_income",
        "subscription_heavy",
        "savings_builder",
        "balanced"
    ]
    ```
  - [ ] Import BehaviorSignals, compute_signals

- [ ] **Task 2: Implement persona matching functions** (AC: #4)
  - [ ] `matches_high_utilization(signals: BehaviorSignals) -> bool`
  - [ ] `matches_variable_income(signals: BehaviorSignals) -> bool`
  - [ ] `matches_subscription_heavy(signals: BehaviorSignals) -> bool`
  - [ ] `matches_savings_builder(signals: BehaviorSignals) -> bool`
  - [ ] Each function checks specific signal thresholds from PRD

- [ ] **Task 3: Implement assign_persona function** (AC: #3, #5, #6, #7, #8)
  - [ ] `async def assign_persona(db: AsyncSession, user_id: str, window_days: int) -> dict`
  - [ ] Call compute_signals() to get all signals
  - [ ] Iterate through PERSONA_PRIORITY
  - [ ] For each persona, call matching function
  - [ ] Return first match with confidence score
  - [ ] Default to "balanced" with confidence 0.60 if no matches

- [ ] **Task 4: Save persona to database** (AC: #9)
  - [ ] Create Persona ORM instance
  - [ ] Set user_id, window, persona_type, confidence, assigned_at
  - [ ] Save to database
  - [ ] Return persona data dict

- [ ] **Task 5: Test with synthetic data** (AC: #10)
  - [ ] Test diverse users
  - [ ] Verify high utilization users matched correctly
  - [ ] Verify variable income users matched
  - [ ] Verify balanced default works
  - [ ] Check priority order (urgent issues first)

## Dev Notes

### Architecture Context

**From architecture.md:**
- Priority order ensures urgent financial issues flagged first
- Only one persona per user per window
- Confidence reflects classification certainty

**Persona Matching Logic:**
```python
# Priority order (check in sequence, first match wins)
def assign_persona(signals):
    if matches_high_utilization(signals):
        return ("high_utilization", 0.95, signals)
    elif matches_variable_income(signals):
        return ("variable_income", 0.90, signals)
    # ... etc
    else:
        return ("balanced", 0.60, signals)
```

### Project Structure Notes

**New files:**
- `src/spendsense/services/personas.py`

**Exports:**
- `from spendsense.services.personas import assign_persona, PERSONA_PRIORITY`

### Testing Strategy

**Manual verification:**
1. Test each persona type matches correctly
2. Verify priority order (high urgency first)
3. Check balanced default
4. Validate confidence scores

### References

- [Source: docs/epics.md#Story 3.1: Persona Assignment Logic]
- [Source: docs/PRD.md#Persona Types and Matching]

### Learnings from Previous Story

**From Story 2-5-signal-computation-service (Status: drafted)**

- compute_signals() returns complete BehaviorSignals object
- Signals available: subscriptions, savings, credit, income
- Use signals to match personas
- Async database operations established

[Source: stories/2-5-signal-computation-service.md]

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
