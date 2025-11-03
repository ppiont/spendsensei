# SpendSense Product Requirements Document
## Streamlined Implementation Guide (2024-2025)

---

## Executive Summary

**SpendSense is a financial behavior analysis platform that detects patterns from synthetic transaction data and delivers personalized financial education.** The system uses Python 3.13 + FastAPI for the backend, Svelte 5 + SvelteKit for the frontend, and SQLite for data storage. The architecture is AI-agnostic, allowing optional LLM integration without code refactoring.

**Key Constraints:**
- **No live Plaid integration** - synthetic data generated with `faker`
- **No LLM required** - template-based content with optional AI swap
- **No caching layer** - direct database queries only
- **No test framework** - linting only (ruff for Python, biome for JS/TS)
- **Local-first** - runs on laptop, no external dependencies

**Target:** 50-100 synthetic users, <5 second response time, 100% explainability

---

## Technology Stack

### Backend
- **Python 3.13** - Latest stable release
- **FastAPI 0.115+** - Async API framework
- **SQLAlchemy 2.0+** - Modern ORM with async support
- **SQLite** - Single-file database with WAL mode
- **Pydantic v2** - Data validation
- **uv** - Dependency management (10-100x faster than pip)
- **faker** - Synthetic data generation
- **ruff** - Linting and formatting
- **No migrations** - Use `create_all()` for fresh schema

### Frontend
- **Svelte 5** - Runes-based reactivity ($state, $derived, $effect)
- **SvelteKit 2.18+** - Full-stack framework
- **TypeScript 5** - Type safety
- **Vite 5** - Build tool
- **Tailwind CSS v4** - Utility-first styling
- **Biome** - Linting and formatting

### Infrastructure
- **SQLite with WAL mode** - Concurrent reads
- **No Redis/caching** - Keep it simple
- **Docker (optional)** - For deployment only

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Svelte 5 Frontend                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Dashboard   │  │ Transactions │  │   Insights   │     │
│  │    +page     │  │    +page     │  │    +page     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                                │
│                     API Client (fetch)                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routers    │  │   Services   │  │  Generators  │     │
│  │  /users      │  │  Analytics   │  │  Template    │     │
│  │  /accounts   │  │  Personas    │  │  (or LLM)    │     │
│  │  /insights   │  │  Recommend   │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                                │
│                     SQLAlchemy ORM                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   SQLite (WAL)   │
                    │  - Users         │
                    │  - Accounts      │
                    │  - Transactions  │
                    │  - Personas      │
                    │  - Content       │
                    └──────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Content Generator (Pluggable)                  │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │ TemplateGenerator│   OR     │   LLMGenerator   │        │
│  │  - Jinja2 temps  │          │  - Anthropic     │        │
│  │  - Static YAML   │          │  - OpenAI        │        │
│  │  - Default       │          │  - Optional      │        │
│  └──────────────────┘          └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

### Backend Structure

```
spendsense-backend/
├── pyproject.toml              # uv config + dependencies
├── .python-version             # 3.13
├── src/
│   └── spendsense/
│       ├── main.py             # FastAPI app entry
│       ├── config.py           # Settings with Pydantic
│       ├── database.py         # SQLAlchemy setup
│       │
│       ├── models/             # SQLAlchemy ORM models
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── account.py
│       │   ├── transaction.py
│       │   ├── persona.py
│       │   └── content.py
│       │
│       ├── schemas/            # Pydantic request/response
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── account.py
│       │   ├── transaction.py
│       │   └── insight.py
│       │
│       ├── routers/            # API endpoints
│       │   ├── __init__.py
│       │   ├── users.py
│       │   ├── accounts.py
│       │   ├── transactions.py
│       │   └── insights.py
│       │
│       ├── services/           # Business logic
│       │   ├── __init__.py
│       │   ├── synthetic_data.py   # Faker generator
│       │   ├── features.py         # Signal detection
│       │   ├── personas.py         # Assignment logic
│       │   └── recommendations.py  # Rec engine
│       │
│       ├── generators/         # Content generation
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract interface
│       │   ├── template.py     # Default (no AI)
│       │   └── llm.py          # Optional AI (future)
│       │
│       └── utils/
│           ├── __init__.py
│           └── guardrails.py   # Consent, eligibility, tone
│
├── data/
│   ├── content_catalog.yaml    # Static education content
│   └── users.json              # Generated synthetic data
│
├── docs/
│   ├── DECISION_LOG.md
│   ├── SCHEMA.md
│   └── LIMITATIONS.md
│
└── ruff.toml                   # Linter config
```

### Frontend Structure

```
spendsense-frontend/
├── package.json
├── svelte.config.js
├── vite.config.ts
├── tailwind.config.js
├── biome.json                  # Linter config
│
├── src/
│   ├── app.html
│   │
│   ├── routes/
│   │   ├── +layout.svelte
│   │   ├── +page.svelte        # Home/landing
│   │   │
│   │   ├── dashboard/
│   │   │   └── +page.svelte
│   │   │
│   │   ├── transactions/
│   │   │   └── +page.svelte
│   │   │
│   │   └── insights/
│   │       └── +page.svelte
│   │
│   └── lib/
│       ├── components/
│       │   ├── TransactionList.svelte
│       │   ├── PersonaCard.svelte
│       │   ├── InsightCard.svelte
│       │   └── RecommendationCard.svelte
│       │
│       ├── stores/
│       │   └── user.svelte.ts  # Svelte 5 runes
│       │
│       ├── api/
│       │   └── client.ts       # Fetch wrapper
│       │
│       └── types/
│           └── index.ts
│
└── static/
```

---

## Core Requirements Implementation

### 1. Synthetic Data Generation

**Goal:** Generate 50-100 realistic users with diverse financial profiles using `faker`.

