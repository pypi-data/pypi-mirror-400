# ATI Integration for LlamaIndex

This package provides OpenTelemetry instrumentation for [LlamaIndex](https://github.com/run-llama/llama_index) applications using Iocane ATI.

It captures:
- **LLM Calls**: Requests to backend models.
- **Retrieval**: Vector store lookups and query engine operations.
- **Synthesizing**: Response generation steps.

## Installation

```bash
pip install ati-integrations-llamaindex opentelemetry-sdk opentelemetry-exporter-otlp
```

## Configuration

Set the standard OpenTelemetry environment variables to point to your Iocane collector:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.iocane.ai/v1/traces"
export OTEL_EXPORTER_OTLP_HEADERS="x-iocane-key=YOUR_KEY,x-ati-env=YOUR_ENV_ID"
export OTEL_SERVICE_NAME="my-llamaindex-app"
```

## Usage

Here is the robust pattern for instrumenting LlamaIndex applications.

**Important**: LlamaIndex creates many internal components. It is crucial to initialize OpenTelemetry *before* importing or initializing heavily dependent LlamaIndex modules if possible, and ensuring the global tracer provider is correctly set.

```python
import os
from ati_llamaindex import LlamaIndexInstrumentor
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def main():
    # 1. Configure OpenTelemetry (Robust Pattern)
    resource = Resource.create(attributes={SERVICE_NAME: "my-llamaindex-service"})
    
    try:
        # Try to set the global provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
    except Exception:
        # If it fails (e.g., already set), ignore and fetch the active one below
        pass

    # ALWAYS get the global provider to ensure we attach to the active pipeline
    provider = trace.get_tracer_provider()

    # 2. Configure Exporter (Iocane)
    # Ensure usage of the correct endpoint from env or default
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and endpoint.endswith("/v1/traces"):
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = OTLPSpanExporter()
        
    if hasattr(provider, "add_span_processor"):
        provider.add_span_processor(BatchSpanProcessor(exporter))
    else:
        print("WARNING: TracerProvider does not support add_span_processor.")

    # 3. Instrument LlamaIndex
    # This should be done before creating indices or query engines
    LlamaIndexInstrumentor().instrument()

    try:
        # 4. Your LlamaIndex Code
        # documents = SimpleDirectoryReader("data").load_data()
        # index = VectorStoreIndex.from_documents(documents)
        # query_engine = index.as_query_engine()
        # response = query_engine.query("What represents this data?")
        # print(response)
        pass

    finally:
        # 5. Flush traces
        LlamaIndexInstrumentor().uninstrument()
        if hasattr(provider, "shutdown"):
            provider.shutdown()

if __name__ == "__main__":
    main()
```

## Environment Variables for Instrumentation

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | set to `true` to capture query text and response content as span events | `false` |
