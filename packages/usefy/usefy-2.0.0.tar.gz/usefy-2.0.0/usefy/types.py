"""
Core types for UsageGuard SDK
"""

from typing import TypedDict, Literal, Optional, Dict, Any
from dataclasses import dataclass


# Decision types
DecisionType = Literal["allow", "block", "allow_with_warning"]


@dataclass
class CostEstimate:
    """Cost estimation result from pre-flight check"""
    estimated_cost: float  # USD
    confidence: float  # 0.0 - 1.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ActualCost:
    """Actual cost extracted from provider response"""
    actual_cost: float  # USD
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Decision:
    """Decision from UsageGuard API"""
    decision: DecisionType
    estimated_cost: float
    confidence: float
    remaining_budget: Optional[float] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProviderRequest(TypedDict, total=False):
    """Provider request metadata (NO raw body/headers)"""
    endpoint: str
    method: str
    metadata: Dict[str, Any]


class ProviderResponse(TypedDict, total=False):
    """Provider response metadata"""
    status_code: int
    actual_cost: float
    metadata: Dict[str, Any]
