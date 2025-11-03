# Architecture

## Executive Summary

SpendSense is a financial behavior analysis platform built with a modern, AI-agnostic architecture. The system uses Python 3.13 + FastAPI for backend processing, Svelte 5 + SvelteKit for the frontend, and SQLite for local-first data storage. The architecture is designed for <5 second response times with 100% explainability for all recommendations.

**Project Context:**
- 6 implementation phases with ~20 stories
- 5 persona types based on behavioral signals
- Template-based content generation (swappable for LLM)
- Local-first, no external dependencies
- Target: 50-100 synthetic users

**Technology Correction:** Using Tailwind CSS v4 (latest)

## Project Initialization

**FIRST IMPLEMENTATION STORY**: Project setup must be completed before any feature development.

### Frontend Initialization

```bash
# Create SvelteKit project with sv CLI using Bun
bunx sv create spendsense-frontend
cd spendsense-frontend

# Install Tailwind CSS v4 with Bun
bun add -d tailwindcss@next @tailwindcss/vite@next

# Initialize shadcn-svelte with Tailwind v4 + Svelte 5 support
bunx shadcn-svelte@latest init

# Configure for Tailwind v4 when prompted
# Select components as needed: card, button, table, badge, etc.
```

**Starter provides:**
- ✅ SvelteKit 2.x project structure
- ✅ TypeScript configuration
- ✅ Vite build tooling
- ✅ ESLint + formatting setup (via sv add-ons)
- ✅ Modern component organization
- ✅ Bun as package manager (faster than npm)
- ✅ shadcn-svelte components (Svelte 5 + Tailwind v4 compatible)

### Backend Initialization

```bash
# Initialize Python project with uv
uv init spendsense-backend
cd spendsense-backend

# Install core dependencies
uv add "fastapi[standard]"  # Includes uvicorn
uv add sqlalchemy aiosqlite  # Database ORM + SQLite async driver
uv add pydantic faker        # Validation + synthetic data
uv add ruff                  # Linting and formatting

# Create src/spendsense/ module structure
# Configure pyproject.toml with Python 3.13
```

**Starter provides:**
- ✅ uv package management (10-100x faster than pip)
- ✅ pyproject.toml for dependencies
- ✅ Virtual environment handling
- ✅ Python 3.13 configuration

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| Backend Language | Python | 3.13.8 | All | Latest stable, free-threading support, JIT improvements |
| Backend Framework | FastAPI | 0.120.4 | All backend | Async support, automatic OpenAPI, matches PRD |
| Database | SQLite | 3.x (WAL mode) | All | Local-first, no server, fast for 50-100 users |
| ORM | SQLAlchemy | 2.0.44 | All backend | Async support, modern API, type safety |
| Python Package Manager | uv | Latest | All backend | 10-100x faster than pip, deterministic |
| Frontend Framework | SvelteKit | 2.48.4 | All frontend | Latest stable, App Router, SSR support |
| Frontend Language | TypeScript | 5.x | All frontend | Type safety, better DX |
| UI Framework | Svelte | 5.x (runes) | All frontend | Modern reactivity, performance, smaller bundles |
| Component Library | shadcn-svelte | Latest | All frontend | Svelte 5 + Tailwind v4 compatible, accessible |
| Styling | Tailwind CSS | 4.x (next) | All frontend | Latest version, Vite plugin, no @apply |
| JS Package Manager | Bun | Latest | All frontend | Faster than npm, native TypeScript |
| Build Tool | Vite | 5.x | All frontend | Fast HMR, optimized builds |
| Linting (Python) | ruff | Latest | All backend | Rust-based, extremely fast |
| Linting (JS/TS) | Biome | Latest | All frontend | Fast, opinionated |
| Synthetic Data | faker | Latest | Phase 1 | Deterministic data generation |
| API Pattern | REST | N/A | All client-facing | Simple, standard, matches PRD examples |
| API Response Format | Direct JSON | N/A | All endpoints | No wrapper, FastAPI standard |
| Date Format | ISO 8601 strings | N/A | All | Timezone-aware, JSON-friendly |
| Error Handling | HTTPException + handler | N/A | All backend | Consistent format, global catching |
| Signal Computation | On-demand | N/A | Phase 2-3 | No caching, always current, <5s achievable |
| Content Generation | Abstract base class | N/A | Phase 3 | Template → LLM swappable |
| Persona Priority | Fixed order | N/A | Phase 3 | Urgent financial issues first |
| State Management | Svelte 5 runes | N/A | All frontend | Modern, no external library |
| Authentication | None (demo) | N/A | N/A | Local demo only, not production |
| Testing | Manual only | N/A | All | No automated tests per requirement |
| Configuration | Pydantic Settings | N/A | All backend | .env support, type-safe |
| Logging | Python logging (text) | N/A | All | Simple, built-in, sufficient for demo |
| Development | Local only | N/A | All | No Docker, runs on laptop |

