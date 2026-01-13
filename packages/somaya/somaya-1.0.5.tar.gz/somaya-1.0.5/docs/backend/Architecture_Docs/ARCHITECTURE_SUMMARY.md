# SOMA Architecture - Complete Summary

## 🎯 Project Overview

**SOMA** is a comprehensive text tokenization framework that provides end-to-end processing from text to semantic search.

### What It Does

1. **Tokenizes text** - Breaks text into tokens using multiple strategies
2. **Generates embeddings** - Converts tokens to numerical vectors
3. **Trains semantic models** - Learns semantic relationships from tokens
4. **Stores vectors** - Indexes embeddings for fast search
5. **Searches similarities** - Finds similar tokens based on embeddings
6. **Provides API** - REST API for all functionality

---

## 🏗️ Architecture Layers

### Layer 1: Client Layer
- Web browsers
- API clients
- Command line
- Frontend applications

### Layer 2: API Server Layer
- FastAPI server
- REST API endpoints
- Request/response handling
- CORS middleware

### Layer 3: Processing Layer
- Tokenization system
- Embedding generation
- Semantic training
- Vector store
- Similarity search

### Layer 4: Storage Layer
- Token data (memory)
- Embeddings (disk)
- Vector stores (FAISS/ChromaDB)
- Semantic models (pickle)

---

## 🔧 Core Components

### 1. Tokenization System

**Location:** `src/core/core_tokenizer.py`

**Type:** OWN/CUSTOM

**What it does:**
- Tokenizes text using multiple strategies
- Generates unique identifiers (UIDs)
- Calculates frontend digits (numerology)
- Composes backend numbers (feature combination)
- Creates TokenRecord objects

**Key Features:**
- ✅ Self-contained (no external tokenization libraries)
- ✅ Multiple tokenization strategies
- ✅ Deterministic UID generation
- ✅ Neighbor awareness
- ✅ Global ID generation

**Dependencies:**
- Python standard library only
- No external tokenization libraries

**Algorithms (OWN):**
- XorShift64* PRNG for UIDs
- Numerology mapping (A-Z → 1-9)
- Backend number composition
- Digital root folding
- Content ID hashing

---

### 2. Embedding System

**Location:** `src/embeddings/embedding_generator.py`

**Type:** OWN + EXTERNAL (optional)

**What it does:**
- Extracts features from TokenRecord objects
- Generates embeddings using different strategies
- Projects features to target dimension (768)
- Supports multiple embedding strategies

**Embedding Strategies:**

#### A. Feature-Based (OWN - DEFAULT)
- Extracts features from tokens
- Projects to 768 dimensions
- No external dependencies
- Fast and deterministic

#### B. Semantic (OWN - TRAINED)
- Uses trained semantic model
- Learns from co-occurrence patterns
- No pretrained models
- Requires training data

#### C. Hybrid (OWN + EXTERNAL)
- Combines text embeddings with features
- Uses sentence-transformers (EXTERNAL)
- Requires sentence-transformers library
- Better semantic understanding

#### D. Hash (OWN)
- Fast hash-based embeddings
- Memory efficient
- Good for large datasets

**Dependencies:**
- NumPy (required)
- sentence-transformers (optional, for hybrid)

**Features Extracted (OWN):**
- UID bytes (8 dimensions)
- Frontend one-hot (9 dimensions)
- Backend bytes (8 dimensions)
- Content ID (1 dimension)
- Global ID bytes (8 dimensions)
- Neighbor UIDs (16 dimensions)
- Index position (1 dimension)
- Stream type one-hot (9 dimensions)
- Token text features (~20 dimensions)
- **Total:** ~60-100 dimensions → Projected to 768

---

### 3. Semantic Training System

**Location:** `src/embeddings/semantic_trainer.py`

**Type:** OWN

**What it does:**
- Trains semantic embeddings from token co-occurrence
- Builds vocabulary from tokens
- Creates co-occurrence matrix
- Trains embeddings using self-supervised learning
- Saves trained model

**Key Features:**
- ✅ No pretrained models
- ✅ Learns from SOMA structure
- ✅ Co-occurrence-based learning
- ✅ Window-based context
- ✅ Self-supervised training

**Dependencies:**
- NumPy (required)
- scipy.sparse (optional, for large vocabularies)
- pickle (Python stdlib)

**Training Process:**
1. Build vocabulary from tokens
2. Build co-occurrence matrix
3. Initialize random embeddings
4. Train embeddings (multiple epochs)
5. Save model