```python
# src/spendsense/services/synthetic_data.py
from faker import Faker
from datetime import datetime, timedelta
import random
import json

fake = Faker()
Faker.seed(42)  # Deterministic for testing

def generate_user():
    """Generate a single synthetic user with accounts and transactions"""
    user_id = fake.uuid4()
    
    # User profile
    user = {
        "id": user_id,
        "name": fake.name(),
        "email": fake.email(),
        "created_at": fake.date_time_between(start_date="-2y").isoformat()
    }
    
    # Generate 1-3 accounts per user
    accounts = []
    for _ in range(random.randint(1, 3)):
        account_type = random.choice([
            "depository/checking",
            "depository/savings",
            "credit/credit_card"
        ])
        
        account = {
            "id": fake.uuid4(),
            "user_id": user_id,
            "type": account_type.split("/")[0],
            "subtype": account_type.split("/")[1],
            "name": f"{fake.company()} {account_type.split('/')[1].title()}",
            "mask": fake.bothify(text="####"),
            "balance": random.randint(100, 50000) * 100,  # In cents
            "currency": "USD"
        }
        
        # Credit card specific fields
        if account_type.startswith("credit"):
            account["limit"] = random.randint(1000, 25000) * 100
            account["apr"] = round(random.uniform(12.99, 29.99), 2)
        
        accounts.append(account)
    
    # Generate transactions (last 180 days)
    transactions = []
    for account in accounts:
        num_txns = random.randint(20, 100)
        
        for _ in range(num_txns):
            date = fake.date_time_between(start_date="-180d")
            
            # Transaction categories weighted by frequency
            categories = [
                ("FOOD_AND_DRINK", 0.25),
                ("GENERAL_MERCHANDISE", 0.20),
                ("TRANSPORTATION", 0.15),
                ("ENTERTAINMENT", 0.10),
                ("UTILITIES", 0.10),
                ("HEALTHCARE", 0.05),
                ("INCOME", 0.15)
            ]
            
            category = random.choices(
                [c[0] for c in categories],
                weights=[c[1] for c in categories]
            )[0]
            
            # Amount varies by category
            if category == "INCOME":
                amount = -random.randint(2000, 6000) * 100  # Negative = credit
            else:
                amount = random.randint(5, 250) * 100
            
            transaction = {
                "id": fake.uuid4(),
                "account_id": account["id"],
                "date": date.isoformat(),
                "amount": amount,
                "merchant_name": fake.company() if category != "INCOME" else "Employer Inc",
                "category": category,
                "pending": random.random() < 0.05  # 5% pending
            }
            
            transactions.append(transaction)
    
    return {
        "user": user,
        "accounts": accounts,
        "transactions": sorted(transactions, key=lambda x: x["date"])
    }

def generate_dataset(num_users: int = 50):
    """Generate full synthetic dataset"""
    dataset = []
    
    for _ in range(num_users):
        dataset.append(generate_user())
    
    # Save to JSON
    with open("data/users.json", "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✓ Generated {num_users} users with accounts and transactions")
    return dataset

if __name__ == "__main__":
    generate_dataset(50)
```

**Key Requirements:**
- ✅ Generate 50-100 users
- ✅ No real PII (faker generates fake data)
- ✅ Diverse financial situations (income levels, spending patterns)
- ✅ Accounts: checking, savings, credit cards with balances/limits
- ✅ Transactions: 180 days, categorized, realistic amounts
- ✅ Deterministic with seed (reproducible)

---

---

### 2. Database Schema (SQLite)

**Simple initialization without migrations:**

```python
# src/spendsense/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///data/spendsense.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

class Base(DeclarativeBase):
    pass

async def init_db():
    """Initialize database - create all tables from SQLAlchemy models"""
    async with engine.begin() as conn:
        # Drop all tables (fresh start for development)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Enable WAL mode for concurrent reads
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA synchronous=NORMAL")

async def get_db():
    """Dependency for FastAPI routes"""
    async with AsyncSessionLocal() as session:
        yield session
```

**SQLAlchemy models:**


```python
# src/spendsense/models/user.py
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    consent: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    
    # Relationships
    accounts: Mapped[list["Account"]] = relationship(back_populates="user")
    personas: Mapped[list["Persona"]] = relationship(back_populates="user")
```

```python
# src/spendsense/models/account.py
from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

class Account(Base):
    __tablename__ = "accounts"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(50))  # depository, credit
    subtype: Mapped[str] = mapped_column(String(50))  # checking, savings, credit_card
    name: Mapped[str] = mapped_column(String(200))
    mask: Mapped[str] = mapped_column(String(4))
    
    # Balances in cents
    balance: Mapped[int] = mapped_column(Integer)
    limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Credit cards
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Credit card specifics
    apr: Mapped[float | None] = mapped_column(nullable=True)
    min_payment: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_overdue: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")
```

```python
# src/spendsense/models/transaction.py
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ..database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    amount: Mapped[int] = mapped_column(Integer)  # In cents (positive = debit)
    merchant_name: Mapped[str | None] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(100))
    pending: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    account: Mapped["Account"] = relationship(back_populates="transactions")
    
    # Composite index for efficient queries
    __table_args__ = (
        Index("ix_txn_account_date", "account_id", "date"),
    )
```

```python
# src/spendsense/models/persona.py
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum
from ..database import Base

class PersonaType(str, Enum):
    HIGH_UTILIZATION = "high_utilization"
    VARIABLE_INCOME = "variable_income"
    SUBSCRIPTION_HEAVY = "subscription_heavy"
    SAVINGS_BUILDER = "savings_builder"
    BALANCED = "balanced"  # Custom 5th persona

class Persona(Base):
    __tablename__ = "personas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    window: Mapped[str] = mapped_column(String(10))  # "30d" or "180d"
    persona_type: Mapped[PersonaType] = mapped_column(SQLEnum(PersonaType))
    confidence: Mapped[float] = mapped_column(Float)  # 0.0-1.0
    assigned_at: Mapped[datetime] = mapped_column(DateTime)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="personas")
```

