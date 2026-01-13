# SOMA Architecture - Visual Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT                                  │
│  (Web Browser / API Client / Command Line / Frontend)          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      API SERVER LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         FastAPI Server (main_server.py)                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   /tokenize  │  │  /embed      │  │ /reconstruct │  │  │
│  │  │   /search    │  │  /docs       │  │    /health   │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Function Calls
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    PROCESSING LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TOKENIZATION                                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ core_tokenizer.py (OWN)                            │  │  │
│  │  │  - Multiple strategies (space, word, char, etc.)   │  │  │
│  │  │  - UID generation (XorShift64*)                    │  │  │
│  │  │  - Frontend/Backend calculation                    │  │  │
│  │  │  - TokenRecord objects                             │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  EMBEDDINGS                                              │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ embedding_generator.py (OWN + EXTERNAL)            │  │  │
│  │  │  - Feature-based (OWN)                             │  │  │
│  │  │  - Semantic (OWN - trained)                        │  │  │
│  │  │  - Hybrid (OWN + sentence-transformers)            │  │  │
│  │  │  - Hash (OWN)                                      │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SEMANTIC TRAINING (Optional)                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ semantic_trainer.py (OWN)                          │  │  │
│  │  │  - Co-occurrence matrix                            │  │  │
│  │  │  - Embedding training                              │  │  │
│  │  │  - Model saving/loading                            │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  VECTOR STORE                                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ vector_store.py (OWN + EXTERNAL)                   │  │  │
│  │  │  - FAISS (EXTERNAL - high performance)             │  │  │
│  │  │  - ChromaDB (EXTERNAL - easy to use)               │  │  │
│  │  │  - Unified interface (OWN)                         │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SIMILARITY SEARCH                                       │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ vector_store.py                                    │  │  │
│  │  │  - Query embedding                                 │  │  │
│  │  │  - Similarity search                               │  │  │
│  │  │  - Results ranking                                 │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Tokens     │  │  Embeddings  │  │ Vector Store │         │
│  │  (Memory)    │  │  (Disk/NPY)  │  │  (FAISS/DB)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │   Semantic   │  │   Metadata   │                           │
│  │   Model      │  │   (JSON)     │                           │
│  │   (Pickle)   │  │              │                           │
│  └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
INPUT TEXT
    │
    ▼
┌─────────────────────────────────────┐
│   TOKENIZATION (core_tokenizer.py)  │
│   ┌───────────────────────────────┐ │
│   │ 1. Text Input                 │ │
│   │ 2. Apply Tokenization Strategy│ │
│   │ 3. Generate UIDs (XorShift64*)│ │
│   │ 4. Calculate Frontend Digits  │ │
│   │ 5. Compose Backend Numbers    │ │
│   │ 6. Assign Neighbor UIDs       │ │
│   │ 7. Generate Content/Global IDs│ │
│   │ 8. Create TokenRecord Objects │ │
│   └───────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ▼
    TokenRecord Objects
    (text, uid, stream, frontend, backend, ...)
               │
               ▼
┌─────────────────────────────────────┐
│  EMBEDDING GENERATION               │
│  (embedding_generator.py)           │
│   ┌───────────────────────────────┐ │
│   │ Strategy: feature_based       │ │
│   │ 1. Extract Features:          │ │
│   │    - UID bytes (8)            │ │
│   │    - Frontend one-hot (9)     │ │
│   │    - Backend bytes (8)        │ │
│   │    - Content ID (1)           │ │
│   │    - Global ID bytes (8)      │ │
│   │    - Neighbor UIDs (16)       │ │
│   │    - Index position (1)       │ │
│   │    - Stream type (9)          │ │
│   │    - Text features (~20)      │ │
│   │ 2. Project to 768 dimensions  │ │
│   │ 3. Return embedding vector    │ │
│   └───────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ▼
    768-dimensional Embedding Vector
               │
               ▼
┌─────────────────────────────────────┐
│  VECTOR STORE (vector_store.py)     │
│   ┌───────────────────────────────┐ │
│   │ 1. Add tokens + embeddings    │ │
│   │ 2. Store in FAISS/ChromaDB    │ │
│   │ 3. Create token mappings      │ │
│   │ 4. Index for search           │ │
│   └───────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ▼
    Vector Store (Indexed)
               │
               ▼
┌─────────────────────────────────────┐
│  SIMILARITY SEARCH                  │
│   ┌───────────────────────────────┐ │
│   │ 1. Query embedding            │ │
│   │ 2. Search vector store        │ │
│   │ 3. Calculate distances        │ │
│   │ 4. Rank results               │ │
│   │ 5. Return top-K results       │ │
│   └───────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ▼
    Search Results
    (similar tokens with distances)
