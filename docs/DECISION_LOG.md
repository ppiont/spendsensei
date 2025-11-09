# Decision Log

This document captures key technical and architectural decisions made during the development of SpendSense.

## Table of Contents
- [Architecture Decisions](#architecture-decisions)
- [Technology Choices](#technology-choices)
- [Design Patterns](#design-patterns)
- [Trade-offs](#trade-offs)

## Architecture Decisions

### ADR-001: No Automated Testing Framework

**Decision:** Manual testing only, no pytest or automated test suite

**Rationale:**
- Project scope is demonstration/prototype, not production system
- Manual test scripts provide sufficient coverage for 50-100 user scale
- Reduces complexity and dependencies
- Faster iteration during development

**Trade-offs:**
- ✅ Simpler codebase, faster development
- ❌ Manual regression testing required for changes
- ❌ No CI/CD automation

**Status:** Implemented - All test scripts in `scripts/test_*.py`

---

### ADR-002: Template-Based Content Generation

**Decision:** Use template-based content generation instead of LLM

**Rationale:**
- Zero cost (no API keys or cloud dependencies)
- 100% explainability and auditability
- Deterministic outputs for testing
- Fast generation (<1ms per recommendation)
- Good enough for demonstration purposes

**Trade-offs:**
- ✅ Free, fast, deterministic, fully auditable
- ❌ Less personalized than LLM-generated content
- ❌ Limited to pre-written content catalog

**Status:** Implemented - `generators/template.py` with 12 educational items

---

### ADR-003: On-Demand Signal Computation

**Decision:** Compute behavioral signals on-demand, no pre-computation or caching

**Rationale:**
- Always current data (no stale recommendations)
- Simpler architecture (no cache invalidation logic)
- Performance adequate for 50-100 users (<5s target easily met)
- Measured: 0.002s average latency (1000x better than target!)

**Trade-offs:**
- ✅ Always fresh, simpler code, sub-10ms latency
- ❌ Repeated computation if same user requests twice
- ❌ Doesn't scale to 1000s of users without caching

**Status:** Implemented - All signals computed per request

---

### ADR-004: SQLite with WAL Mode

**Decision:** Use SQLite with Write-Ahead Logging, single file database

**Rationale:**
- Local-first design (no server required)
- Perfect for 50-100 user scale
- Fast queries with proper indexes
- Easy to version control and share
- WAL mode provides better concurrency

**Trade-offs:**
- ✅ Zero setup, portable, version-controllable
- ❌ Not suitable for production scale (100+ concurrent users)
- ❌ Limited to single-machine deployment

**Status:** Implemented - `data/spendsense.db` with WAL mode enabled

---

### ADR-005: shadcn-svelte Component Library

**Decision:** Use shadcn-svelte for UI components

**Rationale:**
- Copy-paste components (no external dependencies)
- Full customization control
- Svelte 5 + Tailwind v4 compatible
- Accessible out of the box

**Trade-offs:**
- ✅ No runtime dependencies, fully customizable
- ❌ Must manually update components (not npm installed)

**Status:** Implemented - Components in `frontend/src/lib/components/ui/`

---

### ADR-006: Bun over npm

**Decision:** Use Bun as JavaScript package manager and runtime

**Rationale:**
- 10-100x faster than npm for install/run
- Native TypeScript support
- Better developer experience
- Compatible with npm packages

**Trade-offs:**
- ✅ Much faster, better DX
- ❌ Newer tool (less mature than npm)
- ❌ Potential compatibility issues with some packages

**Status:** Implemented - Frontend uses Bun exclusively

---

### ADR-007: Module Reorganization for Project Description Compliance

**Decision:** Reorganize codebase from generic module names (routers/, services/, generators/) to domain-specific modules (ui/, features/, personas/, recommend/, guardrails/, ingest/, eval/)

**Context:**
- Original Project Description specified 8 required modules with specific naming
- Initial implementation used generic names that didn't match requirements
- Needed to refactor for architectural compliance and maintainability

**Rationale:**
- **Compliance**: Project Description explicitly required specific module structure
- **Clarity**: Domain-specific names make purpose immediately obvious
- **Separation of Concerns**: Clear boundaries between data loading, analysis, decision-making, and safety
- **Maintainability**: Easier to locate and modify code when modules match domain concepts
- **Auditability**: Straightforward to verify each requirement is properly implemented

**Implementation:**
- Created 8 new modules: `ingest/`, `features/`, `personas/`, `recommend/`, `guardrails/`, `ui/`, `eval/`
- Split monolithic `services/features.py` (692 lines) into 6 modular files
- Moved 100+ imports across entire codebase
- Added comprehensive `__init__.py` files for clean public APIs
- Maintained backward compatibility through aliases where needed

**Trade-offs:**
- ✅ Clear domain boundaries and improved code organization
- ✅ Easier to audit against Project Description requirements
- ✅ Better separation of concerns (one module = one responsibility)
- ✅ Easier onboarding for new developers (self-documenting structure)
- ❌ One-time refactoring effort (~4-6 hours)
- ❌ Slightly deeper import paths

**Impact:**
- All 16 test scripts pass without modification to logic
- API endpoints continue working identically
- Zero functional changes, pure organizational refactoring
- Documentation updated (README, CLAUDE.md)

**Status:** Implemented (2025-11-09) - All modules reorganized, tests passing, systems operational

---

## Technology Choices

### Backend Stack

| Technology | Version | Rationale |
|------------|---------|-----------|
| Python | 3.13.8 | Latest stable, free-threading support, JIT improvements |
| FastAPI | 0.120.4 | Async support, automatic OpenAPI docs, modern Python |
| SQLAlchemy | 2.0.44 | Async ORM, type safety, modern API |
| SQLite | 3.x | Local-first, zero setup, perfect for demo scale |
| uv | Latest | 10-100x faster than pip, deterministic |
| ruff | Latest | Rust-based Python linter, extremely fast |

### Frontend Stack

| Technology | Version | Rationale |
|------------|---------|-----------|
| SvelteKit | 2.48.4 | Latest stable, SSR support, great DX |
| Svelte | 5.x | Modern runes API, smaller bundles, faster |
| TypeScript | 5.x | Type safety, better IDE support |
| Tailwind CSS | 4.x | Latest version, utility-first, fast |
| Bun | Latest | Faster than npm, native TS support |
| Biome | Latest | Fast linter/formatter for JS/TS |

### Why These Choices?

**Latest versions everywhere:**
- Demonstrates modern best practices
- Access to latest features and performance improvements
- Future-proof for 2025+

**Local-first:**
- No cloud dependencies (except optional MCP servers)
- Works offline
- Zero operational costs
- Easy to demo and share

**Performance-focused:**
- FastAPI (async), Svelte (compiled), SQLite (in-process)
- Result: <10ms per user recommendation generation!

---

## Design Patterns

### Recommendation Pipeline Pattern

**Pattern:** Three-stage pipeline with signal detection → persona assignment → content generation

**Why:**
- Clean separation of concerns
- Each stage independently testable
- Easy to swap implementations (e.g., template → LLM)
- Full traceability at each step

**Implementation:**
```
signals = compute_signals()  # Stage 1: Detection
persona = assign_persona()   # Stage 2: Classification
content = generate_content() # Stage 3: Generation
```

---

### AI-Agnostic Generator Pattern

**Pattern:** Abstract base class `ContentGenerator` with template and LLM implementations

**Why:**
- Template for demo (free, fast, deterministic)
- LLM ready for production (better personalization)
- Same interface for both
- Swap via dependency injection

**Implementation:**
- `generators/base.py` - Abstract interface
- `generators/template.py` - Template implementation
- `generators/llm.py` - LLM implementation (interface only)

---

### Async All The Way

**Pattern:** Full async/await from API routes to database

**Why:**
- Non-blocking I/O for better concurrency
- Natural fit for FastAPI + SQLAlchemy
- Better performance under load
- Modern Python best practice

**Result:** Sub-10ms latency even with database queries

---

## Trade-offs

### Demonstration vs Production

**Demonstration Focus:**
- Manual testing instead of automated
- SQLite instead of PostgreSQL
- Template instead of LLM
- 50-100 users instead of unlimited scale

**Result:**
- ✅ Faster development
- ✅ Zero operational costs
- ✅ Perfect for portfolio/demo
- ❌ Would need significant changes for production

---

### Simplicity vs Features

**Chose Simplicity:**
- No authentication/authorization
- No user management UI
- No real bank integrations
- Synthetic data only

**Result:**
- ✅ Core functionality shines
- ✅ Easy to understand and demo
- ❌ Not directly deployable to real users

---

### Template vs LLM

**Chose Template (with LLM interface ready):**
- Free and deterministic for demo
- LLM infrastructure exists but unused
- Can swap to LLM with zero API changes

**Result:**
- ✅ Works great for demo
- ✅ Ready for LLM when needed
- ❌ Content less personalized than possible

---

## Lessons Learned

### What Worked Well

1. **Local-first architecture** - Zero deployment complexity
2. **Latest tech stack** - Great developer experience
3. **Template-based content** - Fast enough, fully auditable
4. **Comprehensive evaluation** - Proved all metrics exceeded targets

### What We'd Change for Production

1. Add automated testing (pytest)
2. Switch to PostgreSQL for scalability
3. Implement LLM generation for personalization
4. Add authentication and user management
5. Implement real bank integrations (Plaid API)
6. Add caching layer for repeated requests
7. Implement rate limiting and security hardening

---

## Related Documents

- [Architecture](./architecture.md) - Detailed technical architecture
- [Schema](./SCHEMA.md) - Database schema and relationships
- [Limitations](./LIMITATIONS.md) - Known limitations and constraints
- [PRD](./PRD.md) - Product requirements and success criteria
