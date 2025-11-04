# Known Limitations

This document outlines the known limitations, constraints, and areas for improvement in SpendSense.

## Table of Contents
- [Scale Limitations](#scale-limitations)
- [Data Limitations](#data-limitations)
- [Feature Limitations](#feature-limitations)
- [Technical Limitations](#technical-limitations)
- [Security Limitations](#security-limitations)

---

## Scale Limitations

### User Capacity: 50-100 Users Maximum

**Current State:**
- System designed and tested for 50-100 users
- Single SQLite database file
- No caching layer
- On-demand computation for all requests

**Why This Limit:**
- SQLite write concurrency limitations
- No horizontal scaling capabilities
- Signal computation happens per-request

**Production Requirements:**
- Switch to PostgreSQL for better concurrency
- Add Redis for caching computed signals
- Implement read replicas for scaling
- Add CDN for static assets
- Expected capacity with changes: 10,000+ users

**Impact:** ⚠️ Critical - System will slow down significantly beyond 100 concurrent users

---

### Transaction Volume: ~5,000 Transactions

**Current State:**
- 50 users × ~100 transactions each = 5,000 total
- All queries perform well (<10ms)
- No pagination limits or query timeouts

**Why This Limit:**
- SQLite query performance degrades on large tables without proper indexing
- Full table scans become expensive >100K rows
- No query result caching

**Production Requirements:**
- Partition transactions table by date
- Add query result caching (Redis)
- Implement lazy loading in frontend
- Expected capacity: 1M+ transactions with partitioning

**Impact:** ⚠️ Medium - Queries slow down but remain functional up to ~50K transactions

---

## Data Limitations

### Synthetic Data Only

**Current State:**
- All user data is synthetically generated using Faker
- No real bank connections
- No actual PII or financial data

**Why:**
- Demonstration/portfolio project only
- Avoids compliance requirements (PCI-DSS, SOC 2)
- No need for real data to prove concept

**Production Requirements:**
- Integrate with Plaid API for real bank data
- Implement OAuth flow for bank connections
- Add PII encryption at rest
- Implement audit logging
- Obtain necessary compliance certifications

**Impact:** ⚠️ Critical - Cannot be used with real users without bank integration

---

### Historical Data: 90-180 Days Maximum

**Current State:**
- Synthetic transactions cover last 90-180 days only
- Older data not generated to keep dataset manageable
- Signal computation windows: 30d, 90d, 180d

**Why:**
- Sufficient for demonstrating persona assignment
- Keeps database size small (~10MB)
- Faster test data generation

**Production Requirements:**
- Store full transaction history (years)
- Implement data archival strategy
- Add data retention policies

**Impact:** ℹ️ Low - Sufficient for demonstration purposes

---

### Fixed Personas: 5 Types Only

**Current State:**
- Only 5 persona types: high_utilization, variable_income, subscription_heavy, savings_builder, balanced
- Personas assigned based on simple rules
- No persona evolution over time

**Why:**
- Sufficient to demonstrate the concept
- Simple rule-based assignment is transparent
- Complex persona taxonomy adds little value for demo

**Production Requirements:**
- Expand to 10-15 persona types
- Implement ML-based persona assignment
- Track persona changes over time
- Add sub-personas or personas combinations

**Impact:** ℹ️ Low - 5 personas adequate for demonstration

---

## Feature Limitations

### No Authentication

**Current State:**
- No login/signup flow
- No password storage
- No session management
- Users selected via dropdown (development mode)

**Why:**
- Demonstration project focused on core recommendation logic
- Authentication adds complexity without demonstrating unique value
- Synthetic users don't need protection

**Production Requirements:**
- Implement OAuth2/OIDC authentication
- Add password hashing (bcrypt/Argon2)
- Implement JWT-based sessions
- Add 2FA/MFA support
- Implement rate limiting

**Impact:** ⚠️ Critical - Cannot deploy publicly without authentication

---

### No User Management

**Current State:**
- Cannot create/edit/delete users via UI
- User data managed via scripts only
- No user profile pages
- No settings or preferences

**Why:**
- Focus on recommendation quality, not CRUD operations
- Users pre-generated for consistent testing

**Production Requirements:**
- Build user onboarding flow
- Add profile management UI
- Implement user preferences
- Add account deletion (GDPR compliance)

**Impact:** ⚠️ Medium - Limits usability but doesn't affect core functionality

---

### Template-Based Content Only

**Current State:**
- 12 pre-written educational items in content catalog
- Content selected via tag matching
- No AI-generated personalization
- Rationales are templates with signal substitution

**Why:**
- Zero cost (no LLM API fees)
- 100% deterministic and auditable
- Fast generation (<1ms)
- Good enough for demonstration

**Trade-offs:**
- ✅ Free, fast, fully explainable
- ❌ Less personalized than AI-generated content
- ❌ Limited to pre-written catalog
- ❌ Cannot adapt tone/length to user preferences

**Production Requirements:**
- Integrate LLM (OpenAI, Anthropic, or local)
- Implement prompt engineering for personalization
- Add guardrails for LLM outputs
- Expected improvement: 10x more engaging content

**Impact:** ℹ️ Low - Template content is surprisingly effective for demo

---

### No Goal Tracking

**Current State:**
- Recommendations are one-off
- No progress tracking
- No goal setting UI
- No notifications or reminders

**Why:**
- Core recommendation logic is the focus
- Goal tracking is standard CRUD work

**Production Requirements:**
- Add goal setting interface
- Track user progress over time
- Send push notifications
- Gamification (badges, streaks)

**Impact:** ℹ️ Low - Nice-to-have, not essential for demonstration

---

## Technical Limitations

### No Automated Testing

**Current State:**
- Manual test scripts only (scripts/test_*.py)
- No pytest framework
- No CI/CD pipeline
- No test coverage metrics

**Why:**
- ADR-001: Faster development for prototype
- Manual tests sufficient for 50-100 user scale
- Reduces dependencies and complexity

**Trade-offs:**
- ✅ Simpler codebase, faster iteration
- ❌ Manual regression testing required
- ❌ No automated quality gates

**Production Requirements:**
- Add pytest test suite (unit + integration)
- Implement CI/CD (GitHub Actions)
- Add test coverage requirements (>80%)
- Automated API testing (Postman/Newman)

**Impact:** ⚠️ Medium - Increases risk of regressions during changes

---

### No Caching Layer

**Current State:**
- All signals computed on-demand
- No Redis or memcached
- No query result caching
- No CDN for static assets

**Why:**
- ADR-003: Simpler architecture
- Sub-10ms latency without caching
- Always fresh data

**Trade-offs:**
- ✅ Always current, no cache invalidation logic
- ❌ Repeated computation for same user
- ❌ Doesn't scale beyond 100 users

**Production Requirements:**
- Add Redis for computed signals
- Implement cache-aside pattern
- Set appropriate TTLs (5-15 minutes)
- Expected improvement: 10-100x lower latency

**Impact:** ⚠️ Medium - Becomes critical above 100 users

---

### SQLite Concurrency

**Current State:**
- Write-Ahead Logging (WAL) mode enabled
- Single writer, multiple readers
- No connection pooling needed
- ~10-20 concurrent reads comfortable

**Why:**
- Perfect for 50-100 user demonstrations
- Zero setup complexity
- Portable (single file database)

**Trade-offs:**
- ✅ Zero setup, portable, version controllable
- ❌ Single writer bottleneck
- ❌ No multi-machine deployment

**Production Requirements:**
- Migrate to PostgreSQL
- Implement connection pooling
- Add read replicas
- Expected improvement: 1000x write throughput

**Impact:** ⚠️ Critical - Write bottleneck becomes severe >100 users

---

## Security Limitations

### No Input Validation

**Current State:**
- Basic Pydantic validation only
- No SQL injection protection beyond SQLAlchemy parameterization
- No XSS protection
- No CSRF tokens
- No rate limiting

**Why:**
- Synthetic data only (no real user input)
- Demonstration environment
- SQLAlchemy provides parameterization

**Production Requirements:**
- Add comprehensive input validation
- Implement CORS properly
- Add CSRF protection
- Rate limiting (per-user, per-IP)
- SQL injection testing

**Impact:** ⚠️ Critical - Cannot expose to internet without security hardening

---

### No Encryption at Rest

**Current State:**
- SQLite database is unencrypted
- No PII encryption
- Plaintext storage for all fields

**Why:**
- Synthetic data only
- No real user data to protect
- Demonstration purposes

**Production Requirements:**
- Encrypt SQLite database (SQLCipher)
- Field-level encryption for PII
- Secure key management (AWS KMS, HashiCorp Vault)
- Encryption in transit (TLS/HTTPS)

**Impact:** ⚠️ Critical - Cannot store real financial data without encryption

---

### No Audit Logging

**Current State:**
- Basic application logging only
- No user action tracking
- No compliance audit trail
- No anomaly detection

**Why:**
- Not required for demonstration
- Adds complexity

**Production Requirements:**
- Implement comprehensive audit logging
- Track all data access and modifications
- Store logs in separate system (Splunk, ELK)
- Retention per compliance requirements (7 years for financial)

**Impact:** ⚠️ Critical for compliance - Required for any regulated financial service

---

## Performance Benchmarks

### Current Performance (50 users)

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Coverage | 100% | 100% | ✅ Exceeds |
| Explainability | 100% | 100% | ✅ Exceeds |
| Latency (avg) | 0.002s | <5s | ✅ Exceeds |
| Auditability | 100% | 100% | ✅ Exceeds |

### Expected Performance at Scale

| Users | Latency | Notes |
|-------|---------|-------|
| 50 | 0.002s | Current performance |
| 100 | 0.005s | No changes needed |
| 500 | 0.05-0.1s | Add caching |
| 1,000 | 0.1-0.5s | Add caching + PostgreSQL |
| 10,000 | 0.5-2s | Full production stack |

---

## Conclusion

### What SpendSense Does Well

✅ **Demonstrates core concept** - Persona-based financial recommendations
✅ **Exceptional performance** - Sub-10ms latency at current scale
✅ **100% auditable** - Complete decision traceability
✅ **Zero cost** - No API fees or cloud services
✅ **Easy to demo** - Runs on laptop, no setup required

### What It Doesn't Do

❌ **Production scale** - Limited to 50-100 users
❌ **Real data** - Synthetic only, no bank integrations
❌ **Security** - No auth, encryption, or compliance
❌ **Advanced features** - No goals, notifications, or user management
❌ **AI personalization** - Template-based content only

### Path to Production

To deploy SpendSense with real users, you would need:

1. **Infrastructure** (2-3 weeks)
   - Migrate to PostgreSQL
   - Add Redis caching
   - Implement authentication
   - Add encryption

2. **Integrations** (3-4 weeks)
   - Plaid API for bank connections
   - LLM for content generation
   - Email/push notifications

3. **Compliance** (8-12 weeks)
   - PCI-DSS certification
   - SOC 2 audit
   - GDPR compliance
   - Privacy policy and ToS

4. **Scale Testing** (2-3 weeks)
   - Load testing to 10K users
   - Performance optimization
   - CDN setup

**Total Estimate:** 4-6 months to production-ready with real users

---

## Related Documents

- [Architecture](./architecture.md) - Technical architecture details
- [Decision Log](./DECISION_LOG.md) - Why these choices were made
- [Schema](./SCHEMA.md) - Database schema documentation
- [PRD](./PRD.md) - Product requirements and success criteria
