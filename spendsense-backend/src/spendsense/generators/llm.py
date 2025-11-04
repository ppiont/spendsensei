"""LLM-powered content generator (stub implementation).

This module provides a stub interface for future LLM integration. It implements
the same ContentGenerator interface as TemplateGenerator, allowing seamless
swapping between template-based and AI-generated content.

IMPLEMENTATION STATUS: Stub only - no actual LLM calls are made yet.

FUTURE INTEGRATION:
    To add LLM functionality:
    1. Install provider SDK: pip install anthropic  OR  pip install openai
    2. Add API key to environment: ANTHROPIC_API_KEY or OPENAI_API_KEY
    3. Initialize client in __init__ (see comments below)
    4. Implement generate_education() with structured output
    5. Implement generate_rationale() with guardrails
    6. Add prompt templates (see PROMPT_TEMPLATES section)
    7. Configure structured output schemas
    8. Add Guardrails AI integration for validation

SWAPPING INSTRUCTIONS:
    To swap from TemplateGenerator to LLMGenerator in production:
    
    Before:
        from spendsense.generators.template import TemplateGenerator
        generator = TemplateGenerator(catalog_path="content_catalog.yaml")
    
    After:
        from spendsense.generators.llm import LLMGenerator
        generator = LLMGenerator(provider="anthropic", model="claude-3-5-sonnet-20241022")
    
    The interface remains identical - no other code changes required.
"""

from typing import List, Dict, Any, Literal
from spendsense.generators.base import ContentGenerator, EducationItem, Rationale


# ==============================================================================
# PROMPT TEMPLATES (Placeholder)
# ==============================================================================
# When implementing LLM integration, define prompt templates here.
# Use template strings with {variable} placeholders for dynamic content.

EDUCATION_PROMPT_TEMPLATE = """
You are a financial advisor generating personalized educational content.

User Context:
- Persona: {persona}
- Active Signals: {active_signals}
- Signal Data: {signal_data}

Generate {limit} educational items that are:
1. Actionable and specific to the user's situation
2. Prioritized by relevance to their current signals
3. Appropriate for their persona's financial sophistication

Return structured output matching EducationItem schema.
"""

RATIONALE_PROMPT_TEMPLATE = """
You are explaining a financial recommendation to a user.

User Context:
- Persona: {persona}
- Recommendation Type: {recommendation_type}
- Signal Data: {signal_data}

Generate a rationale that:
1. Summarizes the recommendation in one sentence
2. Provides 2-3 paragraphs of detailed reasoning
3. Includes concrete data points from the signal data
4. Is appropriate for the user's financial literacy level

Return structured output matching Rationale schema.
"""


