# SpendSense - Epic Breakdown

**Author:** Peter
**Date:** 2025-11-03
**Project Level:** 3
**Target Scale:** 50-100 synthetic users, <5s response time

---

## Overview

This document provides the detailed epic breakdown for SpendSense, expanding on the high-level epic list in the [PRD](./PRD.md).

Each epic includes:

- Expanded goal and value proposition
- Complete story breakdown with user stories
- Acceptance criteria for each story
- Story sequencing and dependencies

**Epic Sequencing Principles:**

- Epic 1 establishes foundational infrastructure and initial functionality
- Subsequent epics build progressively, each delivering significant end-to-end value
- Stories within epics are vertically sliced and sequentially ordered
- No forward dependencies - each story builds only on previous work

---

## Epic 1: Foundation & Data Infrastructure

**Goal:** Establish the core platform with database, models, and synthetic data generation capability.

**Value Proposition:** Provides the foundational infrastructure that all subsequent features depend on. Enables realistic testing with 50-100 synthetic users without external dependencies.

**Technical Scope:**
- Backend project initialization with uv and Python 3.13
- Frontend project initialization with SvelteKit and Svelte 5
- SQLAlchemy models for all entities
- SQLite database with WAL mode
- Synthetic data generation using faker
- Linting configuration (ruff for Python, Biome for frontend)

---

### Story 1.1: Backend Project Setup

As a developer,
I want the backend project initialized with modern Python tooling,
So that I have a working foundation for API development.

**Acceptance Criteria:**
1. Create `spendsense-backend/` directory with uv project structure
2. Configure `pyproject.toml` with Python 3.13.8 requirement
3. Install core dependencies: `fastapi[standard]`, `sqlalchemy`, `aiosqlite`, `pydantic`, `faker`, `ruff`
4. Create `src/spendsense/` module structure with `__init__.py`
5. Configure `ruff.toml` with linting rules
6. Create `.python-version` file set to 3.13
7. Verify `uv sync` runs successfully
8. Create basic `main.py` with FastAPI app that returns "Hello SpendSense" on GET /

**Prerequisites:** None

**Technical Notes:**
- Use `uv init spendsense-backend` to bootstrap
- FastAPI[standard] includes uvicorn for development
- Follow architecture.md naming conventions (snake_case for files)

---

### Story 1.2: Frontend Project Setup

As a developer,
I want the frontend project initialized with Svelte 5 and modern tooling,
So that I have a working foundation for UI development.

**Acceptance Criteria:**
1. Create `spendsense-frontend/` directory using `bunx sv create`
2. Configure for TypeScript, Svelte 5 (runes), and SvelteKit 2.x
3. Install Tailwind CSS v4: `bun add -d tailwindcss@next @tailwindcss/vite@next`
4. Initialize shadcn-svelte: `bunx shadcn-svelte@latest init`
5. Configure `biome.json` for linting and formatting
6. Create `.env` file with `API_BASE_URL=http://localhost:8000`
7. Set up basic routing structure in `src/routes/`
8. Verify `bun run dev` starts dev server on port 5173
9. Create minimal landing page that displays "SpendSense" heading

**Prerequisites:** None

**Technical Notes:**
- Use Bun instead of npm for faster installs
- shadcn-svelte provides Svelte 5 compatible components
- Follow architecture.md naming conventions (PascalCase for components)

---

### Story 1.3: Database Schema & Models

As a developer,
I want SQLAlchemy models for all entities with proper relationships,
So that I can persist and query financial data efficiently.

**Acceptance Criteria:**
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

**Prerequisites:** Story 1.1 (Backend Project Setup)

**Technical Notes:**
- Use SQLAlchemy 2.0 `Mapped` type hints
- Store currency as integers (cents) not floats
- Use ISO 8601 datetime strings in JSON serialization
- PersonaType as Enum: high_utilization, variable_income, subscription_heavy, savings_builder, balanced

---

### Story 1.4: Synthetic Data Generator

As a developer,
I want to generate 50-100 realistic synthetic users with financial data,
So that I can test the platform without real user data or external APIs.

**Acceptance Criteria:**
1. Create `services/synthetic_data.py` module
2. Initialize Faker with seed=42 for deterministic output
3. Implement `generate_user()` function that creates:
   - User profile (name, email, created_at within last 2 years)
   - 1-3 accounts per user (mix of checking, savings, credit cards)
   - Credit cards include: limit, APR, min_payment fields
   - 20-100 transactions per account (last 180 days)
4. Implement transaction generation with realistic patterns:
   - Categories: FOOD_AND_DRINK, GENERAL_MERCHANDISE, TRANSPORTATION, ENTERTAINMENT, UTILITIES, HEALTHCARE, INCOME
   - Weighted frequency (e.g., 25% food, 15% income)
   - Amounts vary by category (income: $2000-6000, expenses: $5-250)
   - 5% pending transactions
5. Implement `generate_dataset(num_users)` function
6. Save generated data to `data/users.json`
7. Create data loader that populates database from JSON
8. Add CLI command: `uv run python -m spendsense.services.synthetic_data`
9. Verify generates 50 users with diverse financial profiles
10. Confirm deterministic output (same data on repeated runs with same seed)

**Prerequisites:** Story 1.3 (Database Schema & Models)

**Technical Notes:**
- Transaction amount in cents (positive = debit, negative = credit)
- Use `fake.uuid4()` for all IDs
- Ensure date ordering (transactions sorted by date)
- Create mix of financial situations (varied income, spending, utilization)

---

## Epic 2: Behavioral Signal Detection

**Goal:** Implement the analytics engine that detects financial behavioral patterns from transaction data.