## Project Structure

```
spendsensei/
├── spendsense-backend/
│   ├── .env                          # Pydantic settings (DB path, log level)
│   ├── .python-version               # 3.13
│   ├── pyproject.toml                # uv config + dependencies
│   ├── ruff.toml                     # Linter config
│   ├── data/
│   │   ├── spendsense.db             # SQLite database (WAL mode)
│   │   ├── users.json                # Generated synthetic data
│   │   └── content_catalog.yaml      # Static education content
│   ├── src/
│   │   └── spendsense/
│   │       ├── __init__.py
│   │       ├── main.py               # FastAPI app + global exception handler
│   │       ├── config.py             # Pydantic Settings
│   │       ├── database.py           # SQLAlchemy setup + WAL mode
│   │       ├── models/               # SQLAlchemy ORM models (separate files)
│   │       │   ├── __init__.py
│   │       │   ├── user.py           # User model with consent field
│   │       │   ├── account.py        # Account (checking/savings/credit)
│   │       │   ├── transaction.py    # Transaction with indexed queries
│   │       │   ├── persona.py        # Persona assignment records
│   │       │   └── content.py        # Education content catalog
│   │       ├── schemas/              # Pydantic request/response schemas
│   │       │   ├── __init__.py
│   │       │   ├── user.py
│   │       │   ├── account.py
│   │       │   ├── transaction.py
│   │       │   └── insight.py        # Recommendation responses
│   │       ├── routers/              # API endpoints (plural resources)
│   │       │   ├── __init__.py
│   │       │   ├── users.py          # POST /users, POST /consent
│   │       │   ├── accounts.py       # GET /accounts/{user_id}
│   │       │   ├── transactions.py   # GET /transactions/{user_id}
│   │       │   └── insights.py       # GET /insights/{user_id}
│   │       ├── services/             # Business logic
│   │       │   ├── __init__.py
│   │       │   ├── synthetic_data.py # Faker generator (CLI: uv run python -m ...)
│   │       │   ├── features.py       # Behavioral signal detection (on-demand)
│   │       │   ├── personas.py       # Assignment logic (fixed priority)
│   │       │   └── recommendations.py # Recommendation engine
│   │       ├── generators/           # Content generation (AI-agnostic)
│   │       │   ├── __init__.py
│   │       │   ├── base.py           # Abstract ContentGenerator ABC
│   │       │   ├── template.py       # TemplateGenerator (default)
│   │       │   └── llm.py            # LLMGenerator stub (future)
│   │       └── utils/
│   │           ├── __init__.py
│   │           └── guardrails.py     # Consent, eligibility, tone checks
│   └── docs/
│       ├── DECISION_LOG.md
│       ├── SCHEMA.md
│       └── LIMITATIONS.md
│
└── spendsense-frontend/
    ├── package.json                  # Bun dependencies
    ├── svelte.config.js
    ├── vite.config.ts                # @tailwindcss/vite plugin
    ├── tailwind.config.js
    ├── biome.json                    # Linter config
    ├── .env                          # API_BASE_URL=http://localhost:8000
    ├── src/
    │   ├── app.html
    │   ├── app.css                   # @import "tailwindcss"
    │   ├── routes/
    │   │   ├── +layout.svelte        # Import app.css, CORS headers
    │   │   ├── +page.svelte          # Home/landing
    │   │   ├── dashboard/
    │   │   │   └── +page.svelte      # User dashboard (shadcn Card)
    │   │   ├── transactions/
    │   │   │   └── +page.svelte      # Transaction list (shadcn Table)
    │   │   └── insights/
    │   │       └── +page.svelte      # Recommendations (shadcn Card/Badge)
    │   └── lib/
    │       ├── components/
    │       │   └── ui/               # shadcn-svelte components only
    │       │       ├── card/         # Persona cards, insight cards
    │       │       ├── button/       # Action buttons
    │       │       ├── table/        # Transaction display
    │       │       ├── badge/        # Persona tags, status
    │       │       └── alert/        # Recommendations, disclaimers
    │       ├── stores/
    │       │   └── user.svelte.ts    # Svelte 5 runes ($state/$derived)
    │       ├── api/
    │       │   └── client.ts         # Fetch wrapper (localhost CORS)
    │       └── types/
    │           └── index.ts          # TypeScript interfaces
    └── static/
```

