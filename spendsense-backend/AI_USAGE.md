# AI Usage in SpendSense

## Overview

SpendSense uses a **hybrid approach** to recommendation generation, combining deterministic template-based logic with optional AI-powered capabilities. This document describes where AI is used, how to enable it, and guidelines for responsible AI integration.

## Current AI Integration Status

### ✅ Implemented (Production-Ready)
- **Template-Based Recommendations** (Default)
  - Deterministic signal-based content selection
  - Rule-based persona assignment
  - Template-driven rationale generation
  - No AI API calls required
  - 100% reproducible and testable

### 🚧 Stub Implementation (Ready for Integration)
- **AI-Powered Recommendations** (Future Enhancement)
  - Dynamic content ranking with LLMs
  - Custom recommendation generation
  - Adaptive persona explanations
  - Location: `spendsense.recommend.engine.AIRecommendationEngine`
  - Status: Interface defined, implementation TODO

### ❌ Not Used
- AI is **NOT** used for:
  - Signal detection (purely rule-based)
  - Eligibility checking (deterministic guardrails)
  - User data analysis (SQL queries only)
  - Content moderation (rule-based filters)

## Architecture: Adapter Pattern

SpendSense uses the **Adapter Pattern** to enable seamless swapping between recommendation strategies:

```python
# Abstract Interface
class RecommendationEngine(ABC):
    async def generate_recommendations(
        db: AsyncSession,
        user_id: str,
        window_days: int
    ) -> RecommendationResult

# Implementations
- StandardRecommendationEngine (default, no AI)
- AIRecommendationEngine (future, with AI)
```

### Current Default (Template-Based)
```python
# spendsense/ui/insights.py
from spendsense.recommend.engine import StandardRecommendationEngine

engine = StandardRecommendationEngine()
```

### Future AI-Powered (When Implemented)
```python
# spendsense/ui/insights.py
from spendsense.recommend.engine import AIRecommendationEngine

engine = AIRecommendationEngine(
    ai_provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

**That's the only code change needed** - the adapter pattern ensures all downstream code works identically.

## AI Integration Points

### 1. Content Generation

#### Current: Template-Based
```python
# spendsense/recommend/content_selection.py
class TemplateGenerator(ContentGenerator):
    async def generate_education(
        persona_type: str,
        signals: BehaviorSignals,
        limit: int = 3
    ) -> List[EducationItem]:
        # 1. Load content catalog (YAML)
        # 2. Score content by signal tag matching
        # 3. Return top N by relevance
```

**How it works:**
- Content items have `persona_tags` and `signal_tags`
- Matching algorithm scores items: `persona_match + signal_match`
- Deterministic ranking (same signals → same recommendations)

#### Future: AI-Powered
```python
# spendsense/recommend/llm_generation.py (stub exists)
class LLMGenerator(ContentGenerator):
    async def generate_education(
        persona_type: str,
        signals: BehaviorSignals,
        limit: int = 3
    ) -> List[EducationItem]:
        # 1. Query all content from catalog
        # 2. Send user context + content to LLM
        # 3. LLM ranks and selects most relevant items
        # 4. Optionally generates custom content not in catalog
```

**Benefits:**
- More nuanced content selection
- Can generate explanations tailored to user's specific situation
- Adapts to edge cases not covered by templates

**Risks:**
- Non-deterministic (same inputs may vary outputs)
- Requires AI API key and costs
- Latency increase (API round-trip)
- Need monitoring for quality/bias

### 2. Rationale Generation

#### Current: Template-Based
```python
# Uses hardcoded templates per persona
explanation_templates = {
    "high_utilization": "Your credit card utilization is currently at {util}%, "
                       "significantly above the recommended 30% threshold.",
    # More templates...
}
```

**Advantages:**
- Fast (no API calls)
- Consistent messaging
- Easy to audit/review
- Compliant with disclosure requirements

#### Future: AI-Generated (Stub)
```python
# Could use AI to generate personalized explanations
# Still anchored to detected signals for accuracy
prompt = f"""
Given user persona: {persona_type}
Behavioral signals: {signals}
Generate a 1-2 sentence explanation for why this content is relevant.
"""
```

**Guidelines if implementing:**
- Always include specific data points from signals
- Never make assumptions beyond detected signals
- Include standard disclaimers (handled separately)
- Log AI-generated text for review

### 3. Partner Offer Selection

#### Current: Deterministic Eligibility
```python
# spendsense/guardrails/eligibility.py
def check_eligibility(offer, user_data):
    # Rule-based checks:
    # - Income requirements
    # - Existing accounts (avoid duplicates)
    # - Predatory product blocklist
    # - APR caps
```

**This MUST remain deterministic** for compliance and transparency.

#### Future: AI-Enhanced Ranking (Within Eligible Set)
```python
# After eligibility filtering, AI could:
# 1. Rank eligible offers by predicted user fit
# 2. Personalize offer presentation
# 3. Generate comparison explanations

# But eligibility MUST be deterministic
```

## How to Enable AI (Future)

### Step 1: Set Environment Variable
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
# or
OPENAI_API_KEY=sk-...
```

### Step 2: Swap Engine Implementation
```python
# spendsense/ui/insights.py
- engine = StandardRecommendationEngine()
+ engine = AIRecommendationEngine(
+     ai_provider="anthropic",
+     model="claude-3-5-sonnet-20241022"
+ )
```

### Step 3: Deploy and Monitor
- Monitor latency (p95, p99)
- Track AI API costs
- Log all AI-generated content for review
- Set up alerts for quality degradation

