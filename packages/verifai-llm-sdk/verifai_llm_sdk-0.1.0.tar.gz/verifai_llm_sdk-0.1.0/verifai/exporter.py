import json
import requests
import os
import datetime
from typing import Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

class VerifAISpanExporter(SpanExporter):
    def __init__(self, api_url: str, project_name: str = "default_project"):
        self.api_url = f"{api_url}/api/v1/traces"
        self.project_name = project_name
        self.api_key = os.environ.get("VERIFAI_API_KEY")
        if not self.api_key:
             print("⚠️ VerifAI: No API Key found in VERIFAI_API_KEY environment variable.")

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        headers = {
            "Content-Type": "application/json",
            "X-VerifAI-Api-Key": self.api_key
        } if self.api_key else {"Content-Type": "application/json"}
        
        success_count = 0
        for span in spans:
            try:
                payload = self._translate_span(span)
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=5)
                if response.status_code in [200, 201]:
                    success_count += 1
                else:
                    print(f"❌ VerifAI: Failed to upload span {span.name}: {response.status_code} {response.text}")
            except Exception as e:
                print(f"❌ VerifAI: Exception uploading span {span.name}: {e}")
        
        return SpanExportResult.SUCCESS if success_count == len(spans) else SpanExportResult.FAILURE

    def _translate_span(self, span: ReadableSpan):
        ctx = span.get_span_context()
        parent = span.parent
        
        # Convert 128-bit Trace ID to Hex String
        trace_id = f"{ctx.trace_id:032x}"
        # Pad Span ID to 32 hex chars to satisfy backend UUID requirement (OTel uses 16)
        span_id = f"{ctx.span_id:032x}"
        parent_id = f"{parent.span_id:032x}" if parent else None

        # Extract attributes
        attributes = dict(span.attributes or {})
        
        # Extract input/output if they exist in attributes (convention)
        input_data = attributes.pop("input", {})
        output_data = attributes.pop("output", None)
        
        # Try to parse stringified input/output if needed
        # (Our framework stores them as separate keys output.result etc, so we might need reconstructing)
        # For now, let's look for known keys.
        
        if not output_data:
            # Reconstruct output from output.* keys
            output_keys = [k for k in attributes.keys() if k.startswith("output.")]
            if output_keys:
                output_data = {k.replace("output.", ""): attributes.pop(k) for k in output_keys}

        # Determine Span Type (heuristic)
        span_type = "agent" # Default for this app
        if "span_type" in attributes:
            span_type = attributes.pop("span_type")
        elif "tool.name" in attributes:
            span_type = "tool"
        
        # Calculate timing
        start_time = datetime.datetime.fromtimestamp(span.start_time / 1e9).isoformat()
        end_time = datetime.datetime.fromtimestamp(span.end_time / 1e9).isoformat() if span.end_time else None

        return {
            "span_type": span_type,
            "span_name": span.name,
            "project_name": self.project_name,
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_id": parent_id,
            "session_id": trace_id, # Map trace_id to session_id for now to group them??
            "start_time": start_time,
            "end_time": end_time,
            "input": input_data,
            "output": output_data,
            "metadata": attributes, # Remaining attributes
            "events": [
                {
                    "name": event.name,
                    "timestamp": datetime.datetime.fromtimestamp(event.timestamp / 1e9).isoformat(),
                    "attributes": dict(event.attributes or {})
                }
                for event in span.events
            ]
        }

    def shutdown(self):
        pass
