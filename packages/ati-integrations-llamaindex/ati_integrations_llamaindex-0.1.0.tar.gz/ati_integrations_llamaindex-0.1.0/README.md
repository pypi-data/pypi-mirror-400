# ATI Integration for LlamaIndex

This package provides OpenTelemetry instrumentation for LlamaIndex using IOcane ATI.

## Installation

```bash
pip install ati-integrations-llamaindex
```

## Usage

```python
from ati_llamaindex import LlamaIndexInstrumentor
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 1. Enable Instrumentation
# This sets the ATI handler as the LlamaIndex global handler
LlamaIndexInstrumentor().instrument()

# 2. Use LlamaIndex
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is ATI?")

# 3. (Optional) Uninstrument
LlamaIndexInstrumentor().uninstrument()
```

## Configuration

Configure the instrumentation via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | Capture query content and retrieval results | `false` |

## Features
- Captures LLM calls (`ati.span.type=llm`)
- Captures Retrieval steps (`ati.span.type=io`)
- Captures overall Query flow
