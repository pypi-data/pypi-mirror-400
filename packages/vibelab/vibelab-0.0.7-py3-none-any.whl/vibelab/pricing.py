"""Pricing and token cost calculation utilities using LiteLLM's cost database."""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .harnesses.base import Harness

logger = logging.getLogger(__name__)

# LiteLLM model cost database - imported at module level for caching
try:
    from litellm import model_cost as _litellm_model_cost

    LITELLM_AVAILABLE = True
except ImportError:
    _litellm_model_cost = {}
    LITELLM_AVAILABLE = False
    logger.warning("litellm not installed, using harness-specific pricing only")


@dataclass
class PricingInfo:
    """Pricing information for a model."""

    input_price_per_1m: float  # Price per 1M input tokens in USD
    output_price_per_1m: float  # Price per 1M output tokens in USD
    cache_read_price_per_1m: float | None = None  # Price per 1M cached read tokens


def get_litellm_pricing(model: str, provider: str | None = None) -> PricingInfo | None:
    """
    Get pricing from LiteLLM's model cost database.

    LiteLLM maintains an extensive database of model pricing that is
    regularly updated. This is the preferred source for cost data.

    Args:
        model: Model identifier (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')
        provider: Optional provider identifier to help with lookup

    Returns:
        PricingInfo if found in LiteLLM database, None otherwise
    """
    if not LITELLM_AVAILABLE or not _litellm_model_cost:
        return None

    # Try exact match first
    cost_data = _litellm_model_cost.get(model)

    # Try with provider prefix if provided
    if not cost_data and provider:
        cost_data = _litellm_model_cost.get(f"{provider}/{model}")

    # Try with common prefixes if not found
    if not cost_data:
        # Try openai/ prefix for OpenAI models
        cost_data = _litellm_model_cost.get(f"openai/{model}")
    if not cost_data:
        # Try anthropic/ prefix for Anthropic models
        cost_data = _litellm_model_cost.get(f"anthropic/{model}")
    if not cost_data:
        # Try gemini/ prefix for Google models
        cost_data = _litellm_model_cost.get(f"gemini/{model}")
    if not cost_data:
        # Try vertex_ai/ prefix for Vertex AI models
        cost_data = _litellm_model_cost.get(f"vertex_ai/{model}")

    if not cost_data:
        return None

    # LiteLLM stores cost per token, convert to per 1M tokens
    input_cost_per_token = cost_data.get("input_cost_per_token", 0)
    output_cost_per_token = cost_data.get("output_cost_per_token", 0)
    cache_read_cost_per_token = cost_data.get("cache_read_input_token_cost")

    return PricingInfo(
        input_price_per_1m=input_cost_per_token * 1_000_000,
        output_price_per_1m=output_cost_per_token * 1_000_000,
        cache_read_price_per_1m=(
            cache_read_cost_per_token * 1_000_000 if cache_read_cost_per_token else None
        ),
    )


def get_pricing(
    model: str, harness: "Harness | None" = None, provider: str | None = None
) -> PricingInfo | None:
    """
    Get pricing for a model, preferring LiteLLM data with harness fallback.

    Args:
        model: Model identifier
        harness: Optional harness instance for fallback pricing
        provider: Optional provider identifier for harness fallback

    Returns:
        PricingInfo if available, None otherwise
    """
    # Try LiteLLM first (most comprehensive and up-to-date)
    pricing = get_litellm_pricing(model, provider)
    if pricing:
        return pricing

    # Fall back to harness-specific pricing if available
    # This is important for Cursor and OpenAI Codex which may not be in LiteLLM
    if harness and provider:
        harness_pricing = harness.get_pricing(provider, model)
        if harness_pricing:
            return PricingInfo(
                input_price_per_1m=harness_pricing.input_price_per_1m,
                output_price_per_1m=harness_pricing.output_price_per_1m,
            )

    return None


def calculate_cost(
    harness: "Harness",
    provider: str,
    model: str,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    total_tokens: int | None = None,
    cached_tokens: int | None = None,
) -> float | None:
    """
    Calculate cost in USD based on token usage.

    Uses LiteLLM's cost database as primary source, with harness-specific
    pricing as fallback.

    Args:
        harness: Harness instance (for fallback pricing)
        provider: Provider identifier
        model: Model identifier
        input_tokens: Number of input tokens (preferred)
        output_tokens: Number of output tokens (preferred)
        total_tokens: Total tokens if input/output breakdown not available
        cached_tokens: Number of cached input tokens (for prompt caching)

    Returns:
        Cost in USD, or None if pricing not available
    """
    pricing = get_pricing(model, harness, provider)
    if not pricing:
        return None

    # Prefer input/output breakdown
    if input_tokens is not None and output_tokens is not None:
        input_cost = (input_tokens / 1_000_000) * pricing.input_price_per_1m
        output_cost = (output_tokens / 1_000_000) * pricing.output_price_per_1m

        # Account for cached tokens if available
        if cached_tokens and pricing.cache_read_price_per_1m:
            # Cached tokens are charged at lower rate instead of full input rate
            cache_savings = (cached_tokens / 1_000_000) * (
                pricing.input_price_per_1m - pricing.cache_read_price_per_1m
            )
            input_cost -= cache_savings

        return input_cost + output_cost

    # Fallback to total tokens (assume 50/50 split for estimation)
    if total_tokens is not None:
        # Estimate: assume equal input/output split
        estimated_input = total_tokens / 2
        estimated_output = total_tokens / 2
        input_cost = (estimated_input / 1_000_000) * pricing.input_price_per_1m
        output_cost = (estimated_output / 1_000_000) * pricing.output_price_per_1m
        return input_cost + output_cost

    return None


def list_available_models(provider_filter: str | None = None) -> list[dict]:
    """
    List models with pricing available in LiteLLM.

    Args:
        provider_filter: Optional filter by provider (e.g., 'openai', 'anthropic', 'google')

    Returns:
        List of model info dicts with id, provider, and pricing
    """
    if not LITELLM_AVAILABLE:
        return []

    models = []
    for model_id, cost_data in _litellm_model_cost.items():
        litellm_provider = cost_data.get("litellm_provider", "")

        # Apply provider filter if specified
        if provider_filter:
            if provider_filter.lower() not in litellm_provider.lower():
                continue

        input_cost = cost_data.get("input_cost_per_token", 0)
        output_cost = cost_data.get("output_cost_per_token", 0)

        models.append(
            {
                "id": model_id,
                "provider": litellm_provider,
                "input_price_per_1m": input_cost * 1_000_000,
                "output_price_per_1m": output_cost * 1_000_000,
                "max_tokens": cost_data.get("max_tokens"),
                "max_input_tokens": cost_data.get("max_input_tokens"),
            }
        )

    return sorted(models, key=lambda x: x["id"])
