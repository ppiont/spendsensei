# SpendSense: Technical Writeup

**A Behavioral Financial Recommendation System with Explainable AI**

---

## Executive Summary

SpendSense is a full-stack financial education platform that generates personalized recommendations based on behavioral analysis of user spending patterns. The system analyzes transaction data to detect behavioral signals, assigns user personas, and delivers relevant educational content and partner offers—all with transparent, explainable rationales.

**Key Achievements:**
- ✅ Complete REST API with 5 endpoints (FastAPI)
- ✅ Behavioral signal detection engine (4 signal categories)
- ✅ Persona assignment system (6 persona types)
- ✅ Recommendation pipeline with guardrails
- ✅ Evaluation harness (coverage, explainability, relevance, latency)
- ✅ Operator review tools for quality assurance

**Tech Stack:** FastAPI + SvelteKit + SQLite + TypeScript

---

## Architecture Overview

### Three-Tier Architecture

```
┌──────────────────────────────────────────────┐
│          SvelteKit Frontend (Port 5173)      │
│  - Dashboard, Transactions, Insights pages   │
│  - Operator review interface                 │
│  - Type-safe API client                      │
└──────────────────────────────────────────────┘
                     │
                     ├─── API Calls (REST/JSON)
                     ▼
┌──────────────────────────────────────────────┐
│           FastAPI Backend (Port 8000)        │
│  - 5 REST endpoints                          │
│  - Async SQLAlchemy ORM                      │
│  - Recommendation engine                     │
│  - Guardrails pipeline                       │
└──────────────────────────────────────────────┘
                     │
                     ├─── SQL Queries
                     ▼
┌──────────────────────────────────────────────┐
│              SQLite Database                 │
│  - Users, Accounts, Transactions             │
│  - Operator overrides                        │
│  - 50 synthetic test users                   │
└──────────────────────────────────────────────┘
```

### Recommendation Pipeline (Core Innovation)

```
1. Data Ingestion
   ↓
2. Signal Detection (features/)
   - Subscriptions (recurring merchants)
   - Savings patterns (emergency fund analysis)
   - Credit utilization (balances vs limits)
   - Income stability (frequency, variance)
   ↓
3. Persona Assignment (personas/)
   - Priority matching (high_utilization → debt_consolidator → ...)
   - Confidence scoring (signal strength)
   ↓
4. Content Selection (recommend/)
   - Template-based matching (signal tags)
   - Relevance scoring (1-5 scale)
   - Partner offer filtering (eligibility)
   ↓
5. Guardrails (guardrails/)
   - Consent verification
   - Tone checking (shame/blame detection)
   - Eligibility validation (income, accounts, predatory blocking)
   - Operator overrides (flag/approve)
   ↓
6. Response Generation
   - Educational content (3 items)
   - Partner offers (0-3 eligible)
   - Explainable rationales
```

---

## Key Technical Components

### 1. Behavioral Signal Detection

**Location:** `spendsense/features/`

**Innovation:** Modular signal detectors that analyze Plaid-style transaction data to identify financial behaviors.

```python
# Subscription Detection
detect_subscriptions(transactions) → {
    "recurring_merchant_count": 5,
    "monthly_recurring_spend": 7995,  # $79.95 in cents
    "merchants": ["netflix_inc", "spotify_ab", ...]
}

# Credit Analysis
analyze_credit(accounts) → {
    "overall_utilization": 0.85,  # 85%
    "monthly_interest": 12500,    # $125
    "min_payment_ratio": 0.03
}
```

**Challenge Solved:** Converting raw transaction logs into actionable behavioral insights.

### 2. Persona Assignment Engine

**Location:** `spendsense/personas/`

**Innovation:** Priority-based matching that assigns users to financial archetypes based on signal strength.

```python
Persona Priority Order (highest to lowest):
1. high_utilization     (>70% credit utilization)
2. variable_income      (irregular paycheck patterns)
3. debt_consolidator    (multiple high-balance accounts)
4. subscription_heavy   (>3 recurring subscriptions)
5. savings_builder      (consistent savings patterns)
6. balanced             (default fallback)
```

**Confidence Scoring:**
- High (0.8-1.0): Strong signal evidence
- Medium (0.5-0.8): Moderate evidence
- Low (0.0-0.5): Weak evidence

### 3. Content Recommendation System

**Location:** `spendsense/recommend/`

**Architecture:** Adapter pattern enabling swappable recommendation strategies.

