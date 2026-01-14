"""
Base adapter interface for provider integrations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from .types import CostEstimate, ActualCost


class ProviderAdapter(ABC):
    """
    Base interface for all provider adapters.
    
    CRITICAL: Adapters NEVER throw exceptions.
    All errors return cost=0, confidence=0 with error metadata.
    """
    
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Provider identifier (e.g., 'openai', 'anthropic')"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name"""
        pass
    
    @abstractmethod
    def supports_preflight(self) -> bool:
        """Can estimate cost before request?"""
        pass
    
    @abstractmethod
    def supports_postflight(self) -> bool:
        """Can extract actual cost after response?"""
        pass
    
    @abstractmethod
    def estimate_cost(self, request_metadata: Dict[str, Any]) -> CostEstimate:
        """
        Estimate cost before request is sent.
        
        Args:
            request_metadata: Extracted metadata (NO raw body/headers)
        
        Returns:
            CostEstimate with estimated_cost, confidence, metadata
            
        NEVER raises exceptions. Returns cost=0, confidence=0 on error.
        """
        pass
    
    @abstractmethod
    def extract_actual_cost(self, response_data: Dict[str, Any]) -> ActualCost:
        """
        Extract actual cost from provider response.
        
        Args:
            response_data: Provider response data
        
        Returns:
            ActualCost with actual_cost, metadata
            
        NEVER raises exceptions. Returns cost=0 on error.
        """
        pass
