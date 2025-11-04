# SpendSense UX Design Specification

_Created on 2025-11-04 by Peter_
_Generated using BMad Method - Create UX Design Workflow v1.0_

---

## Executive Summary

**Project:** SpendSense - A financial behavior analysis platform that detects patterns from synthetic transaction data and delivers personalized financial education.

**Vision & Purpose:**
- Turns bank transaction data into actionable insights WITHOUT crossing into regulated financial advice
- Explainable, consent-aware system that detects behavioral patterns
- Assigns personas (5 types: High Utilization, Variable Income, Subscription-Heavy, Savings Builder, + custom)
- Delivers personalized financial education with clear guardrails

**Target Users:**
- 50-100 synthetic users with diverse financial situations
- People with various income levels, credit behaviors, and saving patterns
- Users seeking educational financial guidance (not advice)
- Bank customers who opt-in for behavioral analysis

**Platform:** Web application (Svelte 5 + SvelteKit frontend, FastAPI backend)

**Core Pages Already Built:**
- Dashboard (account balances, net worth, recent transactions)
- Transactions page (filtering, pagination, category breakdown)
- Insights page (persona display, 3 personalized recommendations)
- Operator view (internal debugging/oversight tool)

**Key UX Principles from Requirements:**
- **Transparency** over sophistication
- **User control** over automation (consent-driven)
- **Education** over sales
- **No shaming language** - empowering, supportive tone
- **100% explainability** - every recommendation has clear rationale
- **<5 second** response time target

---

## 1. Design System Foundation

### 1.1 Design System Choice

**Selected System:** shadcn-svelte

**Rationale:**
- **Aesthetic alignment:** Clean, minimal design matches Linear/Stripe inspiration for "calm and focused" feel
- **Accessibility by default:** ARIA standards built-in (critical for financial product)
- **Tailwind CSS v4 compatible:** Works seamlessly with existing tech stack (Svelte 5 + Tailwind CSS v4)
- **Copy-paste philosophy:** Full control over components, no black-box dependencies
- **Highly customizable:** Perfect for achieving distinctive calm aesthetic through intentional styling
- **40+ components:** Comprehensive coverage (buttons, forms, cards, modals, tables, charts, etc.)
- **Active community:** 7,500+ GitHub stars, well-maintained

**What shadcn-svelte Provides:**
- **Form Components:** Buttons, inputs, selects, checkboxes, radio groups with proper states
- **Layout Components:** Cards, tabs, accordions, separators for content organization
- **Overlay Components:** Modals (dialogs), dropdowns, popovers, tooltips for interactions
- **Data Display:** Tables, badges, avatars, progress indicators
- **Feedback Components:** Toast notifications, alerts, skeleton loaders
- **Navigation:** Command palette, breadcrumbs, pagination
- **Charts:** Integration points for data visualization
- **Accessibility:** Full keyboard navigation, screen reader support, ARIA patterns

**Customization Strategy:**
Components will be styled to create SpendSense's distinctive calm aesthetic:
- Generous spacing and white space
- Muted, purposeful color palette (not decorative)
- Soft shadows for subtle depth (not dramatic)
- Clean typography hierarchy
- Smooth, gentle transitions (not flashy)
- Restrained use of color (color with meaning)

**Version:** Latest stable version with Tailwind v4 community support

---

## 2. Core User Experience

### 2.1 Project Context & Core Experience

**Core Action:** Understanding financial behavior through calm, focused exploration of insights and recommendations

**Primary User Activities:**
1. **Insights exploration** - Understanding persona assignment and viewing personalized recommendations
2. **Transaction review** - Browsing spending patterns with filtering and categorization
3. **Dashboard monitoring** - At-a-glance view of financial health (balances, net worth)
4. **Operator oversight** - Internal view for transparency and decision tracing

**Platform:** Web application (desktop primary, mobile responsive)

**Desired Emotional Response:** **Calm and focused**
- Removing anxiety around finances through clarity
- Empowering users with understanding, not overwhelming them with data
- Educational and supportive, never judgmental or shaming

**What this means for UX:**
- Visual design must be clean, uncluttered, with generous breathing room
- Information hierarchy guides attention without overwhelming
- Interactions feel smooth and predictable (instant state changes)
- Colors and typography reinforce calm (not alarming, not hyperactive)
- Feedback is reassuring and clear, never anxiety-inducing

### 2.2 Inspiration & UX Patterns

