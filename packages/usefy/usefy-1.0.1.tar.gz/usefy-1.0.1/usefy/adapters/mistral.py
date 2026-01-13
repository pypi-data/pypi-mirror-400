"""
Mistral AI provider adapter implementation
"""

from typing import Any, Dict
from ..adapter import ProviderAdapter
from ..types import CostEstimate, ActualCost


class MistralAdapter(ProviderAdapter):
    """
    Mistral AI provider adapter.
    
    Uses OpenAI-compatible API format.
    """
    
    @property
    def provider_id(self) -> str:
        return "mistral"
    
    @property
    def provider_name(self) -> str:
        return "Mistral AI"
    
    def supports_preflight(self) -> bool:
        return True
    
    def supports_postflight(self) -> bool:
        return True
    
    def estimate_cost(self, request_metadata: Dict[str, Any]) -> CostEstimate:
        """Estimate cost using database pricing (fetched from model_pricing table)"""
        try:
            model = request_metadata.get("model", "mistral-small-latest")
            messages = request_metadata.get("messages", [])
            max_tokens = request_metadata.get("max_tokens", 1000)
            
            # Estimate input tokens (4 chars ≈ 1 token)
            input_text = ""
            for msg in messages:
                if isinstance(msg, dict):
                    input_text += msg.get("content", "") + " "
            
            estimated_input_tokens = len(input_text) / 4
            
            # TODO: Fetch pricing from database
            # For now, use approximate pricing
            input_price_per_1m = 0.25  # Default
            output_price_per_1m = 0.25
            
            input_cost = (estimated_input_tokens / 1_000_000) * input_price_per_1m
            output_cost = (max_tokens / 1_000_000) * output_price_per_1m
            total_cost = input_cost + output_cost
            
            return CostEstimate(
                estimated_cost=total_cost,
                confidence=0.65,
                metadata={
                    "model": model,
                    "estimated_input_tokens": int(estimated_input_tokens),
                    "estimated_output_tokens": max_tokens,
                }
            )
            
        except Exception as e:
            return CostEstimate(
                estimated_cost=0.0,
                confidence=0.0,
                metadata={"error": f"estimation_failed: {str(e)}"}
            )
    
    def extract_actual_cost(self, response_data: Dict[str, Any]) -> ActualCost:
        """Extract actual cost from Mistral response."""
        try:
            model = response_data.get("model", "mistral-small-latest")
            usage = response_data.get("usage", {})
            
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            # TODO: Fetch pricing from database
            input_price_per_1m = 0.25
            output_price_per_1m = 0.25
            
            input_cost = (prompt_tokens / 1_000_000) * input_price_per_1m
            output_cost = (completion_tokens / 1_000_000) * output_price_per_1m
            total_cost = input_cost + output_cost
            
            return ActualCost(
                actual_cost=total_cost,
                metadata={
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                }
            )
            
        except Exception as e:
            return ActualCost(
                actual_cost=0.0,
                metadata={"error": f"extraction_failed: {str(e)}"}
            )
