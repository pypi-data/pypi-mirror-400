"""
Anthropic (Claude) provider adapter implementation
"""

from typing import Any, Dict
from ..adapter import ProviderAdapter
from ..types import CostEstimate, ActualCost


# Hardcoded Anthropic pricing (per 1M tokens)
# Source: https://www.anthropic.com/pricing (as of 2024)
ANTHROPIC_PRICING = {
    "claude-3-5-sonnet-20241022": {"input_price": 3.00, "output_price": 15.00},
    "claude-3-5-sonnet-20240620": {"input_price": 3.00, "output_price": 15.00},
    "claude-3-opus-20240229": {"input_price": 15.00, "output_price": 75.00},
    "claude-3-sonnet-20240229": {"input_price": 3.00, "output_price": 15.00},
    "claude-3-haiku-20240307": {"input_price": 0.25, "output_price": 1.25},
    # Aliases
    "claude-3-5-sonnet": {"input_price": 3.00, "output_price": 15.00},
    "claude-3-opus": {"input_price": 15.00, "output_price": 75.00},
    "claude-3-sonnet": {"input_price": 3.00, "output_price": 15.00},
    "claude-3-haiku": {"input_price": 0.25, "output_price": 1.25},
}


class AnthropicAdapter(ProviderAdapter):
    """
    Anthropic (Claude) provider adapter.
    
    Uses 4 chars/token heuristic for estimation (confidence: 0.65).
    Extracts actual tokens from response usage field.
    Uses hardcoded pricing for accurate cost calculation.
    """
    
    @property
    def provider_id(self) -> str:
        return "anthropic"
    
    @property
    def provider_name(self) -> str:
        return "Anthropic"
    
    def supports_preflight(self) -> bool:
        return True
    
    def supports_postflight(self) -> bool:
        return True
    
    def estimate_cost(self, request_metadata: Dict[str, Any]) -> CostEstimate:
        """
        Estimate cost using 4 chars/token heuristic.
        
        Expected metadata:
        - model: str
        - messages: list[dict] (with 'role' and 'content' fields)
        - max_tokens: int (optional, default 1000)
        """
        try:
            model = request_metadata.get("model", "claude-3-5-sonnet-20241022")
            messages = request_metadata.get("messages", [])
            max_tokens = request_metadata.get("max_tokens", 1000)
            
            # Get pricing
            pricing = ANTHROPIC_PRICING.get(model)
            if not pricing:
                # Unknown model, return zero with low confidence
                return CostEstimate(
                    estimated_cost=0.0,
                    confidence=0.0,
                    metadata={"error": f"unknown_model: {model}"}
                )
            
            # Estimate input tokens (4 chars ≈ 1 token)
            input_text = ""
            for message in messages:
                if isinstance(message, dict):
                    content = message.get("content", "")
                    if isinstance(content, str):
                        input_text += content + " "
                    elif isinstance(content, list):
                        # Handle content blocks
                        for block in content:
                            if isinstance(block, dict):
                                text = block.get("text", "")
                                input_text += text + " "
            
            estimated_input_tokens = len(input_text) / 4
            
            # Calculate costs using catalog pricing
            input_cost = (estimated_input_tokens / 1_000_000) * pricing["input_price"]
            output_cost = (max_tokens / 1_000_000) * pricing["output_price"]
            total_cost = input_cost + output_cost
            
            return CostEstimate(
                estimated_cost=total_cost,
                confidence=0.65,  # Heuristic-based
                metadata={
                    "model": model,
                    "estimated_input_tokens": int(estimated_input_tokens),
                    "estimated_output_tokens": max_tokens,
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                }
            )
            
        except Exception as e:
            # NEVER raise - fail-open principle
            return CostEstimate(
                estimated_cost=0.0,
                confidence=0.0,
                metadata={"error": f"estimation_failed: {str(e)}"}
            )
    
    def extract_actual_cost(self, response_data: Dict[str, Any]) -> ActualCost:
        """
        Extract actual cost from Anthropic response.
        
        Expected response_data:
        - model: str
        - usage: dict with input_tokens, output_tokens
        """
        try:
            model = response_data.get("model", "claude-3-5-sonnet-20241022")
            usage = response_data.get("usage", {})
            
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            
            # Get pricing
            pricing = ANTHROPIC_PRICING.get(model)
            if not pricing:
                return ActualCost(
                    actual_cost=0.0,
                    metadata={"error": f"unknown_model: {model}"}
                )
            
            # Calculate actual cost using catalog pricing
            input_cost = (input_tokens / 1_000_000) * pricing["input_price"]
            output_cost = (output_tokens / 1_000_000) * pricing["output_price"]
            total_cost = input_cost + output_cost
            
            return ActualCost(
                actual_cost=total_cost,
                metadata={
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                }
            )
            
        except Exception as e:
            # NEVER raise - fail-open principle
            return ActualCost(
                actual_cost=0.0,
                metadata={"error": f"extraction_failed: {str(e)}"}
            )
