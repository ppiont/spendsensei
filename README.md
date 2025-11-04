# SpendSense

**Gauntlet Week 4 - Full-Stack Financial Education Platform**

SpendSense is a personalized financial education platform that analyzes user spending patterns and provides tailored recommendations to improve financial health. Built with FastAPI, SvelteKit, and SQLite.

## Project Status

**Current Status:** ✅ **EPICS 1-5 COMPLETE** (5/6 epics done)

### Completed Epics

- ✅ **Epic 1: Foundation** - Backend/Frontend setup, Database, Synthetic data
- ✅ **Epic 2: Signal Detection** - Subscription detection, Savings analysis, Credit utilization, Income analysis
- ✅ **Epic 3: Persona System** - Persona assignment, Content catalog, Recommendation engine
- ✅ **Epic 4: API Layer** - REST API with schemas, endpoints for users/accounts/transactions/insights
- ✅ **Epic 5: Frontend** - Dashboard, Transactions, Insights pages, Operator view

### Remaining Work

- 🚧 **Epic 6: Quality** - Guardrails, Evaluation harness, Documentation polish (3 stories drafted)

## Quick Start

### Backend (FastAPI)

```bash
cd spendsense-backend
uv sync
uv run uvicorn spendsense.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

### Frontend (SvelteKit)

```bash
cd spendsense-frontend
npm install
npm run dev
```

Visit: http://localhost:5173/

## Features

### For Users
- **Dashboard** - View account balances, net worth, and recent transactions
- **Transaction History** - Full transaction list with filtering and category breakdown
- **Personalized Insights** - AI-generated financial recommendations based on spending patterns
- **Persona Assignment** - Automatic classification into financial personas (high_utilization, variable_income, etc.)

### For Developers
- **Operator View** - Internal inspection tool showing complete decision traceability
- **API Documentation** - Auto-generated OpenAPI docs at /docs
- **Synthetic Data** - 5 test users with realistic financial data
- **Type Safety** - Full TypeScript types matching backend Pydantic schemas

## Architecture

### Backend Stack
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Async ORM with SQLite
- **Pydantic** - Data validation and settings management
- **Python 3.11+** - Modern Python features

### Frontend Stack
- **SvelteKit** - Full-stack web framework
- **Svelte 5** - Latest with runes ($state, $derived, $effect)
- **TypeScript** - Type-safe API client
- **Vite** - Fast build tool

### Key Components
1. **Signal Detection** - Analyzes transactions for behavioral patterns
2. **Persona Engine** - Assigns users to financial personas
3. **Content Catalog** - Educational content mapped to personas
4. **Recommendation Engine** - Generates personalized insights

## Project Structure

```
spendsensei/
├── spendsense-backend/          # FastAPI backend
│   ├── src/spendsense/
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── generators/          # Content generation
│   │   ├── schemas/             # Pydantic models
│   │   └── models/              # SQLAlchemy models
│   ├── data/                    # SQLite database
│   └── scripts/                 # Test scripts
├── spendsense-frontend/         # SvelteKit frontend
│   └── src/
│       ├── routes/              # Pages
│       └── lib/                 # API client & types
├── docs/                        # Project documentation
│   ├── PRD.md
│   ├── architecture.md
│   ├── epics.md
│   ├── sprint-status.yaml
│   └── stories/                 # User story files
└── bmad/                        # BMAD workflow system

```

## API Endpoints

- `POST /users` - Create new user
- `POST /users/consent` - Update user consent
- `GET /accounts/{user_id}` - Get user accounts
- `GET /transactions/{user_id}` - Get user transactions (paginated)
- `GET /insights/{user_id}?window=30` - Get personalized recommendations

## Test Users

The system includes 5 synthetic users with realistic financial data:

- Daniel Doyle (bdd640fb-0667-4ad1-9c80-317fa3b1799d)
- Mr. Andrew Foster (97d7a560-adb1-4670-ad9f-b00d4882d73c)
- Amber Cooper (37c86152-beed-4af9-80c5-9f30d1031424)
- Steven Taylor (dc268108-7140-41a1-afc2-ccfc9db7284b)
- Ashley Garcia (c7a9f33c-22d8-49d3-b3e4-f986f18cccdc)

## Development

### Running Tests

Backend tests are located in `spendsense-backend/scripts/test_*.py`:

```bash
# Run all feature tests
cd spendsense-backend
python scripts/test_signal_computation.py
python scripts/test_recommendation_engine.py
python scripts/test_account_transaction_endpoints.py
python scripts/test_insights_endpoint.py
```

### Code Generation

This project uses the BMAD (Business Model Accelerator Development) workflow system for structured development. See `bmad/` directory for workflow definitions.

## Documentation

- **PRD**: `docs/PRD.md` - Product Requirements Document
- **Architecture**: `docs/architecture.md` - Technical architecture decisions
- **Epics**: `docs/epics.md` - Epic and story breakdown
- **Sprint Status**: `docs/sprint-status.yaml` - Current development status
- **Stories**: `docs/stories/*.md` - Individual user story files

## License

Private project - Gauntlet Week 4

## Credits

Built with Claude Code by Peter Piont
