---
date: 2025-12-05T02:41:32Z
researcher: ppiont
git_commit: 2bccf402ce8989de98e194bca8ea6984d1ac316c
branch: master
repository: spendsensei
topic: "Complete Codebase Research and Validation Against Project Description"
tags: [research, codebase, validation, spendsense, full-stack]
status: complete
last_updated: 2025-12-05
last_updated_by: ppiont
---

# Research: SpendSense Codebase Validation Against Project Description

**Date**: 2025-12-05T02:41:32Z
**Researcher**: ppiont
**Git Commit**: 2bccf402ce8989de98e194bca8ea6984d1ac316c
**Branch**: master
**Repository**: spendsensei

## Research Question

Thoroughly research the codebase to understand what exists and validate implementation against the goals in Project Description.md. The CODE is the source of truth, not markdown documentation.

## Summary

SpendSense is a full-stack financial education platform (FastAPI + SvelteKit + SQLite) that is **~80% complete** against the Project Description requirements. The core recommendation pipeline (signals → personas → content selection → rationales) is fully functional with consent and tone guardrails. Key gaps are in the evaluation harness (placeholder only), metrics collection, and some Plaid-compliance details. The Railway deployment likely has issues related to SQLite persistence and/or initialization.

---

## Detailed Findings

### 1. Data Ingestion (Plaid-Style)

**Location**: `spendsense-backend/src/spendsense/ingest/synthetic_generator.py`

**Status**: ✅ Mostly Complete

| Requirement | Implementation | Status |
|------------|----------------|--------|
| Accounts with type/subtype | `synthetic_generator.py:84-90` - checking, savings, credit_card, mortgage, student_loan | ✅ |
| Balances (available, current, limit) | `models/account.py:32-34` | ✅ |
| Transactions with categories | Two-level Plaid categories implemented `models/transaction.py:33-38` | ✅ |
| merchant_entity_id for recurring | `synthetic_generator.py:42-55` - 12 predefined merchant entities | ✅ |
| Credit card APRs/min_payment/overdue | `models/account.py:41-51` - Full credit card schema | ✅ |
| 50-100 synthetic users | Generates exactly 50 users by default `synthetic_generator.py:237` | ✅ |
| Diverse financial situations | Random balances, multiple account types, varied income | ⚠️ |

**Gap**: Diversity is random but not systematic - doesn't guarantee representation of all persona types.

---

### 2. Behavioral Signal Detection

**Location**: `spendsense-backend/src/spendsense/features/`

**Status**: ✅ Complete

#### Subscriptions (`features/subscriptions.py:12-158`)
| Criteria | Code Location | Threshold |
|----------|---------------|-----------|
| Recurring merchants ≥3 | Line 82 | `len(merchant_txns) < 3` skip |
| Monthly cadence | Lines 111-112 | `20 <= avg_gap <= 45` days |
| Weekly cadence | Lines 113-114 | `5 <= avg_gap <= 10` days |
| Monthly spend calculation | Lines 123-127 | Weekly × 4.33 |

#### Savings (`features/savings.py:11-126`)
| Criteria | Code Location | Implementation |
|----------|---------------|----------------|
| Net inflow to savings | Lines 83-86 | credits - debits |
| Growth rate | Lines 113-117 | `(net_inflow / total_balance) * 100` |
| Emergency fund months | Lines 103-111 | `savings_balance / monthly_expenses` |
| Savings subtypes | Line 41 | savings, money_market, cd |

#### Credit (`features/credit.py:13-147`)
| Criteria | Code Location | Threshold |
|----------|---------------|-----------|
| Overall utilization | Lines 59-67 | `(balance / limit) * 100` |
| Flag ≥80% | Line 134 | `high_utilization_80` |
| Flag ≥50% | Line 136 | `high_utilization_50` |
| Flag ≥30% | Line 138 | `moderate_utilization_30` |
| Minimum-payment-only | Lines 113-130 | `last_payment <= min_payment * 1.1` |
| Interest charges | Lines 88-99 | Monthly interest from APR |
| Overdue status | Lines 104-107 | `is_overdue` field check |

#### Income (`features/income.py:11-137`)
| Criteria | Code Location | Threshold |
|----------|---------------|-----------|
| Biweekly detection | Lines 81-82 | `13 <= median_gap <= 16` days |
| Monthly detection | Lines 83-84 | `28 <= median_gap <= 32` days |
| Stability (CV) | Line 104 | CV < 0.15 = stable |
| Cash-flow buffer | Lines 109-127 | `net_cash_flow / monthly_expenses` |