**Value Proposition:** Enables the platform to understand user financial behavior through automated detection of subscriptions, savings patterns, credit utilization, and income stability. This is the core intelligence of SpendSense.

**Technical Scope:**
- Subscription detection algorithm (recurring merchants)
- Savings analysis (growth rate, emergency fund)
- Credit utilization calculation
- Income stability analysis
- Behavioral signal computation service

---

### Story 2.1: Subscription Detection

As a platform,
I want to detect recurring subscription merchants from transaction patterns,
So that I can identify users with high subscription spending.

**Acceptance Criteria:**
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

**Prerequisites:** Story 1.4 (Synthetic Data Generator)

**Technical Notes:**
- Transaction amounts in cents (positive = debit)
- Gap tolerance for monthly: ±7 days, weekly: ±2 days
- Exclude INCOME category from subscription detection
- Store results in BehaviorSignals.subscriptions dict

---

### Story 2.2: Savings Analysis

As a platform,
I want to analyze net savings inflow and emergency fund coverage,
So that I can identify users building financial resilience.

**Acceptance Criteria:**
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

**Prerequisites:** Story 2.1 (Subscription Detection)

**Technical Notes:**
- Negative transaction amount = credit (money in)
- Emergency fund = balance / monthly_expenses
- Monthly expenses exclude INCOME category
- Return 0 for all fields if no savings accounts exist

---

### Story 2.3: Credit Utilization Analysis

As a platform,
I want to calculate credit card utilization and identify high-risk patterns,
So that I can recommend credit management education.

**Acceptance Criteria:**
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

**Prerequisites:** Story 2.2 (Savings Analysis)

**Technical Notes:**
- Utilization threshold priority: check 80% first, then 50%, then 30%
- Only one utilization flag per analysis
- Include both account-level and individual card details
- Interest calculation simplified (assumes balance carries month-to-month)

---

### Story 2.4: Income Stability Analysis

As a platform,
I want to detect payroll frequency and income variability,
So that I can identify users with irregular income patterns.

**Acceptance Criteria:**
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

**Prerequisites:** Story 2.3 (Credit Utilization Analysis)

**Technical Notes:**
- Income transactions have negative amounts (credits)
- Coefficient of variation measures income volatility
- Buffer months can be negative (spending exceeds income)
- Return "unknown" for frequency/stability if insufficient data

---

### Story 2.5: Signal Computation Service

As a platform,
I want a unified service that computes all behavioral signals for a user,
So that API endpoints can get comprehensive financial insights in one call.

**Acceptance Criteria:**
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

**Prerequisites:** Story 2.4 (Income Stability Analysis)

**Technical Notes:**
- Use async SQLAlchemy queries
- Join transactions with accounts to filter by user_id
- Window_days parameter supports 30 or 180
- Signals computed on-demand (no caching per architecture)

---

## Epic 3: Persona Assignment & Content Generation

**Goal:** Transform behavioral signals into persona classifications and deliver targeted educational content.

**Value Proposition:** Converts raw financial data into actionable insights by matching users to financial personas and generating personalized educational recommendations with full explainability.

**Technical Scope:**
- Persona matching logic with priority ordering
- Content catalog (YAML-based educational resources)
- Template-based content generator
- LLM generator interface (future-ready)
- Recommendation engine

---

### Story 3.1: Persona Assignment Logic

As a platform,
I want to assign financial personas based on behavioral signals,
So that users receive education tailored to their financial situation.

**Acceptance Criteria:**
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

**Prerequisites:** Story 2.5 (Signal Computation Service)

**Technical Notes:**
- Priority ensures urgent financial issues flagged first
- Each persona checks specific signal thresholds from PRD
- Confidence reflects certainty of classification
- Only one persona assigned per user per window

---

### Story 3.2: Content Catalog Creation

As a platform,
I want a catalog of educational content mapped to personas and signals,
So that I can deliver relevant financial education to users.

**Acceptance Criteria:**
1. Create `data/content_catalog.yaml` file
2. Define content structure with fields: id, title, summary, body, cta, persona_tags, signal_tags, source
3. Create at least 10 education items covering:
   - Credit utilization education (for high_utilization persona)
   - Subscription audit checklist (for subscription_heavy)
   - Variable income budgeting (for variable_income)
   - Emergency fund building (for savings_builder)
   - General financial wellness (for balanced)
4. Each item includes:
   - Clear, actionable title
   - 2-3 sentence summary
   - 200-500 word educational body text
   - Call-to-action button text
   - Persona tags (which personas see this)
   - Signal tags (which signals trigger this)
   - Source attribution
5. Ensure no shaming language in any content
6. Add disclaimer text for all recommendations
7. Content follows PRD examples (credit utilization, subscription audit, etc.)
8. Verify YAML syntax is valid
9. Include at least 2 items per persona type
10. Map signal_tags to actual detected signals (e.g., "high_credit_utilization", "subscription_heavy")

**Prerequisites:** Story 3.1 (Persona Assignment Logic)

**Technical Notes:**
- YAML format for easy editing by non-developers
- persona_tags as list: ["high_utilization"]
- signal_tags as list: ["high_credit_utilization", "interest_charges"]
- Body text uses markdown formatting
- All content pre-written (no AI generation in this story)

---

### Story 3.3: Template-Based Content Generator

As a platform,
I want to generate personalized recommendations from template-based content,
So that I can deliver explainable insights without requiring AI APIs.

**Acceptance Criteria:**
1. Create `generators/base.py` with abstract `ContentGenerator` class
2. Define `EducationItem` Pydantic model (id, title, summary, body, cta, persona_tags, signal_tags, source)
3. Define `Rationale` Pydantic model (text, data_points, source)
4. Define abstract methods: `generate_education()` and `generate_rationale()`
5. Create `generators/template.py` with `TemplateGenerator` implementation
6. Implement `generate_education()`:
   - Load content_catalog.yaml
   - Filter by persona match
   - Score by signal relevance
   - Return top N items (default 3)
