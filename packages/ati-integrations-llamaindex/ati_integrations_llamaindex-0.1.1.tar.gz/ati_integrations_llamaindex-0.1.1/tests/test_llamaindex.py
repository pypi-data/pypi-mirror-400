
import pytest
from unittest.mock import MagicMock
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace

from llama_index.core.callbacks import CBEventType

from ati_llamaindex import LlamaIndexInstrumentor
from ati_sdk.semantics import ATI_ATTR, AtiSpanType

@pytest.fixture
def memory_exporter():
    exporter = InMemorySpanExporter()
    return exporter

def test_llamaindex_instrumentation(memory_exporter):
    # Setup Tracer
    provider = TracerProvider()
    processor = SimpleSpanProcessor(memory_exporter)
    provider.add_span_processor(processor)

    # Instrument
    instrumentor = LlamaIndexInstrumentor()
    instrumentor.uninstrument()
    handler = instrumentor.instrument()
    
    # Inject local tracer
    handler.tracer.tracer = provider.get_tracer("ati.llamaindex")

    try:
        # Simulate Events manually since we don't want to spin up real LlamaIndex pipelines with API keys
        payload = {"key": "value"}
        
        # 1. Start Event
        event_id = handler.on_event_start(
            CBEventType.LLM,
            payload=payload,
            event_id="evt_123"
        )
        
        # 2. End Event
        handler.on_event_end(
            CBEventType.LLM,
            payload={"response": "ok"},
            event_id=event_id
        )

        # Verification
        spans = memory_exporter.get_finished_spans()
        assert len(spans) == 1
        span = spans[0]
        assert span.name == "llamaindex.llm.call"
        assert span.attributes[ATI_ATTR.span_type] == AtiSpanType.LLM
        
        # Verify uninstrument
        instrumentor.uninstrument()
        assert instrumentor._handler is None

    finally:
        instrumentor.uninstrument()
