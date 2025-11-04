# Content Generators Usage Guide

## Overview

The `generators` module provides content generation capabilities for personalized financial education and explainable rationales. It uses a template-based approach that scores content from a YAML catalog based on user behavioral signals.

## Architecture

```
generators/
├── base.py          # Abstract ContentGenerator interface + Pydantic models
├── template.py      # TemplateGenerator implementation
└── __init__.py      # Module exports
```

### Design Principles

1. **Abstract Interface**: Base class allows swapping implementations (e.g., future LLM-based)
2. **Type Safety**: Pydantic models provide validation and serialization
3. **Explainability**: Rationales include concrete data points from user signals
4. **Deterministic**: Template-based approach ensures consistent results

## Quick Start

### Basic Usage

```python
from spendsense.generators import TemplateGenerator
from spendsense.services.features import BehaviorSignals

# Initialize generator
generator = TemplateGenerator()

# Create user signals
signals = BehaviorSignals(
    credit={
        "overall_utilization": 75.0,
        "total_balance": 750000,
        "total_limit": 1000000,
        "flags": ["interest_charges"]
    },
    income={"median_gap_days": 14, "stability": "stable"},
    savings={"growth_rate": 1.5, "monthly_inflow": 15000},
    subscriptions={"count": 3, "monthly_recurring_spend": 7500}
)

# Generate education content
education_items = await generator.generate_education(
    persona_type="high_utilization",
    signals=signals,
    limit=3
)

# Generate rationale
rationale = await generator.generate_rationale(
    persona_type="high_utilization",
    confidence=0.95,
    signals=signals
)
```

### API Integration Example

```python
from fastapi import APIRouter, Depends
from spendsense.generators import TemplateGenerator
from spendsense.services.personas import assign_persona
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
generator = TemplateGenerator()

@router.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    window_days: int = 180,
    db: AsyncSession = Depends(get_db)
):
    # Assign persona
    persona_result = await assign_persona(db, user_id, window_days)

    # Generate recommendations
    education_items = await generator.generate_education(
        persona_type=persona_result["persona_type"],
        signals=persona_result["signals"],
        limit=3
    )

    rationale = await generator.generate_rationale(
        persona_type=persona_result["persona_type"],
        confidence=persona_result["confidence"],
        signals=persona_result["signals"]
    )

    return {
        "persona": {
            "type": persona_result["persona_type"],
            "confidence": persona_result["confidence"]
        },
        "rationale": {
            "explanation": rationale.explanation,
            "key_signals": rationale.key_signals
        },
        "education": [item.dict() for item in education_items]
    }
```

## Models

### EducationItem

Represents a single educational content item selected for a user.

```python
class EducationItem(BaseModel):
    id: str                    # Unique identifier (e.g., "edu_credit_101")
    title: str                 # Title of the content
    summary: str               # Brief summary
    body: str                  # Full text content
    cta: str                   # Call-to-action text
    source: str                # Source attribution
    relevance_score: float     # Computed relevance (0.0-1.0)
```

### Rationale

Provides explainable reasoning for content selection.

```python
class Rationale(BaseModel):
    persona_type: str          # Assigned persona
    confidence: float          # Confidence score (0.0-1.0)
    explanation: str           # Human-readable explanation
    key_signals: List[str]     # Triggered signal tags
```

## Relevance Scoring Algorithm

The `_calculate_relevance()` method scores content items:

1. **Base Score (0.5)**: Item's persona_tags include user's persona
2. **Signal Bonus (+0.1 each)**: Item's signal_tags match user's active signals
3. **Maximum Bonus (0.5)**: Cap on total signal bonus
4. **Final Cap (1.0)**: Overall score never exceeds 1.0

### Example Scoring

User with `high_utilization` persona and signals `["high_utilization_80", "interest_charges"]`:

- Content with `persona_tags: ["high_utilization"]` and `signal_tags: ["high_utilization_80", "interest_charges"]`
  - Base: 0.5 (persona match)
  - Bonus: 0.2 (2 signal matches × 0.1)
  - **Total: 0.7**

