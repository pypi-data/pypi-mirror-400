"""
OpenAI client wrapper for automatic tracing
"""
import time
from typing import Any, Optional
from opentelemetry import trace as otel_trace


def wrap_openai(client):
    """
    Wrap an OpenAI client to automatically capture all LLM calls as traces.
    
    Usage:
        from verifai import wrap_openai
        import openai
        
        client = wrap_openai(openai.OpenAI(api_key="..."))
        response = client.chat.completions.create(...)  # Automatically traced!
    """
    original_create = client.chat.completions.create
    
    def traced_create(*args, **kwargs):
        tracer = otel_trace.get_tracer("verifai.openai")
        
        with tracer.start_as_current_span("openai.chat.completions") as span:
            # Capture input
            messages = kwargs.get("messages", [])
            model = kwargs.get("model", "unknown")
            
            span.set_attribute("span_type", "llm")
            span.set_attribute("llm.model", model)
            span.set_attribute("llm.request.type", "chat")
            
            # Store structured input
            input_data = {
                "messages": messages,
                "model": model,
                "temperature": kwargs.get("temperature"),
                "max_tokens": kwargs.get("max_tokens"),
            }
            span.set_attribute("input", str(input_data))
            
            start_time = time.time()
            
            try:
                # Call original OpenAI API
                response = original_create(*args, **kwargs)
                
                duration_ms = int((time.time() - start_time) * 1000)
                span.set_attribute("duration_ms", duration_ms)
                
                # Capture output
                if hasattr(response, "choices") and len(response.choices) > 0:
                    completion = response.choices[0].message.content
                    span.set_attribute("output", str({"completion": completion}))
                
                # Capture token usage
                if hasattr(response, "usage"):
                    span.set_attribute("token_count_input", response.usage.prompt_tokens)
                    span.set_attribute("token_count_output", response.usage.completion_tokens)
                    
                    # Estimate cost (simplified, should be model-specific)
                    prompt_cost = response.usage.prompt_tokens * 0.000001
                    completion_cost = response.usage.completion_tokens * 0.000002
                    total_cost = prompt_cost + completion_cost
                    span.set_attribute("cost_usd", total_cost)
                
                return response
                
            except Exception as e:
                span.set_attribute("error", str({"type": type(e).__name__, "message": str(e)}))
                span.record_exception(e)
                raise
    
    # Replace the method
    client.chat.completions.create = traced_create
    return client