```python
# src/spendsense/models/content.py
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from ..database import Base

class Content(Base):
    __tablename__ = "content"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    type: Mapped[str] = mapped_column(String(50))  # article, video, tool
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)
    
    # Targeting
    persona_tags: Mapped[list] = mapped_column(JSON)  # List of persona types
    signal_tags: Mapped[list] = mapped_column(JSON)   # List of signal names
    
    # Metadata
    source: Mapped[str] = mapped_column(String(50))  # "template", "llm", "human"
    created_at: Mapped[datetime] = mapped_column(DateTime)
```

---

### 3. Feature Detection (Behavioral Signals)

```python
# src/spendsense/services/features.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from collections import defaultdict
from ..models import Transaction, Account

class BehaviorSignals:
    """Computed behavioral signals for a user"""
    
    def __init__(self):
        self.subscriptions = {}
        self.savings = {}
        self.credit = {}
        self.income = {}

async def compute_signals(
    db: AsyncSession,
    user_id: str,
    window_days: int = 30
) -> BehaviorSignals:
    """
    Compute all behavioral signals for a user within a time window.
    
    Args:
        db: Database session
        user_id: User ID
        window_days: Time window (30 or 180 days)
    
    Returns:
        BehaviorSignals object with all computed features
    """
    signals = BehaviorSignals()
    cutoff_date = datetime.now() - timedelta(days=window_days)
    
    # Get user accounts
    accounts_stmt = select(Account).where(Account.user_id == user_id)
    accounts_result = await db.execute(accounts_stmt)
    accounts = accounts_result.scalars().all()
    
    # Get transactions in window
    txns_stmt = (
        select(Transaction)
        .join(Account)
        .where(Account.user_id == user_id)
        .where(Transaction.date >= cutoff_date)
        .order_by(Transaction.date)
    )
    txns_result = await db.execute(txns_stmt)
    transactions = txns_result.scalars().all()
    
    # 1. SUBSCRIPTION DETECTION
    signals.subscriptions = await detect_subscriptions(transactions, window_days)
    
    # 2. SAVINGS ANALYSIS
    signals.savings = await analyze_savings(accounts, transactions, window_days)
    
    # 3. CREDIT UTILIZATION
    signals.credit = await analyze_credit(accounts, transactions)
    
    # 4. INCOME STABILITY
    signals.income = await analyze_income(transactions, window_days)
    
    return signals


async def detect_subscriptions(transactions: list, window_days: int) -> dict:
    """
    Detect recurring merchants (≥3 occurrences with monthly/weekly cadence).
    """
    merchant_txns = defaultdict(list)
    
    for txn in transactions:
        if txn.merchant_name and txn.amount > 0:  # Debits only
            merchant_txns[txn.merchant_name].append(txn.date)
    
    recurring = []
    for merchant, dates in merchant_txns.items():
        if len(dates) >= 3:
            # Check if dates are roughly evenly spaced (monthly or weekly)
            dates_sorted = sorted(dates)
            gaps = [(dates_sorted[i+1] - dates_sorted[i]).days 
                    for i in range(len(dates_sorted) - 1)]
            
            avg_gap = sum(gaps) / len(gaps)
            
            # Monthly: 28-35 days, Weekly: 6-8 days
            if (28 <= avg_gap <= 35) or (6 <= avg_gap <= 8):
                recurring.append({
                    "merchant": merchant,
                    "frequency": "monthly" if avg_gap > 20 else "weekly",
                    "count": len(dates),
                    "avg_amount": sum(t.amount for t in transactions 
                                      if t.merchant_name == merchant) / len(dates)
                })
    
    total_recurring_spend = sum(r["avg_amount"] for r in recurring)
    total_spend = sum(t.amount for t in transactions if t.amount > 0)
    
    return {
        "recurring_merchants": recurring,
        "count": len(recurring),
        "monthly_spend": total_recurring_spend * (30 / window_days),
        "pct_of_total": total_recurring_spend / total_spend if total_spend > 0 else 0
    }


async def analyze_savings(accounts: list, transactions: list, window_days: int) -> dict:
    """
    Analyze net inflow to savings-like accounts.
    """
    savings_accounts = [a for a in accounts 
                        if a.subtype in ["savings", "money_market", "cd"]]
    
    if not savings_accounts:
        return {"balance": 0, "growth_rate": 0, "emergency_fund_months": 0}
    
    total_balance = sum(a.balance for a in savings_accounts)
    
    # Calculate net inflow to savings accounts
    savings_txns = [t for t in transactions 
                    if t.account_id in [a.id for a in savings_accounts]]
    
    net_inflow = sum(-t.amount for t in savings_txns)  # Negative = credit (inflow)
    monthly_inflow = net_inflow / (window_days / 30)
    
    # Calculate monthly expenses (from checking/credit accounts)
    expense_txns = [t for t in transactions 
                    if t.amount > 0 and t.category != "INCOME"]
    monthly_expenses = sum(t.amount for t in expense_txns) / (window_days / 30)
    
    emergency_fund_months = (total_balance / monthly_expenses) if monthly_expenses > 0 else 0
    
    return {
        "balance": total_balance,
        "net_inflow": net_inflow,
        "monthly_inflow": monthly_inflow,
        "growth_rate": (net_inflow / total_balance) if total_balance > 0 else 0,
        "emergency_fund_months": emergency_fund_months
    }


async def analyze_credit(accounts: list, transactions: list) -> dict:
    """
    Calculate credit utilization and payment behavior.
    """
    credit_cards = [a for a in accounts if a.type == "credit"]
    
    if not credit_cards:
        return {"utilization": 0, "flags": []}
    
    total_balance = sum(a.balance for a in credit_cards)
    total_limit = sum(a.limit for a in credit_cards if a.limit)
    
    utilization = total_balance / total_limit if total_limit > 0 else 0
    
    flags = []
    if utilization >= 0.80:
        flags.append("high_utilization_80")
    elif utilization >= 0.50:
        flags.append("high_utilization_50")
    elif utilization >= 0.30:
        flags.append("moderate_utilization_30")
    
    # Check for overdue accounts
    if any(a.is_overdue for a in credit_cards):
        flags.append("overdue")
    
    # Estimate interest charges (simplified)
    interest_charges = sum(
        (a.balance * (a.apr / 100) / 12) for a in credit_cards 
        if a.apr and a.balance > 0
    )
    
    if interest_charges > 0:
        flags.append("interest_charges")
    
    return {
        "utilization": utilization,
        "total_balance": total_balance,
        "total_limit": total_limit,
        "monthly_interest": interest_charges,
        "flags": flags,
        "cards": [
            {
                "id": a.id,
                "mask": a.mask,
                "utilization": a.balance / a.limit if a.limit else 0,
                "balance": a.balance,
                "limit": a.limit
            }
            for a in credit_cards
        ]
    }


async def analyze_income(transactions: list, window_days: int) -> dict:
    """
    Detect payroll ACH and calculate income stability.
    """
    income_txns = [t for t in transactions if t.category == "INCOME"]
    
    if len(income_txns) < 2:
        return {"frequency": "unknown", "stability": "unknown", "buffer_months": 0}
    
    # Sort by date
    income_txns_sorted = sorted(income_txns, key=lambda x: x.date)
    
    # Calculate gaps between paychecks
    gaps = [
        (income_txns_sorted[i+1].date - income_txns_sorted[i].date).days
        for i in range(len(income_txns_sorted) - 1)
    ]
    
    median_gap = sorted(gaps)[len(gaps) // 2]
    
    # Determine frequency
    if 13 <= median_gap <= 16:
        frequency = "biweekly"
    elif 28 <= median_gap <= 32:
        frequency = "monthly"
    elif 6 <= median_gap <= 8:
        frequency = "weekly"
    else:
        frequency = "variable"
    
    # Calculate variability
    avg_income = sum(-t.amount for t in income_txns) / len(income_txns)
    income_std = (sum(((-t.amount - avg_income) ** 2) for t in income_txns) / len(income_txns)) ** 0.5
    coefficient_of_variation = income_std / avg_income if avg_income > 0 else 0
    
    stability = "stable" if coefficient_of_variation < 0.15 else "variable"
    
    # Calculate cash flow buffer
    monthly_income = avg_income * (30 / (window_days / len(income_txns)))
    expense_txns = [t for t in transactions if t.amount > 0 and t.category != "INCOME"]
    monthly_expenses = sum(t.amount for t in expense_txns) / (window_days / 30)
    
    buffer_months = (monthly_income - monthly_expenses) / monthly_expenses if monthly_expenses > 0 else 0
    
    return {
        "frequency": frequency,
        "stability": stability,
        "avg_amount": avg_income,
        "coefficient_of_variation": coefficient_of_variation,
        "buffer_months": buffer_months,
        "median_gap_days": median_gap
    }
```

