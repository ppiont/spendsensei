# Story 7.1: Design System Foundation

**Epic:** 7 - UX Redesign - Calm & Focused Interface
**Status:** review
**Assignee:** Developer
**Priority:** P0 (Blocker for Epic 7)

---

## User Story

As a frontend developer,
I want to set up the shadcn-svelte design system with SpendSense design tokens,
So that I have a consistent foundation for building the calm, focused interface.

---

## Context

This story establishes the foundation for the UX redesign. We're transitioning from the current basic UI to a professional, Stripe-inspired dashboard with a "calm and focused" aesthetic. All design decisions are documented in `docs/ux-design-specification.md`.

**Key Changes:**
- Install shadcn-svelte component library
- Configure Tailwind CSS with custom design tokens
- Create three foundational custom components
- Establish generous spacing and subtle depth system

---

## Acceptance Criteria

### 1. Install shadcn-svelte
- [x] Run `bunx shadcn-svelte@latest init` in spendsense-frontend
- [x] Select TypeScript, Svelte 5 (runes), Tailwind CSS v4
- [x] Verify shadcn components directory created at `src/lib/components/ui/`
- [x] Confirm init succeeds without errors

### 2. Configure Tailwind CSS with SpendSense tokens
- [x] Extend `tailwind.config.js` with custom colors:
  - `blue-primary`: #2C5282 (trust, primary actions)
  - `blue-dark`: #1A365D (hover states)
  - `green-primary`: #38A169 (growth, success)
  - `green-light`: #48BB78 (lighter success)
  - `coral`: #F56565 (caution, warnings)
  - `coral-light`: #FC8181 (lighter warnings)
  - `yellow`: #ECC94B (education, highlights)
  - `yellow-light`: #F6E05E (lighter highlights)
- [x] Extend neutrals (gray-50, gray-100, gray-200, gray-600, gray-800)
- [x] Add extended spacing: `18` (4.5rem), `22` (5.5rem)
- [x] Add custom shadows: `subtle` (0 1px 2px rgba(0,0,0,0.05)), `soft` (0 4px 6px rgba(0,0,0,0.07))
- [x] Add border radius values: sm (4px), md (6px), lg (8px), xl (12px)
- [x] Verify Tailwind build compiles successfully

### 3. Add Inter font family for UI
- [x] Add Inter font import to app.html or +layout.svelte
- [x] Include weights: 400 (regular), 500 (medium), 600 (semibold)
- [x] Set as default font family in Tailwind config
- [x] Verify Inter renders correctly in browser

### 4. Add JetBrains Mono for financial data/numbers
- [x] Add JetBrains Mono font import
- [x] Configure as `font-mono` in Tailwind
- [x] Verify monospace font renders for numbers

### 5. Install core shadcn components
- [x] Run `bunx shadcn-svelte@latest add button`
- [x] Run `bunx shadcn-svelte@latest add card`
- [x] Run `bunx shadcn-svelte@latest add input`
- [x] Run `bunx shadcn-svelte@latest add select`
- [x] Run `bunx shadcn-svelte@latest add badge`
- [x] Run `bunx shadcn-svelte@latest add alert`
- [x] Run `bunx shadcn-svelte@latest add tabs`
- [x] Run `bunx shadcn-svelte@latest add tooltip`
- [x] Run `bunx shadcn-svelte@latest add dialog`
- [x] Run `bunx shadcn-svelte@latest add table`
- [x] Run `bunx shadcn-svelte@latest add progress`
- [x] Verify all components exist in `src/lib/components/ui/`

### 6. Create lib/components/ui/ directory structure
- [x] Verify directory exists after shadcn init
- [x] Organize custom components separately from shadcn base components
- [x] Create `src/lib/components/custom/` for SpendSense-specific components

### 7. Create base KPI Card component
- [x] Create `src/lib/components/custom/KpiCard.svelte`
- [x] Add props: `label` (string), `value` (string | number), `change` (number, optional), `variant` ('standard' | 'featured' | 'alert' | 'success')
- [x] Implement anatomy:
  - Label: uppercase, text-small, text-gray-600
  - Value: text-2xl, font-semibold, text-gray-800
  - Change indicator: green/red arrow with percentage (optional)
