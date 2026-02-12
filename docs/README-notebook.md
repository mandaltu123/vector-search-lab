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

## Example: Load FAQ PDF into Chroma
Use this to parse the unstructured FAQ PDF and upsert into Chroma:
```
import os
import re
import chromadb
from pypdf import PdfReader

PDF_PATH = "/Users/tsm/work/learn-perosnal/vectordb-chroma/faq-data/faq_unstructured.pdf"

HOST = os.getenv("CHROMA_HOST", "localhost")
PORT = int(os.getenv("CHROMA_PORT", "8001"))

client = chromadb.HttpClient(host=HOST, port=PORT)
collection = client.get_or_create_collection("faq_unstructured")

# ---- Extract text from PDF ----
reader = PdfReader(PDF_PATH)
raw_pages = [(i, (p.extract_text() or "")) for i, p in enumerate(reader.pages)]
raw_text = "\n".join(text for _, text in raw_pages)

if not raw_text.strip():
    raise ValueError("No text extracted from PDF. Is it scanned? Consider OCR.")

# ---- Clean text ----
raw_text = re.sub(r"-\n(\w)", r"\1", raw_text)
raw_text = re.sub(r"\r\n?", "\n", raw_text)
lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]

def is_question(line: str) -> bool:
    if not line:
        return False
    if line.lower().startswith("frequently asked questions"):
        return False
    if line.endswith("?"):
        return True
    return bool(re.match(r"^(How|What|Why|When|Where|Who|Can|Is|Do|Does|Are|Will)\b", line))

def clean(s: str) -> str:
    return " ".join(s.split()).strip()

documents, metadatas, ids = [], [], []
current_q = None
current_a_lines = []
row_idx = 0

for ln in lines:
    if is_question(ln):
        if current_q and current_a_lines:
            answer = clean(" ".join(current_a_lines))
            documents.append(f"Question: {clean(current_q)}\nAnswer: {answer}")
            metadatas.append({"source": "faq_unstructured.pdf", "row_id": row_idx})
            ids.append(f"faq-pdf-{row_idx:06d}")
            row_idx += 1
        current_q = ln
        current_a_lines = []
    else:
        if current_q:
            current_a_lines.append(ln)

if current_q and current_a_lines:
    answer = clean(" ".join(current_a_lines))
    documents.append(f"Question: {clean(current_q)}\nAnswer: {answer}")
    metadatas.append({"source": "faq_unstructured.pdf", "row_id": row_idx})
    ids.append(f"faq-pdf-{row_idx:06d}")

if not documents:
    raise ValueError("No Q/A pairs parsed. Update parsing rules to match PDF format.")

collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

print("Loaded rows:", len(documents))
print("Collection count:", collection.count())
```

## Stop services (optional)
```
docker stop chroma
```

## FAQ OCR + Llama script (run / access / test)
Script: `scripts/faq_ocr_llama.py`

### Install deps (macOS)
```
brew install tesseract poppler
python -m pip install pytesseract pdf2image pillow
```

### Env vars
```
export CHROMA_HOST=localhost
export CHROMA_PORT=8001

export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.1:latest"
export OLLAMA_TIMEOUT="30"
export OLLAMA_RETRIES="5"
```

### Run
```
python3 scripts/faq_ocr_llama.py
```

### Test (interactive chat)
After the script loads the FAQ, it enters a prompt. Example:
```
You: How do I reset my password?
You: I want to cancel my subscription
You: exit
```

## FAQ OCR + Llama flow (what is happening)
### Flow diagram
```
PDF (faq_unstructured.pdf)
        |
        v
OCR (pdf2image + pytesseract)
        |
        v
Chunked text
        |
        v
Ollama LLM (streaming JSON extraction)
        |
        v
Q/A pairs -> documents + metadata
        |
        v
ChromaDB (collection: faq_ocr_llama)
        |
        v
User question -> vector search -> context
        |
        v
Ollama LLM (answer + citations)
```

### What is used and why (table)
| Step | Component | Purpose | Where in script |
|---|---|---|---|
| 1 | `pdf2image`, `pytesseract` | OCR the PDF into text | OCR block |
| 2 | Chunking logic | Reduce prompt size, avoid context overflow | `chunk_text()` |
| 3 | Ollama `/api/generate` (streaming) | Extract Q/A pairs as JSON | `ollama_generate_stream()` + `extract_qa_pairs()` |
| 4 | `chromadb.HttpClient` | Store Q/A into Chroma | `collection.upsert(...)` |
| 5 | Vector search | Find relevant FAQ entries | `faq_search()` |
| 6 | Ollama `/api/generate` (non-streaming) | Produce final answer with citations | `ollama_chat()` + `rag_answer_faq()` |

### How the answers are produced
- OCR reads the PDF and produces raw text.
- The text is chunked so each LLM call is smaller and reliable.
- Ollama extracts clean JSON Q/A pairs from each chunk.
- Each Q/A is stored in Chroma as a document with metadata.
- When you ask a question, Chroma retrieves the closest FAQ items.
- The retrieved FAQ context is fed to Ollama to produce a grounded answer with citations.

## Interview prep topics (from this use case)
| Topic | What to know | Where it shows up here |
|---|---|---|
| Vector DB basics | Collections, documents, metadata, upsert, delete | Chroma `collection` usage |
| Vector search | Similarity search, Top‑K, distance/score | `collection.query(...)` |
| Embeddings | How text becomes vectors, embedding size/quality | Chroma embeddings under the hood |
| ANN vs exact search | Trade‑offs between speed and recall | Vector DB design questions |
| RAG pipeline | Retrieval → context → generation | `faq_search()` + `rag_answer_faq()` |
| Prompting & grounding | System prompts, constraints, citations | `SYSTEM_PROMPT` in script |
| Hallucination control | Refuse when no good match, cite sources | `max_distance` + citations |
| OCR & parsing | PDF → text → structured Q/A | `pdf2image`, `pytesseract` |
| LLM invocation | API call, streaming, retries, timeouts | Ollama `/api/generate` |
| Chunking | Reduce prompt size, avoid truncation | `chunk_text()` |
| Evaluation | Check answer relevance, inspect matches | Debug list of retrieved hits |
| Ops & reliability | Env vars, timeouts, retries | `OLLAMA_*` configs |