## Epic to Architecture Mapping

| Epic/Phase | Backend Components | Frontend Components | Database Tables | Key Decisions |
|-----------|-------------------|---------------------|----------------|---------------|
| **Phase 1: Foundation** | `database.py`, `models/*`, `config.py` | Project setup only | users, accounts, transactions, personas, content | SQLite WAL mode, separate model files |
| **Phase 2: Feature Detection** | `services/features.py` | N/A | Queries transactions table | On-demand computation, no caching |
| **Phase 3: Personas & Content** | `services/personas.py`, `generators/base.py`, `generators/template.py` | N/A | Writes to personas table | Fixed priority order, abstract generator |
| **Phase 4: API & Frontend** | `routers/*`, `schemas/*` | All routes, shadcn components | All tables | REST plural naming, direct JSON responses |
| **Phase 5: Guardrails** | `utils/guardrails.py`, error handlers in `main.py` | Disclaimer in insights view | consent field in users | Global exception handler, tone checking |
| **Phase 6: Demo** | Evaluation scripts (ad-hoc) | Polish, operator view | Metrics queries | Manual testing only |

## Technology Stack Details

### Backend Stack

**Runtime & Framework:**
- Python 3.13.8 (free-threading, JIT)
- FastAPI 0.120.4 (async, OpenAPI)
- uvicorn (ASGI server, included in fastapi[standard])

**Database & ORM:**
- SQLite 3.x with WAL mode
- SQLAlchemy 2.0.44 (async)
- aiosqlite (async SQLite driver)

**Data & Validation:**
- Pydantic v2 (schemas, settings)
- faker (synthetic data generation, seed=42)

**Development Tools:**
- uv (package manager)
- ruff (linting + formatting)

### Frontend Stack

**Framework & Build:**
- Svelte 5.x (runes-based reactivity)
- SvelteKit 2.48.4 (App Router, SSR)
- Vite 5.x (HMR, optimized builds)
- TypeScript 5.x

**UI & Styling:**
- shadcn-svelte (component library, Svelte 5 + Tailwind v4 compatible)
- Tailwind CSS 4.x (Vite plugin, no @apply)

**Development Tools:**
- Bun (package manager, native TypeScript)
- Biome (linting + formatting)

### Integration Points

**Frontend ↔ Backend:**
- Protocol: HTTP REST
- Format: JSON
- CORS: Localhost origins only (`http://localhost:5173`, `http://localhost:3000`)
- Base URL: `http://localhost:8000` (configured in frontend .env)
- Authentication: None (demo mode)

