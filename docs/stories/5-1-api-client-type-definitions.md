# Story 5.1: API Client & Type Definitions

Status: done

## Story

As a frontend developer,
I want a typed API client for backend communication,
So that I can easily fetch data with type safety.

## Acceptance Criteria

1. Create `lib/types/index.ts` with TypeScript interfaces
2. Create `lib/api/client.ts` with fetch wrapper functions
3. Use environment variable API_BASE_URL from .env
4. Add error handling for failed requests
5. Parse JSON responses automatically
6. Include proper TypeScript return types
7. Handle 404 and 500 errors
8. Add request timeout (10 seconds)
9. Verify client connects to localhost:8000
10. Test with real API calls

## Tasks / Subtasks

- [x] Create lib/types/index.ts with all interfaces
- [x] Create lib/api/client.ts with fetch functions
- [x] Add error handling
- [x] Test with backend API

## Dev Notes

**New files:**
- spendsense-frontend/src/lib/types/index.ts
- spendsense-frontend/src/lib/api/client.ts
- spendsense-frontend/.env
- spendsense-frontend/src/lib/api/client.test.ts

## Dev Agent Record

### Context Reference

No context file provided - implemented based on story file and backend API schemas.

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

**Implementation Plan:**
1. Created lib/types/index.ts with all TypeScript interfaces matching backend Pydantic schemas
2. Created lib/api/client.ts with typed fetch wrapper functions
3. Added .env file with VITE_API_BASE_URL environment variable
4. Implemented comprehensive error handling (APIClientError class)
5. Added 10-second request timeout with AbortController
6. Automatic JSON parsing for all responses
7. Proper TypeScript return types for all API functions
8. 404 and 500 error handling with status codes
9. Created test suite to verify client functionality

### Completion Notes List

- ✅ Created lib/types/index.ts with TypeScript interfaces: User, Account, Transaction, Recommendation
- ✅ Added helper functions: centsToDollars, dollarsToCents, formatCurrency
- ✅ Created lib/api/client.ts with organized API modules: userAPI, accountAPI, transactionAPI, insightsAPI
- ✅ Implemented fetchWithTimeout helper with AbortController for 10s timeout
- ✅ Implemented handleResponse helper for error handling and JSON parsing
- ✅ Added APIClientError class for structured error handling
- ✅ All API functions have proper TypeScript return types
- ✅ Handles 404 and 500 errors with status codes and detail messages
- ✅ Created .env file with API_BASE_URL=http://localhost:8000
- ✅ Created client.test.ts with test functions for all API endpoints
- ✅ Network error handling (timeouts, connection issues)
- ✅ Content-type validation for JSON responses
- ✅ Proper headers including Content-Type: application/json

### File List

**NEW:**
- src/lib/types/index.ts
- src/lib/api/client.ts
- src/lib/api/client.test.ts
- .env

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
| 2025-11-03 | Amelia (Dev Agent) | Complete implementation of typed API client with error handling and tests |
