# Story 3.1: Persona Assignment Logic

Status: done

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

- [x] **Task 1: Create personas module with priority list** (AC: #1, #2)
  - [x] Create `src/spendsense/services/personas.py`
  - [x] Define PERSONA_PRIORITY constant:
    ```python
    PERSONA_PRIORITY = [
        "high_utilization",
        "variable_income",
        "subscription_heavy",
        "savings_builder",
        "balanced"
    ]
    ```
  - [x] Import BehaviorSignals, compute_signals

- [x] **Task 2: Implement persona matching functions** (AC: #4)
  - [x] `matches_high_utilization(signals: BehaviorSignals) -> bool`
  - [x] `matches_variable_income(signals: BehaviorSignals) -> bool`
  - [x] `matches_subscription_heavy(signals: BehaviorSignals) -> bool`
  - [x] `matches_savings_builder(signals: BehaviorSignals) -> bool`
  - [x] Each function checks specific signal thresholds from PRD

- [x] **Task 3: Implement assign_persona function** (AC: #3, #5, #6, #7, #8)
  - [x] `async def assign_persona(db: AsyncSession, user_id: str, window_days: int) -> dict`
  - [x] Call compute_signals() to get all signals
  - [x] Iterate through PERSONA_PRIORITY
  - [x] For each persona, call matching function
  - [x] Return first match with confidence score
  - [x] Default to "balanced" with confidence 0.60 if no matches

- [x] **Task 4: Save persona to database** (AC: #9)
  - [x] Create Persona ORM instance
  - [x] Set user_id, window, persona_type, confidence, assigned_at
  - [x] Save to database
  - [x] Return persona data dict

- [x] **Task 5: Test with synthetic data** (AC: #10)
  - [x] Test diverse users
  - [x] Verify high utilization users matched correctly
  - [x] Verify variable income users matched
  - [x] Verify balanced default works
  - [x] Check priority order (urgent issues first)

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

claude-sonnet-4-5-20250929

### Debug Log References

N/A

### Completion Notes List

**Implementation Summary (2025-11-03):**

Successfully implemented Story 3.1: Persona Assignment Logic. All acceptance criteria met:

1. Created `src/spendsense/services/personas.py` module with:
   - PERSONA_PRIORITY list defining order: high_utilization, variable_income, subscription_heavy, savings_builder, balanced
   - CONFIDENCE_SCORES dict mapping each persona to its confidence level (0.60-0.95)

2. Implemented matching functions for each persona type:
   - `matches_high_utilization()`: Checks utilization ≥50% OR interest charges OR overdue
   - `matches_variable_income()`: Checks median pay gap >45 days AND buffer <1 month
   - `matches_subscription_heavy()`: Checks ≥3 subscriptions AND (monthly spend ≥$50 OR ≥10% of total)
   - `matches_savings_builder()`: Checks growth rate ≥2% OR monthly inflow ≥$200, AND utilization <30%

3. Implemented `assign_persona()` async function:
   - Calls `compute_signals()` to get all behavioral signals
   - Iterates through PERSONA_PRIORITY checking each persona match
   - Returns first match with appropriate confidence score
   - Defaults to "balanced" persona (confidence 0.60) if no matches

4. Database integration:
   - Saves persona assignment to personas table with user_id, window, persona_type, confidence, assigned_at
   - Successfully commits and refreshes persona instances
   - Verified database persistence with SQLite queries

5. Testing with synthetic data:
   - Created `scripts/test_persona_assignment.py` test script
   - Tested with 5 diverse users from synthetic data
   - Verified correct classification: 3 high_utilization, 1 savings_builder, 1 balanced
   - All validation checks passed (3/3):
     - All users received persona assignments
     - All confidence scores in valid range (0.60-0.95)
     - Diverse personas assigned (3 different types)
   - Confirmed priority order works correctly (urgent issues flagged first)

**Key Implementation Details:**

- Proper handling of edge cases (no data, zero values)
- Conversion of dollar amounts: $50 = 5000 cents, $200 = 20000 cents
- Logging at INFO level for assignment tracking
- Clean separation of concerns (matching functions are pure functions)
- Async database operations with proper session management

**Test Results:**

The test demonstrated correct persona classification:
- Users with high credit utilization (≥50%) were flagged as high_utilization (highest priority)
- Users with savings growth ≥2% and low utilization were classified as savings_builder
- Users with no specific patterns defaulted to balanced persona
- No variable_income or subscription_heavy personas found in the test sample (due to synthetic data patterns)

All acceptance criteria verified and working as specified in the PRD.

### File List

**New Files Created:**
- `/Users/ppiont/repos/gauntlet/spendsensei/spendsense-backend/src/spendsense/services/personas.py` - Persona assignment logic module
- `/Users/ppiont/repos/gauntlet/spendsensei/spendsense-backend/scripts/test_persona_assignment.py` - Integration test with synthetic data
- `/Users/ppiont/repos/gauntlet/spendsensei/spendsense-backend/scripts/test_persona_matching.py` - Unit tests for matching functions

**Files Modified:**
- `/Users/ppiont/repos/gauntlet/spendsensei/docs/stories/3-1-persona-assignment-logic.md` - Updated with completion status

**Test Coverage:**

Unit Tests (test_persona_matching.py):
- 6/6 tests passed
- Verified all threshold values and edge cases for each matching function
- Confirmed priority order and confidence scores

Integration Tests (test_persona_assignment.py):
- Tested with 5 real users from synthetic database
- 3/3 validation checks passed
- Verified end-to-end flow including database persistence

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
