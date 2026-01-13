from __future__ import annotations
from typing import Any, Dict, List, Optional

from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.callbacks import CBEventType
from llama_index.core.callbacks.schema import CBEvent
from opentelemetry.trace import Span, Status, StatusCode

from ati_sdk import AtiConfig, AtiTracer
from ati_sdk.semantics import AtiSpanType, ATI_ATTR

class AtiLlamaIndexCallbackHandler(BaseCallbackHandler):
    def __init__(self, tracer: AtiTracer):
        super().__init__(event_starts_to_ignore=[], event_ends_to_ignore=[])
        self.tracer = tracer
        self._spans: Dict[str, Span] = {}

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        span_name = f"llamaindex.{event_type.value}"
        span_type = AtiSpanType.STEP
        
        if event_type == CBEventType.LLM:
             span_name = "llamaindex.llm.call"
             span_type = AtiSpanType.LLM
        elif event_type == CBEventType.RETRIEVE:
             span_name = "llamaindex.retrieve"
             span_type = AtiSpanType.IO
        elif event_type == CBEventType.FUNCTION_CALL:
             span_name = "llamaindex.tool.call"
             span_type = AtiSpanType.TOOL
        elif event_type == CBEventType.QUERY:
             span_name = "llamaindex.query"
             span_type = AtiSpanType.AGENT # or logical step
        
        attributes = {
            ATI_ATTR.step_type: event_type.value
        }

        span = self.tracer.start_span(
             span_name,
             span_type,
             attributes=attributes
        )
        
        if payload and self.tracer.config.capture_payloads:
             content = str(payload)[:1000] # truncate
             self.tracer.add_payload_event(
                 span, kind="event_start_payload", content=content,
                 redaction_patterns=(), enabled=True
             )

        self._spans[event_id] = span
        return event_id

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        span = self._spans.pop(event_id, None)
        if span:
             if payload and self.tracer.config.capture_payloads:
                 content = str(payload)[:1000]
                 self.tracer.add_payload_event(
                     span, kind="event_end_payload", content=content,
                     redaction_patterns=(), enabled=True
                 )
             span.end()

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        pass
