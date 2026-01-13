"""Dynamic model registry using LiteLLM's model cost database.

This module provides utilities for fetching available models dynamically,
ensuring harnesses and the judge picker always have up-to-date model lists.
"""

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import LiteLLM
try:
    from litellm import model_cost as _litellm_model_cost

    LITELLM_AVAILABLE = True
except ImportError:
    _litellm_model_cost = {}
    LITELLM_AVAILABLE = False
    logger.warning("litellm not installed, using fallback model lists")


@dataclass
class ModelInfo:
    """Model information."""

    id: str
    name: str
    input_price_per_1m: float | None = None
    output_price_per_1m: float | None = None


def _is_versioned_model(model_id: str) -> bool:
    """Check if a model ID has a version date (YYYY-MM-DD or YYYYMMDD format)."""
    # Match YYYY-MM-DD (OpenAI) or YYYYMMDD (Anthropic)
    return bool(re.search(r"20[0-9]{2}-?[0-9]{2}-?[0-9]{2}", model_id))


def _format_model_name(model_id: str) -> str:
    """Format a model ID into a friendly display name."""
    # Remove date suffixes for display (both YYYY-MM-DD and YYYYMMDD)
    name = re.sub(r"-20[0-9]{2}-[0-9]{2}-[0-9]{2}$", "", model_id)
    name = re.sub(r"-20[0-9]{6}$", "", name)

    # Handle specific model families
    if name.startswith("gpt-"):
        # GPT models: gpt-5.2 -> GPT-5.2, gpt-4o-mini -> GPT-4o Mini
        name = name.replace("gpt-", "GPT-")
        # Keep version numbers together (5.2, 4.1, etc.)
        name = re.sub(r"GPT-(\d+)\.(\d+)", r"GPT-\1.\2", name)
        # Format suffixes
        name = name.replace("-mini", " Mini")
        name = name.replace("-nano", " Nano")
        name = name.replace("-pro", " Pro")
        name = name.replace("-turbo", " Turbo")
        return name

    if name.startswith("o1") or name.startswith("o3") or name.startswith("o4"):
        # o-series: o1-mini -> o1 Mini
        name = name.replace("-mini", " Mini")
        name = name.replace("-pro", " Pro")
        name = name.replace("-preview", " Preview")
        return name

    if name.startswith("claude-"):
        # Claude models: claude-sonnet-4 -> Claude Sonnet 4
        name = name.replace("claude-", "Claude ")
        # Handle version patterns like "3-5" -> "3.5"
        name = re.sub(r"(\d)-(\d)", r"\1.\2", name)
        name = name.replace("-", " ")
        # Title case the tier names
        name = re.sub(r"(opus|sonnet|haiku)", lambda m: m.group(1).title(), name, flags=re.I)
        # Clean up extra spaces
        name = " ".join(name.split())
        return name

    if name.startswith("gemini-"):
        # Gemini models: gemini-2.0-flash -> Gemini 2.0 Flash
        name = name.replace("gemini-", "Gemini ")
        # Keep version numbers together
        name = re.sub(r"(\d+)\.(\d+)", r"\1.\2", name)
        name = name.replace("-", " ")
        # Title case suffixes
        parts = name.split()
        parts = [
            p.title() if p.lower() in ("flash", "pro", "lite", "ultra", "thinking", "exp") else p
            for p in parts
        ]
        return " ".join(parts)

    # Generic fallback
    name = name.replace("-", " ").title()
    return name


def get_openai_models() -> list[ModelInfo]:
    """Get available OpenAI models from LiteLLM, preferring versioned models."""
    if not LITELLM_AVAILABLE:
        # Fallback to basic list
        return [
            ModelInfo(id="gpt-4o", name="GPT-4o"),
            ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini"),
            ModelInfo(id="o1", name="o1"),
        ]

    models = []
    seen_base_names: set[str] = set()

    for model_id, cost_data in _litellm_model_cost.items():
        # Skip prefixed models (azure/, etc.)
        if "/" in model_id:
            continue

        # Check if it's an OpenAI model
        provider = cost_data.get("litellm_provider", "")
        is_openai = (
            "openai" in provider.lower()
            or model_id.startswith("gpt-")
            or model_id.startswith("o1")
            or model_id.startswith("o3")
            or model_id.startswith("o4")
        )
        if not is_openai:
            continue

        # Only include versioned models for reproducibility
        if not _is_versioned_model(model_id):
            continue

        # Skip non-chat models
        mode = cost_data.get("mode", "")
        if mode and mode not in ("chat", ""):
            continue

        # Skip embedding, moderation, tts, whisper models
        if any(
            x in model_id.lower()
            for x in [
                "embedding",
                "moderation",
                "tts",
                "whisper",
                "realtime",
                "audio",
                "transcribe",
                "image",
                "search",
            ]
        ):
            continue

        # Get pricing
        input_cost = cost_data.get("input_cost_per_token", 0) * 1_000_000
        output_cost = cost_data.get("output_cost_per_token", 0) * 1_000_000

        # Skip models without pricing
        if input_cost == 0 and output_cost == 0:
            continue

        # Track base name to avoid duplicates (keep newest version)
        base_name = re.sub(r"-20[0-9]{2}-[0-9]{2}-[0-9]{2}$", "", model_id)
        if base_name in seen_base_names:
            continue
        seen_base_names.add(base_name)

        models.append(
            ModelInfo(
                id=model_id,
                name=_format_model_name(model_id),
                input_price_per_1m=round(input_cost, 4),
                output_price_per_1m=round(output_cost, 4),
            )
        )

    # Sort by name (GPT-5 > GPT-4, etc.)
    models.sort(key=lambda m: m.name, reverse=True)
    return models


