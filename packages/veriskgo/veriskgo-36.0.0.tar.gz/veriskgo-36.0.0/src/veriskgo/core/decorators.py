# veriskgo/core/decorators.py
"""
Reusable decorator infrastructure for sync/async function wrapping.
Eliminates code duplication between track_function, track_llm_call, and track_langchain.
"""

from __future__ import annotations

import time
import traceback
import functools
import inspect
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

# NOTE: We use late imports to avoid circular import issues


def _get_trace_manager():
    """Lazy import of TraceManager to avoid circular imports."""
    from veriskgo.trace_manager import TraceManager
    return TraceManager


def _get_serialize_value():
    """Lazy import of serialize_value."""
    from veriskgo.trace_manager import serialize_value
    return serialize_value


def _get_capture_function_locals():
    """Lazy import of capture_function_locals."""
    from veriskgo.trace_manager import capture_function_locals
    return capture_function_locals


def _get_send_to_sqs():
    """Lazy import of send_to_sqs."""
    from veriskgo.sqs import send_to_sqs
    return send_to_sqs


@dataclass
class SpanContext:
    """
    Context holder for span execution.
    Provides all necessary data for span creation and finalization.
    """
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    start_time: float
    start_ts: str
    span_name: str
    span_type: str = "span"  # "span" or "generation"
    tags: Optional[Dict[str, Any]] = None
    trace_metadata: Dict[str, Any] = field(default_factory=dict)  # Include trace metadata (e.g., project_id)
    
    # Captured locals
    locals_before: Dict[str, Any] = field(default_factory=dict)
    locals_after: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_ms(self) -> int:
        return int((time.time() - self.start_time) * 1000)


def _get_span_context(span_name: str, span_type: str = "span", tags: Optional[Dict] = None) -> Optional[SpanContext]:
    """
    Create a SpanContext if there's an active trace.
    Returns None if no active trace.
    """
    TraceManager = _get_trace_manager()
    
    if not TraceManager.has_active_trace():
        return None
    
    with TraceManager._lock:
        parent_span_id = (
            TraceManager._active["stack"][-1]["span_id"]
            if TraceManager._active["stack"]
            else None
        )
        trace_id = TraceManager._active["trace_id"]
        trace_metadata = TraceManager._active.get("metadata", {})  # Get trace metadata
    
    return SpanContext(
        trace_id=trace_id,
        span_id=TraceManager._id(),
        parent_span_id=parent_span_id,
        start_time=time.time(),
        start_ts=TraceManager._now(),
        span_name=span_name,
        span_type=span_type,
        tags=tags,
        trace_metadata=trace_metadata,  # Pass trace metadata to context
    )