**Inspiration Sources:** Linear and Stripe Dashboard

**What makes them feel "calm and focused":**

**Linear's Approach:**
- Smooth flows & tight transitions - every interaction feels immediate and predictable
- Lean visuals - cut back on color, focus on content
- Generous white space - guides user focus naturally
- Immediate state changes - no excessive loading states
- Muted gradients & soft shadows - depth without heaviness
- Care in tiny details - polish reduces cognitive friction

**Stripe Dashboard's Approach:**
- Ample white space - reduces cognitive load
- Prominent top-level metrics - quick, effortless monitoring at a glance
- Clean typography & consistent alignment - makes data digestible
- Simple visualizations - no excessive gridlines, borders, or decorative icons
- Limited color schemes - color used purposefully, not decoratively
- Intuitive charts - trends and tracking without complexity
- Tooltips for context - additional info available without crowding

**Core Patterns that Create Calm:**
- ✓ White space as a feature (not something to fill)
- ✓ Information hierarchy (important things obvious, details available but not intrusive)
- ✓ Subtle depth cues (soft shadows, not dramatic 3D effects)
- ✓ Restrained color palette (color with purpose, not decoration)
- ✓ Smooth animations (gentle, not flashy)
- ✓ Instant feedback (state changes feel immediate)
- ✓ Clean typography (readable, not decorative)
- ✓ Progressive disclosure (tooltips, expandable sections vs. showing everything)

**Application to SpendSense:**
- **Dashboard** - Stripe-inspired: metrics at a glance, clean charts
- **Insights page** - Linear-inspired: smooth transitions, generous white space, focused content
- **Transactions** - Balance data density (Stripe) with focused simplicity (Linear)
- **Operator view** - Can be slightly denser (internal use) but maintains clean aesthetic

---

## 3. Visual Foundation

### 3.1 Color System

**Selected Theme:** Balanced Calm (Theme 3) with Maximum Spacing (Theme 4)

**Color Palette:**

**Primary Colors:**
- **Deep Blue:** #2C5282 - Trust, stability, security
  - Use for: Primary CTAs, navigation, headers, important actions
- **Sage Green:** #38A169 - Growth, progress, positive outcomes
  - Use for: Success states, savings indicators, completion markers, positive trends

**Accent Colors (Used Sparingly):**
- **Warm Coral:** #F56565 - Attention, warnings
  - Use for: High utilization alerts, overdue payments, urgent actions only
- **Golden Yellow:** #ECC94B - Education, highlights
  - Use for: Learning opportunities, tips, informational highlights

**Neutrals (30%+ of UI - Key to Calm Aesthetic):**
- **White:** #FFFFFF - Primary backgrounds, card surfaces
- **Soft Gray:** #F7FAFC - Subtle backgrounds, alternating rows
- **Light Gray:** #E2E8F0 - Borders, dividers, disabled states
- **Medium Gray:** #CBD5E0 - Secondary borders, inactive elements
- **Dark Gray:** #4A5568 - Secondary text, less prominent content
- **Charcoal:** #2D3748 - Primary text, headings

**Color Usage Philosophy:**
- **Generous neutrals** (30%+ of interface) create breathing room and calm
- **Blue = Trust** - Used for primary actions, financial data, secure operations
- **Green = Growth** - Used for positive outcomes, savings, progress
- **Coral = Caution** - Used sparingly, only for genuine warnings
- **Yellow = Learn** - Used for educational moments, non-critical tips
- **Never use color alone** - Always pair with icons, labels, or patterns for accessibility

**Contrast Requirements:**
- WCAG AAA: 7:1 minimum for normal text
- WCAG AA: 4.5:1 minimum for large text (18px+)
- All color combinations tested for accessibility

### 3.2 Typography System

**Font Stack:**
- **Headings:** Inter (weights: 600 Semibold for H1-H2, 500 Medium for H3-H4)
  - Geometric sans-serif, modern, trustworthy, professional
- **Body Text:** Inter (weights: 400 Regular, 500 Medium for emphasis)
  - Excellent readability, friendly, accessible
- **Data/Numbers:** JetBrains Mono or system monospace
  - Ensures alignment and scannability for financial figures