```python
# Abstract Interface
class RecommendationEngine(ABC):
    async def generate_recommendations(...) -> RecommendationResult

# Implementations
class StandardRecommendationEngine(RecommendationEngine):
    # Template-based (production)

class AIRecommendationEngine(RecommendationEngine):
    # AI-powered (future, stub exists)
```

**Content Selection Algorithm:**
```python
1. Load content catalog (YAML)
2. Filter by persona tags
3. Score by signal match: relevance_score = Σ(tag_matches)
4. Convert to 1-5 scale (1=Poor, 5=Excellent)
5. Return top N (sorted by relevance)
```

### 4. Guardrails System

**Location:** `spendsense/guardrails/`

**Philosophy:** Deterministic safety checks that cannot be bypassed.

```python
# Consent (ALWAYS checked first)
if not check_consent(user.consent):
    return empty_response

# Tone (shame/blame detection)
shame_patterns = [
    "your fault", "should have known", "irresponsible", ...
]
if any(pattern in text for pattern in shame_patterns):
    block_content()

# Eligibility (income, accounts, predatory blocking)
def check_eligibility(offer, user_data):
    if is_predatory_product(offer):  # APR >36%, payday loans
        return False
    if user_income < offer.min_income:
        return False
    if has_existing_account(user, offer.account_type):
        return False  # Avoid duplicates
    return True

# Operator Overrides (human-in-the-loop)
- "flag" action: Force-exclude recommendation
- "approve" action: Force-include recommendation
- Approve wins if both present
```

---

## Data Models (Plaid-Compliant)

### Core Tables

**Users**
```sql
- id (UUID)
- name, email
- consent (boolean)
- created_at (timestamp)
```

**Accounts** (Multi-type support)
```sql
- id, user_id
- type: depository | credit | loan
- subtype: checking | savings | credit_card | mortgage | student_loan
- balances: current_balance, available_balance, limit
- credit_fields: apr, apr_type (purchase|cash_advance|penalty), min_payment
- loan_fields: interest_rate, next_payment_due_date
```

**Transactions** (Plaid categorization)
```sql
- id, account_id
- date, amount (cents), pending
- merchant_name, merchant_entity_id
- personal_finance_category_primary (e.g., "FOOD_AND_DRINK")
- personal_finance_category_detailed (e.g., "RESTAURANTS")
- payment_channel: online | in_store | other
```

**Operator Overrides** (Quality control)
```sql
- id, user_id, recommendation_id
- action: flag | approve
- reason (required for flags)
- operator_id, created_at
```

---

## API Endpoints

```
POST   /users                    Create user
POST   /users/consent            Update consent
GET    /accounts/{user_id}       Get accounts (with balances)
GET    /transactions/{user_id}   Get transactions (paginated, windowed)
GET    /insights/{user_id}       Get recommendations (with guardrails)
       ?window=30|90|180          Analysis window in days

GET    /operator/review          Review queue (pending recommendations)
POST   /operator/approve         Approve recommendation (force-include)
POST   /operator/flag            Flag recommendation (quality issue)
GET    /operator/inspect/{id}    Multi-window analysis (30d + 180d)
```

**Example Response:** `/insights/{user_id}?window=30`
```json
{
  "persona_type": "high_utilization",
  "confidence": 0.92,
  "education_recommendations": [
    {
      "content": {
        "id": "credit-util-101",
        "title": "Understanding Credit Utilization: The 30% Rule",
        "summary": "Learn why...",
        "relevance_score": 5
      },
      "rationale": {
        "persona_type": "high_utilization",
        "confidence": 0.92,
        "explanation": "Your credit card utilization is at 85%...",
        "key_signals": ["high_credit_utilization", "revolving_balance"]
      }
    }
    // 2 more education items
  ],
  "offer_recommendations": [
    // 0-3 eligible partner offers
  ],
  "signals_summary": {
    "credit": {"utilization": 0.85, "has_interest": true},
    "subscriptions": {"count": 5, "monthly_spend": 79.95}
  }
}
```

---

## Quality Assurance

### Evaluation Harness

**Location:** `scripts/evaluate.py`

**Metrics Tracked:**
```python
1. Coverage: % users with persona + ≥3 signals (target: 100%)
2. Explainability: % recommendations with rationales (target: 100%)
3. Latency: Average recommendation time (target: <5s)
4. Auditability: % with complete decision trace (target: 100%)
5. Relevance: Average 1-5 score (target: ≥3.0)
```

**Output:** `data/evaluation_results.json`

### Decision Trace Logging