---

### 4. Persona Assignment

```python
# src/spendsense/services/personas.py
from .features import BehaviorSignals, compute_signals
from ..models import PersonaType
from sqlalchemy.ext.asyncio import AsyncSession

# Persona priority (highest to lowest urgency)
PERSONA_PRIORITY = [
    PersonaType.HIGH_UTILIZATION,
    PersonaType.VARIABLE_INCOME,
    PersonaType.SUBSCRIPTION_HEAVY,
    PersonaType.SAVINGS_BUILDER,
    PersonaType.BALANCED
]

async def assign_persona(
    db: AsyncSession,
    user_id: str,
    window_days: int = 30
) -> tuple[PersonaType, float, BehaviorSignals]:
    """
    Assign persona based on behavioral signals.
    
    Returns:
        (persona_type, confidence, signals)
    """
    signals = await compute_signals(db, user_id, window_days)
    
    # Check each persona in priority order
    if matches_high_utilization(signals):
        return PersonaType.HIGH_UTILIZATION, 0.95, signals
    
    if matches_variable_income(signals):
        return PersonaType.VARIABLE_INCOME, 0.90, signals
    
    if matches_subscription_heavy(signals):
        return PersonaType.SUBSCRIPTION_HEAVY, 0.85, signals
    
    if matches_savings_builder(signals):
        return PersonaType.SAVINGS_BUILDER, 0.80, signals
    
    # Default: Balanced
    return PersonaType.BALANCED, 0.60, signals


def matches_high_utilization(signals: BehaviorSignals) -> bool:
    """
    Persona 1: High Utilization
    
    Criteria:
    - Any card utilization ≥50% OR
    - Interest charges > 0 OR
    - Overdue status = true
    """
    credit = signals.credit
    
    if not credit or "utilization" not in credit:
        return False
    
    # Check overall utilization
    if credit["utilization"] >= 0.50:
        return True
    
    # Check individual cards
    if any(card["utilization"] >= 0.50 for card in credit.get("cards", [])):
        return True
    
    # Check flags
    flags = credit.get("flags", [])
    if "interest_charges" in flags or "overdue" in flags:
        return True
    
    return False


def matches_variable_income(signals: BehaviorSignals) -> bool:
    """
    Persona 2: Variable Income Budgeter
    
    Criteria:
    - Median pay gap > 45 days AND
    - Cash-flow buffer < 1 month
    """
    income = signals.income
    
    if not income or income.get("frequency") == "unknown":
        return False
    
    median_gap = income.get("median_gap_days", 0)
    buffer = income.get("buffer_months", 0)
    
    return median_gap > 45 and buffer < 1.0


def matches_subscription_heavy(signals: BehaviorSignals) -> bool:
    """
    Persona 3: Subscription-Heavy
    
    Criteria:
    - Recurring merchants ≥3 AND
    - (Monthly recurring spend ≥$50 OR subscription spend share ≥10%)
    """
    subs = signals.subscriptions
    
    if not subs:
        return False
    
    count = subs.get("count", 0)
    monthly_spend = subs.get("monthly_spend", 0) / 100  # Convert from cents
    pct_of_total = subs.get("pct_of_total", 0)
    
    return count >= 3 and (monthly_spend >= 50 or pct_of_total >= 0.10)


def matches_savings_builder(signals: BehaviorSignals) -> bool:
    """
    Persona 4: Savings Builder
    
    Criteria:
    - Savings growth rate ≥2% over window OR
    - Net savings inflow ≥$200/month, AND
    - All card utilizations < 30%
    """
    savings = signals.savings
    credit = signals.credit
    
    if not savings:
        return False
    
    growth_rate = savings.get("growth_rate", 0)
    monthly_inflow = savings.get("monthly_inflow", 0) / 100  # Convert from cents
    
    savings_criteria = growth_rate >= 0.02 or monthly_inflow >= 200
    
    # Check credit utilization
    if credit and credit.get("utilization", 1.0) >= 0.30:
        return False
    
    return savings_criteria


# Persona 5: Balanced (Custom)
# This is the default for users who don't match other personas
# Represents financially stable users with no urgent concerns
```