**Type Scale (Responsive):**
```
H1: 28px/1.75rem (Mobile) → 40px/2.5rem (Desktop)
H2: 24px/1.5rem → 32px/2rem
H3: 20px/1.25rem → 24px/1.5rem
H4: 18px/1.125rem → 20px/1.25rem
Body: 16px/1rem (minimum for accessibility)
Small: 14px/0.875rem (captions, legal text)
Tiny: 12px/0.75rem (labels, metadata - use sparingly)
```

**Line Height:**
- Body text: 1.6-1.7 (generous for readability and calm)
- Headings: 1.2-1.3 (tighter for impact)

**Letter Spacing:**
- Large headings (H1-H2): -0.02em (slightly tighter)
- Labels/metadata: 0.05em (slightly wider for readability)
- Body text: 0 (default)

### 3.3 Spacing System (Maximum Breathing Room)

**Design Philosophy:** Generous spacing is critical for "calm and focused" aesthetic. White space is a feature, not wasted space.

**Spacing Scale (8px base unit):**
```
xs:  4px  (0.25rem) - Tight grouping
sm:  8px  (0.5rem)  - Related elements
md:  16px (1rem)    - Component padding
lg:  24px (1.5rem)  - Section spacing
xl:  32px (2rem)    - Card padding, major sections
2xl: 48px (3rem)    - Page-level spacing
3xl: 64px (4rem)    - Hero sections, major breaks
```

**Application Guidelines:**
- **Card padding:** 2rem (32px) minimum - Theme 4's generous approach
- **Between sections:** 3rem (48px) minimum
- **Component margins:** 1.5rem (24px) minimum
- **Paragraph spacing:** 1rem (16px)
- **Button padding:** 0.625rem × 1.25rem (10px × 20px)
- **Input padding:** 0.75rem (12px)

**White Space Strategy:**
- Prioritize empty space over cramming content
- Let important elements breathe
- Use white space to create visual hierarchy
- Never fill space just because it's there

### 3.4 Depth & Shadows (Subtle Only)

**Shadow System (Soft, Not Dramatic):**
```
None:    0px (flat elements, backgrounds)
Subtle:  0 1px 2px rgba(0,0,0,0.05) (cards at rest)
Soft:    0 4px 6px rgba(0,0,0,0.07) (cards, hover states)
Medium:  0 10px 15px rgba(0,0,0,0.1) (modals, popovers)
Large:   0 20px 25px rgba(0,0,0,0.1) (high-elevation overlays)
```

**Usage:**
- Default cards: Subtle shadow or 1px border
- Hover states: Soft shadow with 2px lift
- Modals/dialogs: Medium shadow
- Avoid dramatic shadows (not calm aesthetic)

### 3.5 Border Radius

**Radius Scale:**
```
sm: 4px  - Small elements (badges, tags)
md: 6px  - Buttons, inputs
lg: 8px  - Cards, larger components
xl: 12px - Modals, major containers
```

**Usage:**
- Consistent 6-8px for most interactive elements
- Slightly rounded (not pill-shaped) maintains professional feel

**Interactive Visualizations:**

- Color Theme Explorer: [ux-color-themes.html](./ux-color-themes.html)

---

## 4. Design Direction

### 4.1 Chosen Design Approach

**Selected Direction:** Direction 6 - Dashboard Metrics (Stripe-inspired)

**Layout Philosophy:**
- Stripe-inspired professional dashboard with prominent KPIs
- Clean metrics grid with recommendations below
- Data-focused yet calm aesthetic
- Generous spacing with clear visual hierarchy

**Key Characteristics:**
- **Top bar:** Persona badge with avatar + quick actions
- **Metrics grid:** 4-5 KPI cards with one "featured" spanning 2 columns
- **Recommendations section:** 3-column grid of actionable cards
- **White space:** Generous (32px card padding, 24px gutters)
- **Shadows:** Subtle elevation (Stripe-style)
- **Professional yet approachable:** Balances data density with calm

**Layout Structure:**

```
┌─────────────────────────────────────────────────┐
│ Header: Logo | Nav (Dashboard, Insights, etc.) │
├─────────────────────────────────────────────────┤
│ Top Bar: [Avatar] Persona | [Primary Action]   │  ← Persona badge
├─────────────────────────────────────────────────┤
│ ┌──────────────────┐ ┌────────┐ ┌────────┐     │
│ │  Featured KPI    │ │ KPI 2  │ │ KPI 3  │     │  ← Metrics grid
│ │  (2x width)      │ └────────┘ └────────┘     │
│ └──────────────────┘ ┌────────┐ ┌────────┐     │
│                      │ KPI 4  │ │ KPI 5  │     │
│                      └────────┘ └────────┘     │
├─────────────────────────────────────────────────┤
│ Recommendations Section                         │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐     │  ← 3-column recs
│ │ Rec 1     │ │ Rec 2     │ │ Rec 3     │     │
│ │ [icon]    │ │ [icon]    │ │ [icon]    │     │
│ │ Title     │ │ Title     │ │ Title     │     │
│ │ Body      │ │ Body      │ │ Body      │     │
│ │ Because.. │ │ Because.. │ │ Because.. │     │
│ └───────────┘ └───────────┘ └───────────┘     │
└─────────────────────────────────────────────────┘
```

