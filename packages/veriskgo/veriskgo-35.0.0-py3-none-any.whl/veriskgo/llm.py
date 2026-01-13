# veriskgo/llm.py
"""
Provider-agnostic LLM tracking decorator.
Automatically captures usage and cost from Bedrock observer.
"""

from __future__ import annotations

import re
import functools
import inspect
from typing import Any, Dict, Optional
from contextvars import ContextVar
import threading

from .core.usage import build_usage_payload, empty_usage_payload
from .core.decorators import create_span_wrapper, SpanContext


# ============================================================
# CONTEXT: Bedrock usage injected by observer
# ============================================================

_bedrock_usage_ctx: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "veriskgo_bedrock_usage",
    default=None,
)

# Thread-safe fallback storage for cross-thread async calls (LangChain)
_bedrock_usage_lock = threading.Lock()
_bedrock_usage_fallback: Optional[Dict[str, Any]] = None


def _set_bedrock_usage(payload: Dict[str, Any]):
    """Set bedrock usage from observer (called by bedrock_observe.py)."""
    global _bedrock_usage_fallback
    # Set in ContextVar (for same-thread sync calls)
    _bedrock_usage_ctx.set(payload)
    # Also set in fallback (for cross-thread async calls like LangChain)
    with _bedrock_usage_lock:
        _bedrock_usage_fallback = payload


def _get_bedrock_usage() -> Optional[Dict[str, Any]]:
    """Get bedrock usage captured by observer."""
    global _bedrock_usage_fallback
    # First try ContextVar (preferred for sync/same-thread)
    result = _bedrock_usage_ctx.get()
    if result:
        return result
    # Fallback to thread-safe storage (for LangChain async)
    with _bedrock_usage_lock:
        result = _bedrock_usage_fallback
        _bedrock_usage_fallback = None  # Clear after reading
        return result


def _clear_bedrock_usage():
    """Clear bedrock usage after reading."""
    global _bedrock_usage_fallback
    _bedrock_usage_ctx.set(None)
    with _bedrock_usage_lock:
        _bedrock_usage_fallback = None


# ============================================================
# LANGCHAIN CALLBACK EXTRACTION (Fallback)
# ============================================================

def _extract_langchain_usage_from_kwargs(kwargs: dict) -> Optional[Dict[str, Any]]:
    """
    Extract token + cost info from LangChain callback text.
    Used as fallback when Bedrock observer doesn't capture usage.
    """
    try:
        config = kwargs.get("config") or {}
        callbacks = config.get("callbacks") or []

        if not callbacks:
            return None

        text = "\n".join(str(c) for c in callbacks)

        def grab(pattern):
            m = re.search(pattern, text)
            return int(m.group(1)) if m else 0

        prompt = grab(r"Prompt Tokens:\s*(\d+)")
        completion = grab(r"Completion Tokens:\s*(\d+)")
        
        if prompt == 0 and completion == 0:
            return None
            
        return build_usage_payload(
            {"input_tokens": prompt, "output_tokens": completion},
            model_id=None  # Model unknown from callback
        )

    except Exception:
        return None


# ============================================================
# UNIVERSAL TEXT EXTRACTION
# ============================================================

def extract_text(resp: Any) -> str:
    """
    Extract text from various LLM response formats.
    Supports: Bedrock Converse, Bedrock InvokeModel, OpenAI, LangChain, etc.
    """
    if isinstance(resp, str):
        return resp

    if not isinstance(resp, dict):
        return str(resp)

    # Bedrock Converse API
    try:
        return resp["output"]["message"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        pass

    # Anthropic Messages API
    try:
        return resp["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        pass

    # Amazon Titan
    try:
        return resp["results"][0]["outputText"]
    except (KeyError, IndexError, TypeError):
        pass

    # Cohere
    try:
        return resp["generation"]
    except (KeyError, TypeError):
        pass

    # AI21
    try:
        return resp["outputs"][0]["text"]
    except (KeyError, IndexError, TypeError):
        pass

    # Generic text field
    try:
        return resp["text"]
    except (KeyError, TypeError):
        pass

    # OpenAI format
    try:
        return resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        pass

    return str(resp)


# ============================================================
# LLM USAGE FINALIZATION
# ============================================================

def _finalize_llm_span(
    ctx: SpanContext,
    result: Any,
    args: tuple,
    kwargs: dict,
) -> Dict[str, Any]:
    """
    Finalize LLM span with usage/cost data.
    Priority: Bedrock observer > LangChain callbacks > Empty
    """
    # 1. Try Bedrock observer (most accurate per-call)
    bedrock_payload = _get_bedrock_usage()
    if bedrock_payload:
        return bedrock_payload
    
    # 2. Fallback: LangChain aggregated usage (chain-level)
    lc_payload = _extract_langchain_usage_from_kwargs(kwargs)
    if lc_payload:
        return lc_payload
    
    # 3. Empty payload
    return empty_usage_payload()


# ============================================================
# DECORATOR: track_llm_call
# ============================================================

def track_llm_call(
    name: Optional[str] = None,
    *,
    tags: Optional[Dict[str, Any]] = None,
    capture_locals: bool = True,
    capture_self: bool = True,
):
    """
    Provider-agnostic LLM generation decorator.
    
    Automatically captures:
    - Token usage (input/output/total)
    - Cost (calculated from model pricing)
    - Model ID (from Bedrock observer)
    - Response text
    
    Usage:
        @track_llm_call()
        def call_llm(prompt):
            return bedrock.converse(...)
            
        @track_llm_call(name="summarize")
        async def summarize(text):
            return await chain.ainvoke(...)
    """
    def decorator(func):
        span_name = name or func.__name__
        
        return create_span_wrapper(
            func,
            span_name=span_name,
            span_type="generation",
            capture_locals=capture_locals,
            capture_self=capture_self,
            tags=tags,
            finalize_fn=_finalize_llm_span,
        )
    
    return decorator