---

### 5. Content Generator (AI-Agnostic)

```python
# src/spendsense/generators/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from ..models import PersonaType
from ..services.features import BehaviorSignals

class EducationItem(BaseModel):
    """Educational content item"""
    id: str
    title: str
    summary: str
    body: str
    cta: str
    persona_tags: list[str]
    signal_tags: list[str]
    source: str  # "template" or "llm"

class Rationale(BaseModel):
    """Plain-language explanation"""
    text: str
    data_points: list[dict]
    source: str

class ContentGenerator(ABC):
    """Abstract interface for content generation"""
    
    @abstractmethod
    async def generate_education(
        self,
        persona: PersonaType,
        signals: BehaviorSignals,
        limit: int = 3
    ) -> list[EducationItem]:
        """Generate educational content items"""
        pass
    
    @abstractmethod
    async def generate_rationale(
        self,
        item: EducationItem,
        signals: BehaviorSignals
    ) -> Rationale:
        """Generate explanation for why this content is recommended"""
        pass
```

```python
# src/spendsense/generators/template.py
from .base import ContentGenerator, EducationItem, Rationale
from ..models import PersonaType
from ..services.features import BehaviorSignals
import yaml

class TemplateGenerator(ContentGenerator):
    """Template-based content generation (no AI required)"""
    
    def __init__(self, catalog_path: str = "data/content_catalog.yaml"):
        with open(catalog_path) as f:
            self.catalog = yaml.safe_load(f)
    
    async def generate_education(
        self,
        persona: PersonaType,
        signals: BehaviorSignals,
        limit: int = 3
    ) -> list[EducationItem]:
        """Select from static catalog based on persona and signals"""
        
        # Filter catalog by persona
        candidates = [
            item for item in self.catalog["education"]
            if persona.value in item["persona_tags"]
        ]
        
        # Score by signal relevance
        scored = []
        for item in candidates:
            score = self._calculate_relevance(item, signals)
            scored.append((score, item))
        
        # Sort by score and take top N
        scored.sort(reverse=True, key=lambda x: x[0])
        top_items = [item for score, item in scored[:limit]]
        
        return [EducationItem(**item) for item in top_items]
    
    def _calculate_relevance(self, item: dict, signals: BehaviorSignals) -> float:
        """Simple relevance scoring"""
        score = 0.0
        
        # Check if item's signal tags match active signals
        for signal_tag in item["signal_tags"]:
            if signal_tag == "high_credit_utilization" and signals.credit.get("utilization", 0) >= 0.50:
                score += 1.0
            elif signal_tag == "subscription_heavy" and signals.subscriptions.get("count", 0) >= 3:
                score += 1.0
            elif signal_tag == "variable_income" and signals.income.get("stability") == "variable":
                score += 1.0
        
        return score
    
    async def generate_rationale(
        self,
        item: EducationItem,
        signals: BehaviorSignals
    ) -> Rationale:
        """Generate explanation using template strings"""
        
        # Select template based on persona
        templates = {
            "high_utilization": (
                "We noticed your {card_description} is at {utilization:.0%} utilization "
                "({balance} of {limit} limit). Bringing this below 30% could improve your "
                "credit score and reduce interest charges of ${interest:.2f}/month."
            ),
            "subscription_heavy": (
                "You have {count} recurring subscriptions totaling ${monthly_spend:.2f}/month "
                "({pct_of_income:.0%} of spending). Reviewing these could free up "
                "${potential_savings:.2f}/month."
            ),
            "variable_income": (
                "Your income arrives every {gap} days on average with {stability} patterns. "
                "Building a {buffer:.1f}-month cash buffer could help smooth irregular income."
            ),
            "savings_builder": (
                "You're saving ${monthly_inflow:.2f}/month with a {growth_rate:.1%} growth rate. "
                "You have {emergency_fund:.1f} months of emergency fund coverage."
            )
        }
        
        # Format template with signal data
        persona_key = item.persona_tags[0] if item.persona_tags else "balanced"
        template = templates.get(persona_key, "")
        
        # Extract data points
        data_points = self._extract_data_points(signals, persona_key)
        
        # Format rationale text
        text = template.format(**self._prepare_template_vars(signals, persona_key))
        
        return Rationale(
            text=text,
            data_points=data_points,
            source="template"
        )
    
    def _extract_data_points(self, signals: BehaviorSignals, persona_key: str) -> list[dict]:
        """Extract concrete data citations"""
        points = []
        
        if persona_key == "high_utilization" and signals.credit:
            card = signals.credit["cards"][0] if signals.credit.get("cards") else {}
            points.append({
                "signal": "credit_utilization",
                "value": f"{card.get('utilization', 0):.0%}",
                "account_hint": f"Card ending in {card.get('mask', 'XXXX')}"
            })
        
        elif persona_key == "subscription_heavy" and signals.subscriptions:
            points.append({
                "signal": "recurring_subscriptions",
                "value": str(signals.subscriptions.get("count", 0)),
                "comparison": "threshold is 3+"
            })
        
        return points
    
    def _prepare_template_vars(self, signals: BehaviorSignals, persona_key: str) -> dict:
        """Prepare variables for template formatting"""
        
        if persona_key == "high_utilization" and signals.credit:
            card = signals.credit["cards"][0] if signals.credit.get("cards") else {}
            return {
                "card_description": f"card ending in {card.get('mask', 'XXXX')}",
                "utilization": card.get("utilization", 0),
                "balance": f"${card.get('balance', 0) / 100:,.2f}",
                "limit": f"${card.get('limit', 0) / 100:,.2f}",
                "interest": signals.credit.get("monthly_interest", 0) / 100
            }
        
        elif persona_key == "subscription_heavy" and signals.subscriptions:
            return {
                "count": signals.subscriptions.get("count", 0),
                "monthly_spend": signals.subscriptions.get("monthly_spend", 0) / 100,
                "pct_of_income": signals.subscriptions.get("pct_of_total", 0),
                "potential_savings": signals.subscriptions.get("monthly_spend", 0) / 100 * 0.3
            }
        
        return {}
```

