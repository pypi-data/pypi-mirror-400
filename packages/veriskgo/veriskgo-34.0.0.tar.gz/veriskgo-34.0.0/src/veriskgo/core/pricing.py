# veriskgo/core/pricing.py
"""
Centralized model pricing registry.
Supports multiple providers and models with fallback to default pricing.
"""

from typing import Dict, Optional

# ============================================================
# MODEL PRICING REGISTRY
# Extensible: Add new models here as needed
# Prices are per token in USD
# ============================================================

MODEL_PRICING: Dict[str, Dict[str, float]] = {
    # Anthropic Claude 3 Family (Bedrock)
    "anthropic.claude-3-sonnet": {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
    "anthropic.claude-3-haiku": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000},
    "anthropic.claude-3-opus": {"input": 15.0 / 1_000_000, "output": 75.0 / 1_000_000},
    "anthropic.claude-3-5-sonnet": {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
    
    # Meta Llama Family (Bedrock) - Pricing TBD
    "meta.llama3-8b": {"input": 0.3 / 1_000_000, "output": 0.6 / 1_000_000},
    "meta.llama3-70b": {"input": 2.65 / 1_000_000, "output": 3.5 / 1_000_000},
    "meta.llama3-1-8b": {"input": 0.22 / 1_000_000, "output": 0.22 / 1_000_000},
    "meta.llama3-1-70b": {"input": 0.99 / 1_000_000, "output": 0.99 / 1_000_000},
    
    # Amazon Titan Family
    "amazon.titan-text-express": {"input": 0.2 / 1_000_000, "output": 0.6 / 1_000_000},
    "amazon.titan-text-lite": {"input": 0.15 / 1_000_000, "output": 0.2 / 1_000_000},
    
    # Cohere Family
    "cohere.command-r": {"input": 0.5 / 1_000_000, "output": 1.5 / 1_000_000},
    "cohere.command-r-plus": {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
    
    # AI21 Labs
    "ai21.jamba-instruct": {"input": 0.5 / 1_000_000, "output": 0.7 / 1_000_000},
    
    # Mistral
    "mistral.mistral-7b": {"input": 0.15 / 1_000_000, "output": 0.2 / 1_000_000},
    "mistral.mixtral-8x7b": {"input": 0.45 / 1_000_000, "output": 0.7 / 1_000_000},
    
    # Default fallback (Claude 3 Sonnet pricing)
    "default": {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
}


def get_pricing(model_id: Optional[str]) -> Dict[str, float]:
    """
    Get pricing for a model ID.
    
    Args:
        model_id: Full model ID (e.g., 'anthropic.claude-3-sonnet-20240229-v1:0')
        
    Returns:
        Dict with 'input' and 'output' prices per token
    """
    if not model_id:
        return MODEL_PRICING["default"]
    
    # Try exact match first
    if model_id in MODEL_PRICING:
        return MODEL_PRICING[model_id]
    
    # Try prefix matching (handles version suffixes)
    model_lower = model_id.lower()
    for key in MODEL_PRICING:
        if key != "default" and model_lower.startswith(key):
            return MODEL_PRICING[key]
    
    # Try partial matching for provider prefixes
    for key in MODEL_PRICING:
        if key != "default" and key in model_lower:
            return MODEL_PRICING[key]
    
    return MODEL_PRICING["default"]


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model_id: Optional[str] = None,
) -> Dict[str, float]:
    """
    Calculate cost from token counts and model.
    
    Args:
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens
        model_id: Optional model ID for pricing lookup
        
    Returns:
        Dict with 'input', 'output', and 'total' costs
    """
    pricing = get_pricing(model_id)
    
    input_cost = round(input_tokens * pricing["input"], 6)
    output_cost = round(output_tokens * pricing["output"], 6)
    total_cost = round(input_cost + output_cost, 6)
    
    return {
        "input": input_cost,
        "output": output_cost,
        "total": total_cost,
    }


def calculate_cost_from_usage(
    usage: Dict[str, int],
    model_id: Optional[str] = None,
) -> Dict[str, float]:
    """
    Calculate cost from a usage dict.
    
    Args:
        usage: Dict with 'input_tokens' or 'input', and 'output_tokens' or 'output'
        model_id: Optional model ID for pricing lookup
        
    Returns:
        Dict with 'input', 'output', and 'total' costs
    """
    input_tokens = usage.get("input_tokens") or usage.get("input", 0)
    output_tokens = usage.get("output_tokens") or usage.get("output", 0)
    
    return calculate_cost(input_tokens, output_tokens, model_id)