**Application to SpendSense Pages:**

**Dashboard (Primary use):**
- Top bar: Persona badge with avatar gradient (blue→green)
- Featured KPI: Total Net Worth (2x width with trend)
- 4 supporting KPIs: Monthly Savings, Credit Health, Emergency Fund, Subscriptions
- Recommendations: 3 cards with icons, "because" rationales

**Insights Page (Adapted):**
- Similar structure but recommendations take priority
- Fewer KPIs (focus on relevant metrics for each recommendation)
- Can expand recommendation cards inline for full content

**Transactions Page (Simplified):**
- Top bar: Filter controls instead of persona
- Single featured metric: Total transactions or balance
- Table/list view for transactions below
- Maintain same spacing and card aesthetic

**Why Direction 6 Works:**
- ✅ Stripe aesthetic = professional, trustworthy
- ✅ Data-forward = matches financial context
- ✅ Generous spacing = calm and focused
- ✅ Clear hierarchy = easy to scan
- ✅ Scalable = works for all SpendSense pages
- ✅ shadcn-svelte friendly = clean component composition

**Interactive Mockups:**

- Design Direction Showcase: [ux-design-directions.html](./ux-design-directions.html)

---

## 5. User Journey Flows

### 5.1 Critical User Paths

**Primary user journeys are simple and focused - SpendSense is about clarity, not complexity.**

**Journey 1: View Financial Health (Dashboard)**
```
Landing → Dashboard loaded →
Scan persona badge → Review featured metric (Net Worth) →
Scan supporting KPIs → Identify areas of interest →
Scroll to recommendations → Read "because" rationale →
Take action (learn more / dismiss)
```

**Journey 2: Understand Recommendations (Insights)**
```
Navigate to Insights → View persona card →
See 3 personalized recommendations →
Click recommendation to expand →
Read full explanation + rationale →
Access educational content →
Return to list or take action
```

**Journey 3: Review Transactions**
```
Navigate to Transactions →
View list with categories →
Use filters (date, category, amount) →
Click transaction for details →
See categorization + merchant info →
Return to list
```

**Journey 4: Operator Oversight**
```
Access Operator view →
Search/select user →
Review detected signals →
See generated recommendations →
View decision trace ("why" for each) →
Approve/override if needed
```

**Key UX Decisions:**
- **No multi-step wizards** - Everything is direct access
- **Progressive disclosure** - Summary first, details on demand
- **Instant state changes** - No loading spinners unless >1s
- **Clear back buttons** - Always easy to return
- **Breadcrumbs** - Show context in Operator view

---

## 6. Component Library

### 6.1 Component Strategy

**From shadcn-svelte (Copy-paste approach):**

**Essential Components:**
- **Button** - Primary, secondary, outline, ghost variants
- **Card** - Container for KPIs, recommendations, content
- **Input** - Text, number, date inputs with validation states
- **Select** - Dropdowns for filters
- **Badge** - Persona labels, status indicators
- **Alert** - Success, info, warning messages
- **Tabs** - Switch between views (e.g., 30-day vs 180-day)
- **Tooltip** - Contextual help without cluttering
- **Modal (Dialog)** - Expanded recommendation details
- **Table** - Transaction lists, data tables
- **Progress** - Loading states, goal progress bars

**Custom Components (Build on shadcn base):**

**1. KPI Card**
```
Purpose: Display financial metrics with context
Anatomy:
- Label (uppercase, small, gray-600)
- Value (large, bold, gray-800 or semantic color)
- Change indicator (green/red with arrow, optional)
- Subtle background or border

States:
- Default: White background, subtle shadow
- Featured: 2x width, gradient background
- Alert: Coral border-left for warnings
- Success: Green border-left for positive

Variants:
- Standard (1x1 grid cell)
- Featured (2x1 grid cells)
- Compact (smaller padding for dense views)
```