```python
# src/spendsense/generators/llm.py (OPTIONAL - for future use)
from .base import ContentGenerator, EducationItem, Rationale
from ..models import PersonaType
from ..services.features import BehaviorSignals

class LLMGenerator(ContentGenerator):
    """
    LLM-powered content generation (OPTIONAL).
    
    This is a placeholder for future AI integration.
    Can swap in Anthropic, OpenAI, or local models without
    changing any other code.
    """
    
    def __init__(self, provider: str = "anthropic", model: str = "claude-sonnet-4"):
        self.provider = provider
        self.model = model
        # Initialize LLM client here when needed
    
    async def generate_education(
        self,
        persona: PersonaType,
        signals: BehaviorSignals,
        limit: int = 3
    ) -> list[EducationItem]:
        """Generate custom educational content via LLM"""
        # TODO: Implement LLM call with structured output
        raise NotImplementedError("LLM generator not yet implemented")
    
    async def generate_rationale(
        self,
        item: EducationItem,
        signals: BehaviorSignals
    ) -> Rationale:
        """Generate personalized explanation via LLM"""
        # TODO: Implement LLM call
        raise NotImplementedError("LLM generator not yet implemented")
```

```yaml
# data/content_catalog.yaml
education:
  - id: "edu_001"
    title: "Understanding Credit Utilization"
    summary: "Learn why keeping credit card balances low helps your credit score"
    body: |
      Credit utilization is the ratio of your credit card balances to your credit limits.
      
      Financial experts recommend keeping utilization below 30% on each card and overall.
      High utilization signals risk to lenders and can lower your credit score.
      
      **Quick wins:**
      - Pay down high balances first
      - Request credit limit increases (if you won't spend more)
      - Set up payment alerts before due dates
      - Consider balance transfer cards (check terms carefully)
      
      Even small reductions in utilization can improve your credit score within weeks.
    cta: "Calculate your utilization"
    persona_tags: ["high_utilization"]
    signal_tags: ["high_credit_utilization", "interest_charges"]
    source: "human"

  - id: "edu_002"
    title: "Subscription Audit Checklist"
    summary: "Find and cancel forgotten subscriptions costing you money"
    body: |
      The average person has 10+ active subscriptions but only uses 5 regularly.
      
      **Your 3-step audit:**
      
      1. **List everything** - Review 3 months of transactions for recurring charges
      2. **Rate by value** - Mark each as Essential / Nice-to-have / Never use
      3. **Cancel the waste** - Start with "never use", negotiate "nice-to-have"
      
      **Common culprits:**
      - Streaming services you forgot about
      - Free trials that auto-renewed
      - Gym memberships you don't use
      - App subscriptions you downloaded once
      
      Pro tip: Set calendar reminders 7 days before renewals to decide if you're still using it.
    cta: "Start your audit"
    persona_tags: ["subscription_heavy"]
    signal_tags: ["subscription_heavy"]
    source: "human"

  - id: "edu_003"
    title: "Budgeting with Variable Income"
    summary: "How to manage money when your income changes month-to-month"
    body: |
      Traditional budgeting assumes steady paychecks. If you're freelance, gig-economy, 
      commission-based, or seasonal, you need a different approach.
      
      **The Variable Income Budget:**
      
      1. **Calculate your baseline** - What's your minimum monthly income over the past year?
      2. **Budget from baseline** - Cover essentials (housing, food, transport) first
      3. **Build a buffer** - Save 1-3 months expenses before increasing lifestyle
      4. **Use percentages** - Budget as % of income, not fixed amounts
      
      **Example:**
      - Housing: 30% (not "$1,500")
      - Savings: 20%
      - Flexible spending: 30%
      - Buffer fund: 20%
      
      On high-income months, the same percentages mean bigger savings. On low months,
      percentages shrink but you stay solvent.
    cta: "Build your variable budget"
    persona_tags: ["variable_income"]
    signal_tags: ["variable_income"]
    source: "human"

  - id: "edu_004"
    title: "Emergency Fund 101"
    summary: "Why you need one and how to build it (even on a tight budget)"
    body: |
      An emergency fund is cash set aside for unexpected expenses like medical bills,
      car repairs, or job loss. It prevents going into debt when life happens.
      
      **How much do I need?**
      - Minimum: $1,000 (covers most small emergencies)
      - Target: 3-6 months of expenses
      - Variable income? Aim for 6-12 months
      
      **Building it:**
      1. Open a separate savings account (hard to raid accidentally)
      2. Automate transfers on payday ($25, $50, $100 - whatever fits)
      3. Add windfalls (tax refunds, bonuses, side gig money)
      4. Don't touch it unless it's a real emergency
      
      **What counts as an emergency?**
      - ✅ Medical bills, car repair, job loss, urgent home repair
      - ❌ Sales, vacations, gifts, wants (use separate savings)
      
      Even $1,000 removes the panic from small crises. Start small, build momentum.
    cta: "Start your emergency fund"
    persona_tags: ["savings_builder", "variable_income"]
    signal_tags: ["low_emergency_fund"]
    source: "human"
```

