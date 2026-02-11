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
    prompt = f"""
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
"""
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

# ---- 3) FAQ chat loop (retrieval + LLM) ----
def parse_qa(doc: str):
    parts = re.split(r"\nAnswer:\s*", doc, maxsplit=1, flags=re.IGNORECASE)
    q = parts[0].replace("Question:", "").strip() if parts else ""
    a = parts[1].strip() if len(parts) > 1 else ""
    return q, a

def faq_search(query: str, k: int = 4):
    res = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        q, a = parse_qa(doc)
        hits.append({
            "question": q,
            "answer": a,
            "distance": dist,
            "row_id": meta.get("row_id"),
            "source": meta.get("source"),
        })
    return hits

SYSTEM_PROMPT = """You are a FAQ assistant.
Answer ONLY from the provided FAQ context.
If not present, say exactly:
"I don't know based on the FAQ."
Then ask ONE clarifying question.
Always include citations like:
(SOURCE: faq_unstructured.pdf, ROW: <row_id>)
"""

def ollama_chat(prompt: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", "").strip()

def rag_answer_faq(question: str, k: int = 4, max_distance: float = 0.8):
    hits = faq_search(question, k=k)
    if not hits or min(h["distance"] for h in hits) > max_distance:
        return "I don't know based on the FAQ. Can you clarify your question?", hits

    context = "\n\n".join(
        f"[ROW {h['row_id']}] Q: {h['question']}\nA: {h['answer']}"
        for h in hits
    )
    prompt = f"""{SYSTEM_PROMPT}

FAQ CONTEXT:
{context}

User question: {question}
Answer:"""

    return ollama_chat(prompt), hits

if __name__ == "__main__":
    print("\nFAQ chat is ready. Ask a question (type 'exit' to quit).")
    while True:
        user_q = input("You: ").strip()
        if user_q.lower() in {"exit", "quit"}:
            break
        answer, hits = rag_answer_faq(user_q)
        print(f"Bot: {answer}\n")
        print("Retrieved matches:")
        for h in hits:
            print(f"- row_id={h['row_id']} dist={h['distance']:.4f} q={h['question']}")
        print()