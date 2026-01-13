import botocore
import json
import uuid
import datetime
from veriskgo.trace_manager import TraceManager
from typing import Any, Dict

def instrument_aws(session=None):
    """
    Registers event hooks with the botocore session.
    If 'session' (boto3.Session) is provided, instruments that session.
    Otherwise, instruments the global botocore session.
    """
    if session:
        # If it's a boto3 Session, get the underlying botocore session
        if hasattr(session, '_session'):
            event_emitter = session._session
        else:
            # Assume it is a botocore session
            event_emitter = session
    else:
        event_emitter = botocore.session.get_session()

    event_emitter.register('before-call.bedrock-runtime.Converse', _on_bedrock_converse_before)
    event_emitter.register('after-call.bedrock-runtime.Converse', _on_bedrock_converse_after)
    
    print(f"[veriskgo] AWS instrumentation enabled for session: {event_emitter}")

def _on_bedrock_converse_before(params, context, **kwargs):
    """
    Called before a Bedrock Converse request is sent.
    """
    try:
        # Check if we are in a trace context
        if not TraceManager.has_active_trace():
            # If no trace, we can't really attach a span.
            # (Future: maybe start a root trace automatically?)
            return

        body = params.get('body', b'{}')
        if isinstance(body, bytes):
            try:
                body = json.loads(body)
            except:
                body = {}
        
        prompt = "Unknown"
        messages = body.get('messages', [])
        if messages:
            content = messages[0].get('content', [])
            if content:
                prompt = content[0].get('text', '')
        
        # Try to get modelId from URL if not in params
        model_id = params.get('modelId')
        if not model_id:
            url = params.get('url', '')
            # Pattern: .../model/{modelId}/converse
            import re
            from urllib.parse import unquote
            match = re.search(r'/model/([^/]+)/converse', url)
            if match:
                model_id = unquote(match.group(1))
        
        # Capture parent span details BEFORE creating the new span
        with TraceManager._lock:
            active_stack = TraceManager._active.get("stack", [])
            parent_span_id = active_stack[-1]["span_id"] if active_stack else None
            trace_id = TraceManager._active.get("trace_id")

        # Start a span using TraceManager
        # Note: TraceManager.start_span will internally use the top of stack as parent,
        # but we captured it explicitly above for event construction later.
        span_id = TraceManager.start_span(
            name="bedrock_llm_call",
            input_data={"prompt": prompt, "provider": "bedrock", "model": model_id},
            tags={"wrapper": "boto3-hook"}
        )
        context['veriskgo_span_id'] = span_id
        context['veriskgo_trace_id'] = trace_id
        context['veriskgo_parent_span_id'] = parent_span_id
        context['veriskgo_start_time'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        context['veriskgo_input_data'] = {"prompt": prompt, "provider": "bedrock", "model": model_id}
        context['veriskgo_model_id'] = model_id
        
    except Exception as e:
        print(f"[veriskgo] Error in before-hook: {e}")

def _on_bedrock_converse_after(http_response, parsed, context, **kwargs):
    """
    Called after a Bedrock Converse request is received.
    """
    try:
        span_id = context.get('veriskgo_span_id')
        if not span_id:
            return

        # Extract response text
        response_text = ""
        output_msg = parsed.get('output', {}).get('message', {})
        content = output_msg.get('content', [])
        if content:
            response_text = content[0].get('text', '')
            
        # Extract usage and metrics
        usage_data = parsed.get('usage', {})
        metrics = parsed.get('metrics', {})
        latency_ms = metrics.get('latencyMs', 0)
        
        input_tokens = usage_data.get('inputTokens', 0)
        output_tokens = usage_data.get('outputTokens', 0)
        total_tokens = usage_data.get('totalTokens', 0)
        
        # Pricing Reference (approximate)
        PRICING = {
            "anthropic.claude-3-sonnet-20240229-v1:0": {"input": 3.0, "output": 15.0},
            "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.25, "output": 1.25},
            "anthropic.claude-3-opus-20240229-v1:0": {"input": 15.0, "output": 75.0},
            # Default fallback (Sonnet-like)
            "default": {"input": 3.0, "output": 15.0}
        }
        
        model_id = context.get('veriskgo_model_id', 'default')
        price_cfg = PRICING.get(model_id, PRICING["default"])
        
        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * price_cfg["input"]
        output_cost = (output_tokens / 1_000_000) * price_cfg["output"]
        total_cost = input_cost + output_cost
        
        output_payload = {
            "text": response_text,
            "finish_reason": parsed.get('stopReason'),
            "model_id": model_id,
            "usage": {
                "input": input_tokens,
                "output": output_tokens,
                "total": total_tokens
            },
            "cost": {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            }
        }

        # End the span
        # Note: TraceManager.end_span typically uses time.time() for end time, 
        # but since we captured latency from AWS, we might want to ensure 'duration_ms' is accurate.
        # However, end_span uses wall clock. The 'latencyMs' from AWS is server processing time.
        # We can update the span timestamp or duration manually if TraceManager allowed it,
        # but standard end_span is fine for now. 
        # Actually, end_span updates duration_ms. We might want to inject our better latency.
        # But TraceManager.end_span doesn't take duration override.
        # We can pass latency in output_payload or metadata?
        # Let's just trust end_span for wall clock duration which includes network overhead.
        
        TraceManager.end_span(span_id, output_data=output_payload)
        
        # Manually send the span event to SQS
        from veriskgo.sqs import send_to_sqs
        from veriskgo.trace_manager import serialize_value
        
        trace_id = context.get('veriskgo_trace_id')
        parent_span_id = context.get('veriskgo_parent_span_id')
        start_time_iso = context.get('veriskgo_start_time')
        # Calculate duration based on wall clock (TraceManager updates it, but we can recalc or trust latency)
        # Let's use latency_ms from the response for 'duration_ms' if available, otherwise 0
        
        span_event = {
            "event_type": "span",
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "name": "bedrock_llm_call",
            "type": "generation",
            "timestamp": start_time_iso,
            "duration_ms": int(latency_ms) if latency_ms else 0, # Use server latency
            "input": context.get('veriskgo_input_data', {}),
            "output": output_payload,
            "model": model_id,
            "usage_details": output_payload["usage"],
            "cost_details": output_payload["cost"],
            "usage": output_payload["usage"],
            "cost": output_payload["cost"],
            "metadata": {"wrapper": "boto3-hook"}
        }
        
        send_to_sqs(span_event)
        
        print(f"[veriskgo] Auto-captured Bedrock call: {input_tokens}in/{output_tokens}out")

    except Exception as e:
        print(f"[veriskgo] Error in after-hook: {e}")
