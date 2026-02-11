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

## 12) OCR + LLM Extraction (PDF FAQ → Chroma)
**Concept**: Use OCR to extract text from a PDF, then use an LLM to structure Q/A pairs,
and upsert into Chroma. This example streams tokens and chunks OCR text to reduce prompt size.

```
import os
import json
import re
import time
import urllib.request
from pdf2image import convert_from_path
import pytesseract
import chromadb

PDF_PATH = "/Users/tsm/work/learn-perosnal/vectordb-chroma/faq-data/faq_unstructured.pdf"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))
OLLAMA_RETRIES = int(os.getenv("OLLAMA_RETRIES", "5"))

HOST = os.getenv("CHROMA_HOST", "localhost")
PORT = int(os.getenv("CHROMA_PORT", "8001"))

client = chromadb.HttpClient(host=HOST, port=PORT)
collection = client.get_or_create_collection("faq_ocr_llama")

# ---- 1) OCR the PDF ----
images = convert_from_path(PDF_PATH, dpi=300)
ocr_text = "\n".join(pytesseract.image_to_string(img) for img in images).strip()
if not ocr_text:
    raise ValueError("OCR produced no text. Check Tesseract install or PDF quality.")

# ---- 2) Chunk OCR text to reduce prompt size ----
def chunk_text(text: str, max_chars: int = 6000):
    parts = []
    buf = []
    size = 0
    for line in text.splitlines():
        if size + len(line) + 1 > max_chars and buf:
            parts.append("\n".join(buf))
            buf = []
            size = 0
        buf.append(line)
        size += len(line) + 1
    if buf:
        parts.append("\n".join(buf))
    return parts

chunks = chunk_text(ocr_text, max_chars=6000)

def ollama_generate_stream(prompt: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    out = []
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
        for line in resp:
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                out.append(data["response"])
            if data.get("done"):
                break
    return "".join(out).strip()

def extract_qa_pairs(text: str):
    prompt = f\"\"\"
You are a strict JSON extractor.

From the text below, extract FAQ question/answer pairs.
Return ONLY valid JSON array of objects like:
[
  {{"question": "...", "answer": "..."}}
]

Rules:
- Keep answers concise but complete.
- Ignore headings or unrelated text.
- If no Q/A pairs, return [].

TEXT:
{text}
\"\"\"
    last_err = None
    for attempt in range(OLLAMA_RETRIES):
        try:
            raw = ollama_generate_stream(prompt)
            json_text = raw[raw.find("["): raw.rfind("]") + 1]
            return json.loads(json_text)
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise last_err

all_pairs = []
for chunk in chunks:
    all_pairs.extend(extract_qa_pairs(chunk))

documents, metadatas, ids = [], [], []
for idx, item in enumerate(all_pairs):
    q = re.sub(r"\s+", " ", item.get("question", "")).strip()
    a = re.sub(r"\s+", " ", item.get("answer", "")).strip()
    if not q or not a:
        continue
    documents.append(f"Question: {q}\nAnswer: {a}")
    metadatas.append({"source": "faq_unstructured.pdf", "row_id": idx})
    ids.append(f"faq-ocr-{idx:06d}")

collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
print("Loaded rows:", len(documents))
print("Collection count:", collection.count())
```

## 13) Clean Up (optional)
```
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
client.delete_collection("concepts_demo")
```