All recommendation decisions logged with `[DecisionTrace]` prefix:
```
[DecisionTrace] Education item 1/3: id=credit-util-101, relevance_score=5/5
[DecisionTrace] Filtered 4/12 education items (zero relevance score)
[DecisionTrace] Partner offers: 8 total, 3 filtered (persona), 2 filtered (eligibility), 3 eligible
```

### Operator Review Tools

- **Review Queue:** See recent recommendations for QA sampling
- **Flag/Approve:** Override algorithm decisions
- **Inspect View:** Multi-window analysis (30d vs 180d) for debugging
- **Rationales:** Full transparency into why content was selected

---

## Testing Infrastructure

### Pytest Setup

**Location:** `tests/`

**Components:**
- `pytest.ini` - Configuration (markers, asyncio, logging)
- `conftest.py` - 15+ fixtures (db, users, accounts, transactions)
- `test_api_users.py` - Converted test (1 of 16)
- `README_TESTING.md` - Conversion guide for remaining 15 tests

**Markers:**
```python
@pytest.mark.unit          # Fast, no dependencies
@pytest.mark.integration   # Database tests
@pytest.mark.api           # Endpoint tests
@pytest.mark.signals       # Signal detection
@pytest.mark.personas      # Persona assignment
```

**Status:** Infrastructure complete, 1/16 tests converted, pattern documented.

---

## Deployment (Railway)

### Backend Service
```toml
# railway.toml
[build]
builder = "NIXPACKS"
buildCommand = "uv sync"

[deploy]
startCommand = "uv run uvicorn spendsense.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/docs"
```

### Frontend Service
```toml
[build]
builder = "RAILPACK"
buildCommand = "bun install && bun run build"

[deploy]
startCommand = "node build/index.js"
```

**Environment Variables:**
- Backend: `DATABASE_URL` (Railway automatically sets)
- Frontend: `PUBLIC_API_BASE_URL` (points to backend service)

**Data Loading:**
```bash
# Initialize database and load 50 synthetic users
railway run python scripts/init_and_load_data.py
```

---

## Future Enhancements

### Immediate (Ready to Implement)
1. **AI Integration** - Swap to `AIRecommendationEngine` (stub exists)
2. **Complete Test Migration** - Convert remaining 15 manual tests
3. **Coverage Reporting** - Enable pytest-cov integration

### Medium-term
1. **Real Plaid Integration** - Replace synthetic data
2. **Multi-window Insights** - Show 30d vs 180d side-by-side
3. **Custom Content** - AI-generated explanations
4. **Budget Tracking** - Spending limits and alerts

### Long-term
1. **Financial Coaching** - Multi-turn Q&A
2. **Predictive Insights** - Forecast future financial health
3. **Goal Setting** - Track progress toward financial goals
4. **Mobile App** - React Native frontend

---

## Project Statistics

**Backend:**
- **Lines of Code:** ~5,000 (Python)
- **Modules:** 30+ Python files
- **API Endpoints:** 8 routes
- **Test Scripts:** 16 manual tests → pytest migration in progress

**Frontend:**
- **Lines of Code:** ~2,000 (TypeScript + Svelte)
- **Pages:** 4 routes (dashboard, transactions, insights, operator)
- **Components:** 10+ reusable Svelte 5 components

**Data:**
- **Synthetic Users:** 50
- **Accounts:** ~100 (1-3 per user)
- **Transactions:** ~3,500 (20-100 per account)
- **Content Catalog:** 12 education items, 6 partner offers

---

## Lessons Learned

1. **Modularity Wins:** Separating signal detection, persona assignment, and content selection made testing and iteration much easier.

2. **Guardrails First:** Implementing consent, tone, and eligibility checks early prevented technical debt and ensured compliance from day one.

3. **Adapter Pattern:** Using an abstract `RecommendationEngine` interface enables future AI integration without changing downstream code.

4. **Decision Traces:** Logging every filtering and ranking decision made debugging and operator review significantly more effective.

5. **Fixture-Based Testing:** pytest fixtures dramatically reduced test setup boilerplate and improved test isolation.

---

## Conclusion

SpendSense demonstrates a production-ready financial recommendation system that balances personalization with transparency, safety, and explainability. The modular architecture, comprehensive guardrails, and evaluation framework provide a solid foundation for future AI integration while maintaining deterministic safety checks.

**Project Completion:** 5 of 6 epics complete (83% done)

**Key Differentiator:** Full traceability from raw transactions → signals → persona → recommendations with human-readable rationales at every step.

---

**For Questions:** See `docs/` directory for PRD, architecture, epics, and sprint status.