**Backend ↔ Database:**
- Connection: `sqlite+aiosqlite:///data/spendsense.db`
- Mode: WAL (Write-Ahead Logging) for concurrent reads
- Async: All queries via async SQLAlchemy sessions

**Content Generation (Swappable):**
- Interface: Abstract `ContentGenerator` class
- Default: `TemplateGenerator` (YAML catalog)
- Future: `LLMGenerator` (Anthropic/OpenAI APIs)
- Swap point: Dependency injection in recommendation service

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Backend Naming Conventions (Python)

**Files:** `snake_case.py`
- ✅ `synthetic_data.py`, `features.py`, `personas.py`
- ❌ `syntheticData.py`, `Features.py`

**Classes:** `PascalCase`
- ✅ `ContentGenerator`, `BehaviorSignals`, `TemplateGenerator`
- ❌ `content_generator`, `behaviorSignals`

**Functions/Methods:** `snake_case`
- ✅ `compute_signals()`, `generate_education()`, `assign_persona()`
- ❌ `computeSignals()`, `GenerateEducation()`

**Variables:** `snake_case`
- ✅ `user_id`, `window_days`, `persona_type`
- ❌ `userId`, `WindowDays`

**Constants:** `UPPER_SNAKE_CASE`
- ✅ `PERSONA_PRIORITY`, `DATABASE_URL`, `LOG_LEVEL`
- ❌ `PersonaPriority`, `database_url`

**REST Endpoints:** `/plural-resources`
- ✅ `/users`, `/accounts/{user_id}`, `/insights/{user_id}`
- ❌ `/user`, `/getUserAccounts`, `/get-insights`

**Route Parameters:** `{snake_case}`
- ✅ `{user_id}`, `{account_id}`
- ❌ `{userId}`, `{id}`

### Frontend Naming Conventions (TypeScript/Svelte)

**Component Files:** `PascalCase.svelte`
- ✅ `PersonaCard.svelte`, `InsightCard.svelte`
- ❌ `persona-card.svelte`, `personaCard.svelte`

**TypeScript Files:** `kebab-case.ts`
- ✅ `api-client.ts`, `user-store.ts`
- ❌ `apiClient.ts`, `UserStore.ts`

**Functions:** `camelCase`
- ✅ `fetchUserInsights()`, `formatCurrency()`
- ❌ `FetchUserInsights()`, `format_currency()`

**Variables:** `camelCase`
- ✅ `userId`, `personaType`, `recommendations`
- ❌ `user_id`, `PersonaType`

**Constants:** `UPPER_SNAKE_CASE`
- ✅ `API_BASE_URL`, `DEFAULT_TIMEOUT`
- ❌ `apiBaseUrl`, `defaultTimeout`

**Types/Interfaces:** `PascalCase`
- ✅ `User`, `Insight`, `PersonaType`, `Recommendation`
- ❌ `user`, `insightType`

### Database Naming Conventions

**Tables:** `snake_case` (plural)
- ✅ `users`, `accounts`, `transactions`, `personas`
- ❌ `Users`, `user`, `Transaction`

**Columns:** `snake_case`
- ✅ `user_id`, `created_at`, `persona_type`
- ❌ `userId`, `createdAt`, `PersonaType`

**Foreign Keys:** `{table}_id`
- ✅ `user_id`, `account_id`
- ❌ `fk_user`, `userId`

**Indexes:** `ix_{table}_{column}`
- ✅ `ix_transactions_account_id`, `ix_transactions_date`
- ❌ `idx_trans_acct`, `transaction_account_idx`

## Consistency Rules

### API Response Formats

**Success Response (Direct JSON):**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "persona": "high_utilization",
  "recommendations": [...]
}
```

**Error Response (HTTPException):**
```json
{
  "detail": "User not found",
  "status_code": 404
}
```

**Dates:** Always ISO 8601 strings
- ✅ `"2025-11-03T10:30:00Z"`
- ❌ `1730631000`, `"2025-11-03"`

**Currency:** Always cents as integers
- ✅ `balance: 5000` (= $50.00)
- ❌ `balance: 50.00`, `balance: "$50.00"`

### Error Handling

**Global Exception Handler (main.py):**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )
```

