"""
Google AI (Gemini) provider adapter implementation
"""

from typing import Any, Dict
from ..adapter import ProviderAdapter
from ..types import CostEstimate, ActualCost


# Hardcoded Gemini pricing (per 1M tokens)
GEMINI_PRICING = {
    "gemini-1.5-pro": {"input_price": 1.25, "output_price": 5.00},
    "gemini-1.5-flash": {"input_price": 0.075, "output_price": 0.30},
    "gemini-2.5-flash": {"input_price": 0.075, "output_price": 0.30},  # Same as 1.5-flash
    "gemini-pro": {"input_price": 0.50, "output_price": 1.50},
}


class GoogleAIAdapter(ProviderAdapter):
    """
    Google AI (Gemini) provider adapter.
    
    Uses 4 chars/token heuristic for estimation (confidence: 0.65).
    Extracts actual tokens from response usage field.
    Uses hardcoded pricing for accurate pricing.
    """
    
    @property
    def provider_id(self) -> str:
        return "google"
    
    @property
    def provider_name(self) -> str:
        return "Google AI"
    
    def supports_preflight(self) -> bool:
        return True
    
    def supports_postflight(self) -> bool:
        return True
    
    def estimate_cost(self, request_metadata: Dict[str, Any]) -> CostEstimate:
        """
        Estimate cost using 4 chars/token heuristic.
        
        Expected metadata:
        - model: str
        - contents: list[dict] (with 'parts' field)
        - max_output_tokens: int (optional, default 1000)
        """
        try:
            model = request_metadata.get("model", "gemini-1.5-flash")
            # Strip "models/" prefix if present
            model = model.replace("models/", "")
            contents = request_metadata.get("contents", [])
            max_tokens = request_metadata.get("max_output_tokens", 1000)
            
            # Get pricing
            pricing = GEMINI_PRICING.get(model)
            if not pricing:
                # Unknown model, return zero with low confidence
                return CostEstimate(
                    estimated_cost=0.0,
                    confidence=0.0,
                    metadata={"error": f"unknown_model: {model}"}
                )
            
            # Estimate input tokens (4 chars ≈ 1 token)
            input_text = ""
            for content in contents:
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, dict):
                            text = part.get("text", "")
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
        Extract actual cost from Google AI response.
        
        Expected response_data:
        - model: str
        - usage_metadata: dict with prompt_token_count, candidates_token_count
        """
        try:
            model = response_data.get("model", "gemini-1.5-flash")
            # Strip "models/" prefix if present
            model = model.replace("models/", "")
            usage = response_data.get("usage_metadata", {})
            
            prompt_tokens = usage.get("prompt_token_count", 0)
            completion_tokens = usage.get("candidates_token_count", 0)
            
            # Get pricing
            pricing = GEMINI_PRICING.get(model)
            if not pricing:
                return ActualCost(
                    actual_cost=0.0,
                    metadata={"error": f"unknown_model: {model}"}
                )
            
            # Calculate actual cost using catalog pricing
            input_cost = (prompt_tokens / 1_000_000) * pricing["input_price"]
            output_cost = (completion_tokens / 1_000_000) * pricing["output_price"]
            total_cost = input_cost + output_cost
            
            return ActualCost(
                actual_cost=total_cost,
                metadata={
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
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
