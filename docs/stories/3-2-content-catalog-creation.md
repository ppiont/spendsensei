# Story 3.2: Content Catalog Creation

Status: drafted

## Story

As a platform,
I want a catalog of educational content mapped to personas and signals,
So that I can deliver relevant financial education to users.

## Acceptance Criteria

1. Create `data/content_catalog.yaml` file
2. Define content structure with fields: id, title, summary, body, cta, persona_tags, signal_tags, source
3. Create at least 10 education items covering all persona types
4. Ensure no shaming language in any content
5. Add disclaimer text for all recommendations
6. Content follows PRD examples
7. Verify YAML syntax is valid
8. Include at least 2 items per persona type
9. Map signal_tags to actual detected signals
10. Body text 200-500 words, actionable and clear

## Tasks / Subtasks

- [ ] **Task 1: Create content catalog structure** (AC: #1, #2)
  - [ ] Create `spendsense-backend/data/content_catalog.yaml`
  - [ ] Define YAML schema with required fields
  
- [ ] **Task 2: Write credit utilization content** (AC: #3)
  - [ ] 2+ items for high_utilization persona
  - [ ] Topics: understanding utilization, reducing balances, payment strategies
  
- [ ] **Task 3: Write subscription management content** (AC: #3)
  - [ ] 2+ items for subscription_heavy persona
  - [ ] Topics: subscription audit, cancellation tips
  
- [ ] **Task 4: Write variable income content** (AC: #3)
  - [ ] 2+ items for variable_income persona
  - [ ] Topics: budgeting for irregular income, building buffer
  
- [ ] **Task 5: Write savings content** (AC: #3)
  - [ ] 2+ items for savings_builder persona
  - [ ] Topics: emergency fund, automation, growth strategies
  
- [ ] **Task 6: Write balanced content** (AC: #3)
  - [ ] 2+ items for balanced persona
  - [ ] Topics: financial wellness, general tips
  
- [ ] **Task 7: Review and validate** (AC: #4, #5, #6, #7)
  - [ ] Check for shaming language
  - [ ] Add disclaimer
  - [ ] Validate YAML syntax
  - [ ] Verify signal_tags match actual signals

## Dev Notes

### Architecture Context

**YAML Structure:**
```yaml
- id: "credit-util-101"
  title: "Understanding Credit Utilization"
  summary: "Learn how credit utilization affects your financial health."
  body: |
    [200-500 words of educational content]
  cta: "Review Your Credit Cards"
  persona_tags: ["high_utilization"]
  signal_tags: ["high_credit_utilization", "interest_charges"]
  source: "Financial Education Database"
```

### Project Structure Notes

**New files:**
- `spendsense-backend/data/content_catalog.yaml`

### Testing Strategy

**Manual verification:**
1. Validate YAML syntax
2. Review all content for tone
3. Verify persona mapping
4. Check signal tag accuracy

### References

- [Source: docs/epics.md#Story 3.2: Content Catalog Creation]
- [Source: docs/PRD.md#Educational Content Examples]

## Dev Agent Record

### Context Reference

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2025-11-03 | Peter (SM) | Initial story creation from epics and architecture |