7. Implement `generate_rationale()`:
   - Use template strings with signal data placeholders
   - Format with actual user data (utilization %, subscription count, etc.)
   - Include data citations (account hints, specific values)
   - Generate plain-language explanation
8. Create `_calculate_relevance()` helper to score content by signals
9. Verify rationales include concrete data points from signals
10. Test with synthetic users (should return 3 relevant items with rationales)

**Prerequisites:** Story 3.2 (Content Catalog Creation)

**Technical Notes:**
- Abstract base class enables future LLM swap
- Template strings use Python .format() syntax
- Rationale templates per persona type
- Data points include signal name, value, and account hints
- Zero external API calls (fully local)

---

### Story 3.4: LLM Generator Interface

As a platform,
I want an LLM generator interface for future AI integration,
So that I can optionally swap template-based content for AI-generated content.

**Acceptance Criteria:**
1. Create `generators/llm.py` with `LLMGenerator` class
2. Extend `ContentGenerator` abstract base class
3. Add `__init__(provider, model)` with provider options: "anthropic", "openai"
4. Implement method signatures for `generate_education()` and `generate_rationale()`
5. Add `NotImplementedError` with message "LLM generator not yet implemented"
6. Document in docstrings:
   - How to add Anthropic/OpenAI API calls
   - Expected input/output formats
   - Structured output requirements
   - Guardrails integration points
7. Add comments showing where to initialize API clients
8. Include placeholder for prompt templates
9. Document swapping instructions in comments (change dependency injection)
10. Verify class structure matches base.py interface exactly

**Prerequisites:** Story 3.3 (Template-Based Content Generator)

**Technical Notes:**
- Stub only - no actual implementation required
- Architecture supports future AI without code refactoring
- Provider parameter future-proofs for multiple LLM vendors
- Same interface as TemplateGenerator ensures drop-in replacement

---

### Story 3.5: Recommendation Engine

As a platform,
I want to combine persona assignment with content generation,
So that I can deliver complete personalized recommendations with rationales.

**Acceptance Criteria:**
1. Create `services/recommendations.py` module
2. Define `Recommendation` Pydantic model (content, rationale, persona, confidence)
3. Implement `generate_recommendations(db, user_id, generator, window_days)` async function
4. Process flow:
   - Call `assign_persona()` to get persona type, confidence, and signals
   - Call `generator.generate_education()` to get top 3 content items
   - For each item, call `generator.generate_rationale()` with signals
   - Build `Recommendation` objects combining content + rationale
5. Return list of recommendations with full traceability
6. Use dependency injection for generator (template by default)
7. Add error handling for missing users or failed signal computation
8. Support both 30d and 180d windows
9. Verify complete workflow: signals → persona → content → rationale
10. Test with synthetic users (should return 3 recommendations in <500ms)

**Prerequisites:** Story 3.4 (LLM Generator Interface)

**Technical Notes:**
- Generator parameter allows template/LLM swap at runtime
- Each recommendation includes full decision trace
- Confidence score from persona assignment
- Complete explainability: signals + persona + rationale
- Target <500ms total processing time

---

## Epic 4: API Layer & Backend Services

**Goal:** Build REST API endpoints that expose all backend functionality to the frontend.

**Value Proposition:** Makes backend features accessible through clean REST APIs with proper error handling, validation, and documentation. Enables frontend development.

**Technical Scope:**
- Pydantic schemas for request/response
- User management endpoints
- Account and transaction endpoints
- Insights endpoint with recommendations
- Global error handling and CORS configuration

---

### Story 4.1: API Schemas & Configuration

As a developer,
I want Pydantic schemas and API configuration,
So that I have type-safe request/response models and proper CORS setup.

**Acceptance Criteria:**
1. Create `schemas/user.py` with UserCreate, UserResponse models
2. Create `schemas/account.py` with AccountResponse model
3. Create `schemas/transaction.py` with TransactionResponse model
4. Create `schemas/insight.py` with RecommendationResponse model
5. All response models use snake_case field names
6. Dates serialized as ISO 8601 strings
7. Currency amounts as integers (cents)
8. Create `config.py` with Pydantic Settings:
   - DATABASE_URL
   - LOG_LEVEL
   - CORS_ORIGINS
9. Update `main.py` with CORS middleware for localhost:5173 and localhost:3000
10. Add global exception handler for unhandled errors
11. Verify schemas validate correctly with test data

**Prerequisites:** Story 3.5 (Recommendation Engine)

**Technical Notes:**
- Use Pydantic v2 syntax
- CORS allows all methods/headers for localhost
- Global handler logs errors and returns 500 with generic message
- Settings loaded from environment variables

---

### Story 4.2: User & Consent Endpoints

As a developer,
I want user creation and consent management endpoints,
So that the frontend can register users and track consent.

**Acceptance Criteria:**
1. Create `routers/users.py` module
2. Implement `POST /users` endpoint:
   - Accept UserCreate schema (name, email)
   - Generate UUID for user
   - Set created_at to current timestamp
   - Save to database
   - Return UserResponse
3. Implement `POST /consent` endpoint:
   - Accept user_id and consent boolean
   - Update user's consent field
   - Return updated UserResponse
4. Add HTTPException for user not found (404)
5. Add Pydantic validation for email format
6. Use async database session from get_db() dependency
7. Register router with FastAPI app in main.py
8. Test endpoints manually with curl or similar
9. Verify OpenAPI docs generated correctly at /docs
10. Confirm consent field updates in database