**All errors logged:** Yes, including stack traces for 500s

**Validation errors:** Automatic via Pydantic (422 Unprocessable Entity)

### Logging Strategy

**Format:** Simple Python logging (text format)
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Log levels:**
- ERROR: Exceptions, failed operations
- INFO: Request/response, key operations
- DEBUG: Detailed signal computation (optional)

**Location:** Console only (no file logging for demo)

## Data Architecture

### Database Schema

**Users Table:**
```sql
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    consent BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL
);
```

**Accounts Table:**
```sql
CREATE TABLE accounts (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users(id),
    type VARCHAR(50) NOT NULL,  -- 'depository', 'credit'
    subtype VARCHAR(50) NOT NULL,  -- 'checking', 'savings', 'credit_card'
    name VARCHAR(200) NOT NULL,
    mask VARCHAR(4) NOT NULL,
    balance INTEGER NOT NULL,  -- in cents
    limit INTEGER,  -- credit cards only
    currency VARCHAR(3) DEFAULT 'USD',
    apr REAL,  -- credit cards
    min_payment INTEGER,
    is_overdue BOOLEAN DEFAULT FALSE,
    INDEX ix_accounts_user_id (user_id)
);
```

**Transactions Table:**
```sql
CREATE TABLE transactions (
    id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL REFERENCES accounts(id),
    date DATETIME NOT NULL,
    amount INTEGER NOT NULL,  -- in cents, positive = debit
    merchant_name VARCHAR(200),
    category VARCHAR(100) NOT NULL,
    pending BOOLEAN DEFAULT FALSE,
    INDEX ix_transactions_account_id (account_id),
    INDEX ix_transactions_date (date),
    INDEX ix_transactions_account_date (account_id, date)
);
```

**Personas Table:**
```sql
CREATE TABLE personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL REFERENCES users(id),
    window VARCHAR(10) NOT NULL,  -- '30d' or '180d'
    persona_type VARCHAR(50) NOT NULL,  -- enum values
    confidence REAL NOT NULL,  -- 0.0-1.0
    assigned_at DATETIME NOT NULL,
    INDEX ix_personas_user_id (user_id)
);
```

**Content Table:**
```sql
CREATE TABLE content (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,  -- 'article', 'video', 'tool'
    title VARCHAR(200) NOT NULL,
    summary VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    persona_tags JSON NOT NULL,  -- list of persona types
    signal_tags JSON NOT NULL,  -- list of signal names
    source VARCHAR(50) NOT NULL,  -- 'template', 'llm', 'human'
    created_at DATETIME NOT NULL
);
```

### Key Relationships

- User → Accounts (1:many)
- Account → Transactions (1:many)
- User → Personas (1:many, one per window)
- Content → Personas (many:many via persona_tags)

## API Contracts

### Endpoints

**POST /users**
- Creates new user
- Body: `{name: string, email: string}`
- Returns: User object

**POST /consent**
- Records user consent
- Body: `{user_id: string, consent: boolean}`
- Returns: Updated user

**GET /accounts/{user_id}**
- Lists user's accounts
- Returns: Array of Account objects

**GET /transactions/{user_id}**
- Lists user's transactions
- Query params: `?limit=100&offset=0`
- Returns: Array of Transaction objects

**GET /insights/{user_id}**
- Generates personalized recommendations
- Query params: `?window=30d` (30d or 180d)
- Returns: Recommendations with rationales
- Response format:
```json
{
  "user_id": "uuid",
  "window": "30d",
  "persona": "high_utilization",
  "confidence": 0.95,
  "recommendations": [
    {
      "content": {
        "id": "edu_001",
        "title": "Understanding Credit Utilization",
        "summary": "...",
        "body": "...",
        "cta": "Calculate your utilization"
      },
      "rationale": {
        "text": "We noticed your card ending in 4523 is at 68% utilization...",
        "data_points": [
          {
            "signal": "credit_utilization",
            "value": "68%",
            "account_hint": "Card ending in 4523"
          }
        ],
        "source": "template"
      }
    }
  ]
}
```