---

### 6. Recommendation Engine

```python
# src/spendsense/services/recommendations.py
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import PersonaType
from ..generators.base import ContentGenerator, EducationItem, Rationale
from .personas import assign_persona
from .features import BehaviorSignals
from pydantic import BaseModel

class Recommendation(BaseModel):
    """Single recommendation with rationale"""
    content: EducationItem
    rationale: Rationale
    persona: str
    confidence: float

async def generate_recommendations(
    db: AsyncSession,
    user_id: str,
    generator: ContentGenerator,
    window_days: int = 30
) -> list[Recommendation]:
    """
    Generate personalized recommendations for a user.
    
    Args:
        db: Database session
        user_id: User ID
        generator: Content generator (Template or LLM)
        window_days: Time window (30 or 180)
    
    Returns:
        List of recommendations with rationales
    """
    
    # 1. Assign persona
    persona_type, confidence, signals = await assign_persona(db, user_id, window_days)
    
    # 2. Generate educational content
    education_items = await generator.generate_education(
        persona=persona_type,
        signals=signals,
        limit=3
    )
    
    # 3. Generate rationales
    recommendations = []
    for item in education_items:
        rationale = await generator.generate_rationale(item, signals)
        
        rec = Recommendation(
            content=item,
            rationale=rationale,
            persona=persona_type.value,
            confidence=confidence
        )
        recommendations.append(rec)
    
    return recommendations
```

---

### 7. API Endpoints

```python
# src/spendsense/routers/insights.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.recommendations import generate_recommendations
from ..generators.template import TemplateGenerator
from ..schemas.insight import RecommendationResponse

router = APIRouter()

# Initialize generator (template-based by default)
generator = TemplateGenerator()

@router.get("/{user_id}", response_model=RecommendationResponse)
async def get_insights(
    user_id: str,
    window: str = "30d",
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized insights and recommendations for a user.
    
    Args:
        user_id: User ID
        window: Time window ("30d" or "180d")
    
    Returns:
        Persona assignment + recommendations with rationales
    """
    
    window_days = 30 if window == "30d" else 180
    
    try:
        recommendations = await generate_recommendations(
            db=db,
            user_id=user_id,
            generator=generator,
            window_days=window_days
        )
        
        return {
            "user_id": user_id,
            "window": window,
            "persona": recommendations[0].persona if recommendations else "balanced",
            "confidence": recommendations[0].confidence if recommendations else 0.0,
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 8. Guardrails

```python
# src/spendsense/utils/guardrails.py
import re

SHAME_PATTERNS = [
    r'\byou\'?re\s+overspending\b',
    r'\bbad\s+(financial|spending)\s+habits?\b',
    r'\birresponsible\b',
    r'\bcareless\b',
    r'\bwasting\s+money\b',
    r'\bpoor\s+choices?\b'
]

def check_tone(text: str) -> tuple[bool, list[str]]:
    """
    Validate that text doesn't contain shaming language.
    
    Returns:
        (passed, violations)
    """
    violations = []
    text_lower = text.lower()
    
    for pattern in SHAME_PATTERNS:
        if re.search(pattern, text_lower):
            violations.append(pattern)
    
    return len(violations) == 0, violations

def check_consent(user_consent: bool) -> bool:
    """Verify user has given consent"""
    return user_consent == True

DISCLAIMER = """
This is educational content, not financial advice. 
Consult a licensed advisor for personalized guidance.
"""
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**PR-01: Project Setup**
- Initialize backend with uv (`uv init`)
- Initialize frontend with SvelteKit (`npm create svelte@latest`)
- Configure ruff + biome linters
- Create basic README

**PR-02: Database Schema**
- Create SQLAlchemy models (User, Account, Transaction, Persona, Content)
- Implement `init_db()` with `create_all()`
- Enable SQLite WAL mode

**PR-03: Synthetic Data Generator**
- Implement `generate_user()` with faker
- Generate 50 users with accounts + transactions
- Save to `data/users.json`
- Create data loader to populate database

### Phase 2: Feature Detection (Week 2)
**PR-04: Subscription Detection**
- Implement `detect_subscriptions()` 
- Find recurring merchants (≥3 occurrences)
- Calculate monthly recurring spend

**PR-05: Savings Analysis**
- Implement `analyze_savings()`
- Calculate net inflow, growth rate, emergency fund coverage

**PR-06: Credit Analysis**
- Implement `analyze_credit()`
- Calculate utilization, detect high utilization, estimate interest

**PR-07: Income Analysis**
- Implement `analyze_income()`
- Detect payroll frequency, calculate stability

### Phase 3: Personas & Content (Week 3)
**PR-08: Persona Assignment Logic**
- Implement `assign_persona()` with priority order
- Create matching functions for all 5 personas
- Add 30d and 180d window support

