# SOMA Architecture - Quick Reference

## 🎯 What is SOMA?

**SOMA** = Self-contained Advanced Text Tokenization Framework

- **Tokenization** - Breaks text into tokens
- **Embeddings** - Converts tokens to vectors
- **Semantic Training** - Learns semantic relationships
- **Vector Store** - Stores embeddings for search
- **Similarity Search** - Finds similar tokens
- **API Server** - REST API for all features

---

## 📦 Components Overview

### 1. Tokenization (OWN)
- **File:** `src/core/core_tokenizer.py`
- **Type:** OWN/CUSTOM
- **Dependencies:** Python stdlib only
- **Features:** Multiple tokenization strategies, UID generation, feature calculation

### 2. Embeddings (OWN + EXTERNAL)
- **File:** `src/embeddings/embedding_generator.py`
- **Type:** OWN (feature extraction) + EXTERNAL (optional sentence-transformers)
- **Strategies:** Feature-based (OWN), Semantic (OWN), Hybrid (OWN + EXT), Hash (OWN)

### 3. Semantic Training (OWN)
- **File:** `src/embeddings/semantic_trainer.py`
- **Type:** OWN
- **Method:** Co-occurrence-based learning
- **No pretrained models** - Learns from SOMA structure

### 4. Vector Store (OWN + EXTERNAL)
- **File:** `src/embeddings/vector_store.py`
- **Type:** OWN (interface) + EXTERNAL (FAISS/ChromaDB)
- **Backends:** FAISS (high performance), ChromaDB (easy to use)

### 5. API Server (OWN + EXTERNAL)
- **File:** `src/servers/main_server.py`
- **Type:** OWN (logic) + EXTERNAL (FastAPI)
- **Framework:** FastAPI + Uvicorn

### 6. Integration (OWN + EXTERNAL)
- **File:** `src/integration/vocabulary_adapter.py`
- **Type:** OWN (adapter) + EXTERNAL (transformers)
- **Purpose:** Maps SOMA tokens to model vocabularies

---

## 🔧 Technology Stack

### OWN/CUSTOM
- ✅ Tokenization engine
- ✅ UID generation (XorShift64*)
- ✅ Feature extraction
- ✅ Embedding projection
- ✅ Semantic training
- ✅ Vector store interface
- ✅ API logic

### EXTERNAL (Required)
- ⚙️ NumPy - Numerical operations
- ⚙️ FastAPI - Web framework
- ⚙️ Uvicorn - ASGI server
- ⚙️ Pydantic - Data validation

### EXTERNAL (Optional)
- ⚙️ FAISS - Vector database
- ⚙️ ChromaDB - Vector database
- ⚙️ sentence-transformers - Hybrid embeddings
- ⚙️ transformers - Model integration

---

## 📊 Data Flow

```
Text → Tokenization → TokenRecord → Embeddings → Vector Store → Similarity Search
```

### Step-by-Step:
1. **Text Input** - Raw text string
2. **Tokenization** - TokenRecord objects
3. **Feature Extraction** - Token features
4. **Embedding Generation** - 768-dim vectors
5. **Vector Store** - Indexed embeddings
6. **Similarity Search** - Search results

---

## 🗂️ File Structure

```
backend/
├── src/
│   ├── core/              # Tokenization (OWN)
│   ├── embeddings/        # Embeddings, Semantic, Vector Store
│   ├── servers/           # API Server
│   ├── integration/       # Model Integration
│   ├── compression/       # Compression Algorithms (OWN)
│   └── utils/             # Utilities (OWN)
├── soma/                # Main Package
├── requirements.txt       # Dependencies
└── setup.py              # Package Setup
```

---

## 🔑 Key Algorithms (OWN)

### 1. XorShift64* PRNG
- **Purpose:** Deterministic UID generation
- **File:** `src/utils/unique_identifier.py`
- **Output:** 64-bit unique identifier

### 2. Numerology Mapping
- **Purpose:** Character-to-digit mapping
- **File:** `src/compression/compression_algorithms.py`
- **Output:** 1-9 digit

### 3. Backend Number Composition
- **Purpose:** Token feature combination
- **File:** `src/core/core_tokenizer.py`
- **Output:** 64-bit backend number

### 4. Feature Extraction
- **Purpose:** Extract token features
- **File:** `src/embeddings/embedding_generator.py`
- **Output:** ~60-100 dimensional feature vector

### 5. Embedding Projection
- **Purpose:** Project features to 768 dimensions
- **File:** `src/embeddings/embedding_generator.py`
- **Output:** 768-dimensional embedding

### 6. Semantic Training
- **Purpose:** Learn semantic relationships
- **File:** `src/embeddings/semantic_trainer.py`
- **Output:** Trained semantic embeddings

---

## 📈 Performance

### Tokenization
- **Speed:** ~1M tokens/second
- **Memory:** ~100 bytes/token

### Embeddings
- **Speed:** ~100K tokens/second
- **Memory:** ~3KB/token

### Vector Store
- **FAISS:** ~1M queries/second
- **ChromaDB:** ~10K queries/second

---

## 🔌 API Endpoints

- `GET /` - Health check
- `POST /tokenize` - Tokenize text
- `POST /reconstruct` - Reconstruct text
- `POST /embed` - Generate embeddings
- `GET /docs` - API documentation

---

## 💾 Storage

### Tokens
- **Format:** In-memory (TokenRecord objects)
- **Size:** ~100 bytes/token

### Embeddings
- **Format:** NumPy arrays (.npy)
- **Size:** ~3KB/token (768-dim float32)

### Vector Store
- **FAISS:** In-memory index
- **ChromaDB:** Disk-based database

### Semantic Model
- **Format:** Pickle (.pkl)
- **Size:** ~100MB-1GB

---

## 🎯 Use Cases

### 1. Tokenization
- Text processing
- NLP pipelines
- Data preprocessing

### 2. Embeddings
- Feature extraction
- Similarity search
- Clustering

### 3. Semantic Training
- Semantic search
- Concept discovery
- Relationship learning

### 4. Vector Store
- Similarity search
- Recommendation systems
- Content discovery

### 5. API Server
- Web applications
- Microservices
- Integration

---

## 🔍 Quick Answers

### What is OWN?
- Tokenization engine
- UID generation
- Feature extraction
- Embedding projection
- Semantic training
- Vector store interface
- API logic

### What is EXTERNAL?
- NumPy (required)
- FastAPI (required)
- Uvicorn (required)
- Pydantic (required)
- FAISS (optional)
- ChromaDB (optional)
- sentence-transformers (optional)
- transformers (optional)

### How does it work?
1. Tokenize text → TokenRecord objects
2. Extract features → Feature vectors
3. Generate embeddings → 768-dim vectors
4. Store in vector store → Indexed
5. Search → Similar tokens

### What are the outputs?
- Tokens (TokenRecord objects)
- Embeddings (768-dim vectors)
- Vector store (indexed embeddings)
- Semantic model (trained embeddings)
- Search results (similar tokens)

---

## 📚 Documentation Files

- `ARCHITECTURE.md` - Complete architecture documentation
- `ARCHITECTURE_DIAGRAM.md` - Visual diagrams
- `ARCHITECTURE_QUICK_REFERENCE.md` - This file
- `README.md` - Backend overview
- `QUICK_START.txt` - Quick start guide

---

**For detailed information, see `ARCHITECTURE.md`**

