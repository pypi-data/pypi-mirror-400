# veriskgo/bedrock_observe.py
"""
Boto3 Bedrock API observer.
Intercepts bedrock-runtime API calls to capture usage data automatically.
"""

import json
import io
import wrapt
from botocore.response import StreamingBody
from typing import Optional, Dict, Any

from .llm import _set_bedrock_usage
from .core.usage import build_usage_payload

# ============================================================
# CONFIGURATION
# ============================================================

# Set to True to enable debug logging
DEBUG_MODE = False


def _debug_log(message: str):
    """Log debug message if debug mode is enabled."""
    if DEBUG_MODE:
        print(f"[BedrockObserver] {message}")


# ============================================================
# OPERATION HANDLERS
# ============================================================

def _handle_invoke_model(response: Dict, model_id: Optional[str]) -> None:
    """Handle InvokeModel API response (non-streaming)."""
    if "body" not in response:
        return
    
    raw = response["body"].read()
    data = json.loads(raw)
    
    _debug_log(f"InvokeModel response keys: {data.keys()}")
    
    usage = data.get("usage")
    if usage:
        _debug_log(f"Found usage: {usage}")
        payload = build_usage_payload(usage, model_id)
        _set_bedrock_usage(payload)
    else:
        _debug_log("No 'usage' found in response")
    
    # Restore body for downstream consumers
    response["body"] = StreamingBody(io.BytesIO(raw), len(raw))


def _handle_invoke_model_stream(response: Dict, model_id: Optional[str]) -> None:
    """Handle InvokeModelWithResponseStream API response (streaming)."""
    original_body = response.get("body")
    if not original_body:
        return
    
    def stream_wrapper(stream):
        for event in stream:
            meta = event.get("metadata")
            if meta and "usage" in meta:
                payload = build_usage_payload(meta["usage"], model_id)
                _set_bedrock_usage(payload)
            yield event
    
    response["body"] = stream_wrapper(original_body)


def _handle_converse(response: Dict, model_id: Optional[str]) -> None:
    """Handle Converse API response."""
    usage = response.get("usage")
    _debug_log(f"Converse usage: {usage}")
    
    if usage:
        payload = build_usage_payload(usage, model_id)
        _set_bedrock_usage(payload)


def _handle_converse_stream(response: Dict, model_id: Optional[str]) -> None:
    """Handle ConverseStream API response (streaming)."""
    original_stream = response.get("stream")
    if not original_stream:
        return
    
    def stream_wrapper(stream):
        for event in stream:
            if "metadata" in event:
                usage = event["metadata"].get("usage")
                if usage:
                    payload = build_usage_payload(usage, model_id)
                    _set_bedrock_usage(payload)
            yield event
    
    response["stream"] = stream_wrapper(original_stream)


# ============================================================
# OPERATION HANDLER REGISTRY
# Extensible: Add new operation handlers here
# ============================================================

OPERATION_HANDLERS = {
    "InvokeModel": _handle_invoke_model,
    "InvokeModelWithResponseStream": _handle_invoke_model_stream,
    "Converse": _handle_converse,
    "ConverseStream": _handle_converse_stream,
    # Future: Add Llama-specific handlers if needed
}


# ============================================================
# MAIN INTERCEPTOR
# ============================================================

def _instrument_bedrock_calls(wrapped, instance, args, kwargs):
    """
    Wrapt interceptor for botocore BaseClient._make_api_call.
    Captures usage data from Bedrock API responses.
    """
    op = args[0]
    
    # Only intercept bedrock-runtime calls
    if instance.meta.service_model.service_name != "bedrock-runtime":
        return wrapped(*args, **kwargs)
    
    _debug_log(f"Operation: {op}")
    
    # Execute the original API call
    response = wrapped(*args, **kwargs)
    
    # Extract modelId from API params
    api_params = kwargs.get("api_params") or (args[1] if len(args) > 1 else {})
    model_id = api_params.get("modelId") if isinstance(api_params, dict) else None
    
    _debug_log(f"Model ID: {model_id}")
    
    # Dispatch to appropriate handler
    handler = OPERATION_HANDLERS.get(op)
    if handler:
        handler(response, model_id)
    else:
        _debug_log(f"Unhandled operation: {op}")
    
    return response


# ============================================================
# INITIALIZATION
# ============================================================

_observer_initialized = False


def init_bedrock_observer():
    """
    Initialize the Bedrock observer.
    Wraps botocore's _make_api_call to intercept Bedrock API responses.
    
    This is automatically called when the veriskgo package is imported.
    """
    global _observer_initialized
    
    if _observer_initialized:
        return
    
    wrapt.wrap_function_wrapper(
        "botocore.client",
        "BaseClient._make_api_call",
        _instrument_bedrock_calls,
    )
    
    _observer_initialized = True


def enable_debug_mode():
    """Enable debug logging for the Bedrock observer."""
    global DEBUG_MODE
    DEBUG_MODE = True


def disable_debug_mode():
    """Disable debug logging for the Bedrock observer."""
    global DEBUG_MODE
    DEBUG_MODE = False