**PR-09: Content Catalog**
- Create `content_catalog.yaml` with 10+ education items
- Map content to personas and signals

**PR-10: Template Generator**
- Implement `TemplateGenerator` 
- Content selection by persona + signals
- Rationale generation with data citations

**PR-11: LLM Generator Stub**
- Create `LLMGenerator` interface (no implementation)
- Document how to swap in AI provider

### Phase 4: API & Frontend (Week 4)
**PR-12: API Endpoints**
- `/users` - User CRUD
- `/accounts/{user_id}` - Get accounts
- `/transactions/{user_id}` - Get transactions (paginated)
- `/insights/{user_id}` - Get recommendations

**PR-13: Svelte 5 Dashboard**
- Create dashboard layout with runes ($state, $derived)
- Display user accounts and balances
- Show recent transactions

**PR-14: Insights UI**
- Display persona assignment
- Show recommendations with rationales
- Highlight data citations

**PR-15: Operator View**
- View all users
- Inspect signals for any user
- See generated recommendations
- Decision trace display

### Phase 5: Guardrails & Polish (Week 5)
**PR-16: Guardrails Implementation**
- Consent checking
- Tone validation (no shaming language)
- Add disclaimers to all recommendations

**PR-17: Evaluation Harness**
- Calculate coverage (% users with persona + ≥3 behaviors)
- Measure explainability (% recommendations with rationales)
- Test latency (<5s per user)
- Generate metrics JSON

**PR-18: Documentation**
- Decision log (why template-based default, why SQLite, etc.)
- Schema documentation
- Limitations (what we're NOT doing)
- Setup instructions (one-command)

### Phase 6: Demo & Submission (Week 6)
**PR-19: Demo Video**
- Record walkthrough of features
- Show data generation, persona assignment, recommendations
- Demonstrate operator view

**PR-20: Final Polish**
- Linting pass on all code
- README completion
- Code comments and docstrings

---

## Success Criteria

| Category | Metric | Target | How to Measure |
|----------|--------|--------|----------------|
| **Coverage** | Users with persona + ≥3 behaviors | 100% | Count users with assigned persona AND ≥3 detected signals |
| **Explainability** | Recommendations with rationales | 100% | Every recommendation has `rationale.text` and `rationale.data_points` |
| **Latency** | Time to generate recommendations | <5s | Measure from `/insights` API call start to response |
| **Auditability** | Recommendations with decision trace | 100% | Every recommendation includes persona logic + signal values |
| **Code Quality** | Passing linter | 100% | `ruff check` and `biome check` pass with 0 errors |
| **Documentation** | Schema + decision log | Complete | All files in `/docs` exist and are comprehensive |

---

## Quick Start Commands

### Backend Setup
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project
cd spendsense-backend
uv sync

# Generate synthetic data
uv run python -m spendsense.services.synthetic_data

# Start API (will auto-create database tables on startup)
uv run uvicorn spendsense.main:app --reload
```

### Frontend Setup
```bash
cd spendsense-frontend
npm install
npm run dev
```

### Linting
```bash
# Backend
cd spendsense-backend
uv run ruff check src/
uv run ruff format src/

# Frontend
cd spendsense-frontend
npx biome check src/
npx biome format --write src/
```

---

## Key Design Decisions

### Why SQLite?
- ✅ Single-file database (no server setup)
- ✅ WAL mode enables concurrent reads
- ✅ Perfect for 50-100 users
- ✅ Portable (can commit to git if small)
- ❌ Not for production scale (but not the goal)

### Why Template-Based Content?
- ✅ Zero cost (no API keys)
- ✅ Fully deterministic
- ✅ Instant response (<1ms)
- ✅ 100% explainable
- ✅ Easy to swap for LLM later
- ❌ Less personalized than AI

### Why No Caching?
- ✅ Simpler architecture
- ✅ Fewer moving parts
- ✅ SQLite is fast enough for 100 users
- ✅ Queries complete in <50ms
- ❌ Won't scale to 10k+ users (but not the goal)

### Why No Testing Framework?
- ✅ Reduces boilerplate
- ✅ Linting catches syntax errors
- ✅ Type hints catch logic errors
- ✅ Manual testing sufficient for demo
- ❌ No regression protection (accept this tradeoff)

---

## Potential Simplifications

**If even this is too complex, we can remove:**

1. **Operator view** → Focus only on user-facing UI
2. **180-day window** → Only implement 30-day analysis
3. **LLM generator stub** → Remove entirely if no AI plans
4. **Biome linting** → Use ESLint (more familiar to most devs)
5. **Multiple personas** → Start with just 2-3 personas instead of 5

**Critical path (absolute minimum):**
1. Synthetic data generation ✓
2. Feature detection (4 signal types) ✓
3. Persona assignment (5 personas) ✓
4. Template-based recommendations ✓
5. Basic API endpoints ✓
6. Simple Svelte UI to display results ✓

---

## Technologies We're NOT Using

To keep complexity low, we explicitly avoid:
- ❌ Redis / Memcached (no caching)
- ❌ Celery / background tasks (synchronous only)
- ❌ Docker Compose (optional for deployment)
- ❌ pytest / vitest (linting only)
- ❌ Real Plaid API (synthetic data only)
- ❌ LLM APIs (template-based default)
- ❌ Kubernetes / cloud deployment
- ❌ Authentication / user login (demo only)
- ❌ Email / notifications
- ❌ A/B testing framework

---

## Final Notes

**This PRD is optimized for:**
- Solo developer or small team
- 4-6 week timeline
- Local laptop development
- Demo-quality (not production)
- Modern best practices (Python 3.13, Svelte 5, uv, ruff)
- Minimal external dependencies

**The goal is to build something impressive that works flawlessly on a laptop, not to build production-scale infrastructure.**

Every requirement from the original Project Description is met, but we've stripped away complexity that doesn't directly serve those requirements.