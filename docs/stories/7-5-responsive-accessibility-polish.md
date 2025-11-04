# Story 7.5: Responsive & Accessibility Polish

**Epic:** 7 - UX Redesign - Calm & Focused Interface
**Status:** TODO
**Assignee:** Developer
**Priority:** P1

---

## User Story

As a user,
I want the interface to work perfectly on any device and be fully accessible,
So that everyone can use SpendSense regardless of device or ability.

---

## Context

Final polish for Epic 7: comprehensive responsive design, WCAG 2.1 AA accessibility compliance, and smooth interactions across all devices.

---

## Acceptance Criteria

### 1. Implement responsive breakpoints
- [ ] **Mobile (320px - 767px):**
  - 1-column layouts
  - Full-width cards
  - Stack all KPIs vertically
  - Hamburger menu for navigation
- [ ] **Tablet (768px - 1023px):**
  - 2-column grid for KPIs
  - 2-column recommendations
  - Horizontal navigation (condensed)
- [ ] **Desktop (1024px - 1439px):**
  - 4-column grid for KPIs
  - 3-column recommendations
  - Full horizontal navigation
- [ ] **Wide (1440px+):**
  - Max-width 1400px container
  - Centered content

### 2. Add keyboard navigation
- [ ] Tab order follows visual hierarchy (top→bottom, left→right)
- [ ] 2px blue outline on all focus states (focus-visible:ring-2 ring-blue-primary)
- [ ] Escape closes modals/dropdowns
- [ ] Arrow keys navigate tables/lists
- [ ] Enter activates buttons/links
- [ ] Space toggles checkboxes/radios
- [ ] Skip to main content link (hidden until focused)

### 3. Test WCAG 2.1 AA compliance
- [ ] **Color contrast:** 4.5:1 minimum for normal text
  - Test all color combinations
  - Use contrast checker tool
- [ ] **Interactive elements:** Visible focus indicators
  - Test with keyboard only
  - Verify focus ring on all elements
- [ ] **No color-only indicators:** Always pair with icon/label
  - Category badges have text labels
  - Status uses icon + text
- [ ] **Form labels:** Properly associated with inputs
  - Use `<label for="...">` pattern
  - ARIA labels on icon-only buttons
- [ ] **ARIA labels:** On icon-only buttons
  - Example: `<button aria-label="Close modal">`

### 4. Add skeleton loaders for loading states
- [ ] **KPI cards:** Animated gray-200 rectangles
  - Label skeleton: w-1/2 h-4
  - Value skeleton: w-3/4 h-8
  - Pulse animation
- [ ] **Recommendation cards:**
  - Title skeleton: w-3/4 h-6
  - Body skeleton: 3 lines, w-full h-4 each
  - Rationale skeleton: w-full h-16
- [ ] **Transactions:** Table row skeletons
  - 5-7 skeleton rows
  - Match table column widths
- [ ] **No spinners** unless <3 elements loading

### 5. Verify touch targets on mobile
- [ ] Minimum 44x44px for all tappable elements
  - Buttons, links, form inputs
  - Table rows (when tappable)
- [ ] 8px spacing between touch targets
- [ ] Full-width buttons for primary actions on mobile
- [ ] No hover-only interactions
  - All hover states also available on focus/active

### 6. Implement smooth transitions
- [ ] Page navigation: fade-in 300ms
- [ ] Card hover: `transform: translateY(-2px)` + shadow-soft, 150ms ease
- [ ] Expand/collapse: height 300ms ease
- [ ] Respect `prefers-reduced-motion`:
  ```css
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```

### 7. Add ARIA live regions
- [ ] Recommendation updates: `<div aria-live="polite" aria-atomic="true">`
- [ ] Filter changes: Announce "X transactions found"
- [ ] Error messages: `aria-live="assertive"`
- [ ] Success messages: `aria-live="polite"`

### 8. Test with screen readers
- [ ] **VoiceOver (macOS) or NVDA (Windows):**
  - All content navigable
  - Headings properly structured (H1→H2→H3)
  - Tables announced correctly
  - Form labels read
- [ ] Semantic HTML (nav, main, aside, article)
- [ ] Skip to main content link
- [ ] Landmark regions properly labeled

### 9. Test responsive behavior
- [ ] **Dashboard:**
  - Grid: 4 → 2 → 1 columns
  - Featured KPI maintains visual priority
- [ ] **Recommendations:**
  - Grid: 3 → 2 → 1 columns
- [ ] **Transactions:**
  - Table → card view on mobile
  - All columns visible on desktop
- [ ] **Navigation:**
  - Horizontal → hamburger menu on mobile

### 10. Run Lighthouse accessibility audit
- [ ] Score: 95+ required
- [ ] Fix all critical issues (contrast, labels, etc.)
- [ ] Document any minor issues in notes
- [ ] Test on:
  - Chrome DevTools Lighthouse
  - Firefox Accessibility Inspector
  - axe DevTools extension

---

## Technical Implementation Notes

### Focus Visible Pattern
```css
/* Global focus styles */
:focus-visible {
  @apply ring-2 ring-blue-primary ring-offset-2 outline-none;
}
```

### Skeleton Loader Component
```svelte
<div class="animate-pulse">
  <div class="h-4 w-1/2 bg-gray-200 rounded mb-2"></div>
  <div class="h-8 w-3/4 bg-gray-200 rounded"></div>
</div>
```

### ARIA Live Region Example
```svelte
<div aria-live="polite" aria-atomic="true" class="sr-only">
  {statusMessage}
</div>
```

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Testing Checklist

### Manual Tests
- [ ] Keyboard navigation: tab through entire app
- [ ] Screen reader: navigate with VoiceOver/NVDA
- [ ] Touch: test on real mobile device
- [ ] Resize: test all breakpoints in DevTools
- [ ] Reduced motion: enable in OS settings

### Automated Tests
- [ ] Lighthouse accessibility: 95+ score
- [ ] Lighthouse performance: 90+ score
- [ ] axe DevTools: 0 violations
- [ ] Wave accessibility: 0 errors

### Device Tests
- [ ] iPhone (Safari): iOS touch targets, gestures
- [ ] Android (Chrome): material design behaviors
- [ ] iPad (Safari): tablet layout, touch
- [ ] Desktop (Chrome, Firefox, Safari): all features

---

## Definition of Done

- [ ] All 4 breakpoints implemented and tested
- [ ] Keyboard navigation works perfectly
- [ ] WCAG 2.1 AA compliance verified
- [ ] Skeleton loaders implemented
- [ ] Touch targets minimum 44px
- [ ] Smooth transitions with reduced motion support
- [ ] ARIA live regions added
- [ ] Screen reader tested
- [ ] Responsive behavior verified
- [ ] Lighthouse score 95+
- [ ] No accessibility violations
- [ ] Real device testing complete

---

## Dependencies

**Prerequisites:** Story 7.4 (Transactions Page Redesign)
**Blocks:** None (final story in Epic 7)

---

## Reference

**Design Spec:** `docs/ux-design-specification.md` Section 8 (Responsive & Accessibility)
**WCAG 2.1:** https://www.w3.org/WAI/WCAG21/quickref/
**Lighthouse:** Chrome DevTools > Lighthouse tab
