"""
Anthropic client wrapper for automatic tracing
"""
import time
from typing import Any
from opentelemetry import trace as otel_trace


def wrap_anthropic(client):
    """
    Wrap an Anthropic client to automatically capture all LLM calls as traces.
    
    Usage:
        from verifai import wrap_anthropic
        import anthropic
        
        client = wrap_anthropic(anthropic.Anthropic(api_key="..."))
        response = client.messages.create(...)  # Automatically traced!
    """
    original_create = client.messages.create
    
    def traced_create(*args, **kwargs):
        tracer = otel_trace.get_tracer("verifai.anthropic")
        
        with tracer.start_as_current_span("anthropic.messages.create") as span:
            # Capture input
            messages = kwargs.get("messages", [])
            model = kwargs.get("model", "unknown")
            system = kwargs.get("system", "")
            
            span.set_attribute("span_type", "llm")
            span.set_attribute("llm.model", model)
            span.set_attribute("llm.request.type", "chat")
            
            # Store structured input
            input_data = {
                "messages": messages,
                "model": model,
                "system": system,
                "max_tokens": kwargs.get("max_tokens"),
                "temperature": kwargs.get("temperature"),
            }
            span.set_attribute("input", str(input_data))
            
            start_time = time.time()
            
            try:
                # Call original Anthropic API
                response = original_create(*args, **kwargs)
                
                duration_ms = int((time.time() - start_time) * 1000)
                span.set_attribute("duration_ms", duration_ms)
                
                # Capture output
                if hasattr(response, "content") and len(response.content) > 0:
                    completion = response.content[0].text if hasattr(response.content[0], "text") else str(response.content[0])
                    span.set_attribute("output", str({"completion": completion}))
                
                # Capture token usage
                if hasattr(response, "usage"):
                    span.set_attribute("token_count_input", response.usage.input_tokens)
                    span.set_attribute("token_count_output", response.usage.output_tokens)
                    
                    # Estimate cost (simplified - Claude pricing varies by model)
                    # Using approximate Claude Sonnet pricing
                    input_cost = response.usage.input_tokens * 0.000003
                    output_cost = response.usage.output_tokens * 0.000015
                    total_cost = input_cost + output_cost
                    span.set_attribute("cost_usd", total_cost)
                
                return response
                
            except Exception as e:
                span.set_attribute("error", str({"type": type(e).__name__, "message": str(e)}))
                span.record_exception(e)
                raise
    
    # Replace the method
    client.messages.create = traced_create
    return client