**Prerequisites:** Story 4.1 (API Schemas & Configuration)

**Technical Notes:**
- POST not GET for data modification
- Use UUID4 for user IDs
- Email validation built into Pydantic
- Async route handlers with Depends(get_db)

---

### Story 4.3: Account & Transaction Endpoints

As a developer,
I want to retrieve user accounts and transactions via API,
So that the frontend can display financial data.

**Acceptance Criteria:**
1. Create `routers/accounts.py` module
2. Implement `GET /accounts/{user_id}` endpoint:
   - Query all accounts for user_id
   - Return list of AccountResponse
   - Include balance, type, subtype, mask
   - Credit cards include limit and APR
3. Create `routers/transactions.py` module
4. Implement `GET /transactions/{user_id}` endpoint:
   - Accept query params: limit (default 100), offset (default 0)
   - Query transactions for user's accounts
   - Order by date descending (newest first)
   - Apply pagination
   - Return list of TransactionResponse
5. Add 404 error if user not found
6. Register both routers with FastAPI app
7. Test with synthetic data (should return realistic results)
8. Verify pagination works (offset=100 returns second page)
9. Confirm OpenAPI docs include query parameters
10. Check response time <100ms for typical queries

**Prerequisites:** Story 4.2 (User & Consent Endpoints)

**Technical Notes:**
- Join accounts table to filter transactions by user
- Pagination prevents large result sets
- Include pending field in transaction response
- Amount in cents (positive = debit, negative = credit)

---

### Story 4.4: Insights Endpoint

As a developer,
I want an insights endpoint that returns personalized recommendations,
So that the frontend can display financial education.

**Acceptance Criteria:**
1. Create `routers/insights.py` module
2. Initialize TemplateGenerator as module-level singleton
3. Implement `GET /insights/{user_id}` endpoint:
   - Accept query param: window (default "30d", options: "30d", "180d")
   - Parse window to days (30 or 180)
   - Call generate_recommendations() with user_id, generator, window_days
   - Return RecommendationResponse with:
     - user_id
     - window
     - persona type
     - confidence
     - list of recommendations (content + rationale)
4. Add 404 error if user not found
5. Add 500 error with logging if recommendation generation fails
6. Register router with FastAPI app
7. Test with synthetic users (should return 3 recommendations)
8. Verify rationales include data citations
9. Confirm response time <5 seconds (target from PRD)
10. Check OpenAPI docs show window parameter options

**Prerequisites:** Story 4.3 (Account & Transaction Endpoints)

**Technical Notes:**
- Generator initialized once (not per request)
- Window validation: only "30d" or "180d" accepted
- Complete recommendation pipeline: signals → persona → content → rationale
- Full traceability in response for debugging

---

## Epic 5: Frontend User Experience

**Goal:** Create the Svelte 5 frontend that delivers financial insights to users.

**Value Proposition:** Provides an intuitive, responsive interface for users to view their accounts, transactions, and personalized financial education. Showcases the platform's capabilities.

**Technical Scope:**
- API client for backend communication
- Dashboard with account overview
- Transaction list view
- Insights page with recommendations
- Operator view for inspecting users

---

### Story 5.1: API Client & Type Definitions

As a frontend developer,
I want a typed API client for backend communication,
So that I can easily fetch data with type safety.

**Acceptance Criteria:**
1. Create `lib/types/index.ts` with TypeScript interfaces:
   - User, Account, Transaction
   - Persona, Recommendation, Rationale
   - Match backend schema field names (snake_case)
2. Create `lib/api/client.ts` with fetch wrapper functions:
   - `fetchAccounts(userId): Promise<Account[]>`
   - `fetchTransactions(userId, limit?, offset?): Promise<Transaction[]>`
   - `fetchInsights(userId, window?): Promise<InsightsResponse>`
3. Use environment variable API_BASE_URL from .env
4. Add error handling for failed requests
5. Parse JSON responses automatically
6. Include proper TypeScript return types
7. Handle 404 and 500 errors with user-friendly messages
8. Add request timeout (10 seconds)
9. Verify client connects to localhost:8000 backend
10. Test with real API calls to synthetic data

**Prerequisites:** Story 4.4 (Insights Endpoint)

**Technical Notes:**
- Use native fetch API (no axios needed)
- Environment variable access via import.meta.env in Vite
- snake_case for API compatibility, convert to camelCase if needed
- Async/await pattern for all functions

---

### Story 5.2: Dashboard Page

As a user,
I want to see my account balances and recent activity,
So that I understand my current financial situation.

**Acceptance Criteria:**
1. Create `routes/dashboard/+page.svelte`
2. Use Svelte 5 runes ($state, $derived) for state management
3. Display user selector dropdown (choose from synthetic users)
4. Fetch and display accounts:
   - Show account name, type, balance
   - Format currency with $ and 2 decimals
   - Highlight credit cards with utilization percentage
   - Use shadcn Card components
5. Show account summary:
   - Total assets (checking + savings)
   - Total liabilities (credit card balances)
   - Net worth
6. Display recent transactions (last 10):
   - Date, merchant, category, amount
   - Use shadcn Table component
7. Add loading states during API calls
8. Handle errors gracefully with error messages
9. Responsive design (mobile and desktop)
10. Verify works with multiple synthetic users

**Prerequisites:** Story 5.1 (API Client & Type Definitions)

**Technical Notes:**
- Use $state for selected user ID
- Use $derived for computed net worth
- Svelte 5 runes replace stores
- Tailwind v4 for styling
- shadcn-svelte Card and Table components

---

### Story 5.3: Transactions Page

As a user,
I want to view my full transaction history with filtering,
So that I can track my spending patterns.

