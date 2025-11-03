# Story 2.1: Subscription Detection

Status: ready-for-dev

## Story

As a platform,
I want to detect recurring subscription merchants from transaction patterns,
So that I can identify users with high subscription spending.

## Acceptance Criteria

1. Create `services/features.py` module with `BehaviorSignals` class
2. Implement `detect_subscriptions(transactions, window_days)` function
3. Group transactions by merchant_name (debits only)
4. Identify recurring merchants with ≥3 occurrences
5. Calculate average gap between transactions for each merchant
6. Classify as "monthly" (28-35 days) or "weekly" (6-8 days) cadence
7. Calculate total recurring spend and percentage of total spending
8. Return subscription data structure with:
   - List of recurring merchants with frequency and average amount
   - Count of recurring merchants
   - Monthly recurring spend estimate
   - Percentage of total spending
9. Handle edge cases: <3 transactions, irregular gaps, no subscriptions
10. Verify detection works with synthetic data (should find Netflix-like patterns)

## Tasks / Subtasks

- [ ] **Task 1: Create features module with BehaviorSignals class** (AC: #1)
  - [ ] Create `src/spendsense/services/features.py`
  - [ ] Import necessary modules: dataclasses, datetime, typing
  - [ ] Define `@dataclass` BehaviorSignals with subscriptions dict field
  - [ ] Initialize subscriptions as empty dict: `{}`

- [ ] **Task 2: Implement subscription detection function** (AC: #2, #3, #4, #5, #6)
  - [ ] Create `detect_subscriptions(transactions: list, window_days: int) -> dict` function
  - [ ] Filter transactions to debits only (amount > 0)
  - [ ] Exclude INCOME category transactions
  - [ ] Group transactions by merchant_name
  - [ ] For each merchant, check if ≥3 occurrences
  - [ ] Calculate gaps between transaction dates (in days)
  - [ ] Determine average gap: sum(gaps) / len(gaps)
  - [ ] Classify cadence:
    - Monthly: 28-35 days (±7 day tolerance)
    - Weekly: 6-8 days (±2 day tolerance)
    - Otherwise: irregular (not classified as subscription)
  - [ ] Calculate average transaction amount for each recurring merchant

- [ ] **Task 3: Calculate subscription spending metrics** (AC: #7, #8)
  - [ ] Sum total recurring spend across all identified subscriptions
  - [ ] Calculate total spending from all debit transactions
  - [ ] Calculate percentage: (recurring_spend / total_spend) * 100
  - [ ] Estimate monthly recurring spend based on cadence:
    - Monthly subscriptions: use average amount
    - Weekly subscriptions: multiply by 4.33 (weeks/month)
  - [ ] Build subscription data structure:
    ```python
    {
      "recurring_merchants": [
        {"name": str, "frequency": str, "avg_amount": int, "count": int}
      ],
      "count": int,
      "monthly_recurring_spend": int,
      "percentage_of_spending": float
    }
    ```
  - [ ] Return complete structure

- [ ] **Task 4: Handle edge cases** (AC: #9)
  - [ ] If <3 transactions total: return empty subscription data (count=0)
  - [ ] If no merchants with ≥3 occurrences: return empty data
  - [ ] If irregular gaps (not monthly/weekly): exclude from recurring list
  - [ ] If no debits (all income): return count=0
  - [ ] Ensure percentage is 0.0 if total_spend is 0

- [ ] **Task 5: Test with synthetic data** (AC: #10)
  - [ ] Load users.json from Story 1.4
  - [ ] Filter transactions for one user with diverse merchants
  - [ ] Call detect_subscriptions() with 180-day window
  - [ ] Verify identifies recurring merchants (e.g., Netflix-like patterns)
  - [ ] Check monthly vs weekly classification is correct
  - [ ] Verify amounts in cents (positive debits)
  - [ ] Confirm percentage calculation is reasonable

## Dev Notes

### Architecture Context

**From architecture.md:**
- Use Python 3.13 with type hints
- snake_case for function names and variables
- Transaction amounts in cents (positive = debit, negative = credit)
- On-demand computation (no caching)
- Target <200ms per user for signal computation

**Key Patterns:**
```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict

@dataclass
class BehaviorSignals:
    subscriptions: dict
    # Additional signal fields to be added in future stories
```

**Subscription Detection Logic:**
1. Filter debits only (amount > 0) and exclude INCOME
2. Group by merchant_name
3. For merchants with ≥3 transactions:
   - Calculate gaps: [date[i+1] - date[i] for each pair]
   - Average gap in days
   - Classify: monthly (28-35), weekly (6-8), else irregular
4. Aggregate results into subscription structure

**Gap Tolerance:**
- Monthly: 28-35 days (allows ±7 day variance)
- Weekly: 6-8 days (allows ±2 day variance)
- Irregular patterns excluded from recurring list

### Project Structure Notes

**Expected directory structure after this story:**
```
spendsense-backend/
├── src/
│   └── spendsense/
│       ├── services/
│       │   ├── __init__.py
│       │   ├── synthetic_data.py  # Existing from Story 1.4
│       │   └── features.py        # New: Behavioral signal detection
│       ├── models/                # Existing from Story 1.3
│       └── database.py            # Existing from Story 1.3
```

**New exports:**
- `from spendsense.services.features import BehaviorSignals, detect_subscriptions`

### Testing Strategy

**Manual verification steps:**
1. Create test script: `scripts/test_subscription_detection.py`
2. Load synthetic data from Story 1.4
3. Select user with diverse transaction history
4. Call `detect_subscriptions(user_transactions, 180)`
5. Print results: recurring merchants, count, monthly spend, percentage
6. Verify:
   - Merchants with ≥3 occurrences identified
   - Cadence classification correct (monthly vs weekly)
   - Amounts in cents
   - Percentage calculation accurate
   - Edge cases handled (empty, <3 txns)

**No automated tests required** per PRD constraints.

### References

- [Source: docs/epics.md#Story 2.1: Subscription Detection]
- [Source: docs/architecture.md#Transaction Amount Convention]
- [Source: docs/PRD.md#Behavioral Signal: Subscription Detection]

### Learnings from Previous Story

**From Story 1-4-synthetic-data-generator (Status: review)**

- **Data Available**: 50 users with 104 accounts and 6,092 transactions generated
- **Data Location**: `data/users.json` contains synthetic dataset
- **Database Populated**: All data loaded into SQLite database at `data/spendsense.db`
- **Transaction Categories**: FOOD_AND_DRINK, GENERAL_MERCHANDISE, TRANSPORTATION, ENTERTAINMENT, UTILITIES, HEALTHCARE, INCOME
- **Transaction Convention**: Positive = debit (expenses), Negative = credit (income) - critical for this story
- **Merchant Names**: Generated using `fake.company()` - realistic names for pattern detection
- **Date Range**: Transactions span last 180 days
- **Services Directory**: Already created at `src/spendsense/services/` with __init__.py

**Key files to import from:**
- `from spendsense.models.transaction import Transaction`
- `from spendsense.database import get_db, AsyncSessionLocal`

**Use established patterns:**
- snake_case for function names
- Type hints for parameters and return values
- Dataclasses for structured data
- Functions accept lists/dicts, not ORM objects (flexibility)

[Source: stories/1-4-synthetic-data-generator.md#Dev-Agent-Record]

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
