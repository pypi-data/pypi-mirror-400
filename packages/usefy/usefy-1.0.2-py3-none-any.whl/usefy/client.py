"""
Main Usefy client with OpenAI wrapper
"""

import time
import uuid
from typing import Optional, Dict, Any, List
from openai import OpenAI
from openai.types.chat import ChatCompletion

from .api_client import UsefyAPIClient
from .adapters import OpenAIAdapter
from .types import Decision


class UsefyClient:
    """
    Usefy client that wraps provider SDKs.
    
    Usage:
        ug = UsefyClient(api_key="ug_xxx", project_id="proj_123")
        openai_client = ug.wrap_openai(OpenAI(api_key="sk-xxx"))
        
        # Use wrapped client normally
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    
    def __init__(
        self,
        api_key: str,
        project_id: str,
        base_url: str = "https://api.usefy.ai",
        timeout_ms: int = 50,
        user_id: Optional[str] = None,
        environment: Optional[str] = None,
    ):
        """
        Initialize Usefy client.
        
        Args:
            api_key: Usefy API key
            project_id: Project ID (required for scope)
            base_url: Usefy API base URL
            timeout_ms: Timeout for pre-flight checks (default 50ms)
            user_id: Optional user ID for user-level policies
            environment: Optional environment tag (e.g., "production")
        """
        self.api_client = UsefyAPIClient(
            api_key=api_key,
            base_url=base_url,
            timeout_ms=timeout_ms,
        )
        self.project_id = project_id
        self.user_id = user_id
        self.environment = environment
        self.adapter = OpenAIAdapter()
    
    
    def wrap_openai(self, openai_client: OpenAI) -> "WrappedOpenAIClient":
        """
        Wrap OpenAI client with Usefy hooks.
        
        Args:
            openai_client: Original OpenAI client
        
        Returns:
            Wrapped client with pre-flight and post-flight hooks
        """
        return WrappedOpenAIClient(
            openai_client=openai_client,
            Usefy_client=self,
        )
    
    def wrap_gemini(self, gemini_model):
        """
        Wrap Gemini model with Usefy hooks.
        
        Args:
            gemini_model: Original Gemini GenerativeModel
        
        Returns:
            Wrapped model with pre-flight and post-flight hooks
        """
        from .gemini_wrapper import WrappedGeminiModel
        return WrappedGeminiModel(
            gemini_model=gemini_model,
            Usefy_client=self,
        )
    
    def _get_scope_context(self) -> Dict[str, Any]:
        """Build scope context for API calls"""
        context = {"project_id": self.project_id}
        if self.user_id:
            context["user_id"] = self.user_id
        if self.environment:
            context["environment"] = self.environment
        return context


class WrappedOpenAIClient:
    """
    Wrapped OpenAI client with Usefy pre-flight and post-flight hooks.
    
    Delegates all calls to original client but intercepts chat.completions.create.
    """
    
    def __init__(self, openai_client: OpenAI, Usefy_client: UsefyClient):
        self._client = openai_client
        self._ug = Usefy_client
        
        # Wrap chat completions
        self.chat = ChatCompletionsWrapper(self._client.chat, self._ug)
    
    def __getattr__(self, name):
        """Delegate all other attributes to original client"""
        return getattr(self._client, name)


class ChatCompletionsWrapper:
    """Wrapper for chat.completions with Usefy hooks"""
    
    def __init__(self, chat_namespace, Usefy_client: UsefyClient):
        self._chat = chat_namespace
        self._ug = Usefy_client
        self.completions = CompletionsWrapper(chat_namespace.completions, Usefy_client)


class CompletionsWrapper:
    """Wrapper for chat.completions.create"""
    
    def __init__(self, completions_namespace, Usefy_client: UsefyClient):
        self._completions = completions_namespace
        self._ug = Usefy_client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ChatCompletion:
        """
        Create chat completion with Usefy hooks.
        
        Pre-flight: Check if request should be allowed
        Post-flight: Track actual cost
        """
        request_id = f"req_{uuid.uuid4().hex}"
        idempotency_key = f"idem_{uuid.uuid4().hex}"
        
        # Extract metadata for adapter (NO raw body)
        request_metadata = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        # Pre-flight: Estimate cost
        start_time = time.time()
        estimate = self._ug.adapter.estimate_cost(request_metadata)
        
        # Pre-flight: Check policy
        decision = self._ug.api_client.check(
            provider="openai",
            request={
                "endpoint": "/v1/chat/completions",
                "method": "POST",
                "metadata": {
                    "model": model,
                    "estimated_input_tokens": estimate.metadata.get("estimated_input_tokens", 0) if estimate.metadata else 0,
                    "max_tokens": kwargs.get("max_tokens", 1000),
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
                f"Usefy blocked request: {decision.reason or 'Budget exceeded'}"
            )
        
        # Make actual OpenAI request
        response = self._completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        # Post-flight: Extract actual cost
        actual = self._ug.adapter.extract_actual_cost({
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            }
        })
        
        # Post-flight: Track (fire-and-forget)
        self._ug.api_client.track(
            provider="openai",
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
        
        # Attach Usefy metadata to response (for debugging)
        response._Usefy = {
            "preflight_latency_ms": preflight_latency,
            "estimated_cost": estimate.estimated_cost,
            "actual_cost": actual.actual_cost,
            "confidence": estimate.confidence,
            "decision": decision.decision,
        }
        
        return response
    
    def __getattr__(self, name):
        """Delegate all other methods to original completions"""
        return getattr(self._completions, name)
