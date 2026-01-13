"""
Google Vertex AI provider adapter implementation
"""

from typing import Any, Dict
from ..adapter import ProviderAdapter
from ..types import CostEstimate, ActualCost


class GoogleVertexAdapter(ProviderAdapter):
    """
    Google Vertex AI provider adapter.
    
    Note: Vertex AI uses service account authentication, not API keys.
    Uses Vertex AI pricing (may differ from Google AI Studio).
    """
    
    @property
    def provider_id(self) -> str:
        return "google_vertex"
    
    @property
    def provider_name(self) -> str:
        return "Google Vertex AI"
    
    def supports_preflight(self) -> bool:
        return True
    
    def supports_postflight(self) -> bool:
        return True
    
    def estimate_cost(self, request_metadata: Dict[str, Any]) -> CostEstimate:
        try:
            model = request_metadata.get("model", "gemini-1.5-pro")
            contents = request_metadata.get("contents", [])
            max_tokens = request_metadata.get("max_output_tokens", 1000)
            
            # Estimate input tokens
            input_text = ""
            for content in contents:
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, dict):
                            input_text += part.get("text", "") + " "
            
            estimated_input_tokens = len(input_text) / 4
            
            # Vertex AI pricing (per 1M tokens)
            input_price_per_1m = 1.25
            output_price_per_1m = 5.00
            
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
            model = response_data.get("model", "gemini-1.5-pro")
            usage = response_data.get("usage_metadata", {})
            
            prompt_tokens = usage.get("prompt_token_count", 0)
            completion_tokens = usage.get("candidates_token_count", 0)
            
            input_price_per_1m = 1.25
            output_price_per_1m = 5.00
            
            total_cost = (prompt_tokens / 1_000_000) * input_price_per_1m + (completion_tokens / 1_000_000) * output_price_per_1m
            
            return ActualCost(
                actual_cost=total_cost,
                metadata={"model": model, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}
            )
        except Exception as e:
            return ActualCost(actual_cost=0.0, metadata={"error": str(e)})
