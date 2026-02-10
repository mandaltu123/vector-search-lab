# ChromaDB & Vector DB Concepts (Notebook-Ready Examples)

This guide explains key vector database concepts with short, copy-paste-friendly examples you can run **one cell at a time** in a Jupyter notebook.

All examples assume a ChromaDB server is running (Docker or `chroma run`) and the notebook uses:
```
export CHROMA_HOST=localhost
export CHROMA_PORT=8001
```

## 0) Connect to ChromaDB
Run this once at the top of your notebook:
```
import os
import chromadb

HOST = os.getenv("CHROMA_HOST", "localhost")
PORT = int(os.getenv("CHROMA_PORT", "8001"))
client = chromadb.HttpClient(host=HOST, port=PORT)
client.heartbeat()
```

## 1) Collections
**Concept**: A collection is a named container for vectors + documents + metadata.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.count()
```

## 2) Documents and IDs
**Concept**: Each document must have a unique ID.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.add(
    ids=["d1", "d2", "d3"],
    documents=[
        "Chroma is a vector database.",
        "Vectors represent meaning.",
        "Metadata helps filtering.",
    ],
)
collection.count()
```

## 3) Metadata
**Concept**: Metadata lets you filter search results.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.add(
    ids=["d4", "d5"],
    documents=[
        "Mac users can run Chroma with Docker.",
        "Server mode uses chroma run.",
    ],
    metadatas=[
        {"topic": "mac", "source": "docs"},
        {"topic": "server", "source": "docs"},
    ],
)
```

## 4) Similarity Search (Query)
**Concept**: A query finds the most similar documents.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.query(
    query_texts=["How do I run Chroma locally?"],
    n_results=2,
)
```

## 5) Metadata Filtering
**Concept**: Filter search by metadata fields.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.query(
    query_texts=["How do I run Chroma locally?"],
    n_results=3,
    where={"topic": "mac"},
)
```

## 6) Get by ID
**Concept**: Fetch stored documents directly by ID.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.get(ids=["d1", "d4"])
```

## 7) Update Documents
**Concept**: Update a document by re-adding with the same ID.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.add(
    ids=["d2"],
    documents=["Vectors represent meaning and context."],
    metadatas=[{"topic": "vectors"}],
)
collection.get(ids=["d2"])
```

## 8) Delete Documents
**Concept**: Remove documents by ID.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.delete(ids=["d3"])
collection.count()
```

## 9) Collections List and Delete
**Concept**: You can list and remove entire collections.

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
client.list_collections()
```

```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
client.delete_collection("concepts_demo")
client.list_collections()
```

## 10) Persistence
**Concept**: Data is persisted to disk by the server container.

For Docker:
- Host path: `./chroma_data`
- Container path: `/chroma/chroma`

To reset:
```
docker stop chroma
rm -rf ./chroma_data
```

## 11) Embeddings (What happens behind the scenes)
**Concept**: Chroma stores vectors computed from text. If you pass raw text,
Chroma uses its default embedding function unless configured otherwise.

You can also supply your own embeddings (example uses dummy vectors):
```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_or_create_collection("concepts_demo")
collection.add(
    ids=["e1", "e2"],
    documents=["alpha", "beta"],
    embeddings=[[0.1, 0.2, 0.3], [0.2, 0.1, 0.0]],
)
```

## 12) Clean Up (optional)
```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
client.delete_collection("concepts_demo")
```
