
from llama_index.core import Document, VectorStoreIndex
from ati_llamaindex import LlamaIndexInstrumentor

def main():
    # 1. Instrument
    print("Instrumenting LlamaIndex...")
    LlamaIndexInstrumentor().instrument()

    # 2. Setup Data
    documents = [
        Document(text="Iocane ATI provides Agent Traffic Intelligence."),
        Document(text="It traces agents using OpenTelemetry."),
    ]
    
    # 3. Create Index (embedding might require KEY, but we can try local or mock if needed)
    # LlamaIndex defaults to OpenAI. To make this runnable without key, 
    # we would need to configure a local embed/llm or just show wiring.
    # For now, we assume user might have key or understands this is an example pattern.
    # To be safe for automated testing, we usually mock.    
    
    print("Note: This example requires OPENAI_API_KEY if default models are used.")
    try:
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        
        # 4. Query
        print("Querying...")
        response = query_engine.query("What does ATI do?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Skipping execution due to missing config/key: {e}")

    # 5. Uninstrument
    LlamaIndexInstrumentor().uninstrument()

if __name__ == "__main__":
    main()