**Acceptance Criteria:**
1. Create `routes/transactions/+page.svelte`
2. Display full transaction list with pagination:
   - Date, merchant, category, amount, status (pending/cleared)
   - Sort by date descending
   - Use shadcn Table with pagination controls
3. Implement category filter dropdown (all categories from data)
4. Implement date range filter (last 30 days, 90 days, 180 days, all)
5. Show category spending breakdown:
   - Pie chart or bar chart showing spend by category
   - Total spend per category
6. Handle pagination (load more transactions)
7. Format amounts with debit (red) and credit (green) colors
8. Add search by merchant name
9. Responsive table (collapse columns on mobile)
10. Test with high transaction volume users

**Prerequisites:** Story 5.2 (Dashboard Page)

**Technical Notes:**
- Client-side filtering for categories
- Use offset pagination with API
- Consider using Chart.js or similar for visualization
- $state for filters and pagination
- Handle empty states (no transactions)

---

### Story 5.4: Insights Page

As a user,
I want to see my financial persona and personalized recommendations,
So that I can learn how to improve my financial health.

**Acceptance Criteria:**
1. Create `routes/insights/+page.svelte`
2. Display persona assignment:
   - Persona name (e.g., "High Utilization")
   - Confidence percentage
   - Plain-language description of what persona means
   - Use shadcn Badge for persona type
3. Display recommendations (3 cards):
   - Each recommendation in shadcn Card
   - Title, summary, full body text
   - Rationale with data citations
   - Call-to-action button
4. Show data citations clearly:
   - "Based on your card ending in 4523 at 68% utilization"
   - "You have 5 recurring subscriptions totaling $87/month"
5. Include disclaimer: "This is educational content, not financial advice"
6. Add window selector (30 days vs 180 days)
7. Loading state during insights generation
8. Handle case where no recommendations available
9. Make recommendation cards expandable (collapsed by default)
10. Verify rationales match user's actual data

**Prerequisites:** Story 5.3 (Transactions Page)

**Technical Notes:**
- Use shadcn Alert for disclaimer
- Badge colors per persona type
- Expandable Card components
- $state for selected window (30d/180d)
- Parse markdown in recommendation body if needed

---

### Story 5.5: Operator View

As a developer/operator,
I want to inspect any user's signals and recommendations,
So that I can verify the system is working correctly.

**Acceptance Criteria:**
1. Create `routes/operator/+page.svelte`
2. Display list of all synthetic users
3. Allow selecting a user to inspect
4. Show raw behavioral signals for selected user:
   - Subscription detection results
   - Savings analysis data
   - Credit utilization details
   - Income stability metrics
5. Display persona matching logic:
   - Which persona matched and why
   - Confidence score breakdown
   - Failed persona checks (if any)
6. Show recommendation generation details:
   - Content items considered
   - Relevance scoring
   - Final selections
7. Display complete decision trace in JSON format (collapsible)
8. Add "Refresh" button to recompute signals
9. Use monospace font for JSON data
10. Verify shows complete traceability for debugging

**Prerequisites:** Story 5.4 (Insights Page)

**Technical Notes:**
- Read-only view (no data modification)
- Use <pre> tags for JSON display
- Consider JSON viewer library for better formatting
- Useful for demo and debugging
- Not user-facing (operator/developer tool)

---

## Epic 6: Guardrails & Quality Assurance

**Goal:** Implement safety features and verify system quality.

**Value Proposition:** Ensures ethical, reliable recommendations with proper tone, consent tracking, and comprehensive documentation. Validates system meets all PRD requirements.

**Technical Scope:**
- Tone checking (no shaming language)
- Consent verification
- Evaluation harness (coverage, explainability, latency)
- Comprehensive documentation

---

### Story 6.1: Guardrails Implementation

As a platform,
I want to enforce ethical guidelines and tone standards,
So that all recommendations are respectful and appropriate.

**Acceptance Criteria:**
1. Create `utils/guardrails.py` module
2. Define `SHAME_PATTERNS` list with regex patterns for:
   - "you're overspending"
   - "bad financial habits"
   - "irresponsible"
   - "careless"
   - "wasting money"
   - "poor choices"
3. Implement `check_tone(text)` function:
   - Returns (passed: bool, violations: list)
   - Checks text against shame patterns
   - Case-insensitive matching
4. Implement `check_consent(user_consent)` function:
   - Returns True if user gave consent
5. Define `DISCLAIMER` constant with financial advice disclaimer
6. Add tone checking to rationale generation
7. Add disclaimer to all recommendation responses
8. Test with edge cases (boundary language)
9. Verify catches shaming language in content
10. Confirm all recommendations include disclaimer

**Prerequisites:** Story 5.5 (Operator View)

**Technical Notes:**
- Regex patterns for flexible matching
- Applied during content generation
- Logs violations but doesn't block (development mode)
- Disclaimer appended to every insight response

---

### Story 6.2: Evaluation Harness

As a developer,
I want to measure system performance against PRD requirements,
So that I can verify quality and identify issues.

**Acceptance Criteria:**
1. Create evaluation script `scripts/evaluate.py`
2. Measure **Coverage**: % of users with persona + ≥3 detected signals
3. Measure **Explainability**: % of recommendations with rationales and data points
4. Measure **Latency**: Average time to generate recommendations
5. Measure **Auditability**: % of recommendations with complete decision trace
6. Run evaluation against all synthetic users
7. Generate metrics JSON file with results
8. Calculate summary statistics:
   - Total users evaluated
   - Average signals per user
   - Persona distribution
   - P50/P95/P99 latency
9. Print results to console in readable format
10. Verify meets targets: 100% coverage, 100% explainability, <5s latency

**Prerequisites:** Story 6.1 (Guardrails Implementation)