**Window Support**: `compute_signals()` accepts `window_days` parameter, passed to all detectors except `analyze_credit()` which analyzes current state only.

---

### 3. Persona Assignment

**Location**: `spendsense-backend/src/spendsense/personas/assignment.py`

**Status**: ✅ Complete (5 personas + default)

#### Priority Order (highest to lowest)
| # | Persona | Criteria (from code) | Confidence Range |
|---|---------|---------------------|------------------|
| 1 | high_utilization | utilization ≥50% OR overdue OR interest_charges OR minimum_payment_only | 0.65-0.98 |
| 2 | variable_income | median_gap >45 days AND buffer <1.0 months | 0.70-0.95 |
| 3 | debt_consolidator | 30% ≤ utilization <70% AND ≥2 cards AND interest >0 AND NOT overdue | 0.75-0.92 |
| 4 | subscription_heavy | count ≥3 AND (monthly ≥$50 OR percentage ≥10%) | 0.70-0.90 |
| 5 | savings_builder | (growth ≥2% OR inflow ≥$200/mo) AND utilization <30% | 0.65-0.88 |
| 6 | balanced | Default fallback | 0.60 (fixed) |

**Custom Persona**: `debt_consolidator` at `assignment.py:271-353` - targets users managing multiple cards with moderate utilization who could benefit from consolidation.

---

### 4. Recommendation Engine

**Location**: `spendsense-backend/src/spendsense/recommend/`

**Status**: ✅ Complete

| Requirement | Implementation | Location |
|-------------|----------------|----------|
| 3-5 education items | Returns exactly 3 | `engine.py:198-202` |
| 1-3 partner offers | Returns 0-3 (only eligible) | `engine.py:212-217` |
| "because" rationales | Generated per persona | `content_selection.py:443-559` |
| Concrete data in rationales | Templates with signal values | `content_selection.py:460-481` |

**Content Catalog**: `data/content_catalog.yaml` - 12 education items
**Offers Catalog**: `data/partner_offers_catalog.yaml` - 14 partner offers

**Scoring Algorithm** (`content_selection.py:175-219`):
- Persona match: +0.5
- Signal tag match: +0.1 per tag (max +0.5)
- Total capped at 1.0, converted to 1-5 scale

---

### 5. Guardrails

**Location**: `spendsense-backend/src/spendsense/guardrails/`

**Status**: ✅ Complete

#### Consent (`guardrails/consent.py`)
| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Require opt-in | `insights.py:78-87` blocks without consent | ✅ |
| Allow revoke | `POST /users/consent?consent=false` | ✅ |
| Track per user | `models/user.py:23` - `consent: bool` field | ✅ |

#### Eligibility (`guardrails/eligibility.py` + `content_selection.py:692-786`)
| Check | Location | Logic |
|-------|----------|-------|
| Income requirement | `eligibility.py:19-38` | `user_income >= min_income` |
| Existing account | `eligibility.py:41-55` | Skip if user has same subtype |
| Predatory products | `eligibility.py:58-86` | Block payday_loan, title_loan, rent_to_own, APR >36% |
| Credit utilization bounds | `content_selection.py:717-726` | min/max from offer rules |
| Required signals | `content_selection.py:762-765` | All required_signals must be active |

#### Tone (`guardrails/tone.py`)
12 shame patterns defined at lines 15-27:
- "overspending", "bad financial habits", "irresponsible", "careless"
- "wasting money", "poor choices", "financial mistakes", "bad decisions"
- "foolish", "stupid", "reckless"

Applied at `content_selection.py:358-365` and `content_selection.py:424-431` - raises `ValueError` on violations.

#### Disclosure (`guardrails/disclosure.py`)
Standard disclaimer auto-attached via Pydantic default at `schemas/insight.py:116`:
> "This content is for educational purposes only and does not constitute financial advice..."

---

### 6. Operator View

**Location**: Backend: `ui/operator.py`, Frontend: `routes/operator/+page.svelte`