def build_span_event(
    ctx: SpanContext,
    *,
    args: tuple,
    kwargs: dict,
    result: Any = None,
    error: Optional[Exception] = None,
    usage_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a span event dict ready for SQS.
    """
    serialize_value = _get_serialize_value()
    
    event = {
        "event_type": "span",
        "trace_id": ctx.trace_id,
        "span_id": ctx.span_id,
        "parent_span_id": ctx.parent_span_id,
        "name": ctx.span_name,
        "type": ctx.span_type,
        "timestamp": ctx.start_ts,
        "duration_ms": ctx.duration_ms,
        "metadata": {**(ctx.tags or {}), **ctx.trace_metadata},  # Merge tags and trace metadata (includes project_id)
    }
    
    # Input
    event["input"] = {
        "args": serialize_value(args),
        "kwargs": serialize_value(kwargs),
    }
    
    # Add prompt extraction for generation spans
    if ctx.span_type == "generation" and args and isinstance(args[0], str):
        event["input"]["prompt"] = args[0]
    
    # Output - error or success
    if error:
        event["output"] = {
            "status": "error",
            "error": str(error),
            "stacktrace": traceback.format_exc(),
            "locals_before": ctx.locals_before,
            "locals_after": ctx.locals_after,
        }
    else:
        event["output"] = {
            "status": "success",
            "latency_ms": ctx.duration_ms,
            "locals_before": ctx.locals_before,
            "locals_after": ctx.locals_after,
            "output": serialize_value(result) if ctx.span_type != "generation" else None,
        }
        
        # For generation spans, text goes in output.text
        if ctx.span_type == "generation":
            event["output"]["text"] = serialize_value(result)
    
    # Add usage/cost data for generation spans
    if usage_payload:
        event["model"] = usage_payload.get("model")
        event["usage"] = usage_payload.get("usage", {})
        event["cost"] = usage_payload.get("cost", {})
        event["usage_details"] = usage_payload.get("usage_details", {})
        event["cost_details"] = usage_payload.get("cost_details", {})
        event.setdefault("model_parameters", usage_payload.get("model_parameters"))
    
    return event


def send_span_event(event: Dict[str, Any], span_name: str, is_error: bool = False):
    """Send span event to SQS with logging."""
    send_to_sqs = _get_send_to_sqs()
    send_to_sqs(event)
    status = "(error)" if is_error else ""
    print(f"[VeriskGO] Span sent{status}: {span_name}")


def create_span_wrapper(
    func: Callable,
    span_name: str,
    span_type: str = "span",
    capture_locals: Union[bool, List[str]] = True,
    capture_self: bool = True,
    tags: Optional[Dict[str, Any]] = None,
    finalize_fn: Optional[Callable[[SpanContext, Any, tuple, dict], Dict[str, Any]]] = None,
):
    """
    Create both sync and async wrappers for a function with tracing.
    
    Args:
        func: The function to wrap
        span_name: Name for the span (defaults to func.__name__)
        span_type: "span" or "generation"
        capture_locals: Whether to capture local variables
        capture_self: Whether to include 'self' in captured locals
        tags: Optional metadata tags
        finalize_fn: Optional function to build usage payload:
                     (ctx, result, args, kwargs) -> usage_payload dict
                     
    Returns:
        Wrapped function (sync or async based on input func)
    """
    is_async = inspect.iscoroutinefunction(func)
    capture_function_locals = _get_capture_function_locals()
    
    def sync_wrapper(*args, **kwargs):
        # Execute without tracing if no active trace
        ctx = _get_span_context(span_name, span_type, tags)
        if ctx is None:
            return func(*args, **kwargs)
        
        # Set up local capture
        tracer, locals_before, locals_after = capture_function_locals(
            func, capture_locals=capture_locals, capture_self=capture_self
        )
        ctx.locals_before = locals_before
        ctx.locals_after = locals_after
        
        if tracer:
            sys.settrace(tracer)
        
        try:
            result = func(*args, **kwargs)
            
            if tracer:
                sys.settrace(None)
            
            # Build usage payload if finalize_fn provided
            usage_payload = None
            if finalize_fn:
                usage_payload = finalize_fn(ctx, result, args, kwargs)
            
            # Build and send span event
            event = build_span_event(
                ctx, args=args, kwargs=kwargs, result=result, usage_payload=usage_payload
            )
            send_span_event(event, span_name)
            
            # Log captured locals if enabled
            if capture_locals:
                print(f"[VeriskGO] Captured Locals (Before): {locals_before}")
                print(f"[VeriskGO] Captured Locals (After): {locals_after}")
            
            return result
            
        except Exception as e:
            if tracer:
                sys.settrace(None)
            
            # Build and send error span event
            event = build_span_event(ctx, args=args, kwargs=kwargs, error=e)
            send_span_event(event, span_name, is_error=True)
            raise
    
    async def async_wrapper(*args, **kwargs):
        # Execute without tracing if no active trace
        ctx = _get_span_context(span_name, span_type, tags)
        if ctx is None:
            return await func(*args, **kwargs)
        
        # Set up local capture
        tracer, locals_before, locals_after = capture_function_locals(
            func, capture_locals=capture_locals, capture_self=capture_self
        )
        ctx.locals_before = locals_before
        ctx.locals_after = locals_after
        
        if tracer:
            sys.settrace(tracer)
        
        try:
            result = await func(*args, **kwargs)
            
            if tracer:
                sys.settrace(None)
            
            # Build usage payload if finalize_fn provided
            usage_payload = None
            if finalize_fn:
                usage_payload = finalize_fn(ctx, result, args, kwargs)
            
            # Build and send span event
            event = build_span_event(
                ctx, args=args, kwargs=kwargs, result=result, usage_payload=usage_payload
            )
            send_span_event(event, span_name)
            
            # Log captured locals if enabled
            if capture_locals:
                print(f"[VeriskGO] Captured Locals (Before): {locals_before}")
                print(f"[VeriskGO] Captured Locals (After): {locals_after}")
            
            return result
            
        except Exception as e:
            if tracer:
                sys.settrace(None)
            
            # Build and send error span event
            event = build_span_event(ctx, args=args, kwargs=kwargs, error=e)
            send_span_event(event, span_name, is_error=True)
            raise
    
    return functools.wraps(func)(async_wrapper if is_async else sync_wrapper)
