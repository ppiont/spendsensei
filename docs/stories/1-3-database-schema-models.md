# Story 1.3: Database Schema & Models

Status: review

## Story

As a developer,
I want SQLAlchemy models for all entities with proper relationships,
So that I can persist and query financial data efficiently.

## Acceptance Criteria

1. Create `database.py` with async SQLAlchemy engine setup
2. Configure SQLite connection: `sqlite+aiosqlite:///data/spendsense.db`
3. Enable WAL mode in `init_db()` function
4. Create `Base` declarative base class
5. Implement models in separate files:
   - `models/user.py` - User (id, name, email, consent, created_at)
   - `models/account.py` - Account (id, user_id, type, subtype, balance, limit, apr, etc.)
   - `models/transaction.py` - Transaction (id, account_id, date, amount, merchant, category, pending)
   - `models/persona.py` - Persona (id, user_id, window, persona_type, confidence, assigned_at)
   - `models/content.py` - Content (id, type, title, summary, body, persona_tags, signal_tags, source)
6. Add proper indexes: `ix_transactions_account_id`, `ix_transactions_date`, `ix_txn_account_date`
7. Add foreign key relationships with `relationship()` back_populates
8. Create `get_db()` dependency for FastAPI routes
9. Verify `init_db()` successfully creates all tables
10. Test database creation runs without errors

## Tasks / Subtasks