**Technical Notes:**
- Run as standalone script: `uv run python scripts/evaluate.py`
- Query database for all users
- Time each recommendation generation
- Output to `data/evaluation_results.json`
- CLI command for easy execution

---

### Story 6.3: Documentation & Polish

As a developer,
I want comprehensive documentation of the system,
So that others can understand design decisions and limitations.

**Acceptance Criteria:**
1. Create `docs/DECISION_LOG.md`:
   - Why SQLite (local-first, WAL mode)
   - Why template-based content (zero cost, explainability)
   - Why no caching (on-demand, always current)
   - Why no testing framework (manual verification)
2. Create `docs/SCHEMA.md`:
   - Entity relationship diagram (text/ASCII)
   - Table descriptions
   - Index strategy
   - Query patterns
3. Create `docs/LIMITATIONS.md`:
   - Not for production scale (50-100 users max)
   - No real financial data
   - Template content less personalized than AI
   - No authentication
4. Update root README.md with:
   - Quick start commands
   - Architecture overview
   - Features list
   - Evaluation results
5. Add docstrings to all public functions
6. Run linters on all code: `ruff check` and `biome check`
7. Fix any linting violations
8. Verify both backend and frontend start with documented commands
9. Test complete user flow end-to-end
10. Create final summary of what was delivered

**Prerequisites:** Story 6.2 (Evaluation Harness)

**Technical Notes:**
- Markdown format for all docs
- Follow architecture.md documentation standards
- Docstrings use Google style
- README includes copy-paste commands
- Linting must pass 100%

---

## Story Guidelines Reference

**Story Format:**

```
**Story [EPIC.N]: [Story Title]**

As a [user type],
I want [goal/desire],
So that [benefit/value].

**Acceptance Criteria:**
1. [Specific testable criterion]
2. [Another specific criterion]
3. [etc.]

**Prerequisites:** [Dependencies on previous stories, if any]
```

**Story Requirements:**

- **Vertical slices** - Complete, testable functionality delivery
- **Sequential ordering** - Logical progression within epic
- **No forward dependencies** - Only depend on previous work
- **AI-agent sized** - Completable in 2-4 hour focused session
- **Value-focused** - Integrate technical enablers into value-delivering stories

---

**For implementation:** Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown.

---

## Implementation Sequence

### Phase 1: Foundation (Week 1)

**Goal:** Establish working infrastructure for all subsequent development

**Stories (Sequential):**
1. Story 1.3: Database Schema & Models
2. Story 1.4: Synthetic Data Generator

**Status:** Stories 1.1 and 1.2 (Backend/Frontend Setup) already complete ✅

**Deliverable:** Working database with 50 synthetic users, all models defined

**Parallel Opportunities:** None (sequential dependencies)

---

### Phase 2: Core Analytics Engine (Week 2)

**Goal:** Build the intelligence layer that detects financial behavior patterns

**Stories (Sequential order, but can parallelize some):**
1. Story 2.1: Subscription Detection
2. Story 2.2: Savings Analysis
3. Story 2.3: Credit Utilization Analysis
4. Story 2.4: Income Stability Analysis
5. Story 2.5: Signal Computation Service

**Parallelization Strategy:**
- Stories 2.1-2.4 CAN run in parallel (independent signal detection functions)
- Story 2.5 MUST wait for 2.1-2.4 (orchestrates all signals)
- **Recommended:** Run 2.1-2.4 in parallel with 4 agents, then 2.5

**Deliverable:** Complete behavioral signal detection for all personas

**Gate:** Verify signals compute in <200ms per user before continuing

---

### Phase 3: Persona & Content (Week 3)

**Goal:** Transform signals into actionable recommendations

**Stories (Sequential):**
1. Story 3.1: Persona Assignment Logic
2. Story 3.2: Content Catalog Creation
3. Story 3.3: Template-Based Content Generator
4. Story 3.4: LLM Generator Interface
5. Story 3.5: Recommendation Engine

**Parallelization Strategy:**
- Stories 3.3 and 3.4 CAN run in parallel (independent generators)
- Story 3.2 (Content Catalog) could start in parallel with 3.1 if copywriting resource available
- **Recommended:** 3.1 → 3.2 → (3.3 + 3.4 parallel) → 3.5

**Deliverable:** End-to-end recommendation generation with full explainability

**Gate:** Verify 100% of users get persona + 3 recommendations before continuing

---

### Phase 4: API Layer (Week 4)

**Goal:** Expose backend functionality through REST APIs

**Stories (Partially parallel):**
1. Story 4.1: API Schemas & Configuration
2. Story 4.2: User & Consent Endpoints
3. Story 4.3: Account & Transaction Endpoints
4. Story 4.4: Insights Endpoint

**Parallelization Strategy:**
- Story 4.1 MUST complete first (schemas needed by all)
- Stories 4.2 and 4.3 CAN run in parallel (independent endpoints)
- Story 4.4 depends on 4.1 but independent of 4.2/4.3
- **Recommended:** 4.1 → (4.2 + 4.3 + 4.4 parallel)

**Deliverable:** Complete REST API with OpenAPI documentation

**Gate:** Verify <5s response time for insights endpoint before continuing

---

### Phase 5: Frontend (Week 5)

**Goal:** Build user-facing interface and operator tools

**Stories (Sequential with some parallel):**
1. Story 5.1: API Client & Type Definitions
2. Story 5.2: Dashboard Page
3. Story 5.3: Transactions Page
4. Story 5.4: Insights Page
5. Story 5.5: Operator View

