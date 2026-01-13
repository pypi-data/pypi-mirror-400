# veriskgo/core/usage.py
"""
Unified usage and cost data structures.
Provides consistent formatting for Langfuse, New Relic, and S3.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from .pricing import calculate_cost


@dataclass
class UsageData:
    """
    Unified usage data structure.
    Supports both token-based and generic naming conventions.
    """
    input_tokens: int = 0
    output_tokens: int = 0
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    def to_details(self) -> Dict[str, int]:
        """
        Returns Langfuse-compatible format.
        Keys: input, output, total
        """
        return {
            "input": self.input_tokens,
            "output": self.output_tokens,
            "total": self.total_tokens,
        }
    
    def to_tokens(self) -> Dict[str, int]:
        """
        Returns token-based format.
        Keys: input_tokens, output_tokens, total_tokens
        """
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageData":
        """
        Create UsageData from various dict formats.
        Handles: input_tokens/output_tokens, input/output, prompt_tokens/completion_tokens
        """
        input_tokens = (
            data.get("input_tokens") or 
            data.get("input") or 
            data.get("prompt_tokens") or 
            0
        )
        output_tokens = (
            data.get("output_tokens") or 
            data.get("output") or 
            data.get("completion_tokens") or 
            0
        )
        return cls(input_tokens=input_tokens, output_tokens=output_tokens)


@dataclass
class CostData:
    """
    Unified cost data structure.
    """
    input_cost: float = 0.0
    output_cost: float = 0.0
    
    @property
    def total_cost(self) -> float:
        return round(self.input_cost + self.output_cost, 6)
    
    def to_details(self) -> Dict[str, float]:
        """
        Returns Langfuse-compatible format.
        Keys: input, output, total
        """
        return {
            "input": self.input_cost,
            "output": self.output_cost,
            "total": self.total_cost,
        }
    
    def to_cost(self) -> Dict[str, float]:
        """
        Returns cost-based format.
        Keys: input_cost, output_cost, total_cost
        """
        return {
            "input_cost": self.input_cost,
            "output_cost": self.output_cost,
            "total_cost": self.total_cost,
        }


def build_usage_payload(
    usage: Dict[str, int],
    model_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build complete usage + cost payload for span events.
    
    Args:
        usage: Dict with token counts (various formats supported)
        model_id: Optional model ID for pricing lookup
        
    Returns:
        Dict with model, usage_details, usage, cost_details, cost
    """
    usage_data = UsageData.from_dict(usage)
    cost_dict = calculate_cost(usage_data.input_tokens, usage_data.output_tokens, model_id)
    cost_data = CostData(input_cost=cost_dict["input"], output_cost=cost_dict["output"])
    
    return {
        "model": model_id,
        "usage_details": usage_data.to_details(),
        "usage": usage_data.to_tokens(),
        "cost_details": cost_data.to_details(),
        "cost": cost_data.to_cost(),
    }


def empty_usage_payload(model_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Build empty usage payload with zero values.
    """
    return {
        "model": model_id,
        "usage_details": {"input": 0, "output": 0, "total": 0},
        "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "cost_details": {"input": 0.0, "output": 0.0, "total": 0.0},
        "cost": {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0},
    }
