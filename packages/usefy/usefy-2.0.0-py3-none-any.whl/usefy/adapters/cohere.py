"""
Cohere provider adapter implementation
"""

from typing import Any, Dict
from ..adapter import ProviderAdapter
from ..types import CostEstimate, ActualCost


class CohereAdapter(ProviderAdapter):
    """Cohere provider adapter."""
    
    @property
    def provider_id(self) -> str:
        return "cohere"
    
    @property
    def provider_name(self) -> str:
        return "Cohere"
    
    def supports_preflight(self) -> bool:
        return True
    
    def supports_postflight(self) -> bool:
        return True
    
    def estimate_cost(self, request_metadata: Dict[str, Any]) -> CostEstimate:
        try:
            model = request_metadata.get("model", "command")
            message = request_metadata.get("message", "")
            max_tokens = request_metadata.get("max_tokens", 1000)
            
            estimated_input_tokens = len(message) / 4
            input_price_per_1m = 0.50
            output_price_per_1m = 1.50
            
            input_cost = (estimated_input_tokens / 1_000_000) * input_price_per_1m
            output_cost = (max_tokens / 1_000_000) * output_price_per_1m
            
            return CostEstimate(
                estimated_cost=input_cost + output_cost,
                confidence=0.65,
                metadata={"model": model, "estimated_input_tokens": int(estimated_input_tokens)}
            )
        except Exception as e:
            return CostEstimate(estimated_cost=0.0, confidence=0.0, metadata={"error": str(e)})
    
    def extract_actual_cost(self, response_data: Dict[str, Any]) -> ActualCost:
        try:
            model = response_data.get("model", "command")
            meta = response_data.get("meta", {})
            billed_units = meta.get("billed_units", {})
            
            input_tokens = billed_units.get("input_tokens", 0)
            output_tokens = billed_units.get("output_tokens", 0)
            
            input_price_per_1m = 0.50
            output_price_per_1m = 1.50
            
            total_cost = (input_tokens / 1_000_000) * input_price_per_1m + (output_tokens / 1_000_000) * output_price_per_1m
            
            return ActualCost(
                actual_cost=total_cost,
                metadata={"model": model, "input_tokens": input_tokens, "output_tokens": output_tokens}
            )
        except Exception as e:
            return ActualCost(actual_cost=0.0, metadata={"error": str(e)})
