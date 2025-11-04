# Story 7.1: Design System Foundation

**Epic:** 7 - UX Redesign - Calm & Focused Interface
**Status:** drafted
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
- [ ] Run `bunx shadcn-svelte@latest init` in spendsense-frontend
- [ ] Select TypeScript, Svelte 5 (runes), Tailwind CSS v4
- [ ] Verify shadcn components directory created at `src/lib/components/ui/`
- [ ] Confirm init succeeds without errors

### 2. Configure Tailwind CSS with SpendSense tokens
- [ ] Extend `tailwind.config.js` with custom colors:
  - `blue-primary`: #2C5282 (trust, primary actions)
  - `blue-dark`: #1A365D (hover states)
  - `green-primary`: #38A169 (growth, success)
  - `green-light`: #48BB78 (lighter success)
  - `coral`: #F56565 (caution, warnings)
  - `coral-light`: #FC8181 (lighter warnings)
  - `yellow`: #ECC94B (education, highlights)
  - `yellow-light`: #F6E05E (lighter highlights)
- [ ] Extend neutrals (gray-50, gray-100, gray-200, gray-600, gray-800)
- [ ] Add extended spacing: `18` (4.5rem), `22` (5.5rem)
- [ ] Add custom shadows: `subtle` (0 1px 2px rgba(0,0,0,0.05)), `soft` (0 4px 6px rgba(0,0,0,0.07))
- [ ] Add border radius values: sm (4px), md (6px), lg (8px), xl (12px)
- [ ] Verify Tailwind build compiles successfully

### 3. Add Inter font family for UI
- [ ] Add Inter font import to app.html or +layout.svelte
- [ ] Include weights: 400 (regular), 500 (medium), 600 (semibold)
- [ ] Set as default font family in Tailwind config
- [ ] Verify Inter renders correctly in browser

### 4. Add JetBrains Mono for financial data/numbers
- [ ] Add JetBrains Mono font import
- [ ] Configure as `font-mono` in Tailwind
- [ ] Verify monospace font renders for numbers

### 5. Install core shadcn components
- [ ] Run `bunx shadcn-svelte@latest add button`
- [ ] Run `bunx shadcn-svelte@latest add card`
- [ ] Run `bunx shadcn-svelte@latest add input`
- [ ] Run `bunx shadcn-svelte@latest add select`
- [ ] Run `bunx shadcn-svelte@latest add badge`
- [ ] Run `bunx shadcn-svelte@latest add alert`
- [ ] Run `bunx shadcn-svelte@latest add tabs`
- [ ] Run `bunx shadcn-svelte@latest add tooltip`
- [ ] Run `bunx shadcn-svelte@latest add dialog`
- [ ] Run `bunx shadcn-svelte@latest add table`
- [ ] Run `bunx shadcn-svelte@latest add progress`
- [ ] Verify all components exist in `src/lib/components/ui/`

### 6. Create lib/components/ui/ directory structure
- [ ] Verify directory exists after shadcn init
- [ ] Organize custom components separately from shadcn base components
- [ ] Create `src/lib/components/custom/` for SpendSense-specific components

### 7. Create base KPI Card component
- [ ] Create `src/lib/components/custom/KpiCard.svelte`
- [ ] Add props: `label` (string), `value` (string | number), `change` (number, optional), `variant` ('standard' | 'featured' | 'alert' | 'success')
- [ ] Implement anatomy:
  - Label: uppercase, text-small, text-gray-600
  - Value: text-2xl, font-semibold, text-gray-800
  - Change indicator: green/red arrow with percentage (optional)
- [ ] Implement variants:
  - **standard**: white bg, subtle shadow, border-gray-100
  - **featured**: 2x width (grid-column: span 2), gradient background
  - **alert**: coral border-left-4
  - **success**: green border-left-4
- [ ] Apply 32px padding (p-8)
- [ ] Test component renders correctly with sample data

### 8. Create base Recommendation Card component
- [ ] Create `src/lib/components/custom/RecommendationCard.svelte`
- [ ] Add props: `icon` (string), `title` (string), `body` (string), `rationale` (string), `cta` (string, optional)
- [ ] Implement anatomy:
  - Icon: 40px circle with blue-primary background
  - Badge: "EDUCATION" label in blue
  - Title: text-base, font-semibold
  - Body: text-small, leading-relaxed
  - Rationale box: gray-50 background, "Because:" prefix
  - CTA button: blue-primary (optional)
- [ ] Implement states:
  - **default**: border-gray-100
  - **hover**: border-blue-primary, shadow-soft
  - **expanded**: (placeholder for Story 7.3)
- [ ] Apply 32px padding (p-8)
- [ ] Test component renders correctly

### 9. Create Persona Badge component
- [ ] Create `src/lib/components/custom/PersonaBadge.svelte`
- [ ] Add props: `personaName` (string), `description` (string), `confidence` (number)
- [ ] Implement anatomy:
  - Gradient avatar: 48px circle, blue→green gradient
  - Persona name: font-semibold, text-gray-800
  - Subtext: description or confidence%, text-small, text-gray-600
- [ ] Use CSS gradient for avatar: `bg-gradient-to-br from-blue-primary to-green-primary`
- [ ] Test component renders correctly

### 10. Verify components render with generous spacing
- [ ] Create test page with all three custom components
- [ ] Verify KPI Card has 32px padding
- [ ] Verify Recommendation Card has 32px padding
- [ ] Verify spacing feels generous and calm (not cramped)
- [ ] Test responsive behavior (mobile/desktop)

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
- [ ] Tailwind builds without errors
- [ ] All shadcn components install successfully
- [ ] Custom components render correctly
- [ ] Fonts load and display properly
- [ ] Colors match UX spec exactly
- [ ] Spacing feels generous and calm

---

## Definition of Done

- [ ] shadcn-svelte installed and configured
- [ ] Tailwind CSS extended with all SpendSense design tokens
- [ ] Inter and JetBrains Mono fonts loaded
- [ ] All 11 shadcn components installed
- [ ] KPI Card component created and tested
- [ ] Recommendation Card component created and tested
- [ ] Persona Badge component created and tested
- [ ] Components use generous 32px padding
- [ ] No build errors or console warnings
- [ ] Visual verification matches UX spec aesthetic

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
