# Story 1.1: Backend Project Setup

Status: drafted

## Story

As a developer,
I want the backend project initialized with modern Python tooling,
So that I have a working foundation for API development.

## Acceptance Criteria

1. Create `spendsense-backend/` directory with uv project structure
2. Configure `pyproject.toml` with Python 3.13.8 requirement
3. Install core dependencies: `fastapi[standard]`, `sqlalchemy`, `aiosqlite`, `pydantic`, `faker`, `ruff`
4. Create `src/spendsense/` module structure with `__init__.py`
5. Configure `ruff.toml` with linting rules
6. Create `.python-version` file set to 3.13
7. Verify `uv sync` runs successfully
8. Create basic `main.py` with FastAPI app that returns "Hello SpendSense" on GET /

## Tasks / Subtasks

- [ ] **Task 1: Initialize project with uv** (AC: #1, #2, #3)
  - [ ] Run `uv init spendsense-backend` from project root
  - [ ] Navigate to `spendsense-backend/` directory
  - [ ] Configure `pyproject.toml`:
    - Set `requires-python = ">=3.13.8"`
    - Add dependencies: `fastapi[standard]`, `sqlalchemy`, `aiosqlite`, `pydantic`, `faker`, `ruff`
  - [ ] Run `uv add "fastapi[standard]" sqlalchemy aiosqlite pydantic faker ruff`

- [ ] **Task 2: Create module structure** (AC: #4)
  - [ ] Create directory structure: `src/spendsense/`
  - [ ] Create `src/spendsense/__init__.py` (empty or with package metadata)

- [ ] **Task 3: Configure linting** (AC: #5, #6)
  - [ ] Create `ruff.toml` in project root with configuration:
    ```toml
    target-version = "py313"
    line-length = 100

    [lint]
    select = ["E", "F", "I", "N", "W"]
    ignore = []

    [format]
    quote-style = "double"
    indent-style = "space"
    ```
  - [ ] Create `.python-version` file containing `3.13`

- [ ] **Task 4: Verify installation** (AC: #7)
  - [ ] Run `uv sync` to verify all dependencies install correctly
  - [ ] Confirm virtual environment created
  - [ ] Verify Python 3.13 is active: `uv run python --version`

- [ ] **Task 5: Create minimal FastAPI application** (AC: #8)
  - [ ] Create `src/spendsense/main.py`
  - [ ] Import FastAPI and create app instance
  - [ ] Add GET / route returning `{"message": "Hello SpendSense"}`
  - [ ] Test with: `uv run uvicorn spendsense.main:app --reload`
  - [ ] Verify endpoint responds at http://localhost:8000/
  - [ ] Verify OpenAPI docs accessible at http://localhost:8000/docs

## Dev Notes

### Architecture Context

**From architecture.md:**
- Backend uses Python 3.13.8 (latest stable, free-threading + JIT support)
- FastAPI 0.120.4 for async API framework
- uv package manager (10-100x faster than pip)
- ruff for linting and formatting
- No migrations framework - use `create_all()` for schema
- No testing framework - linting only

**Backend initialization sequence:**
```bash
# Initialize Python project with uv
uv init spendsense-backend
cd spendsense-backend

# Install core dependencies
uv add "fastapi[standard]"  # Includes uvicorn
uv add sqlalchemy aiosqlite  # Database ORM + SQLite async driver
uv add pydantic faker        # Validation + synthetic data
uv add ruff                  # Linting and formatting
```

**Naming conventions to follow (Python):**
- Files: `snake_case.py` (e.g., `main.py`, `database.py`)
- Classes: `PascalCase` (e.g., `ContentGenerator`)
- Functions: `snake_case()` (e.g., `compute_signals()`)
- Variables: `snake_case` (e.g., `user_id`, `window_days`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DATABASE_URL`)

### Project Structure Notes

**Expected directory structure after this story:**
```
spendsense-backend/
├── .python-version               # 3.13
├── pyproject.toml                # uv config + dependencies
├── ruff.toml                     # Linter config
└── src/
    └── spendsense/
        ├── __init__.py
        └── main.py               # FastAPI app entry
```

**Future structure (subsequent stories will add):**
- `src/spendsense/config.py` - Pydantic Settings
- `src/spendsense/database.py` - SQLAlchemy setup + WAL mode
- `src/spendsense/models/` - ORM models (Story 1.3)
- `src/spendsense/schemas/` - Pydantic request/response
- `src/spendsense/routers/` - API endpoints
- `src/spendsense/services/` - Business logic
- `src/spendsense/generators/` - Content generation
- `src/spendsense/utils/` - Guardrails and utilities
- `data/` - SQLite database and content catalog

### Testing Strategy

**Manual verification only:**
1. Run `uv sync` - should complete without errors
2. Check `uv run python --version` outputs Python 3.13.x
3. Start server: `uv run uvicorn spendsense.main:app --reload`
4. Visit http://localhost:8000/ - should return JSON with "Hello SpendSense"
5. Visit http://localhost:8000/docs - should show Swagger UI
6. Run `ruff check src/` - should pass with no violations

**No automated tests required** per PRD constraints.

### References

- [Source: docs/PRD.md#Technology Stack]
- [Source: docs/architecture.md#Backend Initialization]
- [Source: docs/architecture.md#Backend Naming Conventions (Python)]
- [Source: docs/epics.md#Story 1.1: Backend Project Setup]

### Learnings from Previous Story

**First story in epic** - no predecessor context.

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

_To be filled by dev agent_

### File List

_To be filled by dev agent_

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
