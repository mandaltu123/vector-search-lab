# ChromaDB Lab

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange)
![Ollama](https://img.shields.io/badge/Ollama-LLaMA_3.1-black)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A practical exploration of ChromaDB** — from local setup to production Docker deployment, with real scripts for FAQ ingestion using OCR + LLaMA-powered structuring.

## What's Inside

- ChromaDB setup guides: local Mac, Docker, and remote client
- Concept documentation: vector DB terminology, distance metrics, collection management
- Working Python script: OCR a PDF → LLaMA structures it into Q&A pairs → ingests into ChromaDB
- Jupyter notebook for interactive exploration

## Key Script: FAQ OCR → ChromaDB Pipeline

`scripts/faq_ocr_llama.py` does the full pipeline:

```
Unstructured PDF
      │
      ▼
Tesseract OCR (pdf2image + pytesseract)
      │
      ▼
Text chunking (6000 char windows)
      │
      ▼
Ollama LLaMA: structure into Q&A pairs
      │
      ▼
ChromaDB ingestion (HttpClient)
      │
      ▼
Searchable vector FAQ store
```

## Quick Start

```bash
# Start ChromaDB
docker run -p 8001:8000 chromadb/chroma

# Install deps
pip install -r requirements.txt
cp .env.example .env

# Run the FAQ ingestion script
python scripts/faq_ocr_llama.py
```

**Prerequisites for OCR:** `brew install tesseract poppler` (macOS)

## Documentation

| File | Description |
|---|---|
| `docs/README-chromadb-concepts.md` | Collections, embeddings, distance metrics |
| `docs/README-chromadb-mac-setup.md` | Local setup on macOS |
| `docs/README-chromadb-docker.md` | Docker deployment |
| `docs/README-vector-db-terminology.md` | Key terms: HNSW, cosine, dot product, L2 |
| `docs/README-notebook.md` | Jupyter notebook guide |

## Tech Stack

- **Vector Store**: ChromaDB (local + Docker + remote)
- **LLM**: Ollama + LLaMA 3.1 (local — no API key)
- **OCR**: Tesseract via pytesseract, pdf2image

## Project Structure

```
vectordb-chroma/
├── scripts/
│   └── faq_ocr_llama.py    # OCR → LLaMA → ChromaDB pipeline
├── docs/                    # Concept + setup guides
├── requirements.txt
└── README.md
```

## License

MIT — see [LICENSE](LICENSE)
