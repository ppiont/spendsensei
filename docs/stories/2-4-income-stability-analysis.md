# Story 2.4: Income Stability Analysis

Status: review

## Story

As a platform,
I want to detect payroll frequency and income variability,
So that I can identify users with irregular income patterns.

## Acceptance Criteria

1. Implement `analyze_income(transactions, window_days)` function
2. Filter transactions by category: "INCOME"
3. Calculate gaps between income transactions (in days)
4. Determine median gap and classify frequency:
   - 13-16 days = "biweekly"
   - 28-32 days = "monthly"
   - 6-8 days = "weekly"
   - Other = "variable"
5. Calculate average income amount (absolute value of negative amounts)
6. Calculate income standard deviation
7. Calculate coefficient of variation (std / mean)
8. Classify stability: "stable" if CV < 0.15, else "variable"
9. Calculate cash flow buffer (income - expenses) / expenses in months
10. Return income data structure with:
    - Frequency classification
    - Stability classification
    - Average income amount
    - Coefficient of variation
    - Cash flow buffer in months
    - Median gap in days
11. Handle edge cases: <2 income transactions, zero income

## Tasks / Subtasks

- [x] **Task 1: Filter and extract income transactions** (AC: #1, #2, #3)
  - [x] Add `analyze_income(transactions: list, window_days: int) -> dict` to features.py
  - [x] Filter transactions where category == "INCOME"
  - [x] Sort by date ascending
  - [x] Calculate gaps: [date[i+1] - date[i] in days for each consecutive pair]
  - [x] Calculate median gap using statistics.median()

- [x] **Task 2: Classify income frequency** (AC: #4)
  - [x] Check median gap against thresholds:
    ```python
    if 13 <= median_gap <= 16: "biweekly"
    elif 28 <= median_gap <= 32: "monthly"
    elif 6 <= median_gap <= 8: "weekly"
    else: "variable"
    ```
  - [x] Return "unknown" if <2 income transactions

- [x] **Task 3: Calculate income statistics** (AC: #5, #6, #7, #8)
  - [x] Extract income amounts (take absolute value since INCOME is negative)
  - [x] Calculate average: statistics.mean(amounts)
  - [x] Calculate standard deviation: statistics.stdev(amounts)
  - [x] Calculate coefficient of variation: stdev / mean
  - [x] Classify stability:
    - "stable" if CV < 0.15
    - "variable" if CV >= 0.15

- [x] **Task 4: Calculate cash flow buffer** (AC: #9)
  - [x] Sum total income (absolute value of INCOME transactions)
  - [x] Sum total expenses (all positive transaction amounts, exclude INCOME)
  - [x] Calculate net cash flow: income - expenses
  - [x] Calculate monthly expenses: expenses / (window_days / 30)
  - [x] Buffer in months: net_cash_flow / monthly_expenses
  - [x] Handle negative buffer (spending exceeds income)

- [x] **Task 5: Build income data structure** (AC: #10)
  - [x] Create return dictionary:
    ```python
    {
      "frequency": str,              # "biweekly", "monthly", "weekly", "variable", "unknown"
      "stability": str,              # "stable", "variable", "unknown"
      "average_amount": int,         # Average income in cents
      "coefficient_variation": float, # CV ratio
      "buffer_months": float,        # Cash flow buffer in months
      "median_gap_days": int         # Median days between income
    }
    ```

- [x] **Task 6: Handle edge cases** (AC: #11)
  - [x] <2 income transactions: return "unknown" for frequency/stability
  - [x] Zero income: return zeros and "unknown"
  - [x] Insufficient data for stdev: return "unknown" stability
  - [x] Test with users having irregular income

- [x] **Task 7: Update BehaviorSignals and test**
  - [x] Add income field to BehaviorSignals dataclass
  - [x] Test with synthetic data
  - [x] Verify frequency classification works
  - [x] Validate CV and stability classification

## Dev Notes

### Architecture Context

**From architecture.md:**
- INCOME transactions are negative (credits)
- Use absolute value for calculations
- Coefficient of variation measures income volatility
- Buffer can be negative (deficit)

**Income Analysis Logic:**
```python
# Income amounts (negate negative INCOME values)
amounts = [abs(t.amount) for t in txns if t.category == "INCOME"]

# Gaps between income dates
gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
median_gap = statistics.median(gaps)

# Coefficient of variation
cv = statistics.stdev(amounts) / statistics.mean(amounts)
stability = "stable" if cv < 0.15 else "variable"
```

### Project Structure Notes

**Modified files:**
- `src/spendsense/services/features.py` - Add analyze_income() and update BehaviorSignals

### Testing Strategy

**Manual verification:**
1. Test biweekly, monthly, weekly patterns
2. Test variable income users
3. Verify CV calculation and stability classification
4. Test buffer calculation (positive and negative)

### References

- [Source: docs/epics.md#Story 2.4: Income Stability Analysis]
- [Source: docs/architecture.md#Transaction Amount Convention]

### Learnings from Previous Story

**From Story 2-3-credit-utilization-analysis (Status: drafted)**

- BehaviorSignals growing: subscriptions, savings, credit, now income
- Pattern established for classification with thresholds
- Edge cases: return "unknown" or zeros when insufficient data
- Use standard library (statistics module) for calculations

[Source: stories/2-3-credit-utilization-analysis.md]

## Dev Agent Record

### Context Reference

No context file available - proceeded with story file only.

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

**Implementation Plan:**
1. Created features.py with BehaviorSignals dataclass (foundation for all behavioral signals)
2. Implemented analyze_income() function with comprehensive income analysis logic
3. Added all required fields to BehaviorSignals (subscriptions, savings, credit, income)
4. Handled edge cases: insufficient data, zero income, division by zero
5. Created comprehensive test suite to verify all acceptance criteria

**Technical Decisions:**
- Used statistics module for median, mean, and stdev calculations
- Implemented CV-based stability classification (threshold: 0.15)
- Cash flow buffer can be negative (deficit scenario)
- Rounded CV to 4 decimals, buffer to 2 decimals for precision
- Used __post_init__ for BehaviorSignals to initialize empty dicts

### Completion Notes List

- Successfully implemented analyze_income() function with all 11 acceptance criteria
- BehaviorSignals dataclass created with all 4 signal fields (subscriptions, savings, credit, income)
- All edge cases handled correctly: <2 income transactions, zero income, insufficient stdev data
- Frequency classification working for biweekly (13-16 days), monthly (28-32 days), weekly (6-8 days), and variable
- Stability classification based on coefficient of variation (CV < 0.15 = stable)
- Cash flow buffer calculation handles both surplus and deficit scenarios
- Comprehensive test suite created and all tests passing
- Tested with synthetic data from Story 1.4

### File List

- src/spendsense/services/features.py (created)
- scripts/test_income_analysis.py (created)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
| 2025-11-03 | Claude (DEV) | Implemented income stability analysis with all acceptance criteria |