**Algorithms (OWN):**
- Co-occurrence counting
- Embedding initialization
- Gradient updates
- L2 normalization

---

### 4. Vector Store System

**Location:** `src/embeddings/vector_store.py`

**Type:** OWN + EXTERNAL

**What it does:**
- Stores embeddings in vector database
- Provides unified interface for different backends
- Enables similarity search
- Manages token mappings

**Vector Store Backends:**

#### A. FAISS (EXTERNAL)
- High-performance vector search
- In-memory storage
- Fast similarity search
- Memory efficient

#### B. ChromaDB (EXTERNAL)
- Easy-to-use vector database
- Persistent storage
- Metadata filtering
- Good for small to medium datasets

**Vector Store Interface (OWN):**
- Unified API for both backends
- Token mapping management
- Search functionality
- Save/load operations

**Dependencies:**
- FAISS (optional, for high performance)
- ChromaDB (optional, for easy use)
- NumPy (required)

---

### 5. API Server

**Location:** `src/servers/main_server.py`

**Type:** OWN + EXTERNAL

**What it does:**
- Provides REST API for all functionality
- Handles HTTP requests/responses
- Processes tokenization requests
- Generates embeddings
- Performs similarity search

**API Endpoints:**
- `GET /` - Health check
- `POST /tokenize` - Tokenize text
- `POST /reconstruct` - Reconstruct text
- `POST /embed` - Generate embeddings
- `GET /docs` - API documentation

**Features:**
- FastAPI framework (EXTERNAL)
- CORS support
- Large file support (50GB+)
- Chunked processing
- Parallel processing

**Dependencies:**
- FastAPI (required)
- Uvicorn (required)
- Pydantic (required)
- NumPy (required)

---

### 6. Integration Components

**Location:** `src/integration/vocabulary_adapter.py`

**Type:** OWN + EXTERNAL

**What it does:**
- Maps SOMA tokens to pretrained model vocabularies
- Enables integration with BERT, GPT, T5, etc.
- Converts SOMA tokenization to model-compatible format

**Features:**
- Token mapping
- Model compatibility
- Subword handling
- Attention masks

**Dependencies:**
- transformers (optional, for model integration)
- OWN adapter logic

---

## 📊 Complete Data Flow

```
1. INPUT
   Text string
        │
        ▼
2. TOKENIZATION
   core_tokenizer.py (OWN)
   - Multiple strategies
   - UID generation
   - Feature calculation
        │
        ▼
   TokenRecord objects
   (text, uid, stream, frontend, backend, ...)
        │
        ▼
3. EMBEDDING GENERATION
   embedding_generator.py (OWN + EXTERNAL)
   - Feature extraction (OWN)
   - Embedding generation (OWN/EXTERNAL)
        │
        ▼
   768-dimensional vectors
        │
        ▼
4. SEMANTIC TRAINING (Optional)
   semantic_trainer.py (OWN)
   - Vocabulary building
   - Co-occurrence matrix
   - Embedding training
        │
        ▼
   Trained semantic model
        │
        ▼
5. VECTOR STORE
   vector_store.py (OWN + EXTERNAL)
   - FAISS index (EXTERNAL)
   - ChromaDB (EXTERNAL)
   - Token mappings (OWN)
        │
        ▼
   Indexed embeddings
        │
        ▼
6. SIMILARITY SEARCH
   vector_store.py
   - Query embedding
   - Similarity search
   - Results ranking
        │
        ▼
   Search results
   (similar tokens with distances)
```

---

## 🔑 Key Algorithms (OWN)

### 1. XorShift64* PRNG
- **Purpose:** Deterministic UID generation
- **File:** `src/utils/unique_identifier.py`
- **Algorithm:**
  ```
  x ^= (x >> 12)
  x ^= (x << 25)
  x ^= (x >> 27)
  x *= 2685821657736338717
  ```
- **Output:** 64-bit unique identifier

### 2. Numerology Mapping
- **Purpose:** Character-to-digit mapping
- **File:** `src/compression/compression_algorithms.py`
- **Algorithm:**
  ```
  A-Z → 1-9 (repeating)
  A=1, B=2, ..., I=9
  J=1, K=2, ..., R=9
  S=1, T=2, ..., Z=8
  ```
- **Output:** 1-9 digit

