# ChromaDB via Docker (macOS)

This is the Docker-first setup for running ChromaDB locally and accessing it from the notebook in this repo.

## Prerequisites
- Docker Desktop for Mac
- `curl`

## Start ChromaDB (Docker)
Port `8000` is already used by `codeforge-api` in this environment, so map Chroma to `8001`.
```
docker run -d \
  --name chroma \
  -p 8001:8000 \
  -v "$(pwd)/chroma_data:/chroma/chroma" \
  chromadb/chroma:latest
```

## Verify it is running
```
curl -s http://localhost:8001/api/v2/heartbeat
```

## Use with the notebook
Set the port before launching Jupyter:
```
export CHROMA_PORT=8001
```

Open `chromadb_local_rag_chatbot.ipynb` and run cells top to bottom.

## Stop / Restart
```
docker stop chroma
docker restart chroma
```

## Reset data (safe)
Stop the container first, then remove the data directory:
```
docker stop chroma
rm -rf ./chroma_data
```

## Troubleshooting
- **Port in use**: change the host port:
  ```
  docker run -d --name chroma -p 8002:8000 -v "$(pwd)/chroma_data:/chroma/chroma" chromadb/chroma:latest
  ```
- **Container already exists**:
  ```
  docker rm -f chroma
  ```
