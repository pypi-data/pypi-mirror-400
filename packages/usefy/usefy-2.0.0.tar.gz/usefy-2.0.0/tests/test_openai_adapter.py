"""
Tests for OpenAI adapter
"""

import pytest
from usageguard.adapters import OpenAIAdapter


def test_adapter_properties():
    """Test adapter metadata"""
    adapter = OpenAIAdapter()
    assert adapter.provider_id == "openai"
    assert adapter.provider_name == "OpenAI"
    assert adapter.supports_preflight() is True
    assert adapter.supports_postflight() is True


def test_estimate_cost_gpt4():
    """Test cost estimation for GPT-4"""
    adapter = OpenAIAdapter()
    
    request_metadata = {
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Hello world"}  # ~2 words, ~8 chars, ~2 tokens
        ],
        "max_tokens": 100,
    }
    
    estimate = adapter.estimate_cost(request_metadata)
    
    assert estimate.estimated_cost > 0
    assert estimate.confidence == 0.65
    assert estimate.metadata["model"] == "gpt-4"
    assert estimate.metadata["estimated_input_tokens"] > 0
    assert estimate.metadata["estimated_output_tokens"] == 100


def test_estimate_cost_unknown_model():
    """Test estimation with unknown model"""
    adapter = OpenAIAdapter()
    
    request_metadata = {
        "model": "gpt-99-ultra",
        "messages": [{"role": "user", "content": "Test"}],
    }
    
    estimate = adapter.estimate_cost(request_metadata)
    
    assert estimate.estimated_cost == 0.0
    assert estimate.confidence == 0.0
    assert "error" in estimate.metadata
    assert "unknown_model" in estimate.metadata["error"]


def test_extract_actual_cost():
    """Test actual cost extraction"""
    adapter = OpenAIAdapter()
    
    response_data = {
        "model": "gpt-4",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 50,
        }
    }
    
    actual = adapter.extract_actual_cost(response_data)
    
    assert actual.actual_cost > 0
    assert actual.metadata["model"] == "gpt-4"
    assert actual.metadata["prompt_tokens"] == 10
    assert actual.metadata["completion_tokens"] == 50


def test_extract_actual_cost_missing_usage():
    """Test extraction with missing usage data"""
    adapter = OpenAIAdapter()
    
    response_data = {
        "model": "gpt-4",
        # No usage field
    }
    
    actual = adapter.extract_actual_cost(response_data)
    
    # Should still work, just with 0 tokens
    assert actual.actual_cost == 0.0
    assert actual.metadata["prompt_tokens"] == 0
    assert actual.metadata["completion_tokens"] == 0


def test_never_raises_exception():
    """Test that adapter never raises exceptions"""
    adapter = OpenAIAdapter()
    
    # Malformed request
    estimate = adapter.estimate_cost({"invalid": "data"})
    assert estimate.estimated_cost == 0.0
    assert estimate.confidence == 0.0
    
    # Malformed response
    actual = adapter.extract_actual_cost({"invalid": "data"})
    assert actual.actual_cost == 0.0


def test_cost_calculation_accuracy():
    """Test that cost calculation matches expected pricing"""
    adapter = OpenAIAdapter()
    
    # GPT-4: $30/1M input tokens, $60/1M output tokens
    response_data = {
        "model": "gpt-4",
        "usage": {
            "prompt_tokens": 1000,
            "completion_tokens": 1000,
        }
    }
    
    actual = adapter.extract_actual_cost(response_data)
    
    # Expected: (1000/1M * $30) + (1000/1M * $60) = $0.03 + $0.06 = $0.09
    expected_cost = 0.09
    assert abs(actual.actual_cost - expected_cost) < 0.0001
