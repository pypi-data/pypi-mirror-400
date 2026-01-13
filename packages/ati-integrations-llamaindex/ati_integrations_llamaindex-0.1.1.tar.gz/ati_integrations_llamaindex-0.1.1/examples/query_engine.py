import os
from llama_index.core import Document, VectorStoreIndex
from ati_llamaindex import LlamaIndexInstrumentor

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def main():
    # 1. Configure OpenTelemetry (Robust Pattern)
    resource = Resource.create(attributes={SERVICE_NAME: "ati-llamaindex-example"})
    
    try:
        # Try to set the global provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
    except Exception:
        # If it fails (e.g., already set), ignore and fetch the active one below
        pass

    # ALWAYS get the global provider to ensure we attach to the active pipeline
    provider = trace.get_tracer_provider()

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and endpoint.endswith("/v1/traces"):
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = OTLPSpanExporter()
        
    if hasattr(provider, "add_span_processor"):
        provider.add_span_processor(BatchSpanProcessor(exporter))

    # 2. Instrument
    print("Instrumenting LlamaIndex...")
    LlamaIndexInstrumentor().instrument()

    try:
        # 3. Setup Data
        documents = [
            Document(text="Iocane ATI provides Agent Traffic Intelligence."),
            Document(text="It traces agents using OpenTelemetry."),
        ]
        
        print("Note: This example requires OPENAI_API_KEY if default models are used.")
        
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        
        # 4. Query
        print("Querying...")
        response = query_engine.query("What does ATI do?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        # 5. Flush and Uninstrument
        LlamaIndexInstrumentor().uninstrument()
        if hasattr(provider, "shutdown"):
            provider.shutdown()

if __name__ == "__main__":
    main()