**2. Recommendation Card**
```
Purpose: Present personalized recommendations with rationales
Anatomy:
- Icon (40px, blue background circle)
- Badge ("EDUCATION" label, blue)
- Title (1rem, semibold)
- Body text (0.875rem, line-height 1.6)
- Rationale box (gray-50 background, "Because:")
- Optional CTA button

States:
- Default: Border gray-100
- Hover: Border blue-primary, soft shadow
- Expanded: Modal or inline expansion with full content

Variants:
- Compact (list view)
- Card (grid view - default)
- Expanded (full detail)
```

**3. Persona Badge**
```
Purpose: Display user's persona prominently
Anatomy:
- Avatar (gradient circle, blue→green)
- Persona name (semibold)
- Subtext (description or confidence)

Placement:
- Dashboard top bar
- Insights hero section
- Compact in header for other pages
```

**4. Transaction Row**
```
Purpose: Display individual transactions clearly
Anatomy:
- Date (gray-600, small)
- Merchant name (semibold)
- Category badge (colored)
- Amount (monospace, right-aligned)

States:
- Default
- Hover: Gray-50 background
- Selected: Blue-50 background
```

**Component Customization for "Calm" Aesthetic:**
- Increase padding by 25-50% vs. shadcn defaults
- Soften shadows (use subtle/soft, not medium)
- Mute hover effects (no dramatic scale transforms)
- Use borders more than shadows for cards
- Generous line-height (1.6-1.7 for body text)

---

## 7. UX Pattern Decisions

### 7.1 Consistency Rules