**Parallelization Strategy:**
- Story 5.1 MUST complete first (types and client needed by all pages)
- Stories 5.2, 5.3, 5.4, 5.5 CAN run in parallel (independent pages)
- **Recommended:** 5.1 → (5.2 + 5.3 + 5.4 + 5.5 parallel with 4 agents)

**Deliverable:** Complete Svelte 5 application with all views

**Gate:** Manual testing of complete user flow before continuing

---

### Phase 6: Quality & Documentation (Week 6)

**Goal:** Ensure quality, safety, and comprehensive documentation

**Stories (Sequential):**
1. Story 6.1: Guardrails Implementation
2. Story 6.2: Evaluation Harness
3. Story 6.3: Documentation & Polish

**Parallelization Strategy:**
- Stories must run sequentially (6.2 validates 6.1, 6.3 documents both)
- **Recommended:** Sequential execution

**Deliverable:** Production-ready demo with full documentation

**Gate:** All evaluation metrics meet targets (100% coverage, 100% explainability, <5s latency)

---

## Development Phases Summary

| Phase | Duration | Stories | Parallel Work | Key Deliverable |
|-------|----------|---------|---------------|-----------------|
| Phase 1 | Week 1 | 2 | None | Database + synthetic data |
| Phase 2 | Week 2 | 5 | 4 stories in parallel | Behavioral signal detection |
| Phase 3 | Week 3 | 5 | 2 stories in parallel | Recommendation engine |
| Phase 4 | Week 4 | 4 | 3 stories in parallel | REST API |
| Phase 5 | Week 5 | 5 | 4 stories in parallel | Frontend UI |
| Phase 6 | Week 6 | 3 | None | Documentation + quality |
| **Total** | **6 weeks** | **24 stories** | **13 parallel opportunities** | **Complete platform** |

**Note:** Stories 1.1 and 1.2 already complete, reducing total from 24 to 22 remaining stories.

---

## Dependency Graph

```
Phase 1 (Foundation)
  [1.3] Database Schema
    ↓
  [1.4] Synthetic Data Generator

Phase 2 (Signal Detection)
  [1.4]
    ↓
  [2.1] Subscription ──┐
  [2.2] Savings ───────┤
  [2.3] Credit ────────┤ (Can parallelize)
  [2.4] Income ────────┘
    ↓
  [2.5] Signal Computation Service

Phase 3 (Personas & Content)
  [2.5]
    ↓
  [3.1] Persona Assignment
    ↓
  [3.2] Content Catalog
    ↓
  [3.3] Template Generator ──┐ (Can parallelize)
  [3.4] LLM Interface ───────┘
    ↓
  [3.5] Recommendation Engine

Phase 4 (API Layer)
  [3.5]
    ↓
  [4.1] API Schemas
    ↓
  [4.2] User Endpoints ──┐
  [4.3] Account/Txn ─────┤ (Can parallelize)
  [4.4] Insights ────────┘

Phase 5 (Frontend)
  [4.4]
    ↓
  [5.1] API Client
    ↓
  [5.2] Dashboard ───┐
  [5.3] Transactions ┤
  [5.4] Insights ────┤ (Can parallelize)
  [5.5] Operator ────┘

Phase 6 (Quality)
  [5.5]
    ↓
  [6.1] Guardrails
    ↓
  [6.2] Evaluation
    ↓
  [6.3] Documentation
```

---

## Recommended Agent Allocation

**Single Agent Development:**
- Follow phases sequentially
- Complete all stories in order
- ~24 stories × 2-4 hours = 48-96 hours total work
- Timeline: 6 weeks with part-time development

**Team of 4 Agents:**
- **Week 1:** 1 agent on Phase 1 (2 stories)
- **Week 2:** 4 agents on Phase 2 (stories 2.1-2.4 parallel, then 2.5)
- **Week 3:** 2 agents on Phase 3 (3.3 + 3.4 parallel)
- **Week 4:** 3 agents on Phase 4 (4.2 + 4.3 + 4.4 parallel after 4.1)
- **Week 5:** 4 agents on Phase 5 (5.2-5.5 parallel after 5.1)
- **Week 6:** 1 agent on Phase 6 (sequential)
- Timeline: 4-5 weeks with parallel work

**Maximum Parallelization:**
- Peak concurrency: 4 agents in Phases 2 and 5
- Critical path: 17 sequential stories
- Minimum timeline: ~4 weeks with aggressive parallelization

---

## Development Guidance

### Getting Started

**First Story to Implement:** Story 1.3 (Database Schema & Models)

**Key files to create first:**
1. `spendsense-backend/src/spendsense/database.py` - Database connection and session management
2. `spendsense-backend/src/spendsense/models/` - All SQLAlchemy model files
3. `spendsense-backend/data/` - Directory for SQLite database and generated data

**Prerequisites before starting:**
- ✅ Python 3.13 installed
- ✅ uv package manager installed
- ✅ Backend project initialized (Story 1.1 - Complete)
- ✅ Frontend project initialized (Story 1.2 - Complete)

**Initial development commands:**
```bash
# Backend
cd spendsense-backend
uv sync
uv run uvicorn spendsense.main:app --reload

# Frontend (separate terminal)
cd spendsense-frontend
bun install
bun run dev
```

---

### Technical Notes for Developers

**Architecture Decisions to Follow:**

1. **Database Pattern:**
   - SQLite with WAL mode for concurrent reads
   - No migrations - use `create_all()` for fresh schema
   - Indexes on high-query columns (account_id, date)
   - Store currency as integers (cents)

2. **API Pattern:**
   - REST with plural resource names (`/users`, `/accounts`)
   - Direct JSON responses (no wrapper objects)
   - ISO 8601 for dates
   - HTTPException for errors
   - CORS for localhost only

