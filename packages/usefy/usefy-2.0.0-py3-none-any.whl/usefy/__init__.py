"""
Usefy SDK - Thin wrapper for AI providers via Usefy proxy

Usage:
    from usefy import OpenAI, Anthropic
    
    # Just use your Usefy API key - provider keys are stored in Integrations
    client = OpenAI(api_key="us_live_xxx")
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
"""

__version__ = "2.0.0"

# Base URL for Usefy proxy
USEFY_PROXY_BASE = "https://api.usefy.ai/v1/proxy"


def _get_proxy_url(provider: str) -> str:
    """Get proxy URL for a provider."""
    return f"{USEFY_PROXY_BASE}/{provider}"


# ============================================================================
# OpenAI Wrapper
# ============================================================================
try:
    from openai import OpenAI as _OpenAI
    
    class OpenAI(_OpenAI):
        """
        OpenAI client that routes through Usefy proxy.
        
        Your OpenAI API key should be added in Usefy Dashboard → Integrations.
        Use your Usefy API key (us_live_xxx) here.
        
        Example:
            from usefy import OpenAI
            
            client = OpenAI(api_key="us_live_xxx")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello!"}]
            )
        """
        def __init__(self, api_key: str, **kwargs):
            # Remove base_url if provided, we override it
            kwargs.pop("base_url", None)
            
            super().__init__(
                api_key=api_key,
                base_url=_get_proxy_url("openai"),
                default_headers={
                    "X-API-Key": api_key,  # Usefy auth header
                    **(kwargs.pop("default_headers", {}) or {})
                },
                **kwargs
            )
    
    __all__ = ["OpenAI"]
    
except ImportError:
    # openai package not installed
    OpenAI = None


# ============================================================================
# Anthropic Wrapper
# ============================================================================
try:
    from anthropic import Anthropic as _Anthropic
    
    class Anthropic(_Anthropic):
        """
        Anthropic client that routes through Usefy proxy.
        
        Your Anthropic API key should be added in Usefy Dashboard → Integrations.
        Use your Usefy API key (us_live_xxx) here.
        
        Example:
            from usefy import Anthropic
            
            client = Anthropic(api_key="us_live_xxx")
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": "Hello!"}]
            )
        """
        def __init__(self, api_key: str, **kwargs):
            kwargs.pop("base_url", None)
            
            super().__init__(
                api_key=api_key,
                base_url=_get_proxy_url("anthropic"),
                default_headers={
                    "X-API-Key": api_key,
                    **(kwargs.pop("default_headers", {}) or {})
                },
                **kwargs
            )
    
    if "Anthropic" not in dir():
        __all__.append("Anthropic")
    
except ImportError:
    Anthropic = None


# ============================================================================
# Mistral Wrapper
# ============================================================================
try:
    from mistralai.client import MistralClient as _MistralClient
    
    class Mistral(_MistralClient):
        """
        Mistral client that routes through Usefy proxy.
        """
        def __init__(self, api_key: str, **kwargs):
            super().__init__(
                api_key=api_key,
                endpoint=_get_proxy_url("mistral"),
                **kwargs
            )
    
    if "__all__" in dir():
        __all__.append("Mistral")
    
except ImportError:
    Mistral = None


# ============================================================================
# Cohere Wrapper
# ============================================================================
try:
    import cohere as _cohere
    
    class Cohere(_cohere.Client):
        """
        Cohere client that routes through Usefy proxy.
        """
        def __init__(self, api_key: str, **kwargs):
            super().__init__(
                api_key=api_key,
                base_url=_get_proxy_url("cohere"),
                **kwargs
            )
    
    if "__all__" in dir():
        __all__.append("Cohere")
    
except ImportError:
    Cohere = None


# ============================================================================
# Generic HTTP Client for other providers
# ============================================================================
import httpx

class UsefyClient:
    """
    Generic Usefy client for making proxy requests to any provider.
    
    Example:
        from usefy import UsefyClient
        
        client = UsefyClient(api_key="us_live_xxx")
        response = client.post("openai/chat/completions", json={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello!"}]
        })
    """
    def __init__(self, api_key: str, timeout: int = 120):
        self.api_key = api_key
        self.base_url = USEFY_PROXY_BASE
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            },
            timeout=timeout
        )
    
    def post(self, path: str, **kwargs):
        """Make a POST request to the proxy."""
        return self._client.post(f"/{path}", **kwargs)
    
    def get(self, path: str, **kwargs):
        """Make a GET request to the proxy."""
        return self._client.get(f"/{path}", **kwargs)
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


# Add to exports
if "__all__" not in dir():
    __all__ = []
__all__.append("UsefyClient")
__all__.append("__version__")
