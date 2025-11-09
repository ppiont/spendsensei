# Claude Code Context - SpendSense

## Project Overview

SpendSense is a **full-stack financial education platform** that provides personalized recommendations based on behavioral analysis of user spending patterns. This is a **Gauntlet Week 4** project.

**Tech Stack:** FastAPI + SvelteKit + SQLite + TypeScript

**Current Status:** 5 of 6 epics complete (83% done)

## What's Been Built

### Completed (Epics 1-5)

✅ **Backend** (FastAPI)
- Complete REST API with 5 endpoints (users, accounts, transactions, insights)
- Behavioral signal detection (subscriptions, savings, credit, income)
- Persona assignment engine (5 persona types)
- Recommendation generation pipeline
- Content catalog with 12 educational items
- Async SQLAlchemy with SQLite
- 5 synthetic test users with realistic data

✅ **Frontend** (SvelteKit + Svelte 5)
- Dashboard page (account balances, net worth, recent transactions)
- Transactions page (filtering, pagination, category breakdown)
- Insights page (persona display, 3 personalized recommendations)
- Operator view (internal debugging tool with full traceability)
- Type-safe API client with TypeScript

### Remaining (Epic 6)

🚧 **Quality & Polish**
- Story 6.1: Guardrails implementation (drafted)
- Story 6.2: Evaluation harness (drafted)
- Story 6.3: Documentation polish (drafted)

## Key Directories

**NEW MODULE STRUCTURE** (Reorganized 2025-11-09 for Project Description compliance):

```
spendsense-backend/src/spendsense/
├── ingest/         # Data loading and validation
│   └── synthetic_generator.py
├── features/       # Signal detection and feature engineering
│   ├── types.py    # BehaviorSignals dataclass
│   ├── signals.py  # Orchestrator (compute_signals)
│   ├── income.py   # Income stability analysis
│   ├── savings.py  # Savings patterns
│   ├── credit.py   # Credit utilization
│   └── subscriptions.py  # Subscription detection
├── personas/       # Persona assignment logic
│   ├── types.py    # Persona priority and confidence scores
│   └── assignment.py  # Matching functions (assign_persona)
├── recommend/      # Recommendation engine
│   ├── types.py    # Content types, base classes
│   ├── engine.py   # StandardRecommendationEngine
│   ├── content_selection.py  # TemplateGenerator
│   ├── llm_generation.py     # LLMGenerator
│   └── legacy.py   # Backward compatibility
├── guardrails/     # Content safety and compliance
│   ├── consent.py  # Consent verification
│   ├── tone.py     # Shame pattern detection
│   ├── disclosure.py  # Standard disclaimers
│   └── eligibility.py # Product eligibility checks
├── ui/             # API endpoints (renamed from routers/)
│   ├── users.py
│   ├── accounts.py
│   ├── transactions.py
│   ├── insights.py
│   ├── operator.py
│   └── feedback.py
├── eval/           # Evaluation harness (placeholder)
├── schemas/        # Pydantic models for API
└── models/         # SQLAlchemy ORM models

spendsense-frontend/src/
├── routes/         # Pages (dashboard, transactions, insights, operator)
└── lib/
    ├── api/        # API client
    └── types/      # TypeScript types

docs/
├── PRD.md          # Product requirements
├── architecture.md # Technical decisions
├── epics.md        # Epic breakdown
├── sprint-status.yaml  # Current status
└── stories/        # Individual story files (*.md)
```

## Running the Application

### Backend
```bash
cd spendsense-backend
uv run uvicorn spendsense.main:app --reload --port 8000
```
Visit: http://localhost:8000/docs

### Frontend
```bash
cd spendsense-frontend
bun run dev
```
Visit: http://localhost:5173/

**IMPORTANT:** Always use `bun`/`bunx` instead of `npm`/`npx` for all frontend commands.

## Important Patterns

### Backend Patterns
- **Async/await** everywhere (AsyncSession, async def)
- **Pydantic** for schemas (snake_case, from_orm() converters)
- **Currency in cents** (integers, not floats)
- **Dates as datetime** objects, serialized to ISO 8601
- **Error handling** with HTTPException (404, 500)

