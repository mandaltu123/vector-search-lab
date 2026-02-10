# Run the Notebook (with examples)

This guide shows how to run `chromadb_local_rag_chatbot.ipynb` against a local ChromaDB server (Docker).

## Prerequisites
- Python 3.10–3.12 (3.14 is not supported by ChromaDB yet)
- Docker Desktop (ChromaDB running)

## 1) Start ChromaDB (Docker)
If you already have Chroma running on port `8001`, skip this step.
```
docker run -d \
  --name chroma \
  -p 8001:8000 \
  -v "$(pwd)/chroma_data:/chroma/chroma" \
  chromadb/chroma:latest
```

Verify:
```
curl -s http://localhost:8001/api/v2/heartbeat
```

## 2) Create a Python environment
Use Python 3.11 or 3.12 if available.
```
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install chromadb jupyter
```

## 3) Set notebook environment variables
```
export CHROMA_HOST=localhost
export CHROMA_PORT=8001
```

If you use the LLM section in the notebook:
```
export LLM_PROVIDER=ollama   # or openai
export OLLAMA_MODEL=llama3.1
export OLLAMA_URL=http://localhost:11434
```

## 4) Start Jupyter
```
jupyter notebook
```

Open `chromadb_local_rag_chatbot.ipynb` and run cells top to bottom.

## Example expected outputs
These examples show what you should see when running key cells:

**Heartbeat cell**
```
Heartbeat: {'nanosecond heartbeat': 1770713878128264167}
```

**After adding documents**
```
Count: 3
```

**Query results**
```
{'ids': [['doc-3', 'doc-1']], 'documents': [['macOS users can run Chroma locally using Docker or chroma run.', 'Chroma is a vector database for embeddings.']], 'metadatas': [[{'source': 'docs', 'topic': 'mac'}, {'source': 'docs', 'topic': 'chroma'}]], 'distances': [[...]]}
```

## Stop services (optional)
```
docker stop chroma
```
