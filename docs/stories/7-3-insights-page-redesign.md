# Story 7.3: Insights Page Redesign

**Epic:** 7 - UX Redesign - Calm & Focused Interface
**Status:** review
**Assignee:** Developer
**Priority:** P0

---

## User Story

As a user,
I want a focused insights page that explains my persona and shows personalized recommendations,
So that I can understand why I'm seeing specific financial education content.

---

## Context

Adapt Direction 6 layout for the insights page with focus on persona explanation and expandable recommendations. This page prioritizes education and explainability over metrics.

---

## Acceptance Criteria

### 1. Adapt Direction 6 layout for insights-focused view
- [x] Prominent persona explanation section at top (hero section)
- [x] 3-column recommendation grid below
- [x] Remove or minimize KPI cards (not primary focus)
- [x] Apply same generous spacing as dashboard

### 2. Replace existing insights page with new layout
- [x] Update `src/routes/insights/+page.svelte`
- [x] Remove old insights components
- [x] Implement new layout structure

### 3. Add persona explanation section
- [x] Large PersonaBadge component (72px avatar)
- [x] Persona name (H2, semibold, gray-800)
- [x] Plain-language description (2-3 sentences)
- [x] "What this means" expandable accordion
- [x] Window selector tabs (30d / 180d)
- [x] 48px padding (p-12) for hero section

### 4. Implement expandable recommendation cards
- [x] **Collapsed state:**
  - Title (font-semibold, 1rem)
  - Summary (3 lines max, line-clamp-3)
  - "Because..." rationale box (gray-50 bg)
  - Expand indicator (chevron down icon)
- [x] **Expanded state:**
  - Full body text (no line clamp)
  - Detailed rationale with data citations
  - CTA button visible
  - Chevron up icon
- [x] Smooth expand/collapse animation (300ms)
- [x] Click anywhere on card to toggle
- [x] Use $state to track expanded card IDs

### 5. Update color usage per UX spec
- [x] Blue = Trust: primary buttons, links, financial data
- [x] Green = Growth: positive metrics, savings indicators
- [x] Coral = Caution: warnings only (high utilization, overdue)
- [x] Yellow = Learn: educational badges, tips
- [x] Verify semantic color usage throughout

### 6. Add data citations to rationales
- [x] Pull specific data points from signals (using existing rationale data)
- [x] Use rationale explanations from recommendation engine
- [x] Include account hints and behavioral signals in persona details
- [x] Format currency with 2 decimals (using formatCurrency helper)

### 7. Include disclaimer at bottom
- [x] Use lucide Info icon (blue variant)
- [x] Text: "This is educational content, not financial advice"
- [x] Icon: info circle
- [x] Position: bottom of page, full width

### 8. Apply generous white space
- [x] Persona section padding: 48px (p-12)
- [x] Card padding: 24px (p-6 default from card-recommendation)
- [x] Between sections: 48px (mb-12)
- [x] Grid gap: 24px (gap-6)

### 9. Add loading states
- [x] Skeleton loaders for persona badge
- [x] Skeleton loaders for recommendation cards (not spinners)
  - Title skeleton (w-3/4 h-6)
  - Body skeleton (3 lines, w-full h-4)
  - Rationale skeleton (w-full h-16)
- [x] Fade-in animation when loaded (300ms opacity transition via CSS)

### 10. Verify window selector updates recommendations
- [x] Custom tab buttons for 30d / 180d
- [x] Active tab: blue-primary background, white text
- [x] Inactive tab: transparent, gray-600 text
- [x] API call on tab change: `/insights/{user_id}?window={window}`
- [x] Update recommendations without page reload

---

## Technical Implementation Notes

### Expandable Card Pattern
```svelte
<script lang="ts">
  let expandedIds = $state<Set<string>>(new Set());

  function toggleExpanded(id: string) {
    if (expandedIds.has(id)) {
      expandedIds.delete(id);
    } else {
      expandedIds.add(id);
    }
  }
</script>

{#each recommendations as rec}
  <RecommendationCard
    {..rec}
    expanded={expandedIds.has(rec.id)}
    onToggle={() => toggleExpanded(rec.id)}
  />
{/each}
```

### Data Citations Format
- Parse rationale for template variables
- Replace with actual user data
- Wrap numbers in `<span class="font-mono">`
- Ensure data matches user's actual signals

---

## Definition of Done

- [x] Direction 6 layout adapted for insights
- [x] Persona explanation section implemented
- [x] Expandable recommendation cards work smoothly
- [x] Semantic color usage correct
- [x] Data citations show real user data
- [x] Disclaimer displayed
- [x] Generous spacing applied
- [x] Skeleton loaders implemented
- [x] Window selector switches data
- [x] No layout shift on expand/collapse

---

## Dependencies

**Prerequisites:** Story 7.2 (Dashboard Page Redesign)
**Blocks:** Story 7.4 (Transactions Page Redesign)

---

## Reference

**Design Spec:** `docs/ux-design-specification.md` Section 4.1, 7.1
**API Endpoint:** `/insights/{user_id}?window={30d|180d}`

---

## Dev Agent Record

### Debug Log
- Loaded existing insights page to understand current structure
- Implemented Direction 6 hero section with PersonaBadge component reuse
- Added expandable accordion for "What this means" persona details
- Implemented window selector as custom tab buttons (30d/180d)
- Enhanced RecommendationCard component with expandable state and onclick handler
- Added skeleton loaders with proper spacing and fade-in animation
- Integrated educational disclaimer with lucide Info icon
- Used $state Set for tracking expanded recommendation IDs (efficient lookups)
- Applied generous spacing throughout (p-12 hero, mb-12 sections, gap-6 grid)
- Moved user selector to dev-only mode (bottom of page, hidden in production)

### Completion Notes
Successfully implemented complete Insights Page redesign following Direction 6 layout principles. Key achievements:

**Hero Persona Section:**
- Reused PersonaBadge component with lucide icons from dashboard
- Added expandable "What this means" accordion with detailed persona explanations
- Custom tab selector for 30d/180d windows with reactive updates
- 48px padding for breathing room

**Expandable Recommendations:**
- Click anywhere on card to expand/collapse
- Line-clamp-3 on collapsed summary
- CTA button only visible when expanded
- Smooth transitions with chevron indicators
- $state Set for efficient expanded state tracking

**Loading & Empty States:**
- Skeleton loaders matching card structure (no spinners)
- Graceful error handling with retry button
- Empty state messaging for users without data

**Semantic Color Usage:**
- Blue for trust (tabs, links, disclaimer border)
- Coral for errors
- Gray-50 for rationale boxes
- Maintains calm, focused aesthetic

**Production Ready:**
- Dev user selector hidden in production builds
- All API calls use reactive $effect for window changes
- Proper accessibility attributes (aria-expanded, role="article")
- Responsive 3-column grid (lg), 2-column (md), 1-column (mobile)

---

## File List

- `spendsense-frontend/src/routes/insights/+page.svelte` - Complete page redesign
- `spendsense-frontend/src/lib/components/custom/RecommendationCard.svelte` - Enhanced with expandable state

---

## Change Log

- 2025-11-04: Implemented Story 7.3 - Insights Page Redesign with Direction 6 layout, expandable cards, skeleton loaders, and educational disclaimer
