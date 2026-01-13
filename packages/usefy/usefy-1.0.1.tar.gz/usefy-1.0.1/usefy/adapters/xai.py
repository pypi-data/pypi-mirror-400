"""
xAI (Grok) provider adapter implementation
"""

from typing import Any, Dict
from ..adapter import ProviderAdapter
from ..types import CostEstimate, ActualCost


class XAIAdapter(ProviderAdapter):
    """xAI (Grok) provider adapter - uses OpenAI-compatible API format."""
    
    @property
    def provider_id(self) -> str:
        return "xai"
    
    @property
    def provider_name(self) -> str:
        return "xAI (Grok)"
    
    def supports_preflight(self) -> bool:
        return True
    
    def supports_postflight(self) -> bool:
        return True
    
    def estimate_cost(self, request_metadata: Dict[str, Any]) -> CostEstimate:
        try:
            model = request_metadata.get("model", "grok-2")
            messages = request_metadata.get("messages", [])
            max_tokens = request_metadata.get("max_tokens", 1000)
            
            input_text = ""
            for msg in messages:
                if isinstance(msg, dict):
                    input_text += msg.get("content", "") + " "
            
            estimated_input_tokens = len(input_text) / 4
            input_price_per_1m = 2.00
            output_price_per_1m = 10.00
            
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
            model = response_data.get("model", "grok-2")
            usage = response_data.get("usage", {})
            
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            input_price_per_1m = 2.00
            output_price_per_1m = 10.00
            
            total_cost = (prompt_tokens / 1_000_000) * input_price_per_1m + (completion_tokens / 1_000_000) * output_price_per_1m
            
            return ActualCost(
                actual_cost=total_cost,
                metadata={"model": model, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}
            )
        except Exception as e:
            return ActualCost(actual_cost=0.0, metadata={"error": str(e)})