- [x] Implement variants:
  - **standard**: white bg, subtle shadow, border-gray-100
  - **featured**: 2x width (grid-column: span 2), gradient background
  - **alert**: coral border-left-4
  - **success**: green border-left-4
- [x] Apply 32px padding (p-8)
- [x] Test component renders correctly with sample data

### 8. Create base Recommendation Card component
- [x] Create `src/lib/components/custom/RecommendationCard.svelte`
- [x] Add props: `icon` (string), `title` (string), `body` (string), `rationale` (string), `cta` (string, optional)
- [x] Implement anatomy:
  - Icon: 40px circle with blue-primary background
  - Badge: "EDUCATION" label in blue
  - Title: text-base, font-semibold
  - Body: text-small, leading-relaxed
  - Rationale box: gray-50 background, "Because:" prefix
  - CTA button: blue-primary (optional)
- [x] Implement states:
  - **default**: border-gray-100
  - **hover**: border-blue-primary, shadow-soft
  - **expanded**: (placeholder for Story 7.3)
- [x] Apply 32px padding (p-8)
- [x] Test component renders correctly

### 9. Create Persona Badge component
- [x] Create `src/lib/components/custom/PersonaBadge.svelte`
- [x] Add props: `personaName` (string), `description` (string), `confidence` (number)
- [x] Implement anatomy:
  - Gradient avatar: 48px circle, blue→green gradient
  - Persona name: font-semibold, text-gray-800
  - Subtext: description or confidence%, text-small, text-gray-600
- [x] Use CSS gradient for avatar: `bg-gradient-to-br from-blue-primary to-green-primary`
- [x] Test component renders correctly

### 10. Verify components render with generous spacing
- [x] Create test page with all three custom components
- [x] Verify KPI Card has 32px padding
- [x] Verify Recommendation Card has 32px padding
- [x] Verify spacing feels generous and calm (not cramped)
- [x] Test responsive behavior (mobile/desktop)

---

## Technical Implementation Notes

### Tailwind Config Example
```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        'blue-primary': '#2C5282',
        'blue-dark': '#1A365D',
        'green-primary': '#38A169',
        'green-light': '#48BB78',
        'coral': '#F56565',
        'coral-light': '#FC8181',
        'yellow': '#ECC94B',
        'yellow-light': '#F6E05E',
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
      boxShadow: {
        'subtle': '0 1px 2px rgba(0,0,0,0.05)',
        'soft': '0 4px 6px rgba(0,0,0,0.07)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
}
```

### Component Patterns
- Use Svelte 5 runes: `$state`, `$derived`, `$effect`
- No Tailwind `@apply` directives (Tailwind v4 best practice)
- All spacing uses 8px base unit (4px, 8px, 16px, 24px, 32px, 48px)
- Shadows are subtle (not dramatic)
- Typography: 16px minimum for body text (accessibility)

### Testing Checklist
- [x] Tailwind builds without errors
- [x] All shadcn components install successfully
- [x] Custom components render correctly
- [x] Fonts load and display properly
- [x] Colors match UX spec exactly
- [x] Spacing feels generous and calm

---

## Definition of Done

- [x] shadcn-svelte installed and configured
- [x] Tailwind CSS extended with all SpendSense design tokens
- [x] Inter and JetBrains Mono fonts loaded
- [x] All 11 shadcn components installed
- [x] KPI Card component created and tested
- [x] Recommendation Card component created and tested
- [x] Persona Badge component created and tested
- [x] Components use generous 32px padding
- [x] No build errors or console warnings
- [x] Visual verification matches UX spec aesthetic

---

## Dependencies

**Prerequisites:**
- Story 5.5 (Operator View) - Frontend must be complete

**Blocks:**
- Story 7.2 (Dashboard Page Redesign)
- Story 7.3 (Insights Page Redesign)
- Story 7.4 (Transactions Page Redesign)

---

## Reference

**Design Spec:** `docs/ux-design-specification.md`
- Section 1: Design System Foundation
- Section 3: Visual Foundation (Colors, Typography, Spacing)
- Section 6: Component Library
- Section 9: Implementation Guidance

