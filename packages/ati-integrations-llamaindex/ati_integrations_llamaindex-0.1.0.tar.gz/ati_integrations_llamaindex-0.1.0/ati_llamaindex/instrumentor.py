from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import llama_index.core
from ati_sdk import AtiConfig, AtiTracer
from .callbacks import AtiLlamaIndexCallbackHandler

@dataclass
class LlamaIndexInstrumentor:
    _enabled: bool = False
    _handler: Optional[AtiLlamaIndexCallbackHandler] = None

    def instrument(self, config: AtiConfig | None = None) -> AtiLlamaIndexCallbackHandler:
        if self._enabled and self._handler:
            return self._handler

        cfg = AtiConfig.from_env().merged(config)
        tracer = AtiTracer(framework="llamaindex", tracer_name="ati.llamaindex", config=cfg)
        self._handler = AtiLlamaIndexCallbackHandler(tracer=tracer)
        
        # LlamaIndex global handler registration
        llama_index.core.global_handler = self._handler
        
        self._enabled = True
        return self._handler

    def uninstrument(self) -> None:
        if self._enabled:
            llama_index.core.global_handler = None
            self._handler = None
            self._enabled = False