```

## Component Ownership Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    OWN/CUSTOM COMPONENTS                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ✅ Tokenization Engine (core_tokenizer.py)           │  │
│  │ ✅ UID Generation (unique_identifier.py)             │  │
│  │ ✅ Feature Extraction (embedding_generator.py)       │  │
│  │ ✅ Embedding Projection (embedding_generator.py)     │  │
│  │ ✅ Semantic Training (semantic_trainer.py)           │  │
│  │ ✅ Vector Store Interface (vector_store.py)          │  │
│  │ ✅ API Logic (main_server.py)                        │  │
│  │ ✅ Integration Adapters (vocabulary_adapter.py)      │  │
│  │ ✅ Compression Algorithms (compression_algorithms.py)│  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 EXTERNAL DEPENDENCIES                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ⚙️  NumPy - Numerical operations                     │  │
│  │ ⚙️  FastAPI - Web framework                          │  │
│  │ ⚙️  Uvicorn - ASGI server                            │  │
│  │ ⚙️  Pydantic - Data validation                       │  │
│  │ ⚙️  FAISS - Vector database (optional)               │  │
│  │ ⚙️  ChromaDB - Vector database (optional)            │  │
│  │ ⚙️  sentence-transformers - Hybrid embeddings (opt)  │  │
│  │ ⚙️  transformers - Model integration (optional)      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Tokenization Flow

```
Text Input
    │
    ▼
┌─────────────────┐
│ Tokenization    │
│ Strategies:     │
│  - space        │
│  - word         │
│  - char         │
│  - grammar      │
│  - subword      │
│  - byte         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Token Objects   │
│  - text         │
│  - index        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ UID Assignment  │
│ (XorShift64*)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Frontend Calc   │
│ (Numerology)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend Compose │
│ (Features)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Neighbor UIDs   │
│ (Context)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TokenRecord     │
│ (Complete)      │
└─────────────────┘
```

## Embedding Generation Flow

```
TokenRecord
    │
    ▼
┌─────────────────┐
│ Feature Extract │
│  - UID (8)      │
│  - Frontend (9) │
│  - Backend (8)  │
│  - Content (1)  │
│  - Global (8)   │
│  - Neighbors(16)│
│  - Index (1)    │
│  - Stream (9)   │
│  - Text (~20)   │
└────────┬────────┘
         │
         ▼
   ~60-100 dims
         │
         ▼
┌─────────────────┐
│ Projection      │
│ Matrix (768)    │
└────────┬────────┘
         │
         ▼
   768-dim Vector
         │
         ▼
┌─────────────────┐
│ Embedding       │
│ (float32)       │
└─────────────────┘
```

## Vector Store Architecture

```
┌─────────────────────────────────────────────────────────┐
│              VECTOR STORE INTERFACE                     │
│              (vector_store.py - OWN)                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐        ┌───────────────┐
│  FAISS Store  │        │ ChromaDB Store│
│ (EXTERNAL)    │        │ (EXTERNAL)    │
│               │        │               │
│ - IndexFlatL2 │        │ - Persistent  │
│ - High perf   │        │ - Easy to use │
│ - In-memory   │        │ - Metadata    │
└───────────────┘        └───────────────┘
```

## API Request Flow

```
Client Request
    │
    ▼
┌─────────────────┐
│ FastAPI Server  │
│ (main_server.py)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Endpoint Handler│
│  - /tokenize    │
│  - /embed       │
│  - /search      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Business Logic  │
│  - Tokenization │
│  - Embeddings   │
│  - Vector Store │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Response        │
│ (JSON)          │
└─────────────────┘
```

## Semantic Training Flow

```
Token Streams
    │
    ▼
┌─────────────────┐
│ Build Vocabulary│
│  - Count tokens │
│  - Filter freq  │
│  - Create map   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Co-occurrence   │
│ Matrix          │
│  - Window size  │
│  - Context      │
│  - Frequency    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Initialize      │
│ Embeddings      │
│ (Random)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Training Loop   │
│  - Epochs       │
│  - Updates      │
│  - Normalize    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Trained Model   │
│ (Pickle)        │
└─────────────────┘
```

## Integration Flow

```
SOMA Tokens
    │
    ▼
┌─────────────────┐
│ Vocabulary      │
│ Adapter         │
│ (OWN + EXT)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Tokenizer │
│ (transformers)  │
│ (EXTERNAL)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model IDs       │
│ (BERT/GPT/T5)   │
└─────────────────┘
```

---

## Key Algorithms

### 1. XorShift64* PRNG (OWN)
```
State: 64-bit integer
Operations:
  x ^= (x >> 12)
  x ^= (x << 25)
  x ^= (x >> 27)
  x *= 2685821657736338717