### 3. Backend Number Composition
- **Purpose:** Token feature combination
- **File:** `src/core/core_tokenizer.py`
- **Algorithm:**
  ```
  backend = f(text, index, uid, prev_uid, next_uid, embedding_bit)
  - Weighted character sum
  - UID contribution
  - Neighbor contribution
  - Index contribution
  - Embedding bit
  ```
- **Output:** 64-bit backend number

### 4. Digital Root Folding
- **Purpose:** 9-centric folding
- **File:** `src/core/core_tokenizer.py`
- **Algorithm:**
  ```
  while n > 9:
    n = sum(digits(n))
  return n (1-9)
  ```
- **Output:** 1-9 digit

### 5. Feature Extraction
- **Purpose:** Extract token features
- **File:** `src/embeddings/embedding_generator.py`
- **Features:**
  ```
  - UID bytes (8)
  - Frontend one-hot (9)
  - Backend bytes (8)
  - Content ID (1)
  - Global ID bytes (8)
  - Neighbor UIDs (16)
  - Index (1)
  - Stream one-hot (9)
  - Text features (~20)
  Total: ~60-100 dimensions
  ```
- **Output:** Feature vector

### 6. Embedding Projection
- **Purpose:** Project features to 768 dimensions
- **File:** `src/embeddings/embedding_generator.py`
- **Algorithm:**
  ```
  embedding = projection_matrix @ features
  - Random projection matrix (768 × feature_dim)
  - Matrix multiplication
  ```
- **Output:** 768-dimensional embedding

### 7. Semantic Training
- **Purpose:** Learn semantic relationships
- **File:** `src/embeddings/semantic_trainer.py`
- **Algorithm:**
  ```
  1. Build vocabulary
  2. Build co-occurrence matrix
  3. Initialize embeddings
  4. Train embeddings (epochs)
  5. Save model
  ```
- **Output:** Trained semantic embeddings

---

## 🗂️ File Structure

```
backend/
├── src/
│   ├── core/
│   │   ├── core_tokenizer.py      # Main tokenization (OWN)
│   │   ├── base_tokenizer.py      # Base tokenizers (OWN)
│   │   └── parallel_tokenizer.py  # Parallel processing (OWN)
│   │
│   ├── embeddings/
│   │   ├── embedding_generator.py # Embedding generation (OWN + EXT)
│   │   ├── semantic_trainer.py    # Semantic training (OWN)
│   │   ├── vector_store.py        # Vector store (OWN + EXT)
│   │   └── inference_pipeline.py  # Inference (OWN)
│   │
│   ├── servers/
│   │   ├── main_server.py         # Main API server (OWN + EXT)
│   │   ├── lightweight_server.py  # Lightweight server (OWN + EXT)
│   │   ├── api_server.py          # API server (OWN + EXT)
│   │   └── simple_server.py       # Simple server (OWN + EXT)
│   │
│   ├── integration/
│   │   └── vocabulary_adapter.py  # Model integration (OWN + EXT)
│   │
│   ├── compression/
│   │   └── compression_algorithms.py # Compression (OWN)
│   │
│   ├── utils/
│   │   └── unique_identifier.py   # UID generation (OWN)
│   │
│   └── tests/
│       └── ...                     # Tests
│
├── soma/
│   ├── __init__.py
│   ├── soma.py                  # Main package
│   └── cli.py                     # CLI
│
├── requirements.txt               # Dependencies
├── setup.py                       # Setup
└── README.md                      # Documentation
```

---

## 🔌 Technology Stack

### OWN/CUSTOM Components
- ✅ Tokenization engine
- ✅ UID generation (XorShift64*)
- ✅ Feature extraction
- ✅ Embedding projection
- ✅ Semantic training
- ✅ Vector store interface
- ✅ API logic
- ✅ Integration adapters

### EXTERNAL Dependencies

#### Required:
- ⚙️ **NumPy** - Numerical operations
- ⚙️ **FastAPI** - Web framework
- ⚙️ **Uvicorn** - ASGI server
- ⚙️ **Pydantic** - Data validation

#### Optional:
- ⚙️ **FAISS** - Vector database (high performance)
- ⚙️ **ChromaDB** - Vector database (easy to use)
- ⚙️ **sentence-transformers** - Hybrid embeddings
- ⚙️ **transformers** - Model integration
- ⚙️ **scipy** - Sparse matrices

