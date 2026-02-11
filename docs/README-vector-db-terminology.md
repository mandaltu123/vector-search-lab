# Vector DB Terminology (Interview Cheat Sheet)

Concise definitions for common vector database concepts, optimized for interview prep.

## Core Concepts
- **Vector (Embedding)**: Numeric representation of data (text/image/audio) in high‑dimensional space where semantic similarity is preserved.
- **Embedding Model**: Model that converts raw data into embeddings (e.g., a sentence encoder).
- **Vector Dimension**: Length of the embedding vector (e.g., 384, 768, 1536). Fixed per model.
- **Similarity / Distance Metric**: How closeness is measured (cosine, dot product, L2).
- **Nearest Neighbor (NN) Search**: Finding vectors closest to a query vector.
- **Approximate Nearest Neighbor (ANN)**: Faster NN using indexing structures with some accuracy tradeoffs.
- **Exact Search**: Brute‑force comparison against all vectors; accurate but slow at scale.
- **Top‑K**: Number of closest results returned.
- **Score / Distance**: Numeric result of similarity or distance. Higher or lower depending on metric.
- **Normalization**: Scaling vectors to unit length (common for cosine similarity).
- **Embedding Drift**: Changes in embedding behavior when model version changes.

## Indexing & Performance
- **Index**: Data structure that accelerates vector search (e.g., HNSW, IVF).
- **HNSW**: Graph‑based ANN index; good recall and speed, higher memory use.
- **IVF**: Inverted file index; clusters vectors into centroids to reduce search space.
- **PQ (Product Quantization)**: Compresses vectors for memory savings at some accuracy cost.
- **OPQ**: Optimized PQ; rotates vectors before quantization for better accuracy.
- **Scalar Quantization**: Compresses floats to lower‑precision values.
- **Recall**: Fraction of true nearest neighbors found by ANN vs exact search.
- **Precision@K**: Fraction of top‑K results that are relevant.
- **Latency**: Time to run a search query.
- **Throughput**: Queries per second the system can handle.
- **Warm vs Cold Cache**: Performance differences depending on in‑memory index cache.
- **Build Time**: Time to create index from vectors (often expensive).
- **Recall**: Fraction of true nearest neighbors found by ANN vs exact search.
- **Latency**: Time to run a search query.
- **Throughput**: Queries per second the system can handle.

## Data & Schema
- **Collection / Namespace**: Logical grouping of vectors and metadata.
- **Document**: Original payload (text, image, etc.) stored alongside embedding.
- **ID**: Unique identifier for a vector/document pair.
- **Metadata**: Key‑value attributes used for filtering (e.g., `topic=finance`).
- **Upsert**: Insert or update by ID (idempotent writes).
- **Delete**: Remove vectors by ID or metadata filter.
- **Payload**: Application‑specific fields attached to vectors (often called metadata).
- **Schema / Data Model**: Rules for what metadata fields exist and their types.

## Query & Filtering
- **Query Vector**: Embedding of the input query used in search.
- **Filtering**: Restricting search results using metadata constraints.
- **Hybrid Search**: Combines vector similarity with keyword or metadata filters.
- **Re‑ranking**: Secondary model reorders top‑K results for accuracy.
- **Multi‑vector / Multi‑modal**: Multiple embeddings per item or different modalities (text + image).
- **Dense vs Sparse**: Dense embeddings vs sparse term vectors (BM25, SPLADE).
- **Fusion**: Combining scores from dense and sparse retrievers.

## Retrieval‑Augmented Generation (RAG)
- **RAG**: Using retrieved documents to ground LLM responses.
- **Chunking**: Splitting documents into smaller pieces for embeddings.
- **Chunk Size / Overlap**: Controls how much text per chunk and shared context.
- **Context Window**: Max tokens an LLM can accept as input.
- **Citation / Attribution**: Linking answers to retrieved sources.
- **Retriever**: Component that fetches candidates (vector DB, keyword search).
- **Reader / Generator**: LLM that produces the final answer from context.
- **Query Rewrite**: LLM reformulates the user query to improve retrieval.
- **Answerability**: A measure of whether the context contains enough info to answer.

## Consistency & Operations
- **Persistence**: Saving vectors to disk so data survives restarts.
- **Durability**: Guarantee that written data is not lost.
- **Replication**: Copies of data across nodes for fault tolerance.
- **Sharding**: Split data across multiple nodes for scale.
- **Compaction**: Background process to optimize storage layout.
- **Snapshot / Backup**: Point‑in‑time copy of index and metadata.
- **Schema Migration**: Changing metadata structure or vector dimension safely.

## Metrics & Evaluation
- **Precision**: Fraction of returned results that are relevant.
- **Recall**: Fraction of all relevant results that are returned.
- **MRR**: Mean Reciprocal Rank; emphasizes correct results appearing early.
- **NDCG**: Ranking quality metric with position‑based discounting.
- **Ground Truth**: Labeled data used for evaluation.
- **Hit@K**: Whether a correct item appears in the top‑K results.
- **Coverage**: Percent of queries that return at least one relevant result.

## Security & Compliance
- **Access Control**: Permissions controlling who can read/write.
- **Encryption at Rest**: Data stored on disk is encrypted.
- **Encryption in Transit**: Data is encrypted during network transfer.
- **PII/PHI**: Sensitive data categories requiring strict handling.
- **Data Retention**: Policy for how long vectors and documents are kept.
- **Redaction**: Removing sensitive fields before embedding or storage.

## System Design Topics (Interview Prompts)
- **Why vector DB vs relational DB?**: Vector DBs optimize for similarity search and ANN indexes.
- **How to choose a metric?**: Depends on embedding model and use case (cosine often for normalized embeddings).
- **When use ANN?**: At scale; exact search is too slow for large datasets.
- **How to reduce latency?**: Better indexing, filtering, smaller vectors, caching, lower top‑K.
- **How to improve quality?**: Better embeddings, chunking strategy, metadata filters, re‑ranking.
- **How to handle updates?**: Use upserts, background re‑indexing, and idempotent pipelines.
- **How to monitor quality?**: Evaluate on golden queries, track MRR/Recall over time.

## Quick One‑Liners
- **“Vector DB”**: Database optimized for similarity search over embeddings.
- **“Embedding”**: Dense numeric representation of meaning.
- **“ANN”**: Fast approximate search with good recall.
- **“RAG”**: Retrieval‑augmented LLM responses.
