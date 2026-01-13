# veriskgo/core/__init__.py
"""
Core utilities for VeriskGO SDK.
Provides shared functionality for pricing, usage calculations, and decorator infrastructure.
"""

# These don't have circular import issues
from .pricing import get_pricing, calculate_cost, MODEL_PRICING
from .usage import UsageData, build_usage_payload, empty_usage_payload, CostData

# Lazy import for decorators to avoid circular imports
def create_span_wrapper(*args, **kwargs):
    """Lazy-loaded span wrapper creator."""
    from .decorators import create_span_wrapper as _create_span_wrapper
    return _create_span_wrapper(*args, **kwargs)


def SpanContext(*args, **kwargs):
    """Lazy-loaded SpanContext."""
    from .decorators import SpanContext as _SpanContext
    return _SpanContext(*args, **kwargs)


__all__ = [
    "get_pricing",
    "calculate_cost", 
    "MODEL_PRICING",
    "UsageData",
    "CostData",
    "build_usage_payload",
    "empty_usage_payload",
    "create_span_wrapper",
    "SpanContext",
]
