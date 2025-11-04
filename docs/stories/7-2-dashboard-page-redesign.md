# Story 7.2: Dashboard Page Redesign

**Epic:** 7 - UX Redesign - Calm & Focused Interface
**Status:** TODO
**Assignee:** Developer
**Priority:** P0

---

## User Story

As a user,
I want a calm, data-focused dashboard with prominent KPIs and clear recommendations,
So that I can understand my financial health at a glance without feeling overwhelmed.

---

## Context

Redesign the dashboard page using Direction 6 (Stripe-inspired) layout. Replace the current basic dashboard with a professional metrics grid featuring a 2x-width featured KPI, 4 supporting metrics, and 3 recommendation cards with clear rationales.

**Visual Reference:** `docs/ux-design-specification.md` Section 4 (Design Direction)

---

## Acceptance Criteria

### 1. Implement Direction 6 layout structure
- [ ] Create 4-column CSS Grid for metrics
- [ ] Top bar: Persona badge (left) + user selector (right)
- [ ] Featured KPI spans 2 columns (grid-column: span 2)
- [ ] 4 supporting KPIs in remaining grid cells
- [ ] Recommendations section below metrics (3-column grid)

### 2. Replace existing dashboard with new layout
- [ ] Update `src/routes/dashboard/+page.svelte`
- [ ] Remove old dashboard components
- [ ] Implement new grid-based layout
- [ ] Verify layout renders correctly

### 3. Add 5 KPI cards using KpiCard component
- [ ] **Featured (2x width):** Total Net Worth
  - Calculate from accounts: (checking + savings) - credit balances
  - Show trend arrow (month-over-month change)
  - Use `variant="featured"`
- [ ] **Supporting:** Monthly Savings Rate
  - Calculate: net inflow to savings / total income
  - Format as percentage
- [ ] **Supporting:** Credit Health
  - Show credit utilization percentage
  - Color: green (<30%), yellow (30-50%), coral (>50%)
- [ ] **Supporting:** Emergency Fund
  - Show months of expenses covered
  - Format: "X.X months"
- [ ] **Supporting:** Monthly Subscriptions
  - Show count of recurring transactions
  - Format: "N subscriptions"

### 4. Wire KPI cards to real API data
- [ ] Fetch accounts from `/accounts/{user_id}` endpoint
- [ ] Fetch transactions from `/transactions/{user_id}` endpoint
- [ ] Calculate KPI values from API data
- [ ] Handle loading states (skeleton loaders)
- [ ] Handle errors gracefully

### 5. Format financial values
- [ ] Currency: Use `formatCurrency()` helper
  - Format: $X,XXX.XX (dollars with 2 decimals)
  - Handle negative values (wrap in parentheses)
- [ ] Percentages: 1 decimal place with % symbol
- [ ] Trends:
  - Green arrow ↑ for positive changes
  - Red arrow ↓ for negative changes
  - Show percentage change

### 6. Update recommendation cards with "Because..." rationales
- [ ] Use `RecommendationCard` component from Story 7.1
- [ ] Fetch recommendations from `/insights/{user_id}` endpoint
- [ ] Display icon (40px blue circle with emoji)
- [ ] Show "EDUCATION" badge
- [ ] Display title (font-semibold)
- [ ] Show body text (3-4 lines, collapsed)
- [ ] Show rationale in gray-50 box with "Because:" prefix
- [ ] Add "Learn More" CTA button (blue-primary)

### 7. Apply generous spacing
- [ ] Card padding: 32px (p-8)
- [ ] Grid gaps: 24px (gap-6)
- [ ] Section margins: 48px (space-y-12)
- [ ] Between top bar and metrics: 24px
- [ ] Between metrics and recommendations: 48px

### 8. Add persona badge to top bar
- [ ] Use `PersonaBadge` component from Story 7.1
- [ ] Show gradient avatar (blue→green circle)
- [ ] Display persona name (semibold, gray-800)
- [ ] Show confidence percentage (small, gray-600)
- [ ] Position: left side of top bar
- [ ] User selector: right side of top bar

### 9. Implement subtle shadows
- [ ] Cards at rest: `shadow-subtle` class
- [ ] Cards on hover: `shadow-soft` class
- [ ] Add 2px lift on hover: `translate-y-[-2px]`
- [ ] Smooth transition: `transition-all duration-150`

### 10. Verify responsive behavior
- [ ] **Desktop (1024px+):** 4-column grid
  - Featured KPI spans 2 columns
  - 4 supporting KPIs fill grid
  - 3 recommendation columns
- [ ] **Tablet (768-1023px):** 2-column grid
  - Featured KPI spans 2 columns
  - Supporting KPIs in 2x2 grid
  - 2 recommendation columns
- [ ] **Mobile (<768px):** 1-column stack
  - All KPIs full width
  - Featured KPI gets visual priority (gradient)
  - Recommendations full width

---

## Technical Implementation Notes

### Grid Layout Example
```svelte
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <div class="col-span-1 md:col-span-2">
    <KpiCard variant="featured" label="NET WORTH" value={netWorth} change={netWorthChange} />
  </div>
  <KpiCard label="MONTHLY SAVINGS" value={savingsRate} />
  <KpiCard label="CREDIT HEALTH" value={creditHealth} />
  <KpiCard label="EMERGENCY FUND" value={emergencyFund} />
  <KpiCard label="SUBSCRIPTIONS" value={subscriptionCount} />
</div>
```

### Data Flow
- Use $state for selectedUserId
- Use $derived for computed values (netWorth, savingsRate)
- Use $effect for API calls on user change
- Maintain existing API client from Story 5.2

---

## Definition of Done

- [ ] Direction 6 layout implemented
- [ ] 5 KPI cards render with real data
- [ ] Recommendation cards show with rationales
- [ ] Generous spacing applied throughout
- [ ] Persona badge displays in top bar
- [ ] Subtle shadows and hover states work
- [ ] Responsive at all breakpoints
- [ ] No regressions in functionality
- [ ] Visual matches UX spec

---

## Dependencies

**Prerequisites:** Story 7.1 (Design System Foundation)
**Blocks:** Story 7.3 (Insights Page Redesign)

---

## Reference

**Design Spec:** `docs/ux-design-specification.md` Section 4.1
**API Endpoints:** `/accounts/{user_id}`, `/transactions/{user_id}`, `/insights/{user_id}`