def get_anthropic_models() -> list[ModelInfo]:
    """Get available Anthropic models from LiteLLM, preferring versioned models."""
    if not LITELLM_AVAILABLE:
        return [
            ModelInfo(id="claude-sonnet-4-20250514", name="Claude Sonnet 4"),
            ModelInfo(id="claude-opus-4-20250514", name="Claude Opus 4"),
        ]

    models = []
    seen_normalized: set[str] = set()

    for model_id, cost_data in _litellm_model_cost.items():
        # Skip prefixed models
        if "/" in model_id:
            continue

        # Check if it's an Anthropic model
        provider = cost_data.get("litellm_provider", "")
        is_anthropic = "anthropic" in provider.lower() or model_id.startswith("claude")
        if not is_anthropic:
            continue

        # Only include versioned models (YYYYMMDD format)
        if not _is_versioned_model(model_id):
            continue

        # Skip models with weird suffixes
        if ":0" in model_id or "v1:" in model_id:
            continue

        # Get pricing
        input_cost = cost_data.get("input_cost_per_token", 0) * 1_000_000
        output_cost = cost_data.get("output_cost_per_token", 0) * 1_000_000

        if input_cost == 0 and output_cost == 0:
            continue

        # Normalize the base name to handle different orderings
        # e.g., "claude-sonnet-4" and "claude-4-sonnet" -> same key
        base_name = re.sub(r"-20[0-9]{6}$", "", model_id)
        # Extract tier and version
        tier_match = re.search(r"(opus|sonnet|haiku)", base_name, re.I)
        version_match = re.search(r"(\d+(?:\.\d+)?)", base_name.replace("claude-", ""))
        if tier_match and version_match:
            normalized = f"claude-{tier_match.group(1).lower()}-{version_match.group(1)}"
        else:
            normalized = base_name

        if normalized in seen_normalized:
            continue
        seen_normalized.add(normalized)

        models.append(
            ModelInfo(
                id=model_id,
                name=_format_model_name(model_id),
                input_price_per_1m=round(input_cost, 4),
                output_price_per_1m=round(output_cost, 4),
            )
        )

    # Sort: Opus > Sonnet > Haiku, newer versions first
    def sort_key(m: ModelInfo) -> tuple[int, str]:
        if "opus" in m.id.lower():
            tier = 0
        elif "sonnet" in m.id.lower():
            tier = 1
        elif "haiku" in m.id.lower():
            tier = 2
        else:
            tier = 3
        # Sort by version number descending
        version_match = re.search(r"(\d+)", m.id.replace("claude-", ""))
        version = int(version_match.group(1)) if version_match else 0
        return (tier, -version, m.id)

    models.sort(key=sort_key)
    return models


def get_gemini_models() -> list[ModelInfo]:
    """Get available Gemini models from LiteLLM, preferring versioned models."""
    if not LITELLM_AVAILABLE:
        return [
            ModelInfo(id="gemini-2.0-flash-001", name="Gemini 2.0 Flash"),
            ModelInfo(id="gemini-1.5-pro-002", name="Gemini 1.5 Pro"),
        ]

    models = []
    seen_base_names: set[str] = set()

    for model_id, cost_data in _litellm_model_cost.items():
        # Skip prefixed models
        if "/" in model_id:
            continue

        # Check if it's a Gemini model
        if not model_id.startswith("gemini"):
            continue

        # Prefer versioned models (-001, -002, or date-based)
        is_versioned = bool(re.search(r"-00[0-9]$", model_id)) or _is_versioned_model(model_id)
        if not is_versioned:
            continue

        # Skip experimental/preview models without version numbers
        if "exp" in model_id and not re.search(r"-[0-9]{2}-[0-9]{2}$", model_id):
            continue

        # Skip non-chat models
        if any(x in model_id.lower() for x in ["embedding", "image", "live", "vision"]):
            continue

        # Get pricing
        input_cost = cost_data.get("input_cost_per_token", 0) * 1_000_000
        output_cost = cost_data.get("output_cost_per_token", 0) * 1_000_000

        if input_cost == 0 and output_cost == 0:
            continue

        # Track base name
        base_name = re.sub(r"-00[0-9]$", "", model_id)
        base_name = re.sub(r"-[0-9]{2}-[0-9]{2}$", "", base_name)
        if base_name in seen_base_names:
            continue
        seen_base_names.add(base_name)

        name = _format_model_name(model_id)
        # Clean up Gemini names
        name = re.sub(r" 00[0-9]$", "", name)

        models.append(
            ModelInfo(
                id=model_id,
                name=name,
                input_price_per_1m=round(input_cost, 4),
                output_price_per_1m=round(output_cost, 4),
            )
        )

    # Sort by version (2.5 > 2.0 > 1.5)
    models.sort(key=lambda m: m.id, reverse=True)
    return models
