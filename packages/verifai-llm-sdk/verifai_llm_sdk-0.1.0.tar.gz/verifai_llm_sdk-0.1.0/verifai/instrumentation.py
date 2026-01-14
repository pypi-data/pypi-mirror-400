
import functools
import inspect
from typing import Optional, Callable, Dict, Any
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from .exporter import VerifAISpanExporter

_provider = None
_api_url = "http://localhost:8000"

import os

def auto_instrument(project_name: str, service_name: str = "default", api_url: str = "http://localhost:8000"):
    global _provider, _api_url
    
    # Allow env var override
    env_project_name = os.environ.get("VERIFAI_PROJECT_NAME")
    if env_project_name:
        project_name = env_project_name

    _api_url = api_url
    print(f"✅ VerifAI: Instrumenting project '{project_name}' to {api_url}")
    
    _provider = TracerProvider()
    
    # Custom Exporter to send to backend
    exporter = VerifAISpanExporter(api_url=api_url, project_name=project_name)
    
    _provider.add_span_processor(BatchSpanProcessor(exporter))
    
    otel_trace.set_tracer_provider(_provider)

def trace(
    name: Optional[str] = None,
    span_type: str = "custom",
    tags: list = None,
    metadata: dict = None
) -> Callable:
    """
    Decorator to automatically trace function execution using OpenTelemetry
    """
    def decorator(func: Callable) -> Callable:
        span_name = name or func.__name__
        
        # Determine if async
        is_async = inspect.iscoroutinefunction(func)
        tracer = otel_trace.get_tracer("verifai")

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            attributes = {"span_type": span_type}
            if tags:
                attributes["tags"] = tags
            if metadata:
                attributes.update(metadata)
                
            # Capture Input
            attributes["input.args"] = str(args)
            attributes["input.kwargs"] = str(kwargs)

            with tracer.start_as_current_span(span_name, attributes=attributes) as span:
                try:
                    result = await func(*args, **kwargs)
                    # Capture Output
                    span.set_attribute("output.result", str(result)[:1000]) # Truncate
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            attributes = {"span_type": span_type}
            if tags:
                attributes["tags"] = str(tags) if tags else None
            if metadata:
                for k, v in metadata.items():
                    attributes[k] = str(v)
            
            attributes["input.args"] = str(args)
            attributes["input.kwargs"] = str(kwargs)

            with tracer.start_as_current_span(span_name, attributes=attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("output.result", str(result)[:1000])
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        return async_wrapper if is_async else sync_wrapper
    return decorator

def flush():
    if _provider:
        print(f"⏳ VerifAI: Uploading traces to {_api_url}...")
        try:
            # Force flush returns True if successful, False if timeout/error
            success = _provider.force_flush(timeout_millis=5000)
            if success:
                print(f"✅ VerifAI: Successfully uploaded traces to {_api_url}")
            else:
                print(f"❌ VerifAI: Connection Error or Timeout when sending to {_api_url}")
        except Exception as e:
             print(f"❌ VerifAI: Exception during upload: {e}")