**Status**: ✅ Mostly Complete

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| View signals for any user | `GET /operator/inspect/{user_id}` returns `signals_summary` | ✅ |
| 30-day and 180-day views | Returns both windows in single response | ✅ |
| Review recommendations | Full recommendation details returned | ✅ |
| Approve recommendations | `POST /operator/approve` | ✅ |
| Flag recommendations | `POST /operator/flag` (requires reason) | ✅ |
| Decision trace | `signals_summary` + `rationale` exposed | ✅ |
| Override filtering | Insights endpoint respects flags/approvals | ✅ |

**Gap**: No dedicated "flagged items queue" - flagged items are just filtered from user responses.

---

### 7. API Endpoints

**Location**: `spendsense-backend/src/spendsense/ui/`

| Required Endpoint | Actual Implementation | Status |
|-------------------|----------------------|--------|
| POST /users | `ui/users.py:52-96` | ✅ |
| POST /consent | `POST /users/consent` (query params) | ⚠️ Different path |
| GET /profile/{user_id} | `GET /users/profile/{user_id}` | ✅ |
| GET /recommendations/{user_id} | `GET /insights/{user_id}` | ⚠️ Different path |
| POST /feedback | `ui/feedback.py:17-81` | ✅ |
| GET /operator/review | `ui/operator.py:30-121` | ✅ |

**Additional endpoints implemented**:
- `GET /users` - List all users
- `GET /accounts/{user_id}` - Get user accounts
- `GET /transactions/{user_id}` - Get transactions (paginated)
- `GET /operator/inspect/{user_id}` - Full user inspection
- `POST /operator/approve` - Approve recommendation
- `POST /operator/flag` - Flag recommendation

---

### 8. Evaluation & Metrics

**Location**: `spendsense-backend/src/spendsense/eval/` (placeholder)

**Status**: ❌ Not Implemented

| Required Metric | Status |
|-----------------|--------|
| Coverage (users with persona + ≥3 behaviors) | ❌ Not measured |
| Explainability (% with rationales) | ⚠️ 100% by design but not measured |
| Relevance (education-persona fit) | ❌ Not measured |
| Latency (<5 seconds) | ❌ Not measured |
| Fairness (demographic parity) | ❌ Not implemented |
| JSON/CSV metrics output | ❌ Not implemented |
| Summary report | ❌ Not implemented |

**Note**: A `scripts/evaluate.py` file exists but appears to be a stub or incomplete.

---

### 9. Tests

**Location**: `spendsense-backend/tests/`

**Status**: ✅ Exceeds requirement (≥10 tests)

| Test Area | Files | Test Functions |
|-----------|-------|----------------|
| API endpoints | 3 files | 16 functions |
| Signal detection | 4 files | 21 functions |
| Persona assignment | 1 file | 7 functions |
| Recommendations | 2 files | 15 functions |
| Guardrails | 1 file | 15 functions |
| Models/Schemas | 1 file | 9 functions |
| **Total** | **12 files** | **90+ functions** |

All tests use pytest with async support. Coverage configured but not tracked.

---

### 10. Frontend

**Location**: `spendsense-frontend/src/`

**Status**: ✅ Complete

| Page | Route | Features |
|------|-------|----------|
| Dashboard | `/dashboard` | KPIs, accounts, spending breakdown, recommendations, consent CTA |
| Transactions | `/transactions` | Filtering, pagination, category breakdown |
| Operator | `/operator` | Signal inspection, 30d/180d toggle, JSON dumps |

**Tech Stack**: SvelteKit + Svelte 5 runes ($state, $derived, $effect)
**API Client**: Type-safe client at `lib/api/client.ts`
**State**: Global user selection via Svelte store with localStorage persistence

---

## Validation Against Success Criteria

