# Story 2.5: Signal Computation Service

Status: ready-for-dev

## Story

As a platform,
I want a unified service that computes all behavioral signals for a user,
So that API endpoints can get comprehensive financial insights in one call.

## Acceptance Criteria

1. Implement `compute_signals(db, user_id, window_days)` async function
2. Calculate cutoff date: current date - window_days
3. Query user's accounts from database
4. Query user's transactions within time window
5. Call all signal detection functions:
   - `detect_subscriptions()`
   - `analyze_savings()`
   - `analyze_credit()`
   - `analyze_income()`
6. Populate `BehaviorSignals` object with all results
7. Return complete signals object
8. Add error handling for database queries
9. Verify function works with both 30-day and 180-day windows
10. Test with synthetic users (should complete in <200ms per user)

## Tasks / Subtasks

- [ ] **Task 1: Implement async signal computation function** (AC: #1, #2, #3, #4)
  - [ ] Add `async def compute_signals(db: AsyncSession, user_id: str, window_days: int) -> BehaviorSignals` to features.py
  - [ ] Import datetime, timedelta
  - [ ] Calculate cutoff_date: datetime.now() - timedelta(days=window_days)
  - [ ] Query accounts: `select(Account).where(Account.user_id == user_id)`
  - [ ] Query transactions: `select(Transaction).join(Account).where(Account.user_id == user_id, Transaction.date >= cutoff_date)`
  - [ ] Convert ORM results to lists of dicts for signal functions

- [ ] **Task 2: Call all signal detection functions** (AC: #5)
  - [ ] Call `detect_subscriptions(transactions, window_days)` → subscriptions_data
  - [ ] Call `analyze_savings(accounts, transactions, window_days)` → savings_data
  - [ ] Call `analyze_credit(accounts, transactions)` → credit_data
  - [ ] Call `analyze_income(transactions, window_days)` → income_data

- [ ] **Task 3: Populate BehaviorSignals object** (AC: #6, #7)
  - [ ] Create BehaviorSignals instance
  - [ ] Assign subscriptions_data to .subscriptions
  - [ ] Assign savings_data to .savings
  - [ ] Assign credit_data to .credit
  - [ ] Assign income_data to .income
  - [ ] Return complete BehaviorSignals object

- [ ] **Task 4: Add error handling** (AC: #8)
  - [ ] Wrap database queries in try/except
  - [ ] Handle user not found → raise HTTPException(404)
  - [ ] Handle database errors → log and raise HTTPException(500)
  - [ ] Ensure all signal functions handle empty data gracefully

- [ ] **Task 5: Test with different windows** (AC: #9)
  - [ ] Test with window_days=30 (1 month analysis)
  - [ ] Test with window_days=180 (6 month analysis)
  - [ ] Verify cutoff date calculation correct
  - [ ] Confirm only transactions within window are included

- [ ] **Task 6: Performance testing** (AC: #10)
  - [ ] Time execution with `time.time()` before/after
  - [ ] Test with multiple synthetic users
  - [ ] Verify <200ms per user (target from architecture)
  - [ ] Check database query efficiency (use indexes)
  - [ ] Profile if needed and optimize slow queries

- [ ] **Task 7: Finalize BehaviorSignals dataclass**
  - [ ] Ensure all fields defined:
    ```python
    @dataclass
    class BehaviorSignals:
        subscriptions: dict
        savings: dict
        credit: dict
        income: dict
    ```
  - [ ] Add docstring with field descriptions
  - [ ] Add __post_init__ if needed for validation

## Dev Notes

### Architecture Context

**From architecture.md:**
- Use async SQLAlchemy queries
- On-demand computation (no caching)
- Target <200ms per user
- Use indexed queries (transactions indexed on account_id, date)

**Query Pattern:**
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

async def compute_signals(db: AsyncSession, user_id: str, window_days: int):
    cutoff = datetime.now() - timedelta(days=window_days)

    # Query accounts
    accounts_result = await db.execute(
        select(Account).where(Account.user_id == user_id)
    )
    accounts = accounts_result.scalars().all()

    # Query transactions with join
    txns_result = await db.execute(
        select(Transaction)
        .join(Account)
        .where(Account.user_id == user_id, Transaction.date >= cutoff)
    )
    transactions = txns_result.scalars().all()
```

### Project Structure Notes

**Modified files:**
- `src/spendsense/services/features.py` - Add compute_signals() async function
- Complete BehaviorSignals dataclass with all fields

**This is the orchestration layer** - ties together all signal detection from Stories 2.1-2.4

### Testing Strategy

**Manual verification:**
1. Create test script: `scripts/test_signal_computation.py`
2. Test with multiple users
3. Verify all signals populated
4. Time execution to ensure <200ms
5. Test both 30d and 180d windows

### References

- [Source: docs/epics.md#Story 2.5: Signal Computation Service]
- [Source: docs/architecture.md#Signal Computation]

### Learnings from Previous Story

**From Story 2-4-income-stability-analysis (Status: drafted)**

- All 4 signal functions ready: detect_subscriptions, analyze_savings, analyze_credit, analyze_income
- BehaviorSignals has 4 fields: subscriptions, savings, credit, income
- Functions accept lists/dicts, return structured dicts
- Now need async orchestration layer to query DB and call all functions

[Source: stories/2-4-income-stability-analysis.md]

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

**Implementation Plan:**
1. Add async compute_signals() function to features.py
2. Import AsyncSession from sqlalchemy.ext.asyncio
3. Import Account and Transaction models
4. Calculate cutoff_date using datetime.now() - timedelta(days=window_days)
5. Query accounts for user with await db.execute(select(Account).where(Account.user_id == user_id))
6. Query transactions with join: select(Transaction).join(Account).where(Account.user_id == user_id, Transaction.date >= cutoff_date)
7. Convert ORM objects to list of dicts for signal functions
8. Call all 4 signal functions in sequence
9. Populate BehaviorSignals object
10. Add comprehensive error handling for database operations
11. Test with both 30-day and 180-day windows
12. Verify performance <200ms per user

### Completion Notes List

### File List

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
