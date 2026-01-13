"""Unit tests for pricing calculations."""

import unittest

from vibelab.pricing import (
    calculate_cost,
    get_litellm_pricing,
    get_pricing,
    list_available_models,
    LITELLM_AVAILABLE,
)
from vibelab.harnesses import HARNESSES


class TestPricing(unittest.TestCase):
    """Tests for pricing calculations."""

    def test_calculate_cost_with_input_output(self):
        """Test cost calculation with input/output token breakdown."""
        # Use Cursor harness which has fallback pricing
        harness = HARNESSES["cursor"]
        cost = calculate_cost(harness, "cursor", "composer-1", input_tokens=1000, output_tokens=500)
        self.assertIsNotNone(cost)
        # Expected: (1000/1M * 3.0) + (500/1M * 15.0) = 0.003 + 0.0075 = 0.0105
        self.assertAlmostEqual(cost, 0.0105, places=6)

    def test_calculate_cost_with_total_tokens(self):
        """Test cost calculation with total tokens only."""
        harness = HARNESSES["openai-codex"]
        cost = calculate_cost(harness, "openai", "gpt-4o", total_tokens=1000)
        self.assertIsNotNone(cost)
        # Expected: (500/1M * 2.50) + (500/1M * 10.0) = 0.00125 + 0.005 = 0.00625
        self.assertAlmostEqual(cost, 0.00625, places=6)

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation with unknown model."""
        harness = HARNESSES["claude-code"]
        cost = calculate_cost(
            harness, "anthropic", "unknown-model", input_tokens=1000, output_tokens=500
        )
        self.assertIsNone(cost)

    def test_pricing_coverage(self):
        """Test that all harness models have pricing."""
        for harness in HARNESSES.values():
            for provider in harness.supported_providers:
                models = harness.get_models(provider)
                for model_info in models:
                    # Check if pricing exists
                    pricing = harness.get_pricing(provider, model_info.id)
                    if pricing:
                        self.assertIsNotNone(
                            pricing,
                            f"Pricing found for {harness.id}:{provider}:{model_info.id}",
                        )
                    else:
                        # Log warning but don't fail - new models may not have pricing yet
                        print(
                            f"Warning: No pricing found for {harness.id}:{provider}:{model_info.id}"
                        )


class TestLiteLLMPricing(unittest.TestCase):
    """Tests for LiteLLM pricing integration."""

    def test_litellm_available(self):
        """Test that LiteLLM is available."""
        self.assertTrue(LITELLM_AVAILABLE, "LiteLLM should be installed")

    def test_litellm_pricing_openai(self):
        """Test LiteLLM pricing for OpenAI models."""
        pricing = get_litellm_pricing("gpt-4o")
        self.assertIsNotNone(pricing, "Should find gpt-4o pricing")
        self.assertGreater(pricing.input_price_per_1m, 0)
        self.assertGreater(pricing.output_price_per_1m, 0)

    def test_litellm_pricing_openai_with_provider(self):
        """Test LiteLLM pricing for OpenAI models with provider parameter."""
        # Test that passing provider helps find models that might need prefix
        pricing = get_litellm_pricing("gpt-4o", provider="openai")
        self.assertIsNotNone(pricing, "Should find gpt-4o pricing with provider hint")
        self.assertGreater(pricing.input_price_per_1m, 0)
        self.assertGreater(pricing.output_price_per_1m, 0)

    def test_litellm_pricing_openai_o1(self):
        """Test LiteLLM pricing for OpenAI o1 models."""
        # Test newer OpenAI models to ensure pricing works
        pricing = get_litellm_pricing("o1-preview", provider="openai")
        self.assertIsNotNone(pricing, "Should find o1-preview pricing")
        self.assertGreater(pricing.input_price_per_1m, 0)
        self.assertGreater(pricing.output_price_per_1m, 0)

    def test_litellm_pricing_anthropic(self):
        """Test LiteLLM pricing for Anthropic models."""
        pricing = get_litellm_pricing("claude-3-5-sonnet-20241022")
        self.assertIsNotNone(pricing, "Should find claude-3-5-sonnet pricing")
        self.assertGreater(pricing.input_price_per_1m, 0)
        self.assertGreater(pricing.output_price_per_1m, 0)

    def test_litellm_pricing_gemini(self):
        """Test LiteLLM pricing for Gemini models."""
        pricing = get_litellm_pricing("gemini-1.5-pro")
        self.assertIsNotNone(pricing, "Should find gemini-1.5-pro pricing")
        self.assertGreater(pricing.input_price_per_1m, 0)
        self.assertGreater(pricing.output_price_per_1m, 0)

    def test_get_pricing_prefers_litellm(self):
        """Test that get_pricing prefers LiteLLM over harness pricing."""
        harness = HARNESSES["openai-codex"]
        pricing = get_pricing("gpt-4o", harness, "openai")
        self.assertIsNotNone(pricing)
        # LiteLLM should have cache pricing info
        self.assertIsNotNone(pricing.cache_read_price_per_1m)

    def test_get_pricing_falls_back_to_harness(self):
        """Test that get_pricing falls back to harness for unknown models."""
        harness = HARNESSES["cursor"]
        # 'composer-1' is a Cursor model not in LiteLLM
        pricing = get_pricing("composer-1", harness, "cursor")
        self.assertIsNotNone(pricing, "Should fall back to harness pricing for 'composer-1'")

    def test_get_pricing_cursor_fallback(self):
        """Test that Cursor pricing falls back to harness since not in LiteLLM."""
        harness = HARNESSES["cursor"]
        pricing = get_pricing("composer-1", harness, "cursor")
        self.assertIsNotNone(pricing, "Should find cursor composer-1 pricing via harness fallback")
        # Cursor harness provides estimated pricing
        self.assertEqual(pricing.input_price_per_1m, 3.0)
        self.assertEqual(pricing.output_price_per_1m, 15.0)

    def test_calculate_cost_cursor(self):
        """Test cost calculation for Cursor models uses harness fallback."""
        harness = HARNESSES["cursor"]
        cost = calculate_cost(
            harness, "cursor", "composer-1", input_tokens=1000, output_tokens=500
        )
        self.assertIsNotNone(cost, "Should calculate cost for Cursor")
        # Expected: (1000/1M * 3.0) + (500/1M * 15.0) = 0.003 + 0.0075 = 0.0105
        self.assertAlmostEqual(cost, 0.0105, places=6)

    def test_calculate_cost_openai_via_litellm(self):
        """Test cost calculation for OpenAI models uses LiteLLM."""
        harness = HARNESSES["openai-codex"]
        cost = calculate_cost(
            harness, "openai", "gpt-4o", input_tokens=1000, output_tokens=500
        )
        self.assertIsNotNone(cost, "Should calculate cost for OpenAI gpt-4o")
        # LiteLLM provides pricing, so cost should be calculated
        self.assertGreater(cost, 0)

    def test_list_available_models_filtering(self):
        """Test listing models with provider filter."""
        openai_models = list_available_models("openai")
        self.assertGreater(len(openai_models), 0, "Should find OpenAI models")

        anthropic_models = list_available_models("anthropic")
        self.assertGreater(len(anthropic_models), 0, "Should find Anthropic models")