## Security Architecture

**CORS:** Localhost origins only
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Authentication:** None (demo mode)

**Data Protection:**
- Synthetic data only (no real PII)
- Consent field tracked but not enforced (demo)

**Guardrails:**
- Tone checking (no shaming language)
- Disclaimer on all recommendations
- Eligibility checks for offers (not implemented in demo)

## Performance Considerations

**Target:** <5 seconds for recommendation generation

**Optimization strategies:**
- SQLite WAL mode for concurrent reads
- Indexed queries on transactions (account_id, date)
- On-demand computation (no pre-aggregation overhead)
- Direct JSON responses (no serialization overhead)
- Svelte 5 fine-grained reactivity (minimal re-renders)

**Expected performance (50-100 users):**
- Feature computation: ~100-200ms per user
- Persona assignment: ~10ms
- Content generation: ~1ms (template-based)
- Total: <500ms per user (well under 5s target)

## Development Environment

### Prerequisites

**Backend:**
- Python 3.13.8
- uv package manager
- No Docker required

**Frontend:**
- Bun (latest)
- Node.js not required (Bun replaces it)

### Setup Commands

**Backend Setup:**
```bash
cd spendsense-backend
uv sync
uv run python -m spendsense.services.synthetic_data  # Generate data
uv run uvicorn spendsense.main:app --reload  # Start server on :8000
```

**Frontend Setup:**
```bash
cd spendsense-frontend
bun install
bun run dev  # Start dev server on :5173
```

**Linting:**
```bash
# Backend
uv run ruff check src/
uv run ruff format src/

# Frontend
bun run biome check src/
bun run biome format --write src/
```

## Architecture Decision Records (ADRs)

### ADR-001: No Automated Testing
**Decision:** Manual testing only, no pytest/vitest frameworks

**Rationale:**
- PRD originally specified ≥10 tests but emphasized "linting only"
- Simplified development for 4-6 week timeline
- Demo-quality target, not production
- Architectural decisions ensure consistency without test coverage

**Trade-offs:** No regression protection, manual verification required

### ADR-002: Template-Based Content (Default)
**Decision:** Use YAML catalog for content generation, not LLM

**Rationale:**
- Zero cost (no API keys)
- 100% explainability (required by PRD)
- Deterministic and fast (<1ms)
- AI-agnostic architecture allows future LLM swap

**Trade-offs:** Less personalized than AI-generated content

### ADR-003: On-Demand Signal Computation
**Decision:** Compute behavioral signals on every request, no caching

**Rationale:**
- PRD specifies "no caching layer"
- Always current data
- SQLite fast enough for 50-100 users
- Simpler architecture

**Trade-offs:** Won't scale to 10k+ users (not a goal)

### ADR-004: SQLite with WAL Mode
**Decision:** Single-file SQLite database, not PostgreSQL

**Rationale:**
- Local-first requirement
- Perfect for 50-100 users
- WAL mode enables concurrent reads
- No server setup complexity

**Trade-offs:** Not suitable for production scale (acceptable)

### ADR-005: shadcn-svelte for UI
**Decision:** Use shadcn-svelte components, not custom components

**Rationale:**
- Svelte 5 + Tailwind v4 compatible
- Accessible by default
- Consistent design system
- Faster development

**Trade-offs:** Dependency on third-party library

### ADR-006: Bun Over npm
**Decision:** Use Bun for frontend package management

**Rationale:**
- Faster than npm/yarn
- Native TypeScript support
- Single runtime for JS/TS
- Modern developer experience

**Trade-offs:** Less ecosystem maturity than npm

---

_Generated by BMAD Decision Architecture Workflow v1.3.2_
_Date: 2025-11-03_
_For: Peter_
_Verification Date: 2025-11-03 (versions verified via web search)_
