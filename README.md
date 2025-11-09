# SpendSense

**Personalized Financial Education Platform**

SpendSense analyzes your spending patterns and provides tailored financial recommendations to improve your financial health. Built with FastAPI, SvelteKit, and SQLite.

## Quick Start

### 1. Start the Backend

```bash
cd spendsense-backend
uv sync                              # Install dependencies
uv run uvicorn spendsense.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 2. Start the Frontend

```bash
cd spendsense-frontend
bun install                          # or: npm install
bun run dev                          # or: npm run dev
```

The app will be available at: http://localhost:5173

### 3. Explore the App

The database comes pre-loaded with 50 synthetic users with realistic financial data. Try switching between users in the dropdown to see different financial profiles!

## What Does SpendSense Do?

SpendSense provides personalized financial education by:

1. **Analyzing Spending Patterns** - Detects subscriptions, savings habits, credit usage, and income patterns
2. **Assigning Financial Personas** - Classifies users into personas like "High Utilization" or "Savings Builder"
3. **Generating Recommendations** - Provides 3 personalized educational items based on your financial behavior
4. **Tracking Progress** - Shows complete decision traceability in the Operator view

## Features

### Pages

- **Dashboard** (`/dashboard`) - Account balances, net worth, recent transactions
- **Transactions** (`/transactions`) - Full transaction history with filtering, search, and category breakdown
- **Insights** (`/insights`) - Personalized financial recommendations with explanations
- **Operator** (`/operator`) - Internal debugging view showing complete persona assignment and recommendation logic

### Key Capabilities

- Real-time persona assignment based on spending behavior
- Content catalog with 12 educational items mapped to financial signals
- Transaction categorization using Plaid-compliant two-level hierarchy
- Confidence scoring for all recommendations
- Complete audit trail of all decisions

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy** - Async ORM with SQLite
- **Pydantic** - Data validation and schemas
- **Python 3.11+**

### Frontend
- **SvelteKit** - Full-stack web framework
- **Svelte 5** - With runes ($state, $derived, $effect)
- **TypeScript** - Type-safe API client
- **Tailwind CSS** - Utility-first styling

## API Endpoints

```
POST   /users                     # Create user
POST   /users/consent             # Update consent
GET    /accounts/{user_id}        # Get accounts
GET    /transactions/{user_id}    # Get transactions (paginated)
GET    /insights/{user_id}        # Get recommendations (window param)
```

Full API documentation available at http://localhost:8000/docs

## Data Model

SpendSense uses a Plaid-compliant data model:

- **Users** - Basic user information and consent status
- **Accounts** - Depository accounts (checking, savings) and credit cards with balances, limits, and payment tracking
- **Transactions** - Two-level category hierarchy (primary + detailed), payment channels, merchant entity IDs
- **Personas** - Assigned personas with confidence scores
- **Content** - Educational content catalog with signal tags

## Project Structure

SpendSense follows a modular architecture with 8 core modules for clear separation of concerns:

```
spendsensei/
├── spendsense-backend/          # FastAPI backend
│   ├── src/spendsense/
│   │   ├── ingest/              # Data loading and validation
│   │   ├── features/            # Signal detection (subscriptions, savings, credit, income)
│   │   ├── personas/            # Persona assignment logic
│   │   ├── recommend/           # Recommendation engine and content selection
│   │   ├── guardrails/          # Content safety, consent, eligibility checks
│   │   ├── ui/                  # API endpoints (users, accounts, transactions, insights)
│   │   ├── eval/                # Evaluation harness and metrics
│   │   ├── schemas/             # Pydantic models for API
│   │   └── models/              # SQLAlchemy ORM models
│   ├── data/                    # SQLite database and content catalog
│   └── scripts/                 # Test and utility scripts
├── spendsense-frontend/         # SvelteKit frontend
│   └── src/
│       ├── routes/              # Pages (dashboard, transactions, insights, operator)
│       └── lib/                 # API client and TypeScript types
└── docs/                        # Project documentation (PRD, architecture, etc.)
```

## Development

### Regenerating Synthetic Data

```bash
cd spendsense-backend
uv run python scripts/init_and_load_data.py
```

This will:
1. Drop and recreate the database
2. Generate 50 users with realistic financial profiles
3. Create 1-3 accounts per user (checking, savings, credit cards)
4. Generate 20-100 transactions per account with realistic categories

### Running Tests

```bash
cd spendsense-backend
python scripts/test_signal_computation.py
python scripts/test_recommendation_engine.py
python scripts/test_insights_endpoint.py
```

### Understanding the Recommendation Pipeline

1. **Signal Detection** (`features/`) - Analyzes transactions for patterns (subscriptions, savings, credit, income)
2. **Persona Assignment** (`personas/`) - Matches signals to persona types with confidence scoring
3. **Content Selection** (`recommend/content_selection.py`) - Scores and selects relevant educational content
4. **Recommendation Engine** (`recommend/engine.py`) - Orchestrates the full pipeline with guardrails

## System Performance

SpendSense has been rigorously evaluated against all PRD success criteria:

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| **Coverage** | 100.00% | 100% | ✅ Pass |
| **Explainability** | 100.00% | 100% | ✅ Pass |
| **Latency (avg)** | 0.002s | <5s | ✅ Pass |
| **Auditability** | 100.00% | 100% | ✅ Pass |

**Evaluation Details:**
- Evaluated across 50 users generating 150 recommendations
- Latency percentiles: P50: 0.002s, P95: 0.003s, P99: 0.020s
- All metrics exceed targets by significant margins!

Run evaluation yourself:
```bash
cd spendsense-backend
python scripts/evaluate.py
```

Results saved to `data/evaluation_results.json`

## Documentation

- **README**: You are here!
- **PRD**: `docs/PRD.md` - Product Requirements Document
- **Architecture**: `docs/architecture.md` - Technical decisions and rationale
- **Decision Log**: `docs/DECISION_LOG.md` - Key architectural decisions (ADRs)
- **Schema**: `docs/SCHEMA.md` - Database schema and query patterns
- **Limitations**: `docs/LIMITATIONS.md` - Known constraints and scale limits
- **Epic Breakdown**: `docs/epics.md` - All 6 epics and ~20 user stories
- **Sprint Status**: `docs/sprint-status.yaml` - Current development status

## License

This is a Gauntlet Week 4 project.
