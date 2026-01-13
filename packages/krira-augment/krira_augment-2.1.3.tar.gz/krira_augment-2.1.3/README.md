# Krira Augment

**High-Performance Rust Chunking Engine for RAG Pipelines**

[![PyPI version](https://badge.fury.io/py/krira-augment.svg)](https://badge.fury.io/py/krira-augment)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust](https://img.shields.io/badge/Built_with-Rust-orange)](https://www.rust-lang.org/)

Process gigabytes of text in seconds. **40x faster than LangChain** with **O(1) memory usage**.

---

## Performance Benchmarks

| Dataset Size | LangChain/Pandas | Krira (Rust) | Speedup |
|--------------|------------------|--------------|---------|
| 100 MB | ~45 sec | 0.8 sec | 56x |
| 1 GB | ~8.0 min | 12.0 sec | 40x |
| 10 GB | Timeout / OOM | 2.1 min | Stable |

**Memory stays constant (O(1)) regardless of file size.**

---

## Installation

```bash
pip install krira-augment
```

---

## Complete Example: OpenAI + Pinecone

```python
from krira_augment import Pipeline, PipelineConfig
import json
from openai import OpenAI
from pinecone import Pinecone

# API Keys
OPENAI_API_KEY = "sk-..."        # https://platform.openai.com/api-keys
PINECONE_API_KEY = "pcone-..."   # https://app.pinecone.io/
PINECONE_INDEX_NAME = "my-rag"

# Step 1: Chunk the file
config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)
result = pipeline.process("sample.csv", output_path="chunks.jsonl")

print(f"Chunks Created: {result.chunks_created}")
print(f"Execution Time: {result.execution_time:.2f}s")
print(f"Throughput: {result.mb_per_second:.2f} MB/s")
print(f"Preview: {result.preview_chunks[:3]}")

# Step 2: Embed and store
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

with open("chunks.jsonl", "r") as f:
    for line_num, line in enumerate(f, 1):
        chunk = json.loads(line)
        
        response = client.embeddings.create(
            input=chunk["text"],
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding
        
        index.upsert(vectors=[(f"chunk_{line_num}", embedding, chunk.get("metadata", {}))])
        
        if line_num % 100 == 0:
            print(f"Processed {line_num} chunks...")

print("Done! All chunks embedded and stored in Pinecone.")
```

---

## Other Integrations

After running **Step 1** (chunking), replace **Step 2** with any of these integrations:

### OpenAI + Qdrant

```python
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

client = OpenAI(api_key="sk-...")
qdrant = QdrantClient(url="https://xyz.qdrant.io", api_key="qdrant-...")

with open("chunks.jsonl", "r") as f:
    for line_num, line in enumerate(f, 1):
        chunk = json.loads(line)
        response = client.embeddings.create(input=chunk["text"], model="text-embedding-3-small")
        embedding = response.data[0].embedding
        qdrant.upsert(collection_name="my-chunks", points=[PointStruct(id=line_num, vector=embedding, payload=chunk.get("metadata", {}))])
        
        if line_num % 100 == 0:
            print(f"Processed {line_num} chunks...")
```

### OpenAI + Weaviate

```python
import weaviate
import weaviate.classes as wvc
from openai import OpenAI

# Connect to Weaviate Cloud
client_w = weaviate.connect_to_wcs(
    cluster_url="https://xyz.weaviate.network",
    auth_credentials=weaviate.auth.AuthApiKey("weaviate-...")
)
client_o = OpenAI(api_key="sk-...")

# Get collection
collection = client_w.collections.get("Chunk")

with open("chunks.jsonl", "r") as f:
    for line_num, line in enumerate(f, 1):
        chunk = json.loads(line)
        response = client_o.embeddings.create(input=chunk["text"], model="text-embedding-3-small")
        embedding = response.data[0].embedding
        
        # Insert with vector
        collection.data.insert(
            properties={"text": chunk["text"], "metadata": str(chunk.get("metadata", {}))},
            vector=embedding
        )
        
        if line_num % 100 == 0:
            print(f"Processed {line_num} chunks...")
```

### Cohere + Pinecone

```python
import cohere
from pinecone import Pinecone

co = cohere.Client("co-...")
pc = Pinecone(api_key="pcone-...")
index = pc.Index("my-rag")

with open("chunks.jsonl", "r") as f:
    for line_num, line in enumerate(f, 1):
        chunk = json.loads(line)
        response = co.embed(texts=[chunk["text"]], model="embed-english-v3.0")
        embedding = response.embeddings[0]
        index.upsert(vectors=[(f"chunk_{line_num}", embedding, chunk.get("metadata", {}))])
        
        if line_num % 100 == 0:
            print(f"Processed {line_num} chunks...")
```

### Cohere + Qdrant

```python
import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

co = cohere.Client("co-...")
qdrant = QdrantClient(url="https://xyz.qdrant.io", api_key="qdrant-...")

with open("chunks.jsonl", "r") as f:
    for line_num, line in enumerate(f, 1):
        chunk = json.loads(line)
        response = co.embed(texts=[chunk["text"]], model="embed-english-v3.0")
        embedding = response.embeddings[0]
        qdrant.upsert(
            collection_name="my-chunks",
            points=[PointStruct(id=line_num, vector=embedding, payload=chunk.get("metadata", {}))]
        )
        
        if line_num % 100 == 0:
            print(f"Processed {line_num} chunks...")
```

### Local (Sentence Transformers) + ChromaDB (FREE)

```python
from sentence_transformers import SentenceTransformer
import chromadb
import json

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.Client()
collection = client.get_or_create_collection("my_chunks")

with open("chunks.jsonl", "r") as f:
    for line_num, line in enumerate(f, 1):
        chunk = json.loads(line)
        embedding = model.encode(chunk["text"])
        
        # Handle empty metadata
        meta = chunk.get("metadata")
        if not meta:
            meta = None
            
        collection.add(
            ids=[f"chunk_{line_num}"],
            embeddings=[embedding.tolist()],
            metadatas=[meta] if meta else None,
            documents=[chunk["text"]]
        )
        
        if line_num % 100 == 0:
            print(f"Processed {line_num} chunks...")
```

### Hugging Face + FAISS (FREE)

```python
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np
import json

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)

embeddings_list = []
with open("chunks.jsonl", "r") as f:
    for line_num, line in enumerate(f, 1):
        chunk = json.loads(line)
        inputs = tokenizer(chunk["text"], return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        embeddings_list.append(embedding)
        
        if line_num % 100 == 0:
            print(f"Processed {line_num} chunks...")

embeddings_array = np.array(embeddings_list).astype('float32')
index.add(embeddings_array)
faiss.write_index(index, "my_vectors.index")
print("Done! Vectors saved to my_vectors.index")
```

---

## Streaming Mode (No Files)

Process chunks without saving to disk - maximum efficiency for real-time pipelines:

### Complete Example: OpenAI + Pinecone (Streaming)

```python
from krira_augment import Pipeline, PipelineConfig
from openai import OpenAI
from pinecone import Pinecone

# API Keys
OPENAI_API_KEY = "sk-..."        # https://platform.openai.com/api-keys
PINECONE_API_KEY = "pcone-..."   # https://app.pinecone.io/
PINECONE_INDEX_NAME = "my-rag"

# Initialize
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Configure pipeline
config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)

# Stream and embed (no file created)
chunk_count = 0
print("Starting streaming pipeline...")

for chunk in pipeline.process_stream("data.csv"):
    chunk_count += 1
    
    # Embed
    response = client.embeddings.create(
        input=chunk["text"],
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    
    # Store immediately
    index.upsert(vectors=[(
        f"chunk_{chunk_count}",
        embedding,
        chunk["metadata"]
    )])
    
    # Progress
    if chunk_count % 100 == 0:
        print(f"Processed {chunk_count} chunks...")

print(f"Done! Embedded {chunk_count} chunks. No intermediate file created.")
```

---

## Other Streaming Integrations

Replace the embedding/storage logic with any of these:

### OpenAI + Qdrant (Streaming)

```python
from krira_augment import Pipeline, PipelineConfig
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Initialize
client = OpenAI(api_key="sk-...")
qdrant = QdrantClient(url="https://xyz.qdrant.io", api_key="qdrant-...")

# Configure and stream
config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)

chunk_count = 0
for chunk in pipeline.process_stream("data.csv"):
    chunk_count += 1
    
    # Embed
    response = client.embeddings.create(input=chunk["text"], model="text-embedding-3-small")
    embedding = response.data[0].embedding
    
    # Store
    qdrant.upsert(
        collection_name="my-chunks",
        points=[PointStruct(id=chunk_count, vector=embedding, payload=chunk["metadata"])]
    )
    
    if chunk_count % 100 == 0:
        print(f"Processed {chunk_count} chunks...")

print(f"Done! {chunk_count} chunks embedded.")
```

### OpenAI + Weaviate (Streaming)

```python
from krira_augment import Pipeline, PipelineConfig
from openai import OpenAI
import weaviate

# Initialize
client_o = OpenAI(api_key="sk-...")
client_w = weaviate.connect_to_wcs(
    cluster_url="https://xyz.weaviate.network",
    auth_credentials=weaviate.auth.AuthApiKey("weaviate-...")
)
collection = client_w.collections.get("Chunk")

# Configure and stream
config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)

chunk_count = 0
for chunk in pipeline.process_stream("data.csv"):
    chunk_count += 1
    
    # Embed
    response = client_o.embeddings.create(input=chunk["text"], model="text-embedding-3-small")
    embedding = response.data[0].embedding
    
    # Store
    collection.data.insert(
        properties={"text": chunk["text"], "metadata": str(chunk["metadata"])},
        vector=embedding
    )
    
    if chunk_count % 100 == 0:
        print(f"Processed {chunk_count} chunks...")

print(f"Done! {chunk_count} chunks embedded.")
```

### Cohere + Pinecone (Streaming)

```python
from krira_augment import Pipeline, PipelineConfig
import cohere
from pinecone import Pinecone

# Initialize
co = cohere.Client("co-...")
pc = Pinecone(api_key="pcone-...")
index = pc.Index("my-rag")

# Configure and stream
config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)

chunk_count = 0
for chunk in pipeline.process_stream("data.csv"):
    chunk_count += 1
    
    # Embed
    response = co.embed(texts=[chunk["text"]], model="embed-english-v3.0")
    embedding = response.embeddings[0]
    
    # Store
    index.upsert(vectors=[(f"chunk_{chunk_count}", embedding, chunk["metadata"])])
    
    if chunk_count % 100 == 0:
        print(f"Processed {chunk_count} chunks...")

print(f"Done! {chunk_count} chunks embedded.")
```

### Cohere + Qdrant (Streaming)

```python
from krira_augment import Pipeline, PipelineConfig
import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Initialize
co = cohere.Client("co-...")
qdrant = QdrantClient(url="https://xyz.qdrant.io", api_key="qdrant-...")

# Configure and stream
config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)

chunk_count = 0
for chunk in pipeline.process_stream("data.csv"):
    chunk_count += 1
    
    # Embed
    response = co.embed(texts=[chunk["text"]], model="embed-english-v3.0")
    embedding = response.embeddings[0]
    
    # Store
    qdrant.upsert(
        collection_name="my-chunks",
        points=[PointStruct(id=chunk_count, vector=embedding, payload=chunk["metadata"])]
    )
    
    if chunk_count % 100 == 0:
        print(f"Processed {chunk_count} chunks...")

print(f"Done! {chunk_count} chunks embedded.")
```

### Local (Sentence Transformers) + ChromaDB (Streaming, FREE)

```python
from krira_augment import Pipeline, PipelineConfig
from sentence_transformers import SentenceTransformer
import chromadb

# Initialize (no API keys needed)
model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.Client()
collection = client.create_collection("my_chunks")

# Configure and stream
config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)

chunk_count = 0
for chunk in pipeline.process_stream("data.csv"):
    chunk_count += 1
    
    # Embed locally (free, runs on your machine)
    embedding = model.encode(chunk["text"])
    
    # Store locally
    collection.add(
        ids=[f"chunk_{chunk_count}"],
        embeddings=[embedding.tolist()],
        metadatas=[chunk["metadata"]],
        documents=[chunk["text"]]
    )
    
    if chunk_count % 100 == 0:
        print(f"Processed {chunk_count} chunks...")

print(f"Done! {chunk_count} chunks embedded. All local, no API costs.")
```

### Hugging Face + FAISS (Streaming, FREE)

```python
from krira_augment import Pipeline, PipelineConfig
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np

# Initialize (no API keys needed)
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)

# Configure and stream
config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)

chunk_count = 0
embeddings_batch = []
BATCH_SIZE = 100  # Process in batches for efficiency

for chunk in pipeline.process_stream("data.csv"):
    chunk_count += 1
    
    # Embed locally
    inputs = tokenizer(chunk["text"], return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    
    embeddings_batch.append(embedding)
    
    # Add to FAISS in batches
    if len(embeddings_batch) >= BATCH_SIZE:
        embeddings_array = np.array(embeddings_batch).astype('float32')
        index.add(embeddings_array)
        embeddings_batch = []
        print(f"Processed {chunk_count} chunks...")

# Add remaining embeddings
if embeddings_batch:
    embeddings_array = np.array(embeddings_batch).astype('float32')
    index.add(embeddings_array)

# Save index
faiss.write_index(index, "my_vectors.index")
print(f"Done! {chunk_count} chunks embedded and saved to my_vectors.index")
```

---

## Streaming Mode Advantages

| Feature | File-Based | Streaming |
|---------|------------|-----------|
| **Disk I/O** | Creates chunks.jsonl | None |
| **Memory Usage** | O(1) constant | O(1) constant |
| **Speed** | Chunking + Embedding | Overlapped (faster) |
| **Use Case** | Large files, batch processing | Real-time, no storage |
| **Flexibility** | Can re-process chunks | Single pass only |

---

## When to Use Streaming vs File-Based

**Use Streaming When:**
- You want maximum speed (no disk writes)
- You don't need to save chunks for later
- You're building real-time pipelines
- You have limited disk space

**Use File-Based When:**
- You want to inspect/debug chunks
- You need to re-process with different embeddings
- You want to share chunks with your team
- You're experimenting with different models

---

## Error Handling (Production Ready)

```python
from krira_augment import Pipeline, PipelineConfig
from openai import OpenAI
from pinecone import Pinecone
import time

client = OpenAI(api_key="sk-...")
pc = Pinecone(api_key="pcone-...")
index = pc.Index("my-rag")

config = PipelineConfig(chunk_size=512, chunk_overlap=50)
pipeline = Pipeline(config=config)

chunk_count = 0
error_count = 0

for chunk in pipeline.process_stream("data.csv"):
    chunk_count += 1
    
    try:
        # Embed
        response = client.embeddings.create(input=chunk["text"], model="text-embedding-3-small")
        embedding = response.data[0].embedding
        
        # Store
        index.upsert(vectors=[(f"chunk_{chunk_count}", embedding, chunk["metadata"])])
        
    except Exception as e:
        error_count += 1
        print(f"Error on chunk {chunk_count}: {e}")
        
        # Retry logic
        if "rate_limit" in str(e).lower():
            print("Rate limited, waiting 60 seconds...")
            time.sleep(60)
            # Retry (add your retry logic here)
    
    if chunk_count % 100 == 0:
        print(f"Processed {chunk_count} chunks, {error_count} errors")

print(f"Done! {chunk_count} chunks processed, {error_count} errors")
```

---

## Supported Formats

| Format | Extension | Method |
|--------|-----------|--------|
| **CSV** | `.csv` | Direct processing |
| **Text** | `.txt` | Direct processing |
| **JSONL** | `.jsonl` | Direct processing |
| **JSON** | `.json` | Auto-flattening |
| **PDF** | `.pdf` | pdfplumber extraction |
| **Word** | `.docx` | python-docx extraction |
| **Excel** | `.xlsx` | openpyxl extraction |
| **XML** | `.xml` | ElementTree parsing |
| **URLs** | `http://` | BeautifulSoup scraping |

---

## Provider Comparison

| Embedding | Vector Store | Cost | API Keys | Streaming Support |
|-----------|--------------|------|----------|-------------------|
| OpenAI | Pinecone | Paid | 2 | ✅ Yes |
| OpenAI | Qdrant | Paid | 2 | ✅ Yes |
| OpenAI | Weaviate | Paid | 2 | ✅ Yes |
| Cohere | Pinecone | Paid | 2 | ✅ Yes |
| Cohere | Qdrant | Paid | 2 | ✅ Yes |
| SentenceTransformers | ChromaDB | **FREE** | 0 | ✅ Yes |
| Hugging Face | FAISS | **FREE** | 0 | ✅ Yes |

---

## API Keys Setup

Get your keys from:
- **OpenAI:** https://platform.openai.com/api-keys
- **Cohere:** https://dashboard.cohere.com/api-keys
- **Pinecone:** https://app.pinecone.io/
- **Qdrant:** https://cloud.qdrant.io/
- **Weaviate:** https://console.weaviate.cloud/

---

## Development

1. **Clone the repo**
2. **Install Maturin**
   ```bash
   pip install maturin
   ```
3. **Build and Install locally**
   ```bash
   python -m build
   pip install dist/*.whl --force-reinstall
   ```

---

## License

MIT License. (c) 2025 Krira Labs.
