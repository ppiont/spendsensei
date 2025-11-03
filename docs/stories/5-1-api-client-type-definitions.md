# Story 5.1: API Client & Type Definitions

Status: drafted

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

- [ ] Create lib/types/index.ts with all interfaces
- [ ] Create lib/api/client.ts with fetch functions
- [ ] Add error handling
- [ ] Test with backend API

## Dev Notes

**New files:**
- spendsense-frontend/src/lib/types/index.ts
- spendsense-frontend/src/lib/api/client.ts

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation |
