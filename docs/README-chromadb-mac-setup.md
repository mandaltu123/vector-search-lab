# ChromaDB on macOS (MacBook) — Local Setup Guide

## Overview
This guide shows two supported ways to run ChromaDB locally on macOS:
- **Method A (Embedded mode)**: In-process `PersistentClient` for local dev.
- **Method B (Server mode)**: `chroma run` daemon you can start/stop/restart.
- **Method C (Docker, optional)**: Clean containerized server if you prefer.

It is beginner-friendly and copy-paste-ready. All commands assume **zsh**, **Python 3.10–3.12**, and **pip**.

## Prerequisites
- macOS (Apple Silicon or Intel)
- `python3` **3.10–3.12** (ChromaDB does not support Python 3.14 yet)
- `pip` (bundled with Python)
- Terminal shell: `zsh`
- Optional: Docker Desktop (for Method C)

Check your Python version:
```
python3 --version
```

## Quickstart (fast path)
If you just want local embedded usage in a project folder:
```
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install chromadb
python3 - <<'PY'
import chromadb
from chromadb import PersistentClient

client = PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection("quickstart")
collection.add(documents=["hello world"], ids=["doc1"])
print(collection.query(query_texts=["hello"], n_results=1))
PY
```

## How to use with the provided notebook
The repo includes `chromadb_local_rag_chatbot.ipynb`.

Set environment variables before launching Jupyter:
```
export LLM_PROVIDER=ollama   # or openai
export OLLAMA_MODEL=llama3.1
export OLLAMA_URL=http://localhost:11434
```

Then run the notebook in your preferred environment. If using `openai`, set the appropriate API key and provider config in your notebook or environment.

## Method A: Embedded mode (PersistentClient)
**Best for**: local dev, tests, scripts, notebooks.

### Prerequisites
- Python 3.10+
- `pip`

### Install steps
```
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install chromadb
```

### Basic usage
```
python3 - <<'PY'
from chromadb import PersistentClient

client = PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection("demo")
collection.add(ids=["1"], documents=["hello from chroma"])
print(collection.count())
PY
```

### Verification
```
python3 - <<'PY'
from chromadb import PersistentClient
client = PersistentClient(path="./chroma_data")
collection = client.get_collection("demo")
print(collection.query(query_texts=["hello"], n_results=1))
PY
```

### Troubleshooting
- **Python env issues**: ensure your virtual env is active:
  ```
  which python3
  ```
  It should point to `.venv/bin/python3`.
- **Python 3.14 error** (`ConfigError: unable to infer type for attribute "chroma_server_nofile"`):
  Use Python 3.10–3.12 and recreate your venv.
- **Permission errors**: use a writable path, e.g. `./chroma_data` or `~/chroma_data`.
- **Version conflicts**: upgrade and pin:
  ```
  pip install --upgrade chromadb
  ```

## Method B: Server mode (chroma run)
**Best for**: local daemon, multiple clients, service-like usage.

### Prerequisites
- Python 3.10+
- `pip`

### Install steps
```
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install chromadb
```

### Start / Stop / Restart
**Start (foreground):**
```
chroma run --host 0.0.0.0 --port 8000 --path ./chroma_data
```

**Start (background):**
```
nohup chroma run --host 0.0.0.0 --port 8000 --path ./chroma_data > chroma.log 2>&1 &
echo $! > chroma.pid
```

**Stop (if started in background):**
```
kill "$(cat chroma.pid)"
```

**Restart (background):**
```
kill "$(cat chroma.pid)"
nohup chroma run --host 0.0.0.0 --port 8000 --path ./chroma_data > chroma.log 2>&1 &
echo $! > chroma.pid
```

### Verification
```
curl -s http://localhost:8000/api/v2/heartbeat
```

### Troubleshooting
- **Port in use**:
  ```
  lsof -i :8000
  ```
  Change the port or stop the process using it.
- **Permission issues**: ensure `--path` is writable.
- **Python env issues**: confirm `chroma` comes from your venv:
  ```
  which chroma
  ```
 - **Python 3.14 error**: install Python 3.11 or 3.12 and recreate your venv.

## Method C: Docker (optional)
**Best for**: isolation, avoiding local Python deps.

### Prerequisites
- Docker Desktop for Mac

### Start / Stop / Restart
**Start (if port 8000 is free):**
```
docker run -d \
  --name chroma \
  -p 8000:8000 \
  -v "$(pwd)/chroma_data:/chroma/chroma" \
  chromadb/chroma:latest
```

**Start (if port 8000 is already in use):**
```
docker run -d \
  --name chroma \
  -p 8001:8000 \
  -v "$(pwd)/chroma_data:/chroma/chroma" \
  chromadb/chroma:latest
```

**Stop:**
```
docker stop chroma
```

**Restart:**
```
docker restart chroma
```

### Verification
```
curl -s http://localhost:8000/api/v2/heartbeat
```
If you mapped a different host port (e.g. `8001`), use that instead.

### Troubleshooting
- **Port in use**: either stop the process using `8000` or map to another port:
  ```
  lsof -i :8000
  docker run -d --name chroma -p 8001:8000 -v "$(pwd)/chroma_data:/chroma/chroma" chromadb/chroma:latest
  ```
- **Permission issues on volume**: ensure the host folder is writable:
  ```
  ls -la ./chroma_data
  ```

## Health checks / verification
- **Server heartbeat**:
  ```
  curl -s http://localhost:8000/api/v2/heartbeat
  ```
- **Python client (server mode)**:
  ```
  python3 - <<'PY'
  import chromadb
  client = chromadb.HttpClient(host="localhost", port=8000)
  print(client.heartbeat())
  PY
  ```

## Persistence & backups
### Where data is stored
- **Embedded & server mode**: `--path` or `PersistentClient(path=...)` (e.g. `./chroma_data`)
- **Docker**: host path mapped to `/chroma/chroma` inside the container

### Change the path
- Embedded:
  ```
  client = PersistentClient(path="/absolute/path/to/chroma_data")
  ```
- Server:
  ```
  chroma run --path /absolute/path/to/chroma_data
  ```
- Docker:
  ```
  -v "/absolute/path/to/chroma_data:/chroma/chroma"
  ```

### Clean/reset safely
Stop any running server first, then remove the data directory:
```
rm -rf ./chroma_data
```

### Backup
Use `tar` to snapshot your data directory:
```
tar -czf chroma_data_backup.tgz ./chroma_data
```

## Troubleshooting FAQ
- **Port already in use**:
  ```
  lsof -i :8000
  ```
  Stop the process or use a different port.
- **Permission denied**:
  ```
  ls -ld ./chroma_data
  ```
  Use a path you can write to, like `~/chroma_data`.
- **Python env issues**:
  ```
  which python3
  which chroma
  ```
  Ensure both are from your active `.venv`.
- **Version conflicts**:
  ```
  pip install --upgrade chromadb
  pip install "chromadb<1.0.0"
  ```
  If you need a specific version, pin it in `requirements.txt`.

## Appendix: Useful commands
```
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip chromadb
python3 -c "import chromadb; print(chromadb.__version__)"
```