class LLMGenerator(ContentGenerator):
    """LLM-powered content generator (stub implementation).
    
    This class provides a future-ready interface for LLM-based content generation.
    It implements the same interface as TemplateGenerator, allowing seamless swapping.
    
    Attributes:
        provider: LLM provider ("anthropic" or "openai")
        model: Model identifier (e.g., "claude-3-5-sonnet-20241022" or "gpt-4")
        
    Example:
        >>> # Future usage (not yet implemented):
        >>> generator = LLMGenerator(provider="anthropic", model="claude-3-5-sonnet-20241022")
        >>> education = generator.generate_education(
        ...     persona="paycheck_to_paycheck",
        ...     active_signals=["high_subscription_spending"],
        ...     signal_data={"subscription_spending_ratio": 0.15}
        ... )
    """
    
    def __init__(
        self,
        provider: Literal["anthropic", "openai"] = "anthropic",
        model: str = "claude-3-5-sonnet-20241022"
    ):
        """Initialize LLM generator (stub).
        
        Args:
            provider: LLM provider to use ("anthropic" or "openai")
            model: Model identifier for the chosen provider
            
        Raises:
            NotImplementedError: Always raised - LLM integration not yet implemented
            
        FUTURE IMPLEMENTATION:
            # For Anthropic:
            import anthropic
            import os
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            # For OpenAI:
            import openai
            import os
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Store configuration
            self.provider = provider
            self.model = model
            
            # Optional: Initialize Guardrails for validation
            # import guardrails as gd
            # self.guard = gd.Guard.from_pydantic(...)
        """
        self.provider = provider
        self.model = model
        
        # ==================================================================
        # TODO: Initialize LLM client here when implementing
        # ==================================================================
        # Uncomment and complete based on chosen provider:
        #
        # if provider == "anthropic":
        #     import anthropic
        #     import os
        #     self.client = anthropic.Anthropic(
        #         api_key=os.getenv("ANTHROPIC_API_KEY")
        #     )
        # elif provider == "openai":
        #     import openai
        #     import os
        #     self.client = openai.OpenAI(
        #         api_key=os.getenv("OPENAI_API_KEY")
        #     )
        # else:
        #     raise ValueError(f"Unsupported provider: {provider}")
        
        raise NotImplementedError("LLM generator not yet implemented")
    
    def generate_education(
        self,
        persona: str,
        active_signals: List[str],
        signal_data: Dict[str, Any],
        limit: int = 3
    ) -> List[EducationItem]:
        """Generate educational content using LLM (stub).
        
        Args:
            persona: User's assigned persona (e.g., "paycheck_to_paycheck")
            active_signals: List of triggered signal names
            signal_data: Dictionary of signal values and metadata
            limit: Maximum number of items to return
            
        Returns:
            List of EducationItem objects, sorted by relevance
            
        Raises:
            NotImplementedError: Always raised - LLM integration not yet implemented
            
        FUTURE IMPLEMENTATION STEPS:
            1. Format prompt using EDUCATION_PROMPT_TEMPLATE
            2. Call LLM API with structured output schema
            3. Parse response into EducationItem objects
            4. Validate with Guardrails (optional)
            5. Sort by relevance_score
            6. Return top N items (limit)
            
        STRUCTURED OUTPUT EXAMPLE (Anthropic):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                tools=[{
                    "name": "generate_education",
                    "description": "Generate educational items",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": EducationItem.model_json_schema()
                            }
                        }
                    }
                }]
            )
            
        GUARDRAILS INTEGRATION EXAMPLE:
            from guardrails import Guard
            guard = Guard.from_pydantic(EducationItem)
            validated_items = [
                guard.parse(item)
                for item in raw_items
            ]
        """
        raise NotImplementedError("LLM generator not yet implemented")
    
    def generate_rationale(
        self,
        recommendation_type: str,
        persona: str,
        signal_data: Dict[str, Any]
    ) -> Rationale:
        """Generate recommendation rationale using LLM (stub).
        
        Args:
            recommendation_type: Type of recommendation being made
            persona: User's assigned persona
            signal_data: Dictionary of signal values that triggered the recommendation
            
        Returns:
            Rationale object with summary, reasoning, and confidence
            
        Raises:
            NotImplementedError: Always raised - LLM integration not yet implemented
            
        FUTURE IMPLEMENTATION STEPS:
            1. Format prompt using RATIONALE_PROMPT_TEMPLATE
            2. Call LLM API with structured output schema
            3. Parse response into Rationale object
            4. Validate with Guardrails (check for hallucinations)
            5. Verify all data_points reference actual signal_data
            6. Return validated Rationale
            
        STRUCTURED OUTPUT EXAMPLE (OpenAI):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "rationale",
                        "schema": Rationale.model_json_schema()
                    }
                }
            )
            
        GUARDRAILS VALIDATION EXAMPLE:
            # Check for data point accuracy
            guard = Guard.from_string(
                validators=[
                    ValidRange(min=0, max=1, on_fail="fix"),  # confidence
                    ValidChoices(choices=list(signal_data.keys()), on_fail="fix")  # data_points
                ]
            )
            validated_rationale = guard.parse(rationale)
            
        IMPORTANT CONSIDERATIONS:
            - Ensure all numeric data points match signal_data exactly
            - Check that reasoning references concrete values, not hallucinated data
            - Validate confidence score is realistic based on signal strength
            - Consider adding citation tracking to map statements to source data
        """
        raise NotImplementedError("LLM generator not yet implemented")


# ==============================================================================
# INTEGRATION CHECKLIST
# ==============================================================================
"""
Before deploying LLM integration to production, verify:

1. API Keys and Authentication:
   [ ] API key is stored securely (environment variable, secrets manager)
   [ ] Key has appropriate rate limits and quotas configured
   [ ] Error handling for authentication failures

2. Structured Output Implementation:
   [ ] LLM provider supports structured output (Anthropic tools, OpenAI JSON mode)
   [ ] Pydantic schemas are properly converted to JSON schemas
   [ ] Response parsing handles all edge cases

3. Guardrails Integration:
   [ ] Guardrails validators are configured for EducationItem
   [ ] Guardrails validators are configured for Rationale
   [ ] Data point validation checks against source signal_data
   [ ] Hallucination detection is enabled
   [ ] On-fail strategies are appropriate (fix, reask, exception)

4. Testing:
   [ ] Unit tests with mock LLM responses
   [ ] Integration tests with real API calls (in test environment)
   [ ] Synthetic user data tests
   [ ] Edge case handling (empty signals, extreme values, etc.)
   [ ] Cost analysis and rate limiting tests

5. Monitoring:
   [ ] Log all LLM API calls with request/response metadata
   [ ] Track token usage and costs
   [ ] Monitor response quality metrics
   [ ] Alert on validation failures or high error rates

6. Swapping Process:
   [ ] Feature flag to enable/disable LLM generator
   [ ] Gradual rollout strategy (A/B test, percentage rollout)
   [ ] Rollback plan if quality degrades
   [ ] Side-by-side comparison with TemplateGenerator

7. Cost Management:
   [ ] Set per-user rate limits
   [ ] Cache common responses
   [ ] Implement request batching where appropriate
   [ ] Monitor and alert on unexpected cost spikes
"""