### Python Standard Library
- ✅ `json` - JSON handling
- ✅ `time` - Time operations
- ✅ `datetime` - Date/time
- ✅ `os` - File system
- ✅ `pickle` - Serialization
- ✅ `threading` - Multi-threading
- ✅ `multiprocessing` - Multi-processing
- ✅ `collections` - Data structures

---

## 📈 Performance

### Tokenization
- **Speed:** ~1M tokens/second
- **Memory:** ~100 bytes/token
- **Parallel:** Supported

### Embeddings
- **Speed:** ~100K tokens/second
- **Memory:** ~3KB/token
- **Batch:** Supported

### Vector Store
- **FAISS:** ~1M queries/second
- **ChromaDB:** ~10K queries/second
- **Memory:** ~3KB/token

### Semantic Training
- **Speed:** Depends on vocabulary size
- **Memory:** ~1GB per 1M tokens
- **Time:** Minutes to hours

---

## 🎯 Use Cases

### 1. Text Tokenization
- NLP pipelines
- Data preprocessing
- Text analysis

### 2. Embedding Generation
- Feature extraction
- Similarity search
- Clustering

### 3. Semantic Search
- Concept discovery
- Related term finding
- Content recommendation

### 4. Vector Store
- Similarity search
- Recommendation systems
- Content discovery

### 5. API Integration
- Web applications
- Microservices
- Integration with other systems

---

## 🔍 Component Ownership

### OWN/CUSTOM (100% SOMA)
- ✅ Tokenization engine
- ✅ UID generation
- ✅ Feature extraction
- ✅ Embedding projection
- ✅ Semantic training algorithm
- ✅ Vector store interface
- ✅ API business logic
- ✅ Integration adapters

### EXTERNAL (Third-Party Libraries)
- ⚙️ NumPy - Numerical operations
- ⚙️ FastAPI - Web framework
- ⚙️ Uvicorn - ASGI server
- ⚙️ Pydantic - Data validation
- ⚙️ FAISS - Vector database
- ⚙️ ChromaDB - Vector database
- ⚙️ sentence-transformers - Text embeddings
- ⚙️ transformers - Model integration

### HYBRID (OWN + EXTERNAL)
- 🔄 Embedding generation (OWN features + optional EXTERNAL text embeddings)
- 🔄 Vector store (OWN interface + EXTERNAL backends)
- 🔄 API server (OWN logic + EXTERNAL framework)
- 🔄 Integration (OWN adapter + EXTERNAL transformers)

---

## 📚 Documentation Files

1. **ARCHITECTURE.md** - Complete architecture documentation
2. **ARCHITECTURE_DIAGRAM.md** - Visual diagrams
3. **ARCHITECTURE_QUICK_REFERENCE.md** - Quick reference
4. **ARCHITECTURE_SUMMARY.md** - This file (summary)
5. **README.md** - Backend overview
6. **QUICK_START.txt** - Quick start guide

---

## ✅ Summary

### What SOMA Is:
- ✅ Self-contained tokenization system (no external tokenization libraries)
- ✅ Feature-based embedding generation (OWN)
- ✅ Semantic training system (OWN, no pretrained models)
- ✅ Vector store interface (OWN) with external backends (FAISS/ChromaDB)
- ✅ REST API server (OWN logic + FastAPI framework)
- ✅ Integration adapters (OWN + transformers)

### What SOMA Uses:
- ⚙️ NumPy - Numerical operations (required)
- ⚙️ FastAPI - Web framework (required)
- ⚙️ Uvicorn - ASGI server (required)
- ⚙️ Pydantic - Data validation (required)
- ⚙️ FAISS - Vector database (optional)
- ⚙️ ChromaDB - Vector database (optional)
- ⚙️ sentence-transformers - Hybrid embeddings (optional)
- ⚙️ transformers - Model integration (optional)

### How It Works:
1. **Tokenize** text → TokenRecord objects (OWN)
2. **Extract features** → Feature vectors (OWN)
3. **Generate embeddings** → 768-dim vectors (OWN + optional EXTERNAL)
4. **Train semantic model** → Semantic embeddings (OWN)
5. **Store in vector store** → Indexed embeddings (OWN interface + EXTERNAL backends)
6. **Search** → Similar tokens (OWN + EXTERNAL)

---

**For detailed information, see:**
- `ARCHITECTURE.md` - Complete documentation
- `ARCHITECTURE_DIAGRAM.md` - Visual diagrams
- `ARCHITECTURE_QUICK_REFERENCE.md` - Quick reference

---

**Last Updated:** 2025-11-09
**Version:** 1.0.0