3. **Frontend Pattern:**
   - Svelte 5 runes ($state, $derived, $effect)
   - shadcn-svelte components (not custom)
   - Tailwind v4 (no @apply)
   - TypeScript for all files
   - snake_case for API compatibility

4. **Content Generation:**
   - Template-based by default (YAML catalog)
   - Abstract base class for future LLM swap
   - No external API calls required

---

### Watch Out For

**Common Pitfalls:**

1. **Currency Formatting:**
   - ❌ Store as floats: `balance: 50.00`
   - ✅ Store as integers: `balance: 5000` (cents)
   - Convert to dollars only for display: `$${balance / 100}.toFixed(2)}`

2. **Transaction Amounts:**
   - Positive = debit (money out)
   - Negative = credit (money in)
   - Income transactions are negative
   - Follow this convention consistently

3. **Persona Priority:**
   - MUST check in exact order: high_utilization → variable_income → subscription_heavy → savings_builder → balanced
   - First match wins
   - Don't change order (affects results)

4. **Signal Computation:**
   - Compute on-demand (no caching per architecture)
   - Must complete in <200ms per user
   - Use indexed queries on transactions

5. **Svelte 5 Runes:**
   - Use `$state` not writable stores
   - Use `$derived` for computed values
   - Use `$effect` for side effects
   - Don't mix runes with legacy stores

---

### Success Metrics Per Phase

**Phase 1 Complete When:**
- ✅ Database creates all tables without errors
- ✅ 50 synthetic users generated with deterministic seed
- ✅ Each user has 1-3 accounts
- ✅ Each account has 20-100 transactions
- ✅ Data loads into database successfully

**Phase 2 Complete When:**
- ✅ All 4 signal types detect patterns
- ✅ Subscription detection finds recurring merchants
- ✅ Credit utilization calculates correctly
- ✅ Income frequency classified accurately
- ✅ Signal computation completes in <200ms per user

**Phase 3 Complete When:**
- ✅ 100% of users assigned to a persona
- ✅ Content catalog has ≥10 items
- ✅ Template generator returns 3 recommendations per user
- ✅ Every recommendation has rationale with data citations
- ✅ Complete workflow runs in <500ms

**Phase 4 Complete When:**
- ✅ All endpoints respond correctly
- ✅ OpenAPI docs generate automatically at /docs
- ✅ Insights endpoint returns in <5s
- ✅ CORS configured for localhost
- ✅ Error handling returns proper status codes

**Phase 5 Complete When:**
- ✅ All 5 pages render without errors
- ✅ Dashboard displays accounts and balances
- ✅ Transactions page shows paginated list
- ✅ Insights page shows persona + 3 recommendations
- ✅ Operator view displays raw signals

**Phase 6 Complete When:**
- ✅ Tone checking catches shaming language
- ✅ Evaluation harness runs and outputs metrics
- ✅ All metrics meet targets (100% coverage, <5s latency)
- ✅ Documentation complete (README, DECISION_LOG, SCHEMA, LIMITATIONS)
- ✅ Linting passes (ruff check, biome check)

---

### Risk Mitigation

**Risk 1: Slow Signal Computation**
- **Symptom:** Insights endpoint takes >5 seconds
- **Solution:** Add indexes on transactions (account_id, date)
- **Mitigation:** Test with 100-user dataset early

**Risk 2: Persona Misclassification**
- **Symptom:** Users assigned wrong persona
- **Solution:** Verify thresholds match PRD exactly
- **Mitigation:** Use operator view to inspect signals

**Risk 3: Frontend/Backend Mismatch**
- **Symptom:** Type errors, undefined fields
- **Solution:** Keep TypeScript interfaces synced with Pydantic schemas
- **Mitigation:** Use OpenAPI codegen or manual validation

**Risk 4: Content Catalog Quality**
- **Symptom:** Generic or unhelpful recommendations
- **Solution:** Review PRD examples, ensure actionable advice
- **Mitigation:** Test with diverse user personas

**Risk 5: Dependency Conflicts**
- **Symptom:** Stories blocked waiting for incomplete dependencies
- **Solution:** Follow dependency graph strictly
- **Mitigation:** Complete foundation (Phase 1) thoroughly before Phase 2

---

### Testing Strategy

**Manual Testing Approach:**
(No automated tests per PRD requirements)

1. **Unit-Level Validation:**
   - Run each function with sample data
   - Verify output matches expected format
   - Check edge cases (zero, null, missing data)

2. **Integration Testing:**
   - Test API endpoints with curl or Postman
   - Verify database queries return correct data
   - Check frontend displays API responses correctly

3. **End-to-End Validation:**
   - Select synthetic user
   - View accounts and transactions
   - Generate insights
   - Verify recommendations match user's data

4. **Performance Testing:**
   - Time signal computation (target <200ms)
   - Time insights endpoint (target <5s)
   - Test with 50 users, then 100 users

5. **Quality Checks:**
   - Run linters: `ruff check`, `biome check`
   - Review code for naming conventions
   - Verify all acceptance criteria met

---

### Handoff to Development

**Ready to Start Development When:**
- ✅ Epic breakdown reviewed and approved
- ✅ Technical stack confirmed (Python 3.13, Svelte 5, etc.)
- ✅ Development environment set up
- ✅ Architecture document referenced
- ✅ First story identified (Story 1.3)

**Recommended Development Flow:**
1. Pick next story from current phase
2. Read acceptance criteria carefully
3. Review technical notes and prerequisites
4. Implement incrementally (commit frequently)
5. Validate against acceptance criteria
6. Mark story complete only when ALL criteria met
7. Move to next story

**Communication Guidelines:**
- Update progress after each story completion
- Report blockers immediately
- Ask questions about ambiguous requirements
- Review dependency graph before starting new phase

---