## AI Guardrails

When AI is integrated, the following guardrails MUST remain in place:

### 1. Consent Checking
```python
# ALWAYS check consent before generating insights
if not check_consent(user.consent):
    return empty_response  # No AI or template recommendations
```

### 2. Tone Guardrails
```python
# Screen ALL AI-generated content for shame/blame
if detect_shame_pattern(ai_generated_text):
    logger.warning("Blocked AI content: shame pattern detected")
    fallback_to_template()
```

### 3. Eligibility Filtering
```python
# NEVER let AI override eligibility checks
eligible_offers = [o for o in all_offers if check_eligibility(o, user_data)]
ai_ranked = ai.rank_offers(eligible_offers)  # AI ranks AFTER filtering
```

### 4. Disclosure Requirements
```python
# ALWAYS include standard disclaimers
# These are added by disclosure.py, not AI-generated
response.disclaimer = generate_standard_disclaimer()
```

### 5. Data Minimization
```python
# Only send necessary data to AI
context = {
    "persona_type": persona,  # Not user ID
    "signals_summary": signals_summary,  # Aggregated, not raw transactions
    # Never include: SSN, account numbers, PII
}
```

## Testing AI Integration

### Unit Tests
```python
# tests/test_ai_engine.py
@pytest.mark.ai
async def test_ai_engine_fallback(monkeypatch):
    """Test that AI failures fall back to templates"""
    # Mock AI API failure
    monkeypatch.setattr("anthropic.Anthropic", MagicMock(side_effect=Exception))

    # Should fall back to template-based
    result = await engine.generate_recommendations(db, user_id)
    assert len(result.education_recommendations) == 3  # Still works
```

### Integration Tests
```python
@pytest.mark.ai
@pytest.mark.slow
async def test_ai_recommendation_quality():
    """Test AI generates appropriate recommendations"""
    result = await ai_engine.generate_recommendations(db, user_id)

    # Verify guardrails applied
    assert all(check_tone(rec.content.summary) for rec in result.education_recommendations)
    assert all(rec.offer.eligibility_met for rec in result.offer_recommendations)
```

### Evaluation Metrics
```python
# scripts/evaluate.py already tracks:
- Coverage (% users with recommendations)
- Explainability (% with rationales)
- Relevance (1-5 scale, target ≥3.0)
- Latency (target <5s)

# Add for AI:
- AI API success rate
- Fallback rate (when templates used)
- Cost per recommendation
- Quality score (human review sample)
```

## Cost Considerations

### Template-Based (Current)
- **Cost**: $0
- **Latency**: ~100-200ms
- **Scalability**: Unlimited

### AI-Powered (Future)
- **Cost**: ~$0.001-0.01 per recommendation (varies by model)
- **Latency**: ~500-2000ms (includes API round-trip)
- **Scalability**: Subject to API rate limits

**Recommendation**: Use AI selectively:
- High-value users (paid tier)
- Complex edge cases (low signal confidence)
- A/B testing new content strategies

## Responsible AI Checklist

Before deploying AI-powered recommendations:

- [ ] AI-generated content reviewed by compliance team
- [ ] Tone guardrails tested with adversarial examples
- [ ] Fallback to templates works when AI fails
- [ ] Cost monitoring and alerts configured
- [ ] Latency SLAs defined and monitored
- [ ] Bias testing completed (diverse user demographics)
- [ ] User notification that AI is used (if required by regulation)
- [ ] Audit log captures all AI decisions
- [ ] Human review process for flagged AI content
- [ ] Incident response plan for AI failures

## Example: AI Integration Sequence

```python
# 1. User requests insights
GET /insights/{user_id}

# 2. Check consent (deterministic)
if not user.consent:
    return empty_response

# 3. Compute behavioral signals (deterministic)
signals = await compute_signals(db, user_id, window_days)

# 4. Assign persona (deterministic or AI-enhanced)
persona = await assign_persona(signals)

# 5. Generate recommendations (template or AI)
if use_ai_engine:
    # AI selects from catalog + optional custom generation
    recommendations = await ai_engine.generate(persona, signals)
else:
    # Template-based selection
    recommendations = await template_engine.generate(persona, signals)

# 6. Apply guardrails (ALWAYS deterministic)
filtered = apply_guardrails(recommendations, user_data)

# 7. Add disclaimers (ALWAYS standard)
filtered = add_disclaimers(filtered)

# 8. Return response
return InsightsResponse(recommendations=filtered)
```

## Future Enhancements

### Short-term (Next Quarter)
1. Implement LLMGenerator with Claude 3.5 Sonnet
2. A/B test AI vs templates on 10% of users
3. Measure quality, latency, cost metrics
4. Set up monitoring and alerting

### Medium-term (6 months)
1. AI-powered content ranking (keeping template fallback)
2. Personalized rationale generation
3. Dynamic offer explanations
4. Adaptive persona descriptions

### Long-term (1 year)
1. Custom content generation (beyond catalog)
2. Multi-turn financial Q&A
3. Predictive recommendations (before signals detected)
4. AI-powered financial coaching

## Questions and Contact

For questions about AI integration:
- Technical: See `spendsense/recommend/engine.py` adapter pattern
- Compliance: Ensure all guardrails remain in place
- Cost/Ops: Monitor with `scripts/evaluate.py` metrics

**Key Principle**: AI should enhance, not replace, deterministic guardrails and compliance checks.
