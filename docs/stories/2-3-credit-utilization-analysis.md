# Story 2.3: Credit Utilization Analysis

Status: review

## Story

As a platform,
I want to calculate credit card utilization and identify high-risk patterns,
So that I can recommend credit management education.

## Acceptance Criteria

1. Implement `analyze_credit(accounts, transactions)` function
2. Filter accounts by type: "credit"
3. Calculate overall utilization: total_balance / total_limit
4. Generate utilization flags:
   - "high_utilization_80" if ≥80%
   - "high_utilization_50" if ≥50%
   - "moderate_utilization_30" if ≥30%
5. Check for overdue accounts (is_overdue field)
6. Estimate monthly interest charges: (balance × APR / 100) / 12
7. Add "interest_charges" flag if interest > 0
8. Return credit data structure with:
   - Overall utilization percentage
   - Total balance and total limit
   - Monthly interest estimate
   - List of flags
   - Per-card utilization breakdown
9. Handle edge cases: no credit cards, zero limit, missing APR
10. Verify with synthetic data (should detect high utilization users)

## Tasks / Subtasks

- [x] **Task 1: Implement credit account filtering and utilization** (AC: #1, #2, #3)
  - [x] Add `analyze_credit(accounts: list, transactions: list) -> dict` to features.py
  - [x] Filter accounts where type == "credit"
  - [x] Sum total_balance across all credit accounts
  - [x] Sum total_limit across all credit accounts
  - [x] Calculate overall utilization: (total_balance / total_limit) * 100
  - [x] Handle zero limit edge case

- [x] **Task 2: Generate utilization flags** (AC: #4)
  - [x] Check utilization percentage against thresholds
  - [x] Priority order: 80% → 50% → 30%
  - [x] Add only ONE flag (highest threshold met)
  - [x] Flags: "high_utilization_80", "high_utilization_50", "moderate_utilization_30"

- [x] **Task 3: Calculate interest charges and check overdue** (AC: #5, #6, #7)
  - [x] For each credit account, calculate monthly interest: (balance * APR / 100) / 12
  - [x] Sum total monthly interest across all cards
  - [x] Add "interest_charges" flag if total interest > 0
  - [x] Check is_overdue field on any account, add "overdue" flag if true

- [x] **Task 4: Build credit data structure** (AC: #8)
  - [x] Create return dictionary:
    ```python
    {
      "overall_utilization": float,     # Percentage
      "total_balance": int,             # In cents
      "total_limit": int,               # In cents
      "monthly_interest": int,          # Estimated monthly interest in cents
      "flags": list,                    # ["high_utilization_80", etc.]
      "per_card": [                     # Individual card details
        {"account_id": str, "utilization": float, "balance": int, "limit": int}
      ]
    }
    ```

- [x] **Task 5: Handle edge cases** (AC: #9)
  - [x] No credit cards: return zeros and empty lists
  - [x] Zero limit: set utilization to 0
  - [x] Missing APR: default to 0 for interest calculation
  - [x] Test with users having no credit accounts

- [x] **Task 6: Update BehaviorSignals and test** (AC: #10)
  - [x] Add credit field to BehaviorSignals dataclass
  - [x] Test with synthetic data users
  - [x] Verify high utilization users are detected
  - [x] Validate interest calculations

## Dev Notes

### Architecture Context

**From architecture.md:**
- Credit card accounts have: balance, limit, APR, is_overdue fields
- Utilization = (balance / limit) * 100
- Interest simplified: assumes balance carries month-to-month
- Only one utilization flag per analysis (highest threshold)

**Credit Analysis Logic:**
```python
# Utilization priority
if utilization >= 80:
    flags.append("high_utilization_80")
elif utilization >= 50:
    flags.append("high_utilization_50")
elif utilization >= 30:
    flags.append("moderate_utilization_30")

# Monthly interest (simplified)
monthly_interest = sum((card.balance * card.apr / 100) / 12 for card in cards)
```

### Project Structure Notes

**Modified files:**
- `src/spendsense/services/features.py` - Add analyze_credit() and update BehaviorSignals

### Testing Strategy

**Manual verification:**
1. Test high utilization users (≥80%, ≥50%, ≥30%)
2. Test users with no credit cards
3. Test interest calculation accuracy
4. Verify per-card breakdown

### References

- [Source: docs/epics.md#Story 2.3: Credit Utilization Analysis]
- [Source: docs/architecture.md#Credit Card Model]

### Learnings from Previous Story

**From Story 2-2-savings-analysis (Status: drafted)**

- BehaviorSignals class being built incrementally (subscriptions, savings, now credit)
- Pattern: filter accounts → calculate metrics → return structured dict
- Edge case handling: return zeros/empty when no relevant accounts
- Functions accept lists, return dicts

[Source: stories/2-2-savings-analysis.md]

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

**Implementation Plan:**
- Added `analyze_credit()` function to features.py module
- BehaviorSignals class already had credit field defined (from Story 2.4)
- Implemented credit account filtering, utilization calculation, and flag generation
- Added per-card breakdown with individual utilization percentages
- Calculated monthly interest using formula: (balance * APR / 100) / 12
- Handled all edge cases: no credit accounts, zero limit, missing APR

**Testing Approach:**
- Created test script: scripts/test_credit_analysis.py
- Tested with synthetic data from Story 1.4
- Verified high utilization detection (found 4 users with ≥80% utilization)
- Validated interest calculation accuracy
- Confirmed edge case handling for users without credit accounts

### Completion Notes List

**Story 2.3 Implementation Complete (2025-11-03)**

Successfully implemented credit utilization analysis functionality with all acceptance criteria met:

1. **analyze_credit() Function**: Added to features.py with complete credit analysis logic
2. **Account Filtering**: Filters accounts by type "credit" correctly
3. **Utilization Calculation**: Computes overall utilization as (total_balance / total_limit) * 100
4. **Flag Generation**: Generates proper flags with priority: high_utilization_80, high_utilization_50, moderate_utilization_30
5. **Overdue Detection**: Checks is_overdue field and adds "overdue" flag
6. **Interest Calculation**: Estimates monthly interest charges using APR formula
7. **Complete Data Structure**: Returns all required fields including per-card breakdown
8. **Edge Cases**: Handles no credit accounts, zero limit, and missing APR gracefully
9. **BehaviorSignals Class**: Credit field already present in dataclass structure
10. **Verification**: Tested with synthetic data, detected 4 high-utilization users correctly

**Test Results:**
- 6 users with credit accounts analyzed
- High utilization (≥80%): 4 users
- Medium utilization (50-79%): 2 users
- Edge case test passed: no credit accounts returns zeros
- Interest calculation verified: manual vs computed match

**Key Implementation Details:**
- Used dict.get() with defaults for robust field access
- Rounded utilization to 2 decimal places for precision
- Rounded monthly interest to nearest cent (int)
- Flag order ensures only highest threshold flag is added
- Per-card utilization includes individual account details

### File List

- `src/spendsense/services/features.py` - Added analyze_credit() function
- `scripts/test_credit_analysis.py` - Created test script for verification

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
| 2025-11-03 | Dev Agent (Claude Sonnet 4.5) | Implemented analyze_credit() function, tested with synthetic data, all ACs verified |
