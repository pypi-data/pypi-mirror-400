"""
Gemini wrapper implementation for UsageGuard
"""

import time
import uuid
from typing import Any, Dict, List, Optional


class WrappedGeminiModel:
    """
    Wrapped Gemini model with UsageGuard hooks.
    
    Intercepts generate_content() calls for pre-flight and post-flight tracking.
    """
    
    def __init__(self, gemini_model, usageguard_client):
        self._model = gemini_model
        self._ug = usageguard_client
    
    def generate_content(
        self,
        contents: Any,
        **kwargs
    ):
        """
        Generate content with UsageGuard hooks.
        
        Pre-flight: Check if request should be allowed
        Post-flight: Track actual cost
        """
        request_id = f"req_{uuid.uuid4().hex}"
        idempotency_key = f"idem_{uuid.uuid4().hex}"
        
        # Extract metadata for adapter
        # Convert contents to list if it's a string
        if isinstance(contents, str):
            contents_list = [{"parts": [{"text": contents}]}]
        else:
            contents_list = contents if isinstance(contents, list) else [contents]
        
        request_metadata = {
            "model": self._model.model_name,
            "contents": contents_list,
            "max_output_tokens": kwargs.get("max_output_tokens", 1000),
        }
        
        # Pre-flight: Estimate cost
        start_time = time.time()
        from usageguard.adapters import GoogleAIAdapter
        adapter = GoogleAIAdapter()
        estimate = adapter.estimate_cost(request_metadata)
        
        # Pre-flight: Check policy
        decision = self._ug.api_client.check(
            provider="google",
            request={
                "endpoint": "/v1/models/generate",
                "method": "POST",
                "metadata": {
                    "model": self._model.model_name,
                    "estimated_input_tokens": estimate.metadata.get("estimated_input_tokens", 0) if estimate.metadata else 0,
                    "max_output_tokens": kwargs.get("max_output_tokens", 1000),
                },
            },
            scope_context=self._ug._get_scope_context(),
            request_id=request_id,
            idempotency_key=idempotency_key,
        )
        
        preflight_latency = (time.time() - start_time) * 1000  # ms
        
        # Block if policy says so
        if decision.decision == "block":
            raise RuntimeError(
                f"UsageGuard blocked request: {decision.reason or 'Budget exceeded'}"
            )
        
        # Make actual Gemini request
        response = self._model.generate_content(
            contents,
            **kwargs
        )
        
        # Post-flight: Extract actual cost
        actual = adapter.extract_actual_cost({
            "model": self._model.model_name,
            "usage_metadata": {
                "prompt_token_count": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                "candidates_token_count": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
            }
        })
        
        # Post-flight: Track (fire-and-forget)
        self._ug.api_client.track(
            provider="google",
            response={
                "status_code": 200,
                "actual_cost": actual.actual_cost,
                "metadata": actual.metadata or {},
            },
            scope_context=self._ug._get_scope_context(),
            request_id=request_id,
            idempotency_key=idempotency_key,
            estimated_cost=estimate.estimated_cost,
        )
        
        # Attach UsageGuard metadata to response (for debugging)
        response._usageguard = {
            "preflight_latency_ms": preflight_latency,
            "estimated_cost": estimate.estimated_cost,
            "actual_cost": actual.actual_cost,
            "confidence": estimate.confidence,
            "decision": decision.decision,
        }
        
        return response
    
    def __getattr__(self, name):
        """Delegate all other methods to original model"""
        return getattr(self._model, name)
