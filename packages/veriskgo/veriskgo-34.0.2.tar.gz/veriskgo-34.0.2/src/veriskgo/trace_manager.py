from __future__ import annotations
import uuid
import threading
import time
import traceback
import json
import sys
import inspect
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Union, List
import functools

from .sqs import send_to_sqs

# ============================================================
# Safe Serialization Helpers
# ============================================================

# Maximum size for serialized output (200 KB)
MAX_OUTPUT_SIZE = 200 * 1024  # 200 KB

def serialize_value(value: Any, max_size: int = MAX_OUTPUT_SIZE) -> Any:
    """Serialize value with size limit to prevent SQS errors.
    
    Args:
        value: Value to serialize
        max_size: Maximum size in bytes (default 200 KB)
    
    Returns:
        Serialized value, truncated if necessary
    """
    try:
        # First, serialize to JSON
        serialized_str = json.dumps(value, default=str)
        serialized_bytes = serialized_str.encode('utf-8')
        
        # Check size
        if len(serialized_bytes) <= max_size:
            return json.loads(serialized_str)
        
        # Too large - return truncation info instead
        preview_size = min(1000, max_size // 2)  # Show first 1KB as preview
        preview = serialized_str[:preview_size]
        
        print(f"[VeriskGO] Output truncated: {len(serialized_bytes)} bytes → {max_size} bytes limit")
        
        return {
            "_truncated": True,
            "_original_size_bytes": len(serialized_bytes),
            "_original_size_mb": round(len(serialized_bytes) / (1024 * 1024), 2),
            "_preview": preview + "...",
            "_message": f"Output truncated (original: {round(len(serialized_bytes) / (1024 * 1024), 2)} MB, limit: {round(max_size / 1024, 0)} KB)"
        }
    except Exception as e:
        return str(value)


def safe_locals(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: serialize_value(v) for k, v in d.items() if not k.startswith("_")}


# ============================================================
# Core Trace Manager
# ============================================================

class TraceManager:
    _lock = threading.Lock()

    _active: Dict[str, Any] = {
        "trace_id": None,
        "spans": [],
        "stack": [],
        "metadata": {},  # Store trace metadata including project_id
    }

    @classmethod
    def finalize_and_send(
        cls,
        *,
        user_id: str,
        session_id: str,
        trace_name: str,
        trace_input: dict,
        trace_output: dict,
        extra_spans: list = [],
    ):
        with cls._lock:
            trace_id = cls._active["trace_id"]
            trace_metadata = cls._active.get("metadata", {})
            
            if not trace_id:
                print("[VeriskGO] ERROR: No active trace.")
                return False
            
            # Send trace_end event to SQS (with metadata including project_id)
            trace_end_event = {
                "event_type": "trace_end",
                "trace_id": trace_id,
                "user_id": user_id,
                "session_id": session_id,
                "trace_name": trace_name,
                "trace_input": trace_input,
                "trace_output": trace_output,
                "metadata": trace_metadata,  # Include metadata with project_id
                "timestamp": cls._now()
            }
            
            # Clear active trace
            cls._active["trace_id"] = None
            cls._active["spans"] = []
            cls._active["stack"] = []
            cls._active["metadata"] = {}
        
        # CRITICAL: Flush all pending span events before sending trace_end
        # This ensures all spans arrive at Lambda before trace_end
        from .sqs import _sqs_instance
        if _sqs_instance and hasattr(_sqs_instance, 'force_flush'):
            _sqs_instance.force_flush()
            import time
            time.sleep(0.5)  # Increased delay to ensure all messages are fully sent
        
        send_to_sqs(trace_end_event)
        print(f"[VeriskGO] Trace ended: {trace_id}\n")
        
        return True

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _id() -> str:
        return uuid.uuid4().hex

    # ---------------------------------------------------------
    # Trace API
    # ---------------------------------------------------------
    @classmethod
    def has_active_trace(cls) -> bool:
        return cls._active["trace_id"] is not None

    @classmethod
    def start_trace(cls, name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        with cls._lock:
            trace_id = cls._id()
            root_id = cls._id()
            
            # Auto-inject project_id from config into metadata
            from .config import get_cfg
            cfg = get_cfg()
            final_metadata = metadata.copy() if metadata else {}
            
            # Add project_id if not already provided
            if "project_id" not in final_metadata:
                final_metadata["project_id"] = cfg.get("project_id", "default")
                print(f"[VeriskGO] Auto-injected project_id: {final_metadata['project_id']}")

            root_span = {
                "span_id": root_id,
                "parent_span_id": None,
                "name": name,
                "type": "root",
                "timestamp": cls._now(),
                "input": None,
                "output": None,
                "metadata": final_metadata,
                "duration_ms": 0,
            }

            cls._active["trace_id"] = trace_id
            cls._active["spans"] = [root_span]
            cls._active["stack"] = [{"span_id": root_id, "start": time.time()}]
            cls._active["metadata"] = final_metadata  # Store metadata for later use

            # Send trace_start event to SQS immediately
            trace_start_event = {
                "event_type": "trace_start",
                "trace_id": trace_id,
                "trace_name": name,
                "timestamp": cls._now(),
                "metadata": final_metadata
            }
            send_to_sqs(trace_start_event)
            print(f"[VeriskGO] Trace started: {trace_id}")

            return trace_id

    @classmethod
    def end_trace(cls, final_output: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        with cls._lock:
            if not cls._active["trace_id"]:
                return None

            while cls._active["stack"]:
                cls._end_current_span()

            if final_output:
                cls._active["spans"][0]["output"] = final_output

            flat_spans = cls._active["spans"].copy()

            # Convert flat spans into a nested structure for consumers that
            # expect nested observations. Keep the flat list for compatibility
            # and add `nested_spans` which is a tree of spans.
            def _to_observation(sp: Dict[str, Any]) -> Dict[str, Any]:
                # map internal fields to a more consumer-friendly shape
                start = sp.get("timestamp")
                duration = sp.get("duration_ms") or 0
                # handle trailing Z if present
                try:
                    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    end_dt = start_dt + timedelta(milliseconds=duration)
                    end = end_dt.isoformat()
                except Exception:
                    end = None

                obs = {
                    "id": sp.get("span_id"),
                    "parentObservationId": sp.get("parent_span_id"),
                    "type": "SPAN",
                    "name": sp.get("name"),
                    "startTime": start,
                    "endTime": end,
                    "latency": duration,
                    "level": sp.get("type", "DEFAULT"),
                    "input": sp.get("input"),
                    "output": sp.get("output"),
                    "metadata": sp.get("metadata", {}),
                }
                return obs

            # build mapping and attach children
            id_map: Dict[str, Dict[str, Any]] = {}
            for s in flat_spans:
                id_map[s["span_id"]] = _to_observation(s)
                id_map[s["span_id"]]["children"] = []

            roots = []
            for s in flat_spans:
                node = id_map[s["span_id"]]
                parent = s.get("parent_span_id")
                if parent and parent in id_map:
                    id_map[parent]["children"].append(node)
                else:
                    roots.append(node)

            bundle = {
                "trace_id": cls._active["trace_id"],
                # keep the original flat list for compatibility
                "spans": flat_spans,
                # nested tree representation (roots list)
                "nested_spans": roots,
            }

            cls._active["trace_id"] = None
            cls._active["spans"] = []
            cls._active["stack"] = []

            return bundle

    # ---------------------------------------------------------
    # Span API
    # ---------------------------------------------------------
    @classmethod
    def start_span(cls, name: str, input_data=None, tags=None):
        with cls._lock:
            if not cls._active["trace_id"]:
                return None

            parent = cls._active["stack"][-1]["span_id"]
            sid = cls._id()

            span = {
                "span_id": sid,
                "parent_span_id": parent,
                "name": name,
                "type": "child",
                "timestamp": cls._now(),
                "input": input_data,
                "metadata": tags or {},
                "output": None,
                "duration_ms": 0,
            }

            cls._active["spans"].append(span)
            cls._active["stack"].append({"span_id": sid, "start": time.time()})

            return sid

    @classmethod
    def end_span(cls, span_id: Optional[str], output_data=None):
        with cls._lock:
            if not cls._active["stack"]:
                return

            for i in reversed(range(len(cls._active["stack"]))):
                entry = cls._active["stack"][i]

                if entry["span_id"] == span_id:
                    duration = int((time.time() - entry["start"]) * 1000)
                    cls._active["stack"].pop(i)

                    for sp in cls._active["spans"]:
                        if sp["span_id"] == span_id:
                            sp["duration_ms"] = duration
                            sp["output"] = output_data

                            if isinstance(output_data, dict):
                                if "usage" in output_data:
                                    sp["usage"] = output_data["usage"]
                                if "usage_details" in output_data:
                                    sp["usage_details"] = output_data["usage_details"]
                                if "cost" in output_data:
                                    sp["cost"] = output_data["cost"]
                                if "cost_details" in output_data:
                                    sp["cost_details"] = output_data["cost_details"]

                            return

    @classmethod
    def _end_current_span(cls, output_data=None):
        entry = cls._active["stack"].pop()
        sid = entry["span_id"]
        duration = int((time.time() - entry["start"]) * 1000)

        for sp in cls._active["spans"]:
            if sp["span_id"] == sid:
                sp["duration_ms"] = duration
                if output_data:
                    sp["output"] = output_data

                    if isinstance(output_data, dict):
                        if "usage" in output_data:
                            sp["usage"] = output_data["usage"]
                        if "usage_details" in output_data:
                            sp["usage_details"] = output_data["usage_details"]
                        if "cost" in output_data:
                            sp["cost"] = output_data["cost"]
                        if "cost_details" in output_data:
                            sp["cost_details"] = output_data["cost_details"]

                return


# ============================================================
# Local Capture Utilities
# ============================================================

def capture_function_locals(func, capture_locals=True, capture_self=True):
    locals_before = {}
    locals_after = {}

    if not capture_locals:
        return None, locals_before, locals_after

    target_code = func.__code__
    target_name = func.__name__
    target_module = func.__module__

    entered = False

    def tracer(frame, event, arg):
        nonlocal entered

        if frame.f_code is target_code and frame.f_globals.get("__name__") == target_module:
            try:

                if not entered:
                    entered = True
                    f_locals = frame.f_locals
                    
                    # Filter specific variables if capture_locals is a list
                    if isinstance(capture_locals, list):
                        f_locals = {k: v for k, v in f_locals.items() if k in capture_locals}

                    if not capture_self and "self" in f_locals:
                        f_locals = {k: v for k, v in f_locals.items() if k != "self"}
                    locals_before.update(safe_locals(f_locals))

                if event == "return":
                    f_locals = frame.f_locals
                    
                    # Filter specific variables if capture_locals is a list
                    if isinstance(capture_locals, list):
                        f_locals = {k: v for k, v in f_locals.items() if k in capture_locals}
                    
                    if not capture_self and "self" in f_locals:
                        f_locals = {k: v for k, v in f_locals.items() if k != "self"}
                    locals_after.update(safe_locals(f_locals))
                    locals_after["_return"] = serialize_value(arg)
            except Exception as e:
                print(f"[DEBUG] TRACER ERROR: {e}")
                traceback.print_exc()

        return tracer

    return tracer, locals_before, locals_after


# ============================================================
# Decorator: track_function
# ============================================================

def track_function(name: Optional[str] = None, *, tags=None, capture_locals: Union[bool, List[str]] = True, capture_self=True):

    def decorator(func):

        span_name = name or func.__name__
        is_async = inspect.iscoroutinefunction(func)

        def sync_wrapper(*args, **kwargs):

            if not TraceManager.has_active_trace():
                return func(*args, **kwargs)

            # Get parent span ID from stack
            with TraceManager._lock:
                parent_span_id = TraceManager._active["stack"][-1]["span_id"] if TraceManager._active["stack"] else None
                trace_id = TraceManager._active["trace_id"]
            
            span_id = TraceManager._id()
            start_time = time.time()
            start_timestamp = TraceManager._now()

            tracer, locals_before, locals_after = capture_function_locals(func, capture_locals=capture_locals, capture_self=capture_self)
            if tracer:
                sys.settrace(tracer)

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if tracer:
                    sys.settrace(None)
                
                # Send error span event to SQS immediately
                duration_ms = int((time.time() - start_time) * 1000)
                span_event = {
                    "event_type": "span",
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": parent_span_id,
                    "name": span_name,
                    "timestamp": start_timestamp,
                    "duration_ms": duration_ms,
                    "input": {"args": serialize_value(args), "kwargs": serialize_value(kwargs)},
                    "output": {
                        "status": "error",
                        "error": str(e),
                        "stacktrace": traceback.format_exc(),
                        "locals_before": locals_before,
                        "locals_after": locals_after,
                    },
                    "metadata": tags or {}
                }
                send_to_sqs(span_event)
                print(f"[VeriskGO] Span sent (error): {span_name}")
                raise

            if tracer:
                sys.settrace(None)

            latency = int((time.time() - start_time) * 1000)

            # Send successful span event to SQS immediately
            span_event = {
                "event_type": "span",
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "name": span_name,
                "timestamp": start_timestamp,
                "duration_ms": latency,
                "input": {"args": serialize_value(args), "kwargs": serialize_value(kwargs)},
                "output": {
                    "status": "success",
                    "latency_ms": latency,
                    "locals_before": locals_before,
                    "locals_after": locals_after,
                    "output": serialize_value(result),
                },
                "metadata": tags or {}
            }
            send_to_sqs(span_event)
            if capture_locals:
                print(f"[VeriskGO] Captured Locals (Before): {locals_before}")
                print(f"[VeriskGO] Captured Locals (After): {locals_after}")
            print(f"[VeriskGO] Span sent: {span_name}")

            return result

        async def async_wrapper(*args, **kwargs):

            if not TraceManager.has_active_trace():
                return await func(*args, **kwargs)

            # Get parent span ID from stack
            with TraceManager._lock:
                parent_span_id = TraceManager._active["stack"][-1]["span_id"] if TraceManager._active["stack"] else None
                trace_id = TraceManager._active["trace_id"]
            
            span_id = TraceManager._id()
            start_time = time.time()
            start_timestamp = TraceManager._now()

            tracer, locals_before, locals_after = capture_function_locals(func, capture_locals=capture_locals, capture_self=capture_self)
            if tracer:
                sys.settrace(tracer)

            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                if tracer:
                    sys.settrace(None)
                
                # Send error span event to SQS immediately
                duration_ms = int((time.time() - start_time) * 1000)
                span_event = {
                    "event_type": "span",
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": parent_span_id,
                    "name": span_name,
                    "timestamp": start_timestamp,
                    "duration_ms": duration_ms,
                    "input": {"args": serialize_value(args), "kwargs": serialize_value(kwargs)},
                    "output": {
                        "status": "error",
                        "error": str(e),
                        "stacktrace": traceback.format_exc(),
                        "locals_before": locals_before,
                        "locals_after": locals_after,
                    },
                    "metadata": tags or {}
                }
                send_to_sqs(span_event)
                print(f"[VeriskGO] Span sent (error): {span_name}")
                raise

            if tracer:
                sys.settrace(None)

            latency = int((time.time() - start_time) * 1000)

            # Send successful span event to SQS immediately
            span_event = {
                "event_type": "span",
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "name": span_name,
                "timestamp": start_timestamp,
                "duration_ms": latency,
                "input": {"args": serialize_value(args), "kwargs": serialize_value(kwargs)},
                "output": {
                    "status": "success",
                    "latency_ms": latency,
                    "locals_before": locals_before,
                    "locals_after": locals_after,
                    "output": serialize_value(result),
                },
                "metadata": tags or {}
            }
            send_to_sqs(span_event)
            if capture_locals:
                print(f"[VeriskGO] Captured Locals (Before): {locals_before}")
                print(f"[VeriskGO] Captured Locals (After): {locals_after}")
            print(f"[VeriskGO] Span sent: {span_name}")
            
            return result

        return functools.wraps(func)(async_wrapper if is_async else sync_wrapper)

    return decorator


# ============================================================
# LEGACY EXPORTS (for backward compatibility)
# Use core.pricing and core.usage for new code
# ============================================================

def calculate_cost(usage: dict):
    """
    DEPRECATED: Use veriskgo.core.pricing.calculate_cost instead.
    Kept for backward compatibility.
    """
    from .core.pricing import calculate_cost as _calculate_cost
    return {
        "input_cost": _calculate_cost(
            usage.get("input_tokens", 0), 
            usage.get("output_tokens", 0)
        )["input"],
        "output_cost": _calculate_cost(
            usage.get("input_tokens", 0),
            usage.get("output_tokens", 0)
        )["output"],
        "total_cost": _calculate_cost(
            usage.get("input_tokens", 0),
            usage.get("output_tokens", 0)
        )["total"],
    }


