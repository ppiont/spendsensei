# Story 2.4: Income Stability Analysis

Status: ready-for-dev

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

- [ ] **Task 1: Filter and extract income transactions** (AC: #1, #2, #3)
  - [ ] Add `analyze_income(transactions: list, window_days: int) -> dict` to features.py
  - [ ] Filter transactions where category == "INCOME"
  - [ ] Sort by date ascending
  - [ ] Calculate gaps: [date[i+1] - date[i] in days for each consecutive pair]
  - [ ] Calculate median gap using statistics.median()

- [ ] **Task 2: Classify income frequency** (AC: #4)
  - [ ] Check median gap against thresholds:
    ```python
    if 13 <= median_gap <= 16: "biweekly"
    elif 28 <= median_gap <= 32: "monthly"
    elif 6 <= median_gap <= 8: "weekly"
    else: "variable"
    ```
  - [ ] Return "unknown" if <2 income transactions

- [ ] **Task 3: Calculate income statistics** (AC: #5, #6, #7, #8)
  - [ ] Extract income amounts (take absolute value since INCOME is negative)
  - [ ] Calculate average: statistics.mean(amounts)
  - [ ] Calculate standard deviation: statistics.stdev(amounts)
  - [ ] Calculate coefficient of variation: stdev / mean
  - [ ] Classify stability:
    - "stable" if CV < 0.15
    - "variable" if CV >= 0.15

- [ ] **Task 4: Calculate cash flow buffer** (AC: #9)
  - [ ] Sum total income (absolute value of INCOME transactions)
  - [ ] Sum total expenses (all positive transaction amounts, exclude INCOME)
  - [ ] Calculate net cash flow: income - expenses
  - [ ] Calculate monthly expenses: expenses / (window_days / 30)
  - [ ] Buffer in months: net_cash_flow / monthly_expenses
  - [ ] Handle negative buffer (spending exceeds income)

- [ ] **Task 5: Build income data structure** (AC: #10)
  - [ ] Create return dictionary:
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

- [ ] **Task 6: Handle edge cases** (AC: #11)
  - [ ] <2 income transactions: return "unknown" for frequency/stability
  - [ ] Zero income: return zeros and "unknown"
  - [ ] Insufficient data for stdev: return "unknown" stability
  - [ ] Test with users having irregular income

- [ ] **Task 7: Update BehaviorSignals and test**
  - [ ] Add income field to BehaviorSignals dataclass
  - [ ] Test with synthetic data
  - [ ] Verify frequency classification works
  - [ ] Validate CV and stability classification

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
