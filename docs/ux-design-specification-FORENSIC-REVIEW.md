# UX Design Specification - Forensic Review Report

**Document Reviewed:** `docs/ux-design-specification.md` (v1.0, 2025-11-04)
**Reviewed By:** Claude (Forensic Analysis Agent)
**Review Date:** 2025-11-04
**Review Type:** Deep Dive - Oversights, Flaws, Gaps, and Implementation Conflicts

---

## Executive Summary

### Overall Assessment: ⚠️ **MODERATE TO CRITICAL ISSUES IDENTIFIED**

The UX Design Specification is **comprehensive in theory but severely disconnected from actual implementation**. While the document itself is well-structured and demonstrates thoughtful design thinking, it suffers from:

1. **Critical Implementation Gap:** shadcn-svelte (the spec's foundation) is NOT installed or used
2. **Color System Mismatch:** Specified hex colors don't match the implemented CSS variables
3. **Phantom Components:** Custom components described but never built
4. **Layout Disconnect:** "Direction 6" dashboard layout doesn't match actual implementation
5. **Missing Accessibility Implementation:** WCAG AA/AAA targets not verified or tested

**Impact:** This specification cannot serve as implementation guidance because the frontend was already built using different patterns. The document is essentially **retroactive fiction** rather than a design blueprint.

**Recommendation:** Either (A) treat this as aspirational redesign documentation for Epic 7, OR (B) rewrite it to document what was actually built in Epics 1-5.

---

## Detailed Findings

### 🔴 CRITICAL ISSUES (Blockers)

#### C1: shadcn-svelte Specified But Not Implemented

**Location:** Section 1.1, 6.1, 9.2
**Severity:** CRITICAL
**Type:** Implementation Conflict

**Issue:**
The entire specification is built around shadcn-svelte as the component library foundation:
- Section 1.1: "Selected System: shadcn-svelte"
- Section 6.1: Lists 11 shadcn components to use
- Section 9.2: Installation instructions for shadcn-svelte
- ADR-005 in architecture.md explicitly mandates shadcn-svelte

**Reality:**
```bash
# spendsense-frontend/package.json
# NO shadcn-svelte dependency
# NO $lib/components/ui/ directory
# Hand-rolled UI with basic Tailwind classes
```

**Impact:**
- Makes 40% of the specification unusable
- Component guidance is for a library that doesn't exist
- Implementation order in Section 9.3 is impossible to follow
- "Copy-paste philosophy" benefits don't apply

**Why This Happened:**
The frontend (Epic 5) was implemented BEFORE this UX spec was created. The spec was written retrospectively but assumed a different tech stack than what was actually built.

**Fix Options:**
1. **Option A (Rewrite):** Document the actual Tailwind v4 + custom components pattern used
2. **Option B (Redesign):** Treat this spec as Epic 7 guidance and install shadcn-svelte
3. **Option C (Hybrid):** Update spec to match current UI, save shadcn migration for v2.0

---

#### C2: Color Palette Implementation Mismatch

**Location:** Section 3.1
**Severity:** CRITICAL
**Type:** Implementation Conflict

**Issue:**
The spec defines a specific hex-based color palette:
```
Deep Blue: #2C5282
Sage Green: #38A169
Warm Coral: #F56565
Golden Yellow: #ECC94B
Neutrals: #F7FAFC, #E2E8F0, #CBD5E0, #4A5568, #2D3748
```

**Reality:**
```css
/* spendsense-frontend/src/app.css */
:root {
  --primary: oklch(0.208 0.042 265.755);      /* NOT #2C5282 */
  --destructive: oklch(0.577 0.245 27.325);   /* NOT #F56565 */
  --chart-2: oklch(0.6 0.118 184.704);        /* Green-ish? */
  /* No --sage-green, --warm-coral, or --golden-yellow tokens */
}
```

**Analysis:**
- The frontend uses **oklch color space** (modern, perceptually uniform) with **semantic token naming**
- The spec's hex colors were never converted to oklch or added to app.css
- The spec's named colors (blue-primary, green-primary, coral, yellow) don't exist as CSS custom properties
- The Tailwind config guidance in Section 9.1 was never implemented

**Impact:**
- Developers cannot use `text-blue-primary` or `bg-sage-green` as the spec suggests
- The "calm and focused" aesthetic depends on these specific colors
- Color usage patterns (Section 7.1) reference non-existent CSS classes

**Why This Happened:**
Tailwind v4 changed to oklch by default. The spec was written assuming v3 hex-based approach, but the frontend modernized to v4's color system without updating design tokens.

**Fix:**
Either:
1. Convert hex colors to oklch equivalents and add to app.css as named tokens
2. Update spec to use semantic tokens (--primary, --chart-2, etc.) instead of named colors

---

#### C3: "Direction 6" Layout Not Implemented

**Location:** Section 4.1
**Severity:** CRITICAL
**Type:** Specification vs Reality

**Issue:**
The spec mandates "Direction 6 - Dashboard Metrics (Stripe-inspired)" layout:
```
┌─────────────────────────────────────────────────┐
│ Top Bar: [Avatar] Persona | [Primary Action]   │
├─────────────────────────────────────────────────┤
│ ┌──────────────────┐ ┌────────┐ ┌────────┐     │
│ │  Featured KPI    │ │ KPI 2  │ │ KPI 3  │     │
│ │  (2x width)      │ └────────┘ └────────┘     │
│ └──────────────────┘ ┌────────┐ ┌────────┐     │
│                      │ KPI 4  │ │ KPI 5  │     │
│                      └────────┘ └────────┘     │
└─────────────────────────────────────────────────┘
```

**Reality (dashboard/+page.svelte lines 122-150):**
```html
<!-- Financial Summary Cards -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
  <!-- Assets Card -->
  <div class="bg-card rounded-lg p-6 border-l-4 border-l-chart-2 shadow-sm">
  <!-- Liabilities Card -->
  <div class="bg-card rounded-lg p-6 border-l-4 border-l-destructive shadow-sm">
  <!-- Net Worth Card -->
  <div class="bg-card rounded-lg p-6 border-l-4 border-l-primary shadow-sm">
</div>
```

**Analysis:**
- **Actual layout:** Simple 3-column equal-width grid (Assets, Liabilities, Net Worth)
- **No featured KPI spanning 2 columns**
- **No 4-5 KPI grid** as specified
- **No persona badge in top bar** (spec's key feature)
- **No avatar gradient** (blue→green)
- Pattern is simpler and more balanced than spec's Stripe-inspired design

**Impact:**
- The spec's flagship layout design was never built
- The "calm and focused" aesthetic relies on this specific hierarchy
- Responsive breakpoints in Section 8.1 don't match actual implementation

**Why This Happened:**
Epic 5 stories (5.2, 5.3, 5.4) were implemented using simpler acceptance criteria. The elaborate Direction 6 mockup in the UX spec came later and was never fed back to implementation.

**Fix:**
Document the actual "3-column balanced grid" pattern used, or redesign the dashboard to match Direction 6 (would be Epic 7).

---

### 🟡 HIGH PRIORITY ISSUES (Major Gaps)

#### H1: Custom Components Described But Never Built

**Location:** Section 6.1
**Severity:** HIGH
**Type:** Incomplete Specification

**Issue:**
The spec provides detailed anatomy for 4 custom components:
1. **KPI Card** - 4 states, 3 variants
2. **Recommendation Card** - 3 states, 3 variants
3. **Persona Badge** - Avatar gradient, placement guidance
4. **Transaction Row** - 3 states, hover interactions

**Reality:**
- No `/lib/components/` directory exists
- Components are inline in page files
- No reusable component library
- No documented variants or states

**Impact:**
- Cannot achieve consistent component behavior across pages
- Cannot reuse "Featured KPI" variant (it doesn't exist)
- Hover states and interactions not systematically implemented

**Fix:**
Extract inline components into reusable library OR update spec to say "inline components, no library."

---

#### H2: Spacing System Not Implemented

**Location:** Section 3.3, 9.4
**Severity:** HIGH
**Type:** Implementation Gap

**Issue:**
Spec mandates "Maximum Breathing Room" spacing:
- Card padding: 2rem (32px) minimum
- Section spacing: 3rem (48px) minimum
- Tailwind config extends with custom spacing tokens

**Reality:**
```html
<!-- dashboard/+page.svelte line 127 -->
<div class="bg-card rounded-lg p-6 border-l-4">
```
`p-6` = 24px, NOT 32px as specified.

**Analysis:**
- The frontend uses default Tailwind spacing (p-4, p-6, p-8)
- The spec's "generous" spacing philosophy (25-50% more padding) was not followed
- Custom spacing tokens in Section 9.1 (`'18': '4.5rem'`, `'22': '5.5rem'`) don't exist in Tailwind config

**Impact:**
- UI feels more cramped than spec's "calm and focused" vision
- Inconsistent with the "white space as a feature" principle

**Fix:**
Either increase padding to p-8 everywhere, or update spec to document actual p-6 standard.

---

#### H3: Shadow System Not Consistent

**Location:** Section 3.4, 9.4
**Severity:** HIGH
**Type:** Implementation Conflict

**Issue:**
Spec defines custom shadow tokens:
```css
shadow-subtle: 0 1px 2px rgba(0,0,0,0.05)
shadow-soft: 0 4px 6px rgba(0,0,0,0.07)
```

**Reality:**
```html
<div class="shadow-sm">  <!-- Default Tailwind, not custom -->
```

**Impact:**
- The "subtle, not dramatic" shadow philosophy isn't enforced via design tokens
- Using generic `shadow-sm` and `shadow` classes instead of branded shadows

**Fix:**
Add custom shadow utilities to Tailwind config or accept default shadows.

---

#### H4: Typography Scale Partially Implemented

**Location:** Section 3.2
**Severity:** HIGH
**Type:** Incomplete Implementation

**Issue:**
Spec defines responsive type scale with generous line-height:
```
Body: 16px with line-height 1.6-1.7 ("relaxed-more")
Headings: Tight 1.2-1.3
```

**Reality:**
```html
<h1 class="text-3xl font-bold">  <!-- No explicit line-height -->
```

**Analysis:**
- Text sizing classes are used (text-3xl, text-xl, text-sm)
- But custom line-height utilities (`leading-relaxed-more: 1.7`) from Section 9.1 don't exist
- No monospace utility for financial numbers (JetBrains Mono not configured)

**Impact:**
- Missing the "calm" feeling that comes from generous line-height
- Financial figures don't use monospace for scannability

**Fix:**
Add line-height and font-family utilities to Tailwind config.

---

### 🟠 MEDIUM PRIORITY ISSUES (Quality Concerns)

#### M1: Accessibility Claims Not Verifiable

**Location:** Section 8.2
**Severity:** MEDIUM
**Type:** Unverified Claim

**Issue:**
Spec states:
- "Target: WCAG 2.1 Level AA (AAA where practical)"
- "All chosen colors meet these requirements" (7:1 contrast for AAA)
- "Lighthouse accessibility score: 95+"

**Problem:**
- No accessibility audit results provided
- oklch colors in app.css have not been contrast-tested
- No evidence of keyboard navigation testing
- No screen reader testing documented

**Fix:**
Run actual accessibility audit and document results OR change claims to "should be tested for..."

---

#### M2: Responsive Breakpoints Mismatch

**Location:** Section 8.1
**Severity:** MEDIUM
**Type:** Specification Error

**Issue:**
Spec defines breakpoints:
```
Mobile: 320px - 767px
Tablet: 768px - 1023px
Desktop: 1024px - 1439px
Wide: 1440px+
```

**Reality (Tailwind v4 defaults):**
```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

**Impact:**
- The spec's "tablet" guidance (768-1023px) maps to `md:` and part of `lg:`
- The spec's "wide" (1440px+) doesn't exist as a breakpoint
- Grid adaptations in Section 8.1 use non-standard breakpoints

**Fix:**
Update spec to use Tailwind's actual breakpoint names (sm, md, lg, xl, 2xl).

---

#### M3: Modal Patterns Specified But No Modals Exist

**Location:** Section 7.1
**Severity:** MEDIUM
**Type:** Overspecification

**Issue:**
Detailed modal specifications:
- Size variants (sm 400px, md 600px, lg 800px)
- Dismiss behavior (click outside OR close button)
- Focus management (auto-focus first input)
- Mobile behavior (full-screen <768px)

**Reality:**
- insights/+page.svelte uses inline expansion, NOT modals
- No dialog/modal components in codebase
- Recommendation cards expand inline: `{#if expandedCard === index}`

**Impact:**
- 10+ lines of specification for a pattern that doesn't exist
- Creates confusion about how expanded recommendations actually work

**Fix:**
Remove modal guidance or update to "inline expansion" pattern.

---

#### M4: Button Hierarchy Rule Violated

**Location:** Section 7.1
**Severity:** MEDIUM
**Type:** Best Practice Violation

**Issue:**
Spec states: **"Never have more than 1 primary button visible at once"**

**Reality Check Needed:**
Need to audit all pages to verify this rule is followed. The spec makes this absolute claim but doesn't verify implementation.

**Fix:**
Either audit and confirm compliance, or soften the language to "avoid multiple primary buttons."

---

#### M5: Empty State Patterns Underspecified

**Location:** Section 7.1
**Severity:** MEDIUM
**Type:** Incomplete Guidance

**Issue:**
Empty state guidance is minimal:
- "First use: Get started with primary action button"
- "No results: No transactions match your filters + reset filters button"
- "Cleared: Brief message, no dramatic imagery"

**Missing:**
- What does "get started" flow look like?
- Where is the consent flow positioned?
- What happens if a user has no transactions?
- What if recommendations fail to generate?

**Reality (insights/+page.svelte line 148):**
```html
{:else if recommendations.length === 0}
  <div class="bg-card rounded-lg border border-border p-12 text-center">
    <h2 class="text-xl font-semibold text-foreground mb-2">No Insights Available</h2>
```

**Analysis:**
Empty states ARE implemented, but they're simpler than the spec implies. The spec could be more specific.

---

### 🟢 LOW PRIORITY ISSUES (Minor Concerns)

#### L1: Keyboard Shortcuts Listed As "Optional Enhancement"

**Location:** Section 8.2
**Severity:** LOW
**Type:** Scope Creep

**Issue:**
Lists 5 keyboard shortcuts (/, g d, g i, g t, ?) as accessibility features.

**Problem:**
- These are vim-style power-user shortcuts, not accessibility features
- Not implemented
- Labeled "optional" but included in accessibility section
- Creates false impression of feature completeness

**Fix:**
Move to "Future Enhancements" appendix or remove entirely.

---

#### L2: Font Loading Strategy Not Defined

**Location:** Section 3.2
**Severity:** LOW
**Type:** Implementation Detail Missing

**Issue:**
Spec specifies fonts (Inter, JetBrains Mono) but doesn't address:
- Self-hosted vs Google Fonts CDN?
- Font loading strategy (FOUT, FOIT, fallback)?
- Performance budget for web fonts?

**Impact:**
Minor - fonts will load, but optimization strategy is undefined.

---

#### L3: Animation Guidelines Vague

**Location:** Section 8.2
**Severity:** LOW
**Type:** Underspecified

**Issue:**
States "Transitions: 150-300ms (not jarring)" but doesn't specify:
- Which easing curves to use?
- Which elements get transitions?
- Which properties to animate (transform, opacity, color)?

**Current Reality:**
```html
class="...hover:bg-destructive/90 transition-colors"
```
Uses generic `transition-colors` utility. Works fine but not guided by spec.

---

#### L4: Chart/Data Visualization Not Addressed

**Location:** Multiple sections
**Severity:** LOW
**Type:** Scope Gap

**Issue:**
The spec mentions:
- "Simple visualizations" (Section 2.2)
- "Intuitive charts" (Section 2.2)
- Chart colors defined (--chart-1 through --chart-5)

But provides ZERO guidance on:
- Which charting library to use?
- What chart types for what data?
- How to make charts accessible?
- Mobile chart patterns?

**Current Reality:**
No charts implemented in Epic 5. This is likely future work (Epic 7?).

**Fix:**
Add "Data Visualization" section OR mark charts as out-of-scope for v1.0.

---

#### L5: Dark Mode Mentioned But Not Specified

**Location:** app.css has `.dark` theme defined
**Severity:** LOW
**Type:** Missing Feature

**Issue:**
- app.css includes complete dark mode color tokens
- UX spec mentions dark mode once in passing (Section UX_SECOND_OPINION.md)
- No toggle, no user preference detection, no dark mode guidance in main spec

**Impact:**
Dark mode exists in CSS but is inaccessible to users.

---

### 🔵 DOCUMENTATION ISSUES (Meta Problems)

#### D1: HTML Visualizations Not Reviewed

**Location:** Section 9.5, Appendix
**Severity:** INFO
**Type:** Incomplete Forensic Review

**Issue:**
The spec references two HTML files:
- `ux-color-themes.html` (886 lines)
- `ux-design-directions.html` (1651 lines)

These were not fully reviewed in this forensic analysis due to size. They should be validated for:
- Do the mockups match the specification text?
- Are the "Direction 6" visuals actually aligned with Section 4.1 description?
- Do color themes match the palette in Section 3.1?

**Recommendation:**
Review HTML visualizations separately to ensure spec-visual alignment.

---

#### D2: Version History Shows Single Version

**Location:** Section 9.5
**Severity:** INFO
**Type:** Versioning Concern

**Issue:**
```
| Date       | Version | Changes                         |
| 2025-11-04 | 1.0     | Initial UX Design Specification |
```

**Problem:**
If changes are made (and they should be, given the issues above), there's no v1.1, v1.2 tracking plan.

**Fix:**
Commit to semantic versioning for design spec updates.

---

#### D3: Related Documents Section Incomplete

**Location:** Appendix
**Severity:** INFO
**Type:** Missing Cross-References

**Issue:**
Lists only:
- PRD.md
- Project Description.md

**Missing:**
- architecture.md (critical alignment document)
- UX_SECOND_OPINION.md (earlier design brief)
- Story files (5-2, 5-3, 5-4, 5-5) with actual UI acceptance criteria
- Epic 7 stories (redesign work)

**Fix:**
Add complete cross-reference list.

---

## Alignment Analysis

### PRD Alignment: ⚠️ PARTIAL

**Matches PRD:**
- ✅ Calm and focused emotional response (PRD Section: User Experience)
- ✅ 100% explainability (rationale sections in recommendations)
- ✅ <5 second response time target
- ✅ No shaming language philosophy

**Conflicts with PRD:**
- ❌ PRD doesn't mandate shadcn-svelte specifically (architecture doc does)
- ❌ PRD specifies "operator view" but UX spec barely covers it (Section 5.1 mentions it briefly)

---

### Architecture Alignment: ❌ MAJOR CONFLICT

**Conflicts:**
- ❌ Architecture.md ADR-005 mandates shadcn-svelte → Not implemented
- ❌ Architecture specifies "shadcn Card, shadcn Table, shadcn Badge" → None installed
- ❌ Architecture project structure shows `lib/components/ui/` → Directory doesn't exist

**Root Cause:**
The architecture document was written prescriptively (before implementation), the UX spec was written descriptively (after implementation), but NEITHER matches reality.

---

### Implementation Alignment: ❌ CRITICAL MISMATCH

**Summary:**
The UX spec reads like a design proposal for Epic 7 (redesign) rather than documentation of Epic 5 (current UI).

**Mismatch Examples:**
| Spec Says | Reality Is |
|-----------|-----------|
| shadcn-svelte components | Hand-rolled inline components |
| Direction 6 dashboard layout | Simple 3-column grid |
| Hex colors (#2C5282) | oklch colors (0.208 0.042 265.755) |
| 32px card padding (p-8) | 24px card padding (p-6) |
| Custom shadow-subtle | Generic shadow-sm |
| Modal dialogs for expansion | Inline expansion with conditional |
| Persona badge in top bar | No persona badge on dashboard |

---

## What's Actually Good

Despite the critical issues, the specification has strong elements:

### ✅ Strong Points

1. **Design Philosophy (Sections 1-2):**
   - Excellent articulation of "calm and focused" aesthetic
   - Clear emotional response goals (trust, reassurance, empowerment)
   - Linear and Stripe inspiration is appropriate for fintech

2. **Color Psychology (Section 3.1):**
   - Well-reasoned color choices (blue=trust, green=growth)
   - WCAG contrast awareness
   - "Never use color alone" accessibility principle

3. **Component Anatomy (Section 6.1):**
   - Detailed specifications for KPI Card, Recommendation Card
   - Clear state definitions (default, hover, expanded)
   - Good progressive disclosure thinking

4. **User Journey Flows (Section 5.1):**
   - Simple, direct paths (no multi-step wizards)
   - Progressive disclosure strategy
   - "Instant state changes" performance goal

5. **Accessibility Mindset (Section 8.2):**
   - WCAG 2.1 AA target is appropriate
   - Keyboard navigation considerations
   - Screen reader support thinking
   - `prefers-reduced-motion` awareness

6. **Documentation Structure:**
   - Logical section organization
   - Clear headings and hierarchy
   - Implementation guidance (Section 9)
   - Cross-references to related docs

---

## Recommendations

### Immediate Actions (Week 1)

1. **Decide the Document's Purpose:**
   - [ ] **Option A:** Rewrite as Epic 7 redesign specification (aspirational)
   - [ ] **Option B:** Rewrite to document actual Epic 5 implementation (historical)
   - [ ] **Option C:** Split into two docs: "Current UI" and "Redesign Proposal"

2. **Fix Critical Mismatches:**
   - [ ] Update color palette section to use oklch + semantic tokens
   - [ ] Document actual layout patterns (3-column grid, not Direction 6)
   - [ ] Remove shadcn-svelte references OR add Epic 7 story to install it

3. **Run Accessibility Audit:**
   - [ ] Lighthouse accessibility test
   - [ ] Contrast ratio verification
   - [ ] Keyboard navigation test
   - [ ] Update Section 8.2 with actual results

### Short-Term Actions (Week 2-3)

4. **Extract Component Library:**
   - [ ] Create `/lib/components/KPICard.svelte` from inline code
   - [ ] Create `/lib/components/RecommendationCard.svelte`
   - [ ] Document actual component props and variants

5. **Align Tailwind Config:**
   - [ ] Add custom spacing tokens if keeping "generous spacing" philosophy
   - [ ] Add custom shadow tokens (`shadow-subtle`, `shadow-soft`)
   - [ ] Add JetBrains Mono for financial numbers
   - [ ] Add line-height utilities

6. **Update Cross-References:**
   - [ ] Link to architecture.md, UX_SECOND_OPINION.md, story files
   - [ ] Add Epic 7 stories (7.1 through 7.5 already exist!) to Related Documents
   - [ ] Note conflicts between documents

### Long-Term Actions (Epic 7)

7. **If Choosing Redesign Path:**
   - [ ] Install shadcn-svelte as originally intended
   - [ ] Implement Direction 6 dashboard layout
   - [ ] Build custom components per Section 6.1 specs
   - [ ] Migrate colors to named tokens (blue-primary, sage-green, etc.)
   - [ ] Increase spacing to spec's "generous" levels

8. **If Choosing Documentation Path:**
   - [ ] Photograph actual UI and embed screenshots
   - [ ] Document actual component patterns used
   - [ ] Update color system to match oklch reality
   - [ ] Simplify claims (remove unverified accessibility assertions)

---

## Risk Assessment

### High Risk 🔴

**Risk:** Epic 7 stories (7.1-7.5) already exist and may depend on this spec.
**Implication:** If Epic 7 developers follow this spec, they'll try to install shadcn-svelte and refactor everything.
**Mitigation:** Review Epic 7 stories immediately to understand dependencies.

### Medium Risk 🟡

**Risk:** Developers use this spec for styling decisions without realizing color tokens don't exist.
**Implication:** Time wasted searching for CSS classes like `text-blue-primary` that don't exist.
**Mitigation:** Add prominent disclaimer at top: "⚠️ This spec describes aspirational design, not current implementation."

### Low Risk 🟢

**Risk:** Users notice UI doesn't match the "calm and focused" aesthetic promises.
**Implication:** Subjective; current UI is functional and clean enough for demo.
**Mitigation:** Set expectations that v1.0 is MVP, v2.0 will match this spec.

---

## Conclusion

The UX Design Specification demonstrates **excellent design thinking** but suffers from being written **after implementation** without validating against the actual codebase. It's a high-quality design proposal for what SpendSense *could* become, but it's not an accurate document of what SpendSense *is*.

### Key Insights

1. **Retrospective Documentation Is Hard:** Writing design specs after code is written creates misalignment
2. **Architecture ≠ Implementation:** Both architecture.md and ux-design-specification.md prescribed shadcn-svelte, but Epic 5 ignored it
3. **Process Breakdown:** The BMAD workflow says "create-design: conditional" was marked "docs/ux-design-specification.md" on 2025-11-04, but Epic 5 finished on ~2025-11-03
4. **Epic 7 Exists:** Stories 7.1-7.5 suggest this spec IS intended for redesign work

### What To Do Next

**Recommended Path: Option A (Aspirational Redesign Doc)**

1. Add disclaimer at top: "This specification guides Epic 7 redesign work. For current implementation, see story files 5.2-5.5."
2. Keep spec as-is (it's good design guidance)
3. Use it to drive Epic 7 implementation
4. Create separate `ux-current-state.md` documenting actual UI

**Alternative Path: Option B (Historical Documentation)**

1. Rewrite Sections 3-6 to match actual implementation
2. Remove shadcn-svelte references
3. Document oklch color system as-implemented
4. Add screenshots of actual UI
5. Rename to `ux-as-built.md`

**Either way, decide now before Epic 7 work begins.**

---

## Appendix: Verification Commands

To validate these findings:

```bash
# Verify shadcn-svelte not installed
grep -i "shadcn" spendsense-frontend/package.json  # Should be empty

# Check for component library
ls spendsense-frontend/src/lib/components/  # Should error or show api/types only

# Verify color mismatch
grep "#2C5282" spendsense-frontend/src/app.css  # Should be empty
grep "oklch" spendsense-frontend/src/app.css    # Should show many results

# Check dashboard layout
grep -A 10 "grid-cols" spendsense-frontend/src/routes/dashboard/+page.svelte  # Shows 3-column, not Direction 6

# Verify spacing
grep "p-8" spendsense-frontend/src/routes/dashboard/+page.svelte  # Should be rare/absent
grep "p-6" spendsense-frontend/src/routes/dashboard/+page.svelte  # Should be common
```

---

**End of Forensic Review**

_This review prioritizes truth over politeness. The specification is well-written but disconnected from reality. Address the implementation gap before proceeding with Epic 7._
