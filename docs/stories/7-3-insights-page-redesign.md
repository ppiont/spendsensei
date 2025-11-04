# Story 7.3: Insights Page Redesign

**Epic:** 7 - UX Redesign - Calm & Focused Interface
**Status:** TODO
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
- [ ] Prominent persona explanation section at top (hero section)
- [ ] 3-column recommendation grid below
- [ ] Remove or minimize KPI cards (not primary focus)
- [ ] Apply same generous spacing as dashboard

### 2. Replace existing insights page with new layout
- [ ] Update `src/routes/insights/+page.svelte`
- [ ] Remove old insights components
- [ ] Implement new layout structure

### 3. Add persona explanation section
- [ ] Large PersonaBadge component (72px avatar)
- [ ] Persona name (H2, semibold, gray-800)
- [ ] Plain-language description (2-3 sentences)
- [ ] "What this means" expandable accordion
- [ ] Window selector tabs (30d / 180d)
- [ ] 48px padding (p-12) for hero section

### 4. Implement expandable recommendation cards
- [ ] **Collapsed state:**
  - Title (font-semibold, 1rem)
  - Summary (3 lines max, line-clamp-3)
  - "Because..." rationale box (gray-50 bg)
  - Expand indicator (chevron down icon)
- [ ] **Expanded state:**
  - Full body text (no line clamp)
  - Detailed rationale with data citations
  - CTA button visible
  - Chevron up icon
- [ ] Smooth expand/collapse animation (300ms)
- [ ] Click anywhere on card to toggle
- [ ] Use $state to track expanded card IDs

### 5. Update color usage per UX spec
- [ ] Blue = Trust: primary buttons, links, financial data
- [ ] Green = Growth: positive metrics, savings indicators
- [ ] Coral = Caution: warnings only (high utilization, overdue)
- [ ] Yellow = Learn: educational badges, tips
- [ ] Verify semantic color usage throughout

### 6. Add data citations to rationales
- [ ] Pull specific data points from signals:
  - "Based on your card ending in {last4} at {utilization}% utilization"
  - "You have {count} recurring subscriptions totaling ${amount}/month"
  - "Your emergency fund covers {months} months of expenses"
- [ ] Use monospace font (font-mono) for numbers
- [ ] Include account hints (last 4 digits)
- [ ] Format currency with 2 decimals

### 7. Include disclaimer at bottom
- [ ] Use shadcn Alert component (blue variant, info type)
- [ ] Text: "This is educational content, not financial advice"
- [ ] Icon: info circle
- [ ] Position: bottom of page, full width

### 8. Apply generous white space
- [ ] Persona section padding: 48px (p-12)
- [ ] Card padding: 32px (p-8)
- [ ] Between sections: 48px (space-y-12)
- [ ] Grid gap: 24px (gap-6)

### 9. Add loading states
- [ ] Skeleton loaders for persona badge
- [ ] Skeleton loaders for recommendation cards (not spinners)
  - Title skeleton (w-3/4 h-6)
  - Body skeleton (3 lines, w-full h-4)
  - Rationale skeleton (w-full h-16)
- [ ] Fade-in animation when loaded (300ms opacity transition)

### 10. Verify window selector updates recommendations
- [ ] shadcn Tabs component for 30d / 180d
- [ ] Active tab: blue-primary background, white text
- [ ] Inactive tab: transparent, gray-600 text
- [ ] API call on tab change: `/insights/{user_id}?window={window}`
- [ ] Update recommendations without page reload

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

- [ ] Direction 6 layout adapted for insights
- [ ] Persona explanation section implemented
- [ ] Expandable recommendation cards work smoothly
- [ ] Semantic color usage correct
- [ ] Data citations show real user data
- [ ] Disclaimer displayed
- [ ] Generous spacing applied
- [ ] Skeleton loaders implemented
- [ ] Window selector switches data
- [ ] No layout shift on expand/collapse

---

## Dependencies

**Prerequisites:** Story 7.2 (Dashboard Page Redesign)
**Blocks:** Story 7.4 (Transactions Page Redesign)

---

## Reference

**Design Spec:** `docs/ux-design-specification.md` Section 4.1, 7.1
**API Endpoint:** `/insights/{user_id}?window={30d|180d}`