**Key Files to Create/Modify:**
- `tailwind.config.js`
- `src/lib/components/custom/KpiCard.svelte`
- `src/lib/components/custom/RecommendationCard.svelte`
- `src/lib/components/custom/PersonaBadge.svelte`

---

## Notes

- This is a foundational story - take time to get it right
- All subsequent Epic 7 stories depend on these components
- shadcn-svelte uses copy-paste philosophy (full control over components)
- Test components in isolation before integrating into pages
- Generous spacing is intentional (creates calm aesthetic)

---

## Dev Agent Record

### Debug Log

**Implementation Plan:**
1. shadcn-svelte was already partially initialized from previous work (5 components existed)
2. Configure Tailwind v4 inline theme in app.css with SpendSense design tokens
3. Add Inter and JetBrains Mono fonts via Google Fonts CDN in app.html
4. Install remaining 6 shadcn components (input, select, tabs, tooltip, dialog, progress)
5. Create custom components directory structure (src/lib/components/custom/)
6. Build three custom Svelte 5 components using runes ($state, $derived)
7. Create comprehensive test page at /design-test to verify all components

**Key Decisions:**
- Used Tailwind v4's inline @theme directive instead of separate config.js file
- Configured all SpendSense design tokens as CSS custom properties (--color-*, --spacing-*, --shadow-*)
- Added fonts via Google Fonts for simplicity (Inter 400/500/600, JetBrains Mono 400/500/600)
- Created separate custom/ directory to distinguish SpendSense components from shadcn base components
- Used Svelte 5 runes ($state for hover, $derived for computed values) throughout custom components
- Built test page with extensive examples to visually verify spacing, colors, and interactions

### Completion Notes

Successfully implemented complete design system foundation:
- ✅ 12 shadcn-svelte components installed (11 required + separator bonus)
- ✅ Tailwind CSS extended with all SpendSense design tokens (colors, spacing, shadows, radius)
- ✅ Inter (UI text) and JetBrains Mono (financial data) fonts loaded
- ✅ Three custom components created with Svelte 5 runes:
  - KpiCard: 4 variants (standard, featured, alert, success), optional change indicator, 32px padding
  - RecommendationCard: Interactive hover states, EDUCATION badge, rationale box, optional CTA, 32px padding
  - PersonaBadge: Gradient avatar circle (blue→green), persona name + description/confidence
- ✅ Test page created at /design-test with comprehensive examples
- ✅ Build successful, no errors or warnings
- ✅ All components use generous spacing (32px padding) for calm aesthetic

---

## File List

**Modified:**
- `spendsense-frontend/src/app.css` - Added SpendSense design tokens to @theme inline
- `spendsense-frontend/src/app.html` - Added Inter and JetBrains Mono fonts from Google Fonts

**Created:**
- `spendsense-frontend/src/lib/components/custom/` - New directory for custom components
- `spendsense-frontend/src/lib/components/custom/KpiCard.svelte` - KPI card component (4 variants)
- `spendsense-frontend/src/lib/components/custom/RecommendationCard.svelte` - Recommendation card with hover states
- `spendsense-frontend/src/lib/components/custom/PersonaBadge.svelte` - Persona display with gradient avatar
- `spendsense-frontend/src/routes/design-test/+page.svelte` - Comprehensive test page for design system
- `spendsense-frontend/src/lib/components/ui/input/` - shadcn input component
- `spendsense-frontend/src/lib/components/ui/select/` - shadcn select component
- `spendsense-frontend/src/lib/components/ui/tabs/` - shadcn tabs component
- `spendsense-frontend/src/lib/components/ui/tooltip/` - shadcn tooltip component
- `spendsense-frontend/src/lib/components/ui/dialog/` - shadcn dialog component
- `spendsense-frontend/src/lib/components/ui/progress/` - shadcn progress component
- `spendsense-frontend/src/lib/components/ui/separator/` - shadcn separator component (bonus)

**Dependencies Added:**
- `tailwind-variants@3.1.1` - Required by shadcn badge component

---

## Change Log

- 2025-11-04: Story 7.1 implementation complete - Design system foundation established with shadcn-svelte, SpendSense design tokens, custom fonts, and three foundational custom components. Ready for Story 7.2 (Dashboard redesign).