- Content with `persona_tags: ["high_utilization"]` and `signal_tags: ["high_utilization_50"]`
  - Base: 0.5 (persona match)
  - Bonus: 0.0 (no signal matches)
  - **Total: 0.5**

## Signal Tag Extraction

The generator extracts these signal tags from `BehaviorSignals`:

### Credit Signals
- `high_utilization_80` - Utilization ≥80%
- `high_utilization_50` - Utilization ≥50%
- `moderate_utilization_30` - Utilization ≥30%
- `interest_charges` - Has interest charges flag
- `overdue` - Has overdue flag

### Income Signals
- `variable_income` - Median pay gap >45 days
- `stable_income` - Stability = "stable"

### Subscription Signals
- `subscription_heavy` - Count ≥3

### Savings Signals
- `positive_savings` - Monthly inflow >0
- `low_emergency_fund` - Buffer <3 months

## Rationale Templates

Each persona has a custom explanation template with concrete data:

### High Utilization
```
"You've been identified as a High Utilization user because your credit card
utilization is {utilization}%, which is above the recommended 30% threshold.
You're currently using ${balance} of your ${limit} total credit limit..."
```

### Variable Income
```
"You've been identified as a Variable Income user because your income arrives
irregularly, with a median gap of {gap} days between payments..."
```

### Subscription Heavy
```
"You've been identified as a Subscription Heavy user because you have {count}
active recurring subscriptions totaling ${spend} per month..."
```

### Savings Builder
```
"You've been identified as a Savings Builder because you're making consistent
progress with {rate}% growth and ${inflow} monthly inflow..."
```

### Balanced
```
"You've been identified as a Balanced user, maintaining healthy financial habits
without critical issues. Specifically, {adaptive insights}..."
```

## Configuration

### Custom Catalog Path

```python
# Default: data/content_catalog.yaml relative to spendsense-backend/
generator = TemplateGenerator()

# Custom path
generator = TemplateGenerator(catalog_path="/custom/path/to/catalog.yaml")
```

### Adjusting Limit

```python
# Default: 3 items
education_items = await generator.generate_education(
    persona_type="high_utilization",
    signals=signals
)

# Custom limit
education_items = await generator.generate_education(
    persona_type="high_utilization",
    signals=signals,
    limit=5  # Return top 5 items
)
```

## Testing

Run the test suite:

```bash
python scripts/test_template_generator.py
```

Run the integration demo:

```bash
python scripts/demo_template_integration.py
```

## Error Handling

The generator raises clear errors for invalid inputs:

```python
# ValueError: Missing required parameters
await generator.generate_education(
    persona_type="",  # Empty string
    signals=None      # Missing signals
)

# FileNotFoundError: Catalog not found
generator = TemplateGenerator(catalog_path="/nonexistent/path.yaml")
```

## Future Enhancements

The abstract base class design enables future implementations:

1. **LLM-Based Generator**: Use GPT-4/Claude for dynamic content generation
2. **Hybrid Approach**: Template fallback when API unavailable
3. **A/B Testing**: Compare template vs LLM effectiveness
4. **Multi-Language**: Internationalization with locale-specific templates

Simply implement the `ContentGenerator` interface:

```python
class LLMGenerator(ContentGenerator):
    async def generate_education(self, persona_type, signals, limit=3):
        # Call OpenAI/Anthropic API
        pass

    async def generate_rationale(self, persona_type, confidence, signals):
        # Generate with LLM
        pass
```

## Dependencies

- `pydantic` - Data validation and serialization
- `pyyaml` - YAML catalog parsing
- `spendsense.services.features` - BehaviorSignals dataclass

## See Also

- [Content Catalog Structure](../data/content_catalog.yaml)
- [Persona Assignment Logic](../src/spendsense/services/personas.py)
- [Behavioral Signals](../src/spendsense/services/features.py)