Result: 64-bit UID
```

### 2. Numerology Mapping (OWN)
```
A-Z → 1-9 (repeating)
  A=1, B=2, ..., I=9
  J=1, K=2, ..., R=9
  S=1, T=2, ..., Z=8
```

### 3. Backend Number Composition (OWN)
```
backend = f(text, index, uid, prev_uid, next_uid, embedding_bit)
  - Weighted character sum
  - UID contribution
  - Neighbor contribution
  - Index contribution
  - Embedding bit
```

### 4. Digital Root Folding (OWN)
```
digital_root(n):
  while n > 9:
    n = sum(digits(n))
  return n (1-9)
```

### 5. Feature Extraction (OWN)
```
features = [
  UID_bytes(8),
  Frontend_onehot(9),
  Backend_bytes(8),
  Content_ID(1),
  Global_ID_bytes(8),
  Neighbor_UIDs(16),
  Index(1),
  Stream_onehot(9),
  Text_features(~20)
]
Total: ~60-100 dimensions
```

### 6. Embedding Projection (OWN)
```
embedding = projection_matrix @ features
  - Random projection matrix (768 × feature_dim)
  - Matrix multiplication
  - Result: 768-dimensional vector
```

---

## Memory Usage

### Token Storage
```
TokenRecord: ~100 bytes
  - text: ~20 bytes
  - uid: 8 bytes
  - metadata: ~70 bytes

1M tokens ≈ 100 MB
```

### Embedding Storage
```
Embedding: 768 × 4 bytes = 3,072 bytes
  - float32: 4 bytes per dimension
  - 768 dimensions

1M embeddings ≈ 3 GB
```

### Vector Store
```
FAISS Index: ~3 GB per 1M tokens
  - Embeddings: 3 GB
  - Index overhead: ~100 MB
  - Token mappings: ~100 MB

Total: ~3.2 GB per 1M tokens
```

---

## Performance Metrics

### Tokenization
- **Speed:** ~1M tokens/second (single-threaded)
- **Parallel:** ~5M tokens/second (multi-threaded)
- **Memory:** ~100 bytes per token

### Embedding Generation
- **Speed:** ~100K tokens/second (feature-based)
- **Memory:** ~3KB per token
- **Batch:** Supported (10K-100K tokens/batch)

### Vector Store
- **FAISS Search:** ~1M queries/second
- **ChromaDB Search:** ~10K queries/second
- **Memory:** ~3KB per token

### Semantic Training
- **Speed:** Depends on vocabulary size
- **Memory:** ~1GB per 1M tokens
- **Training Time:** Minutes to hours

---

## File Formats

### Token Data
```json
{
  "text": "hello",
  "uid": 12345678901234567890,
  "stream": "word",
  "frontend": 5,
  "backend_huge": 12345678901234567890,
  "content_id": 12345,
  "global_id": 98765432109876543210
}
```

### Embeddings
```
NumPy Array:
  - Format: .npy
  - Shape: (n_tokens, 768)
  - Dtype: float32
  - Size: ~3KB per token
```

### Vector Store
```
FAISS Index:
  - Format: .index
  - Type: IndexFlatL2
  - Storage: In-memory
  - Persistence: Manual save/load

ChromaDB:
  - Format: SQLite database
  - Storage: Disk
  - Persistence: Automatic
```

### Semantic Model
```
Pickle File:
  - Format: .pkl
  - Contents: Model state
  - Size: ~100MB-1GB
  - Includes: Embeddings, vocabulary, co-occurrence
```

---

## Dependencies Tree

```
SOMA
├── Core (OWN)
│   ├── Tokenization (OWN)
│   ├── UID Generation (OWN)
│   └── Feature Extraction (OWN)
│
├── Embeddings (OWN + EXTERNAL)
│   ├── Feature-based (OWN)
│   ├── Semantic (OWN)
│   ├── Hybrid (OWN + sentence-transformers)
│   └── Hash (OWN)
│
├── Vector Store (OWN + EXTERNAL)
│   ├── Interface (OWN)
│   ├── FAISS (EXTERNAL)
│   └── ChromaDB (EXTERNAL)
│
├── API Server (OWN + EXTERNAL)
│   ├── Logic (OWN)
│   ├── FastAPI (EXTERNAL)
│   └── Uvicorn (EXTERNAL)
│
└── Integration (OWN + EXTERNAL)
    ├── Adapter (OWN)
    └── Transformers (EXTERNAL)
```

---

**This document provides visual representations of the SOMA architecture.**

