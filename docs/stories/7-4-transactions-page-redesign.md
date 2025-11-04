# Story 7.4: Transactions Page Redesign

**Epic:** 7 - UX Redesign - Calm & Focused Interface
**Status:** TODO
**Assignee:** Developer
**Priority:** P1

---

## User Story

As a user,
I want a clean, scannable transaction list with effective filtering,
So that I can review my spending patterns without visual clutter.

---

## Context

Redesign the transactions page with shadcn Table component, generous spacing, and semantic color coding. Focus on scannability and calm aesthetic.

---

## Acceptance Criteria

### 1. Replace existing transactions page with calm aesthetic
- [ ] Update `src/routes/transactions/+page.svelte`
- [ ] Remove old transaction components
- [ ] Implement new table-based layout

### 2. Implement shadcn Table component
- [ ] Columns: Date, Merchant, Category, Amount, Status
- [ ] Alternating row backgrounds (white / gray-50)
- [ ] Hover state: gray-100 background
- [ ] Header: semibold, gray-700, uppercase tracking-wide
- [ ] Borders: subtle gray-100 (not heavy)

### 3. Apply generous spacing
- [ ] Table cell padding: 12px vertical, 16px horizontal (py-3 px-4)
- [ ] Row height: minimum 48px for touch targets
- [ ] Table margin: 24px from filters (mt-6)

### 4. Format transaction data
- [ ] **Date:** gray-600, small font (text-small)
  - Format: MMM DD, YYYY
- [ ] **Merchant:** semibold, gray-800
  - Capitalize properly
- [ ] **Category:** Badge with semantic color
  - See criteria #5
- [ ] **Amount:** JetBrains Mono (font-mono), right-aligned
  - Debit (positive): text-red-600
  - Credit (negative): text-green-600
  - Format: $X,XXX.XX
- [ ] **Status:** Badge
  - Pending: yellow badge
  - Cleared: no badge (default)

### 5. Update category badges
- [ ] **INCOME:** blue badge (blue-primary background)
- [ ] **SAVINGS:** green badge (green-primary background)
- [ ] **HIGH_VALUE (>$200):** coral badge
- [ ] **DEFAULT:** gray badge (gray-200 background)
- [ ] Badge size: small, rounded-sm
- [ ] Text: uppercase, text-tiny

### 6. Add filter controls in top bar
- [ ] **Category dropdown:** shadcn Select component
  - All categories from transactions
  - "All Categories" default
- [ ] **Date range buttons:** Button group
  - Options: 30d, 90d, 180d, All
  - Active: blue-primary background
  - Inactive: gray-100 background
- [ ] **Search by merchant:** shadcn Input
  - Placeholder: "Search merchants..."
  - Debounce: 300ms
- [ ] **Clear filters button:** Ghost variant
  - Only show when filters active

### 7. Implement pagination
- [ ] Show 25 transactions per page
- [ ] shadcn Pagination component
- [ ] Page numbers + Next/Prev buttons
- [ ] Show "Showing X-Y of Z transactions"
- [ ] Maintain filters across pages

### 8. Add category spending summary card
- [ ] Card at top of page (before filters)
- [ ] Total spend by category (pie chart or bars)
- [ ] Percentage breakdown
- [ ] Use semantic colors per category
- [ ] 32px padding (p-8)

### 9. Implement responsive behavior
- [ ] **Desktop (1024px+):** Full table with all columns
- [ ] **Tablet (768-1023px):**
  - Hide status column
  - Collapse date to "MM/DD"
- [ ] **Mobile (<768px):** Card view (not table)
  - Each transaction as card
  - Merchant (bold), category badge, amount on one line
  - Date below
  - Tap to expand for full details

### 10. Add empty state
- [ ] "No transactions match your filters" message
- [ ] Icon: search with X
- [ ] "Reset filters" button (blue-primary)
- [ ] Subtle illustration (optional)

---

## Technical Implementation Notes

### Table Structure
```svelte
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Date</TableHead>
      <TableHead>Merchant</TableHead>
      <TableHead>Category</TableHead>
      <TableHead class="text-right">Amount</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {#each transactions as txn}
      <TableRow>
        <TableCell class="text-gray-600">{formatDate(txn.date)}</TableCell>
        <TableCell class="font-semibold">{txn.merchant}</TableCell>
        <TableCell><Badge>{txn.category}</Badge></TableCell>
        <TableCell class="font-mono text-right" class:text-red-600={txn.amount > 0} class:text-green-600={txn.amount < 0}>
          {formatCurrency(txn.amount)}
        </TableCell>
        <TableCell>{txn.pending ? <Badge variant="warning">Pending</Badge> : ''}</TableCell>
      </TableRow>
    {/each}
  </TableBody>
</Table>
```

### Filtering Logic
- Client-side filtering for categories and search
- API pagination with offset
- $state for active filters
- Debounce search input

---

## Definition of Done

- [ ] shadcn Table implemented
- [ ] Generous spacing applied
- [ ] Semantic colors for categories
- [ ] Filter controls functional
- [ ] Pagination works correctly
- [ ] Category summary card displays
- [ ] Responsive at all breakpoints
- [ ] Empty state handles no results
- [ ] Touch targets minimum 44px (mobile)
- [ ] No horizontal scroll on mobile

---

## Dependencies

**Prerequisites:** Story 7.3 (Insights Page Redesign)
**Blocks:** Story 7.5 (Responsive & Accessibility Polish)

---

## Reference

**Design Spec:** `docs/ux-design-specification.md` Section 6.1, 7.1
**API Endpoint:** `/transactions/{user_id}?limit={25}&offset={page}`