### Frontend Patterns
- **Package manager**: ALWAYS use `bun`/`bunx` instead of `npm`/`npx` for all commands
- **Svelte 5 runes**: $state, $derived, $effect (not stores!)
- **Type safety**: Import types from $lib/types
- **API calls**: Use api.* from $lib/api/client
- **Currency**: Use formatCurrency() helper
- **Loading states**: Always show loading/error states

## Test Users

5 synthetic users with full transaction history:
- Daniel Doyle: bdd640fb-0667-4ad1-9c80-317fa3b1799d
- Mr. Andrew Foster: 97d7a560-adb1-4670-ad9f-b00d4882d73c
- Amber Cooper: 37c86152-beed-4af9-80c5-9f30d1031424
- Steven Taylor: dc268108-7140-41a1-afc2-ccfc9db7284b
- Ashley Garcia: c7a9f33c-22d8-49d3-b3e4-f986f18cccdc

## Recommendation Pipeline

The system follows this modular flow:

1. **Signal Detection** (`features/`)
   - `features/subscriptions.py` - detect_subscriptions()
   - `features/savings.py` - analyze_savings()
   - `features/credit.py` - analyze_credit()
   - `features/income.py` - analyze_income()
   - `features/signals.py` - compute_signals() orchestrates all

2. **Persona Assignment** (`personas/`)
   - `personas/assignment.py` - assign_persona()
   - Matches signals to persona types
   - Priority order: high_utilization → variable_income → debt_consolidator → subscription_heavy → savings_builder → balanced
   - Assigns confidence scores from `personas/types.py`

3. **Content Selection** (`recommend/`)
   - `recommend/content_selection.py` - TemplateGenerator
   - Loads content catalog (YAML)
   - Scores content by signal tag matching
   - Returns top 3 recommendations with rationales

4. **Recommendation Engine** (`recommend/engine.py`)
   - StandardRecommendationEngine
   - Orchestrates full pipeline with guardrails
   - Returns RecommendationResult with education + offers

## API Endpoints

```
POST   /users                   Create user
POST   /users/consent           Update consent
GET    /accounts/{user_id}      Get accounts
GET    /transactions/{user_id}  Get transactions (paginated)
GET    /insights/{user_id}      Get recommendations (window param)
```

## Development Workflow (BMAD)

This project uses BMAD workflows for structured development:
- Stories tracked in `docs/sprint-status.yaml`
- Story files in `docs/stories/*.md`
- Workflow definitions in `bmad/bmm/workflows/`
- Agents: SM (Scrum Master), Dev (Developer), etc.

## What to Know When Modifying

### Adding New Signals
1. Create detection function in appropriate `features/*.py` file
2. Call from `features/signals.py` - `compute_signals()`
3. Add fields to `BehaviorSignals` dataclass in `features/types.py`
4. Update persona matching in `personas/assignment.py`
5. Add content with matching tags to `data/content_catalog.yaml`

### Adding New Endpoints
1. Create router in `ui/*.py`
2. Register in `main.py`
3. Add schema to `schemas/*.py`
4. Create test script in `scripts/test_*.py`
5. Add TypeScript types to `frontend/src/lib/types/index.ts`
6. Add API function to `frontend/src/lib/api/client.ts`

### Adding New Pages
1. Create `routes/{page}/+page.svelte`
2. Use Svelte 5 runes ($state, $derived, $effect)
3. Import types from $lib/types
4. Use api.* from $lib/api/client
5. Add link to home page navigation

## Common Issues

- **CORS errors**: Check frontend is using VITE_API_BASE_URL=http://localhost:8000
- **Import errors**: Backend uses `from spendsense.*`, not relative imports
- **Currency display**: Always use formatCurrency(cents), not direct division
- **Svelte 5**: Don't use writable/readable stores, use runes instead
- **Type errors**: Make sure TypeScript types match backend Pydantic schemas

## Testing

All tests are Python scripts in `spendsense-backend/scripts/`:
- Run with: `python scripts/test_*.py`
- Tests use synthetic data from database
- All tests should pass before committing

## Next Steps (Epic 6)

If continuing with Epic 6:
1. **Guardrails** - Content safety, bias detection
2. **Evaluation** - Test harness for recommendation quality
3. **Documentation** - Polish all docs, add examples

## Questions?

Check these files:
- `docs/PRD.md` - Product requirements and user stories
- `docs/architecture.md` - Technical decisions and rationale
- `docs/epics.md` - Full epic and story breakdown
- `docs/sprint-status.yaml` - Current development status
