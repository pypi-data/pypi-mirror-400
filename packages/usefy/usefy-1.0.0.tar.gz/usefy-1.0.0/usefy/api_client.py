"""
Usefy API client for pre-flight and post-flight requests
"""

import time
import uuid
import requests
from typing import Optional, Dict, Any
from .types import Decision, ProviderRequest, ProviderResponse


class UsefyAPIClient:
    """
    Client for Usefy API endpoints.
    
    Implements fail-open behavior:
    - Timeout → allow request
    - Error → allow request
    - API down → allow request
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.Usefy.dev",
        timeout_ms: int = 50,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_ms / 1000  # Convert to seconds
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        })
    
    def check(
        self,
        provider: str,
        request: ProviderRequest,
        scope_context: Dict[str, Any],
        request_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Decision:
        """
        Pre-flight check: Should this request be allowed?
        
        Args:
            provider: Provider ID (e.g., "openai")
            request: Provider request metadata
            scope_context: Context (project_id, user_id, etc.)
            request_id: Optional request ID (generated if not provided)
            idempotency_key: Optional idempotency key
        
        Returns:
            Decision object
            
        FAIL-OPEN: Returns allow decision on any error/timeout.
        """
        request_id = request_id or f"req_{uuid.uuid4().hex}"
        idempotency_key = idempotency_key or f"idem_{uuid.uuid4().hex}"
        
        payload = {
            "request_id": request_id,
            "idempotency_key": idempotency_key,
            "timestamp": int(time.time() * 1000),
            "scope_context": scope_context,
            "provider": provider,
            "request": request,
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/check",
                json=payload,
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                data = response.json()
                return Decision(
                    decision=data["decision"],
                    estimated_cost=data.get("estimated_cost", 0.0),
                    confidence=data.get("confidence", 0.0),
                    remaining_budget=data.get("remaining_budget"),
                    reason=data.get("reason"),
                    metadata=data.get("metadata"),
                )
            else:
                # API error → fail-open
                return self._fail_open_decision(f"api_error: {response.status_code}")
                
        except requests.Timeout:
            # Timeout → fail-open
            return self._fail_open_decision("timeout")
        
        except Exception as e:
            # Any error → fail-open
            return self._fail_open_decision(f"error: {str(e)}")
    
    def track(
        self,
        provider: str,
        response: ProviderResponse,
        scope_context: Dict[str, Any],
        request_id: str,
        idempotency_key: str,
        estimated_cost: Optional[float] = None,
    ) -> bool:
        """
        Post-flight tracking: Report actual cost.
        
        Args:
            provider: Provider ID
            response: Provider response metadata
            scope_context: Context (same as pre-flight)
            request_id: Request ID from pre-flight
            idempotency_key: Idempotency key from pre-flight
            estimated_cost: Optional estimated cost for variance tracking
        
        Returns:
            True if tracked successfully, False otherwise
            
        FIRE-AND-FORGET: Errors are logged but don't affect caller.
        """
        payload = {
            "request_id": request_id,
            "idempotency_key": idempotency_key,
            "timestamp": int(time.time() * 1000),
            "scope_context": scope_context,
            "provider": provider,
            "response": response,
        }
        
        if estimated_cost is not None:
            payload["estimated_cost"] = estimated_cost
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/track",
                json=payload,
                timeout=self.timeout * 2,  # More lenient for async tracking
            )
            return response.status_code == 200
            
        except Exception:
            # Fire-and-forget: log error but don't raise
            # TODO: Add structured logging
            return False
    
    def _fail_open_decision(self, reason: str) -> Decision:
        """Return allow decision for fail-open behavior"""
        return Decision(
            decision="allow",
            estimated_cost=0.0,
            confidence=0.0,
            metadata={"fail_open": True, "reason": reason},
        )