| Category | Target | Actual | Status |
|----------|--------|--------|--------|
| **Coverage** | 100% users with persona + ≥3 behaviors | Not measured | ❌ |
| **Explainability** | 100% with rationales | 100% (by design) | ✅ |
| **Latency** | <5 seconds | Not measured | ⚠️ |
| **Auditability** | 100% decision traces | 100% (signals_summary always included) | ✅ |
| **Code Quality** | ≥10 tests | 90+ tests | ✅ |
| **Documentation** | Complete | Schema docs exist, but may not reflect code | ⚠️ |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SvelteKit Frontend                        │
│  /dashboard    /transactions    /operator                    │
│      │              │               │                        │
│      └──────────────┴───────────────┴────────────────────────┤
│                        API Client                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ /users   │  │/accounts │  │/insights │  │/operator │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │             │             │           │
│       └─────────────┴──────┬──────┴─────────────┘           │
│                            │                                 │
│  ┌─────────────────────────▼─────────────────────────────┐  │
│  │           StandardRecommendationEngine                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │ Signals     │→ │ Personas    │→ │ Content       │  │  │
│  │  │ (features/) │  │ (personas/) │  │ (recommend/)  │  │  │
│  │  └─────────────┘  └─────────────┘  └───────────────┘  │  │
│  │                        │                               │  │
│  │                        ▼                               │  │
│  │              ┌─────────────────┐                       │  │
│  │              │   Guardrails    │                       │  │
│  │              │ consent/tone/   │                       │  │
│  │              │ eligibility     │                       │  │
│  │              └─────────────────┘                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  SQLite + WAL  │
                    │  (async)       │
                    └────────────────┘
```

---

## Potential Railway Deployment Issues

The user mentioned the Railway deployment is broken. Based on code analysis:

### 1. SQLite Persistence
- SQLite uses file-based storage at `data/spendsense.db`
- Railway ephemeral filesystem loses data on restart
- Solution: Use Railway persistent volume or migrate to PostgreSQL

### 2. Database Initialization
- `init_db()` at `database.py:40-89` auto-generates 50 users if DB empty
- If volume not persisted, regenerates on each deploy
- `scripts/init_db_railway.py` exists but may not be invoked correctly

### 3. Environment Variables
- `DATABASE_URL` configurable via env var
- `CORS_ORIGINS` for frontend URLs
- Must be set correctly in Railway

### 4. Missing Railway Configuration
- No `railway.toml` found in current state (deleted files shown in git status)
- Deployment may be using default settings

---

## Code References

### Backend Entry Point
- `spendsense-backend/src/spendsense/main.py:1-88`

### Signal Detection Orchestrator
- `spendsense-backend/src/spendsense/features/signals.py:22-144`

### Persona Assignment
- `spendsense-backend/src/spendsense/personas/assignment.py:356-448`

### Recommendation Engine
- `spendsense-backend/src/spendsense/recommend/engine.py:142-292`

### Content Catalogs
- `spendsense-backend/data/content_catalog.yaml` (12 items)
- `spendsense-backend/data/partner_offers_catalog.yaml` (14 offers)

### Guardrails
- `spendsense-backend/src/spendsense/guardrails/consent.py:12-39`
- `spendsense-backend/src/spendsense/guardrails/tone.py:15-65`
- `spendsense-backend/src/spendsense/guardrails/eligibility.py:19-122`

### Frontend API Client
- `spendsense-frontend/src/lib/api/client.ts:1-261`

### Test Suite
- `spendsense-backend/tests/` (12 files, 90+ tests)

---

## Summary: What's Complete vs Missing

### Complete (✅)
1. Data ingestion with Plaid-style schemas
2. All 4 signal detection modules (subscriptions, savings, credit, income)
3. 5 personas + balanced default with priority ordering
4. Recommendation engine with template-based content selection
5. Content catalog (12 education items, 14 partner offers)
6. Consent guardrails (require opt-in, allow revoke)
7. Tone guardrails (12 shame patterns blocked)
8. Eligibility guardrails (predatory products, income requirements)
9. Operator view with 30d/180d analysis
10. Approve/flag override system
11. Full frontend (dashboard, transactions, operator)
12. 90+ automated tests (exceeds 10 requirement)

### Partially Complete (⚠️)
1. API paths differ from spec (e.g., `/insights` vs `/recommendations`)
2. Synthetic data diversity not systematic
3. Evaluation metrics not measured (code exists to compute but not reported)
4. Documentation may not match code

### Missing (❌)
1. Evaluation harness (placeholder only)
2. Coverage metric calculation
3. Latency measurement
4. Fairness analysis
5. JSON/CSV metrics output
6. Summary evaluation report
7. Railway deployment configuration (deleted)

---

## Open Questions

1. **Railway Configuration**: What deployment configuration was being used before the deletions shown in git status?
2. **Evaluation Requirements**: Is the evaluation harness blocking for the project, or nice-to-have?
3. **Synthetic Data**: Should the generator ensure coverage of all persona types rather than random assignment?
4. **API Paths**: Should paths match Project Description exactly, or are current paths acceptable?