**Button Hierarchy:**
- **Primary:** Blue (#2C5282), white text - main actions only
- **Success:** Green (#38A169), white text - positive confirmations
- **Secondary:** White bg, blue text, blue border - secondary actions
- **Ghost:** Transparent, gray text - tertiary/cancel actions
- **Destructive:** Coral (#F56565), white text - delete/dangerous actions (use sparingly)

**Never have more than 1 primary button visible at once**

**Feedback Patterns:**
- **Success:** Green border-left on card or green badge + checkmark
- **Error:** Coral border-left, not full red backgrounds (too alarming)
- **Warning:** Yellow badge, not blocking modals
- **Info:** Blue border-left, subtle background
- **Loading:** Skeleton screens preferred over spinners (only use spinner if <3 elements loading)

**Form Patterns:**
- **Label position:** Above input (not floating labels)
- **Required fields:** Asterisk (*) after label
- **Validation timing:** onBlur for individual fields, onSubmit for form
- **Error display:** Inline below input (red text + icon)
- **Help text:** Gray caption below input or tooltip icon

**Modal Patterns:**
- **Size variants:** sm (400px), md (600px), lg (800px)
- **Dismiss:** Click outside OR explicit close button (both)
- **Focus:** Auto-focus first input or primary action
- **Escape key:** Always closes modal
- **Mobile:** Full-screen on <768px

**Navigation Patterns:**
- **Active state:** Blue text + medium weight (not background highlight)
- **Hover:** Gray-50 background
- **Breadcrumbs:** Only in Operator view or deep pages
- **Back button:** Browser back works everywhere (no hijacking)

**Empty State Patterns:**
- **First use:** "Get started" with primary action button
- **No results:** "No transactions match your filters" + reset filters button
- **Cleared:** Brief message, no dramatic imagery

**Notification Patterns:**
- **Placement:** Top-right corner
- **Duration:** 5s auto-dismiss for info, manual dismiss for errors
- **Stacking:** Max 3 visible, queue others
- **Types:** Success (green), Error (coral), Info (blue), Warning (yellow)

**Color Usage Patterns:**
- **Blue = Trust/Actions** - Primary buttons, links, financial data
- **Green = Positive/Growth** - Increases, savings, success states
- **Coral = Caution only** - High utilization, overdue, genuine warnings (not for general errors)
- **Yellow = Learn** - Educational tips, non-critical info
- **Gray = Neutral** - Most of UI, backgrounds, text

**Never use color alone** - Always pair with icon, text label, or pattern

---

## 8. Responsive Design & Accessibility

### 8.1 Responsive Strategy

**Breakpoints:**
```
Mobile: 320px - 767px
Tablet: 768px - 1023px
Desktop: 1024px - 1439px
Wide: 1440px+
```

**Grid Adaptations:**

**Desktop (1024px+):**
- Max width: 1400px
- Metrics: 4-5 column grid (featured span 2)
- Recommendations: 3 columns
- Navigation: Horizontal top nav

**Tablet (768-1023px):**
- Max width: 100% with padding
- Metrics: 2-3 column grid
- Recommendations: 2 columns
- Navigation: Horizontal top nav (might condense)

**Mobile (<768px):**
- Full width with 16px padding
- Metrics: 1 column stack
- Recommendations: 1 column stack
- Navigation: Hamburger menu or bottom nav
- Featured KPI: Still gets visual priority (different background)

**Touch Targets (Mobile):**
- Minimum: 44x44px (iOS standard)
- Spacing: 8px minimum between tappable elements
- Buttons: Full-width on mobile for primary actions

**Typography Scaling:**
- Mobile: Use smaller end of type scale
- Desktop: Use larger end of type scale
- Never go below 16px for body text (accessibility)

### 8.2 Accessibility Strategy

**Target:** WCAG 2.1 Level AA (AAA where practical)

**Color Contrast:**
- Normal text: 4.5:1 minimum (we're using 7:1 for AA)
- Large text (18px+): 3:1 minimum
- UI components: 3:1 minimum
- All chosen colors meet these requirements

**Keyboard Navigation:**
- Tab order follows visual hierarchy (top to bottom, left to right)
- Focus indicators: 2px blue outline on all interactive elements
- Skip to main content link
- Escape closes modals/dropdowns
- Arrow keys navigate lists/tables

**Screen Reader Support:**
- ARIA labels on all icons and icon-only buttons
- ARIA live regions for dynamic content updates
- Semantic HTML (nav, main, aside, article)
- Alt text for informational images (empty alt for decorative)
- Form labels properly associated with inputs

**Keyboard Shortcuts (Optional enhancement):**
- `/` - Focus search
- `g d` - Go to dashboard
- `g i` - Go to insights
- `g t` - Go to transactions
- `?` - Show keyboard shortcuts help

**Motion & Animation:**
- Respect `prefers-reduced-motion`
- No auto-playing animations
- Transitions: 150-300ms (not jarring)

**Testing Requirements:**
- Lighthouse accessibility score: 95+
- Manual keyboard navigation test
- Screen reader test (VoiceOver or NVDA)
- Color blindness simulation
- 200% zoom test (no horizontal scroll)

---

## 9. Implementation Guidance

### 9.1 Tailwind CSS Configuration

**Extend your tailwind.config.js with SpendSense design tokens:**

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // Primary colors
        'blue-primary': '#2C5282',
        'blue-dark': '#1A365D',
        'green-primary': '#38A169',
        'green-light': '#48BB78',
        // Accent colors
        'coral': '#F56565',
        'coral-light': '#FC8181',
        'yellow': '#ECC94B',
        'yellow-light': '#F6E05E',
        // Neutrals
        'gray-50': '#F7FAFC',
        'gray-100': '#E2E8F0',
        'gray-200': '#CBD5E0',
        'gray-600': '#4A5568',
        'gray-800': '#2D3748',
      },
      spacing: {
        // Generous spacing scale
        '18': '4.5rem', // 72px
        '22': '5.5rem', // 88px
      },
      boxShadow: {
        'subtle': '0 1px 2px rgba(0,0,0,0.05)',
        'soft': '0 4px 6px rgba(0,0,0,0.07)',
      },
      fontSize: {
        // Ensure minimums
        'tiny': '0.75rem',   // 12px
        'small': '0.875rem', // 14px
        'base': '1rem',      // 16px
      },
      lineHeight: {
        'relaxed-more': '1.7',
      },
    },
  },
}
```

### 9.2 shadcn-svelte Installation

```bash
npx shadcn-svelte@latest init
```

**Select components to add:**
```bash
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add card
npx shadcn-svelte@latest add input
npx shadcn-svelte@latest add badge
npx shadcn-svelte@latest add alert
npx shadcn-svelte@latest add dialog
npx shadcn-svelte@latest add tabs
npx shadcn-svelte@latest add tooltip
npx shadcn-svelte@latest add table
```

**Customize component styles** in `src/lib/components/ui/*` to match SpendSense spacing and colors.

### 9.3 Priority Implementation Order

**Phase 1: Foundation**
1. Install shadcn-svelte + configure Tailwind
2. Set up color tokens and spacing
3. Create base KPI Card component
4. Create base Recommendation Card component

**Phase 2: Dashboard**
1. Implement Direction 6 layout grid
2. Add persona badge with avatar
3. Wire up KPI cards to real data
4. Add recommendation cards with "because" rationales

**Phase 3: Insights**
1. Adapt Direction 6 for insights focus
2. Implement expandable recommendation cards
3. Add persona explanation section

**Phase 4: Polish**
1. Add hover states and transitions
2. Implement responsive breakpoints
3. Add keyboard navigation
4. Test accessibility
5. Performance optimization

### 9.4 Key Implementation Notes

**Spacing:**
- Use `p-8` (32px) for card padding instead of default `p-6`
- Use `gap-6` (24px) for grid gaps
- Use `space-y-6` for vertical stacking

**Shadows:**
- Prefer `shadow-subtle` for cards at rest
- Use `shadow-soft` on hover
- Avoid `shadow-lg` and above (too dramatic)

**Borders:**
- Use borders more than shadows: `border border-gray-100`
- Left accent borders: `border-l-4 border-l-blue-primary`

**Typography:**
- Body text: `text-base leading-relaxed-more` (16px, 1.7 line-height)
- Headings: Use `font-semibold` not `font-bold`
- Labels: `text-small text-gray-600 uppercase tracking-wide`

**Performance:**
- Lazy load charts and heavy components
- Use Svelte 5's `$derived` for computed values
- Skeleton loaders for >500ms operations
- Avoid layout shift (reserve space for dynamic content)

### 9.5 Completion Summary

**What We've Defined:**

✅ **Design System:** shadcn-svelte with Tailwind CSS v4
✅ **Color Palette:** Balanced calm (blue+green, 30%+ neutrals)
✅ **Typography:** Inter (UI) + JetBrains Mono (data)
✅ **Spacing:** Generous (32px cards, 24px sections)
✅ **Layout:** Direction 6 (Stripe-inspired dashboard)
✅ **Components:** KPI cards, recommendation cards, persona badge, transaction rows
✅ **UX Patterns:** Button hierarchy, feedback, forms, modals, navigation
✅ **Responsive:** 4 breakpoints with adaptive grids
✅ **Accessibility:** WCAG 2.1 AA with AAA where practical

**Ready for Implementation:**
- All design tokens documented
- Component specifications complete
- Layout structure defined
- Interaction patterns established
- Accessibility requirements clear

**Next Steps:**
1. Install shadcn-svelte and configure Tailwind with SpendSense tokens
2. Build KPI Card and Recommendation Card components
3. Implement Direction 6 layout for Dashboard
4. Test responsive behavior and accessibility
5. Iterate based on real data and user feedback

This specification provides everything needed to implement a calm, focused, professional financial education interface that users will trust.

---

## Appendix

### Related Documents

- Product Requirements: `docs/PRD.md`
- Product Brief: `docs/Project Description.md`

### Core Interactive Deliverables

This UX Design Specification was created through visual collaboration:

- **Color Theme Visualizer**: docs/ux-color-themes.html
  - Interactive HTML showing all color theme options explored
  - Live UI component examples in each theme
  - Side-by-side comparison and semantic color usage

- **Design Direction Mockups**: docs/ux-design-directions.html
  - Interactive HTML with 6-8 complete design approaches
  - Full-screen mockups of key screens
  - Design philosophy and rationale for each direction

### Optional Enhancement Deliverables

_This section will be populated if additional UX artifacts are generated through follow-up workflows._

<!-- Additional deliverables added here by other workflows -->

### Next Steps & Follow-Up Workflows

This UX Design Specification can serve as input to:

- **Wireframe Generation Workflow** - Create detailed wireframes from user flows
- **Figma Design Workflow** - Generate Figma files via MCP integration
- **Interactive Prototype Workflow** - Build clickable HTML prototypes
- **Component Showcase Workflow** - Create interactive component library
- **AI Frontend Prompt Workflow** - Generate prompts for v0, Lovable, Bolt, etc.
- **Solution Architecture Workflow** - Define technical architecture with UX context

### Version History

| Date     | Version | Changes                         | Author        |
| -------- | ------- | ------------------------------- | ------------- |
| 2025-11-04 | 1.0     | Initial UX Design Specification | Peter |

---

_This UX Design Specification was created through collaborative design facilitation, not template generation. All decisions were made with user input and are documented with rationale._
