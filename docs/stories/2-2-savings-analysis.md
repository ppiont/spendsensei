# Story 2.2: Savings Analysis

Status: review

## Story

As a platform,
I want to analyze net savings inflow and emergency fund coverage,
So that I can identify users building financial resilience.

## Acceptance Criteria

1. Implement `analyze_savings(accounts, transactions, window_days)` function
2. Filter accounts by subtype: "savings", "money_market", "cd"
3. Calculate total savings balance across all savings accounts
4. Calculate net inflow to savings accounts (credits - debits)
5. Estimate monthly savings inflow rate
6. Calculate monthly expenses from non-savings accounts
7. Calculate emergency fund coverage (months of expenses covered)
8. Calculate savings growth rate (net inflow / total balance)
9. Return savings data structure with:
   - Total savings balance
   - Net inflow and monthly inflow rate
   - Growth rate percentage
   - Emergency fund months
10. Handle edge cases: no savings accounts, zero balance, negative inflow

## Tasks / Subtasks

- [x] **Task 1: Implement savings account filtering** (AC: #1, #2, #3)
  - [x] Add `analyze_savings(accounts: list, transactions: list, window_days: int) -> dict` to features.py
  - [x] Filter accounts where subtype in ["savings", "money_market", "cd"]
  - [x] Sum balance across all savings accounts to get total_savings_balance
  - [x] Store savings account IDs for transaction filtering

- [x] **Task 2: Calculate net savings inflow** (AC: #4, #5)
  - [x] Filter transactions to savings accounts only (use account IDs from Task 1)
  - [x] Filter by date within window_days
  - [x] Calculate net inflow: sum(credits) - sum(debits)
    - Credits: transactions with amount < 0 (money in)
    - Debits: transactions with amount > 0 (money out)
  - [x] Estimate monthly inflow rate: net_inflow / (window_days / 30)
  - [x] Handle negative inflow (withdrawals exceed deposits)

- [x] **Task 3: Calculate monthly expenses** (AC: #6)
  - [x] Filter transactions to non-savings accounts
  - [x] Filter by date within window_days
  - [x] Exclude INCOME category transactions
  - [x] Sum all debit transactions (amount > 0)
  - [x] Calculate monthly expenses: total_debits / (window_days / 30)

- [x] **Task 4: Calculate emergency fund and growth rate** (AC: #7, #8)
  - [x] Emergency fund coverage: total_savings_balance / monthly_expenses
  - [x] Handle division by zero if monthly_expenses == 0
  - [x] Growth rate: (net_inflow / total_savings_balance) * 100 if balance > 0
  - [x] Return 0 for growth rate if balance is 0

- [x] **Task 5: Build savings data structure** (AC: #9)
  - [x] Create return dictionary:
    ```python
    {
      "total_balance": int,           # Total savings balance in cents
      "net_inflow": int,              # Net inflow in cents
      "monthly_inflow": int,          # Estimated monthly rate in cents
      "growth_rate": float,           # Percentage (e.g., 2.5 for 2.5%)
      "emergency_fund_months": float  # Months of expenses covered
    }
    ```
  - [x] Ensure all amounts in cents (integers)
  - [x] Round percentages to 2 decimal places

- [x] **Task 6: Handle edge cases** (AC: #10)
  - [x] If no savings accounts: return all zeros
  - [x] If total_balance == 0: return zeros for growth_rate, emergency_fund_months
  - [x] If monthly_expenses == 0: return float('inf') or special value for emergency_fund_months
  - [x] If net_inflow < 0: return negative growth rate
  - [x] Test with users having no savings accounts

- [x] **Task 7: Update BehaviorSignals class**
  - [x] Add savings field to BehaviorSignals dataclass
  - [x] Initialize as empty dict: `{}`
  - [x] Document expected structure in docstring

- [x] **Task 8: Test with synthetic data**
  - [x] Load test users with savings accounts
  - [x] Call analyze_savings() with 30-day and 180-day windows
  - [x] Verify calculations:
    - Total balance sums correctly
    - Net inflow accounts for credits and debits
    - Monthly inflow extrapolated correctly
    - Emergency fund months calculated properly
  - [x] Test edge cases with print statements

## Dev Notes

### Architecture Context

**From architecture.md:**
- Transaction amounts in cents (positive = debit, negative = credit)
- Negative amount = credit = money INTO account
- Use type hints for function parameters
- On-demand computation (no caching)

**Savings Analysis Logic:**
1. Identify savings accounts by subtype (savings, money_market, cd)
2. Calculate total balance across savings accounts
3. Analyze transaction flow:
   - Credits (negative amounts): money deposited
   - Debits (positive amounts): money withdrawn
   - Net inflow = |credits| - debits
4. Extrapolate monthly rate based on window_days
5. Calculate emergency fund: balance / monthly_expenses
6. Calculate growth rate: inflow / balance

**Key Formulas:**
```python
# Net inflow (credits are negative, so negate them)
credits = sum(abs(t.amount) for t in savings_txns if t.amount < 0)
debits = sum(t.amount for t in savings_txns if t.amount > 0)
net_inflow = credits - debits

# Monthly rate
monthly_inflow = net_inflow / (window_days / 30)

# Emergency fund (months of expenses covered)
emergency_fund_months = total_balance / monthly_expenses

# Growth rate (percentage)
growth_rate = (net_inflow / total_balance) * 100
```

### Project Structure Notes

**Modified files:**
- `src/spendsense/services/features.py` - Add analyze_savings() function and update BehaviorSignals

**Expected structure:**
```python
@dataclass
class BehaviorSignals:
    subscriptions: dict  # From Story 2.1
    savings: dict        # New in this story
```

### Testing Strategy

**Manual verification:**
1. Create test script: `scripts/test_savings_analysis.py`
2. Load users with diverse account types
3. Test user WITH savings accounts:
   - Verify total balance calculation
   - Check net inflow (deposits - withdrawals)
   - Validate monthly inflow extrapolation
   - Confirm emergency fund calculation
   - Check growth rate percentage
4. Test user WITHOUT savings accounts:
   - Should return all zeros
5. Test edge cases:
   - Zero balance
   - Negative inflow (withdrawals)
   - Zero expenses (divide by zero)

### References

- [Source: docs/epics.md#Story 2.2: Savings Analysis]
- [Source: docs/architecture.md#Transaction Amount Convention]
- [Source: docs/PRD.md#Behavioral Signal: Savings Pattern]

### Learnings from Previous Story

**From Story 2-1-subscription-detection (Status: drafted)**

- **BehaviorSignals Class**: Created in features.py with subscriptions field
- **Features Module**: Located at `src/spendsense/services/features.py`
- **Pattern Established**: Functions accept lists/dicts, not ORM objects
- **Return Structure**: Detailed dictionaries with named fields
- **Edge Case Handling**: Return empty/zero structures when insufficient data
- **Testing Approach**: Load synthetic data, test with diverse users, verify calculations

**Use established patterns:**
- Add analyze_savings() to same features.py module
- Follow same function signature pattern: (data, data, window_days)
- Return structured dict with named fields
- Handle edge cases gracefully with zeros/empty values
- Update BehaviorSignals dataclass to include savings field

[Source: stories/2-1-subscription-detection.md]

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

N/A

### Completion Notes List

Implemented complete savings analysis feature with all acceptance criteria:

1. Created analyze_savings() function in features.py that:
   - Filters savings accounts by subtype (savings, money_market, cd)
   - Calculates total savings balance across all accounts
   - Computes net inflow (credits - debits) for savings accounts
   - Estimates monthly inflow rate based on window_days
   - Calculates monthly expenses from non-savings accounts
   - Computes emergency fund coverage in months
   - Calculates growth rate percentage

2. Updated BehaviorSignals dataclass to include savings field initialized as empty dict

3. Created comprehensive test script (test_savings_analysis.py) that:
   - Loads data from SQLite database
   - Tests with real user having savings accounts
   - Verifies all calculations (balance, inflow, growth rate, emergency fund)
   - Tests edge cases (no savings, empty transactions, zero balance)
   - All tests pass successfully

4. Test results show proper functionality:
   - Total balance calculation: PASS
   - Net inflow calculation: PASS
   - Monthly inflow extrapolation: PASS
   - Growth rate calculation: PASS
   - Emergency fund calculation: PASS
   - All edge cases: PASS

### File List

- spendsense-backend/src/spendsense/services/features.py (modified - added analyze_savings function and updated imports)
- spendsense-backend/scripts/test_savings_analysis.py (created - comprehensive test script)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
| 2025-11-03 | Claude DEV | Implementation complete - all tasks and acceptance criteria met |
