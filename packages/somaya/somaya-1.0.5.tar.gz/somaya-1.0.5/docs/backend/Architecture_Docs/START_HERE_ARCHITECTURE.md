# SOMA Architecture - START HERE

## 🎯 Quick Answer: What is SOMA?

**SOMA** = Text Tokenization → Embeddings → Vector Store → Similarity Search

### Complete Flow:
```
Text → Tokenization → Embeddings → Vector Store → Similarity Search
```

---

## 📚 Architecture Documentation

### 1. **ARCHITECTURE.md** - Complete Documentation
   - **Read this for:** Complete understanding of the architecture
   - **Contains:** All components, how they work, what they use

### 2. **ARCHITECTURE_DIAGRAM.md** - Visual Diagrams
   - **Read this for:** Visual understanding
   - **Contains:** Diagrams, flows, visual representations

### 3. **ARCHITECTURE_QUICK_REFERENCE.md** - Quick Reference
   - **Read this for:** Quick lookups
   - **Contains:** Quick answers, reference tables

### 4. **ARCHITECTURE_SUMMARY.md** - Complete Summary
   - **Read this for:** Complete summary
   - **Contains:** Summary of everything

### 5. **ARCHITECTURE_INDEX.md** - Index
   - **Read this for:** Navigation
   - **Contains:** Index to all documentation

---

## 🏗️ Architecture Overview

### Components:

1. **Tokenization (OWN)**
   - `src/core/core_tokenizer.py`
   - Self-contained, no external tokenization libraries
   - Multiple strategies (space, word, char, etc.)

2. **Embeddings (OWN + EXTERNAL)**
   - `src/embeddings/embedding_generator.py`
   - Feature-based (OWN) - Default
   - Semantic (OWN) - Trained
   - Hybrid (OWN + sentence-transformers) - Optional

3. **Semantic Training (OWN)**
   - `src/embeddings/semantic_trainer.py`
   - Co-occurrence-based learning
   - No pretrained models

4. **Vector Store (OWN + EXTERNAL)**
   - `src/embeddings/vector_store.py`
   - FAISS (EXTERNAL) - High performance
   - ChromaDB (EXTERNAL) - Easy to use

5. **API Server (OWN + EXTERNAL)**
   - `src/servers/main_server.py`
   - FastAPI (EXTERNAL) - Web framework
   - OWN logic - Business logic

---

## 🔧 Technology Stack

### OWN/CUSTOM:
- ✅ Tokenization engine
- ✅ UID generation
- ✅ Feature extraction
- ✅ Embedding projection
- ✅ Semantic training
- ✅ Vector store interface
- ✅ API logic

### EXTERNAL (Required):
- ⚙️ NumPy
- ⚙️ FastAPI
- ⚙️ Uvicorn
- ⚙️ Pydantic

### EXTERNAL (Optional):
- ⚙️ FAISS
- ⚙️ ChromaDB
- ⚙️ sentence-transformers
- ⚙️ transformers

---

## 📊 Data Flow

```
Text Input
    │
    ▼
Tokenization (OWN)
    │
    ▼
TokenRecord Objects
    │
    ▼
Feature Extraction (OWN)
    │
    ▼
Embedding Generation (OWN + optional EXTERNAL)
    │
    ▼
768-dimensional Vectors
    │
    ▼
Vector Store (OWN interface + EXTERNAL backends)
    │
    ▼
Similarity Search
    │
    ▼
Results
```

---

## 🎯 Quick Answers

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

---

## 📖 Where to Read More

### For Complete Understanding:
→ Read: **ARCHITECTURE.md**

### For Visual Understanding:
→ Read: **ARCHITECTURE_DIAGRAM.md**

### For Quick Reference:
→ Read: **ARCHITECTURE_QUICK_REFERENCE.md**

### For Complete Summary:
→ Read: **ARCHITECTURE_SUMMARY.md**

---

## ✅ That's It!

**All architecture documentation is in the `backend/` folder!**

Start with **ARCHITECTURE_SUMMARY.md** for overview, then read **ARCHITECTURE.md** for details.

