pk-ai-tools

`pk-ai-tools` is a small Python library that provides a reusable RAG (Retrieval-Augmented Generation) pipeline and a flexible document ingestion system.

It is built on top of:
- LangChain
- Chroma
- Ollama

The main goal of this project is to make it easy to:
- Ingest documents from many formats (PDF, Word, Excel, CSV, Markdown, HTML, etc.)
- Build or update a Chroma vector database
- Ask questions using a simple RAG pipeline backed by local Ollama models

This library was originally created for personal use and has been generalized to be reusable across projects.

## Installation

bash
pip install pk-ai-tools

Requires:

Python 3.9+

Ollama installed and running

## Quick example

```python
from pk_ai_tools import RAGPipeline

rag = RAGPipeline(
    doc_folder="./data",
    language="en",
    uuid="demo-user",
    model_name="llama3"
)

answer = rag.ask("What is this documentation about?")
print(answer)