- [x] **Task 1: Create database connection module** (AC: #1, #2, #3, #4)
  - [x] Create `src/spendsense/database.py` file
  - [x] Import SQLAlchemy async components (`create_async_engine`, `AsyncSession`, `declarative_base`)
  - [x] Define `DATABASE_URL = "sqlite+aiosqlite:///data/spendsense.db"`
  - [x] Create async engine with connection args for WAL mode
  - [x] Create `AsyncSessionLocal` factory with proper configuration
  - [x] Create `Base = declarative_base()` for ORM models
  - [x] Implement `init_db()` async function that:
    - Creates `data/` directory if it doesn't exist
    - Executes `PRAGMA journal_mode=WAL` on connection
    - Calls `Base.metadata.create_all()` to create tables
  - [x] Implement `get_db()` async generator dependency for FastAPI

- [x] **Task 2: Create User model** (AC: #5)
  - [x] Create `src/spendsense/models/__init__.py` (empty or with imports)
  - [x] Create `src/spendsense/models/user.py`
  - [x] Define `User` class extending `Base`
  - [x] Add table name: `__tablename__ = "users"`
  - [x] Define columns with `Mapped` type hints:
    - `id: Mapped[str]` (primary key, VARCHAR(50))
    - `name: Mapped[str]` (VARCHAR(200), not null)
    - `email: Mapped[str]` (VARCHAR(200), unique, not null)
    - `consent: Mapped[bool]` (default False)
    - `created_at: Mapped[datetime]` (not null)
  - [x] Add `__repr__()` method for debugging

- [x] **Task 3: Create Account model** (AC: #5)
  - [x] Create `src/spendsense/models/account.py`
  - [x] Define `Account` class extending `Base`
  - [x] Add table name: `__tablename__ = "accounts"`
  - [x] Define columns with `Mapped` type hints:
    - `id: Mapped[str]` (primary key, VARCHAR(50))
    - `user_id: Mapped[str]` (foreign key to users.id, VARCHAR(50))
    - `type: Mapped[str]` (VARCHAR(50)) - 'depository' or 'credit'
    - `subtype: Mapped[str]` (VARCHAR(50)) - 'checking', 'savings', 'credit_card'
    - `name: Mapped[str]` (VARCHAR(200))
    - `mask: Mapped[str]` (VARCHAR(4)) - last 4 digits
    - `balance: Mapped[int]` (INTEGER, in cents)
    - `limit: Mapped[Optional[int]]` (INTEGER, nullable, credit cards only)
    - `currency: Mapped[str]` (VARCHAR(3), default 'USD')
    - `apr: Mapped[Optional[float]]` (REAL, nullable, credit cards only)
    - `min_payment: Mapped[Optional[int]]` (INTEGER, nullable)
    - `is_overdue: Mapped[bool]` (default False)
  - [x] Add index on `user_id`: `Index('ix_accounts_user_id', 'user_id')`
  - [x] Add foreign key relationship: `user = relationship("User", back_populates="accounts")`
  - [x] Update User model to add: `accounts = relationship("Account", back_populates="user")`

- [x] **Task 4: Create Transaction model** (AC: #5, #6)
  - [x] Create `src/spendsense/models/transaction.py`
  - [x] Define `Transaction` class extending `Base`
  - [x] Add table name: `__tablename__ = "transactions"`
  - [x] Define columns with `Mapped` type hints:
    - `id: Mapped[str]` (primary key, VARCHAR(50))
    - `account_id: Mapped[str]` (foreign key to accounts.id, VARCHAR(50))
    - `date: Mapped[datetime]` (not null, indexed)
    - `amount: Mapped[int]` (INTEGER, in cents, positive = debit)
    - `merchant_name: Mapped[Optional[str]]` (VARCHAR(200), nullable)
    - `category: Mapped[str]` (VARCHAR(100)) - e.g., FOOD_AND_DRINK, INCOME
    - `pending: Mapped[bool]` (default False)
  - [x] Add indexes (critical for query performance):
    - `Index('ix_transactions_account_id', 'account_id')`
    - `Index('ix_transactions_date', 'date')`
    - `Index('ix_txn_account_date', 'account_id', 'date')` - composite for filtered queries
  - [x] Add foreign key relationship: `account = relationship("Account", back_populates="transactions")`
  - [x] Update Account model to add: `transactions = relationship("Transaction", back_populates="account")`

- [x] **Task 5: Create Persona model** (AC: #5)
  - [x] Create `src/spendsense/models/persona.py`
  - [x] Define `PersonaType` enum with values:
    - `high_utilization`
    - `variable_income`
    - `subscription_heavy`
    - `savings_builder`
    - `balanced`
  - [x] Define `Persona` class extending `Base`
  - [x] Add table name: `__tablename__ = "personas"`
  - [x] Define columns with `Mapped` type hints:
    - `id: Mapped[int]` (primary key, autoincrement)
    - `user_id: Mapped[str]` (foreign key to users.id, VARCHAR(50))
    - `window: Mapped[str]` (VARCHAR(10)) - '30d' or '180d'
    - `persona_type: Mapped[str]` (VARCHAR(50)) - use PersonaType enum values
    - `confidence: Mapped[float]` (REAL, 0.0-1.0)
    - `assigned_at: Mapped[datetime]` (not null)
  - [x] Add index on `user_id`: `Index('ix_personas_user_id', 'user_id')`
  - [x] Add foreign key relationship: `user = relationship("User", back_populates="personas")`
  - [x] Update User model to add: `personas = relationship("Persona", back_populates="user")`

- [x] **Task 6: Create Content model** (AC: #5)
  - [x] Create `src/spendsense/models/content.py`
  - [x] Define `Content` class extending `Base`
  - [x] Add table name: `__tablename__ = "content"`
  - [x] Define columns with `Mapped` type hints:
    - `id: Mapped[str]` (primary key, VARCHAR(50))
    - `type: Mapped[str]` (VARCHAR(50)) - 'article', 'video', 'tool'
    - `title: Mapped[str]` (VARCHAR(200))
    - `summary: Mapped[str]` (VARCHAR(500))
    - `body: Mapped[str]` (TEXT)
    - `persona_tags: Mapped[str]` (JSON stored as text, list of persona types)
    - `signal_tags: Mapped[str]` (JSON stored as text, list of signal names)
    - `source: Mapped[str]` (VARCHAR(50)) - 'template', 'llm', 'human'
    - `created_at: Mapped[datetime]` (not null)

- [x] **Task 7: Initialize and test database** (AC: #9, #10)
  - [x] Create `data/` directory in backend root if it doesn't exist
  - [x] Update `src/spendsense/main.py` to call `init_db()` on startup
  - [x] Add startup event handler:
    ```python
    @app.on_event("startup")
    async def startup_event():
        await init_db()
    ```
  - [x] Run the backend: `uv run uvicorn spendsense.main:app --reload`
  - [x] Verify `data/spendsense.db` is created
  - [x] Use SQLite CLI or DB browser to verify tables exist:
    - users, accounts, transactions, personas, content
  - [x] Verify indexes are created correctly
  - [x] Verify WAL mode is enabled: check for `.db-wal` and `.db-shm` files
  - [x] Test get_db() dependency works (can be tested in next story with first endpoint)

## Dev Notes

### Architecture Context

**From architecture.md:**
- SQLite with WAL (Write-Ahead Logging) mode for concurrent reads
- No migrations framework - use `create_all()` for schema
- SQLAlchemy 2.0 with async support (`AsyncSession`, `create_async_engine`)
- Store currency as integers (cents) not floats
- Store dates as datetime objects, serialize to ISO 8601 strings in API responses
- Use `Mapped` type hints for all columns (SQLAlchemy 2.0 syntax)
- Separate model files for organization (not monolithic models.py)

**Database connection pattern:**
```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite+aiosqlite:///data/spendsense.db"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Set to False in production
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Enable WAL mode
        await conn.execute("PRAGMA journal_mode=WAL")
```

**Model conventions:**
- Table names: plural, snake_case (users, accounts, transactions)
- Column names: snake_case (user_id, created_at, persona_type)
- Primary keys: VARCHAR(50) for UUIDs, INTEGER for auto-increment
- Foreign keys: {table}_id pattern (user_id, account_id)
- Indexes: ix_{table}_{column} pattern
- Relationships: use `back_populates` for bidirectional access

**PersonaType enum values (from PRD):**
- high_utilization - Credit card usage ≥50%
- variable_income - Irregular payroll patterns
- subscription_heavy - Multiple recurring merchants
- savings_builder - Growing savings accounts
- balanced - Default, no specific patterns

**Transaction amount convention (CRITICAL):**
- Positive integer = debit (money out, expenses)
- Negative integer = credit (money in, income)
- Example: Income transaction = -300000 (= -$3,000.00)
- Example: Purchase = 5000 (= $50.00)

### Project Structure Notes

**Expected directory structure after this story:**
```
spendsense-backend/
├── data/
│   └── spendsense.db         # Created on first run
├── src/
│   └── spendsense/
│       ├── __init__.py
│       ├── main.py           # Updated with startup event
│       ├── database.py       # New: DB connection
│       └── models/           # New directory
│           ├── __init__.py
│           ├── user.py       # New
│           ├── account.py    # New
│           ├── transaction.py # New
│           ├── persona.py    # New
│           └── content.py    # New
```

**Future additions (subsequent stories):**
- Story 1.4: `services/synthetic_data.py` - generates faker data
- Story 2.x: `services/features.py` - signal detection functions
- Story 3.x: `services/personas.py`, `generators/` - persona assignment and content
- Story 4.x: `routers/`, `schemas/` - API endpoints

### Testing Strategy

**Manual verification steps:**
1. Start backend: `cd spendsense-backend && uv run uvicorn spendsense.main:app --reload`
2. Check console for "Application startup complete" message
3. Verify files created:
   - `data/spendsense.db`
   - `data/spendsense.db-wal` (indicates WAL mode active)
   - `data/spendsense.db-shm`
4. Use SQLite CLI to inspect schema:
   ```bash
   sqlite3 data/spendsense.db
   .tables  # Should show: users accounts transactions personas content
   .schema users  # Verify columns and constraints
   PRAGMA journal_mode;  # Should return: wal
   ```
5. Check for any errors in console during startup
6. Verify no import errors when importing models in Python REPL:
   ```python
   from spendsense.models.user import User
   from spendsense.models.account import Account
   from spendsense.models.transaction import Transaction
   ```

**No automated tests required** per PRD constraints.

### References

- [Source: docs/PRD.md#Technology Stack - Database]
- [Source: docs/architecture.md#Database Schema]
- [Source: docs/architecture.md#Backend Naming Conventions (Python)]
- [Source: docs/architecture.md#Implementation Patterns]
- [Source: docs/epics.md#Story 1.3: Database Schema & Models]

### Learnings from Previous Story

**From Story 1-2-frontend-project-setup (Status: done)**

Previous story not yet documented - Story 1-2 file does not exist. This is the third story in Epic 1, following backend setup (1-1) and frontend setup (1-2).

**Expected foundation from Stories 1-1 and 1-2:**
- Backend project initialized with uv and Python 3.13
- FastAPI basic app structure exists in `src/spendsense/main.py`
- Frontend project initialized with SvelteKit and Svelte 5
- Development servers can start successfully
- Linting configured (ruff for backend, biome for frontend)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

**Implementation Plan:**
1. Created src/spendsense/ directory structure with models/ subdirectory
2. Implemented database.py with async SQLAlchemy engine and WAL mode configuration
3. Created all 5 model files with proper SQLAlchemy 2.0 `Mapped` type hints
4. Added foreign key relationships with `back_populates` for bidirectional access
5. Configured performance indexes on transactions table
6. Added greenlet dependency (required for SQLAlchemy async operations)
7. Updated pyproject.toml with build system configuration for src layout
8. Tested database initialization and verified all tables/indexes created successfully

### Completion Notes List

- ✅ Database connection module created with async SQLAlchemy engine
- ✅ WAL mode enabled for concurrent read performance (verified with PRAGMA journal_mode)
- ✅ All 5 models implemented: User, Account, Transaction, Persona, Content
- ✅ PersonaType enum created with all 5 persona types
- ✅ Foreign key relationships configured with bidirectional back_populates
- ✅ Performance indexes added: ix_transactions_account_id, ix_transactions_date, ix_txn_account_date
- ✅ get_db() async dependency created for FastAPI routes
- ✅ Database tested: all 5 tables created, WAL mode active, API endpoint responding
- ✅ Added greenlet>=3.2.4 dependency (required for SQLAlchemy async)
- ✅ Configured pyproject.toml with hatchling build system for src layout

**Testing Results:**
- Database file created: `data/spendsense.db`
- All 5 tables present: users, accounts, transactions, personas, content
- All 5 indexes created successfully
- WAL mode confirmed active
- FastAPI server starts without errors
- API endpoint returns {"message": "Hello SpendSense"}

### File List

**NEW:**
- src/spendsense/__init__.py
- src/spendsense/database.py
- src/spendsense/main.py
- src/spendsense/models/__init__.py
- src/spendsense/models/user.py
- src/spendsense/models/account.py
- src/spendsense/models/transaction.py
- src/spendsense/models/persona.py
- src/spendsense/models/content.py
- data/spendsense.db (created at runtime)

**MODIFIED:**
- pyproject.toml (added greenlet dependency, build system configuration)

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
| 2025-11-03 | Dev Agent (claude-sonnet-4-5) | Implemented all database models, indexes, and initialization logic. Story complete and ready for review. |
