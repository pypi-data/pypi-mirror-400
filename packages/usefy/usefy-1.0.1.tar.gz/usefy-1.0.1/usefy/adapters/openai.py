"""
OpenAI provider adapter implementation
"""

from typing import Any, Dict
from ..adapter import ProviderAdapter
from ..types import CostEstimate, ActualCost


# Hardcoded OpenAI pricing (per 1M tokens)
OPENAI_PRICING = {
    "gpt-4": {"input_price": 30.00, "output_price": 60.00},
    "gpt-4-turbo": {"input_price": 10.00, "output_price": 30.00},
    "gpt-4-turbo-preview": {"input_price": 10.00, "output_price": 30.00},
    "gpt-3.5-turbo": {"input_price": 0.50, "output_price": 1.50},
    "gpt-3.5-turbo-16k": {"input_price": 3.00, "output_price": 4.00},
}


class OpenAIAdapter(ProviderAdapter):
    """
    OpenAI provider adapter.
    
    Uses 4 chars/token heuristic for estimation (confidence: 0.65).
    Extracts actual tokens from response usage field.
    Uses hardcoded pricing for accurate pricing.
    """
    
    @property
    def provider_id(self) -> str:
        return "openai"
    
    @property
    def provider_name(self) -> str:
        return "OpenAI"
    
    def supports_preflight(self) -> bool:
        return True
    
    def supports_postflight(self) -> bool:
        return True
    
    def estimate_cost(self, request_metadata: Dict[str, Any]) -> CostEstimate:
        """
        Estimate cost using 4 chars/token heuristic.
        
        Expected metadata:
        - model: str
        - messages: list[dict] (with 'content' field)
        - max_tokens: int (optional, default 1000)
        """
        try:
            model = request_metadata.get("model", "gpt-4")
            messages = request_metadata.get("messages", [])
            max_tokens = request_metadata.get("max_tokens", 1000)
            
            # Get pricing
            pricing = OPENAI_PRICING.get(model)
            if not pricing:
                # Unknown model, return zero with low confidence
                return CostEstimate(
                    estimated_cost=0.0,
                    confidence=0.0,
                    metadata={"error": f"unknown_model: {model}"}
                )
            
            # Estimate input tokens (4 chars ≈ 1 token)
            input_text = " ".join(
                msg.get("content", "") for msg in messages if isinstance(msg.get("content"), str)
            )
            estimated_input_tokens = len(input_text) / 4
            
            # Calculate costs using catalog pricing
            input_cost = (estimated_input_tokens / 1_000_000) * pricing["input_price"]
            output_cost = (max_tokens / 1_000_000) * pricing["output_price"]
            total_cost = input_cost + output_cost
            
            return CostEstimate(
                estimated_cost=total_cost,
                confidence=0.65,  # Heuristic-based, not exact tokenizer
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
        Extract actual cost from OpenAI response.
        
        Expected response_data:
        - model: str
        - usage: dict with prompt_tokens, completion_tokens
        """
        try:
            model = response_data.get("model", "gpt-4")
            usage = response_data.get("usage", {})
            
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            # Get pricing
            pricing = OPENAI_PRICING.get(model)
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
