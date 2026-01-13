# SOMA Inference-Ready Implementation Plan

## Overview

This document provides a step-by-step implementation plan to make SOMA inference-ready with embeddings and vector database support.

---

## Phase 1: Core Embedding Generation (Week 1-2)

### 1.1 Setup Project Structure

```
src/embeddings/
├── __init__.py
├── embedding_generator.py      # Core embedding generation
├── feature_extractor.py        # Feature extraction utilities
├── vector_store.py             # Vector database interface
├── inference_pipeline.py       # End-to-end pipeline
└── backends/
    ├── __init__.py
    ├── chroma_store.py         # ChromaDB implementation
    └── faiss_store.py          # FAISS implementation
```

### 1.2 Implementation Tasks

- [x] Create `SOMAEmbeddingGenerator` class
- [x] Implement feature extraction from TokenRecord
- [x] Implement feature-based embedding strategy
- [x] Add hash-based embedding strategy
- [ ] Add unit tests
- [ ] Create example scripts

### 1.3 Dependencies

Add to `requirements.txt`:
```
numpy>=1.24.3
sentence-transformers>=2.2.0  # For hybrid embeddings
chromadb>=0.4.0               # Vector database option 1
faiss-cpu>=1.7.4              # Vector database option 2
```

### 1.4 Testing

Create test file: `tests/test_embedding_generator.py`

```python
def test_feature_extraction():
    """Test feature extraction from TokenRecord"""
    pass

def test_embedding_generation():
    """Test embedding generation"""
    pass

def test_embedding_normalization():
    """Test embedding normalization"""
    pass

def test_batch_generation():
    """Test batch embedding generation"""
    pass
```

---

## Phase 2: Vector Database Integration (Week 2-3)

### 2.1 ChromaDB Integration

- [x] Implement `ChromaVectorStore` class
- [x] Add persistence support
- [ ] Add metadata filtering
- [ ] Performance testing

### 2.2 FAISS Integration

- [x] Implement `FAISSVectorStore` class
- [ ] Add index types (IVF, HNSW)
- [ ] Add GPU support option
- [ ] Performance benchmarking

### 2.3 Unified Interface

- [x] Create `SOMAVectorStore` base class
- [x] Implement common interface
- [ ] Add backend switching
- [ ] Add migration tools

---

## Phase 3: Hybrid Embedding Strategy (Week 3-4)

### 3.1 Text Embedding Integration

- [x] Integrate sentence-transformers
- [x] Implement hybrid combination
- [ ] Add weight tuning utilities
- [ ] Benchmark performance

### 3.2 Configuration

Create config file: `config/embedding_config.yaml`

```yaml
embedding:
  strategy: "hybrid"  # feature_based, hybrid, hash
  dimension: 768
  text_model: "sentence-transformers/all-MiniLM-L6-v2"
  feature_weights:
    text: 0.7
    features: 0.3

vector_store:
  backend: "chroma"  # chroma, faiss
  collection_name: "soma_embeddings"
  persist_directory: "./vector_db"
```

---

## Phase 4: Inference Pipeline (Week 4-5)

### 4.1 Pipeline Implementation

- [x] Create `SOMAInferencePipeline` class
- [x] Implement text processing
- [x] Implement similarity search
- [ ] Add batch processing optimization
- [ ] Add caching

### 4.2 API Endpoints

Create: `src/servers/embedding_server.py`

```python
@app.post("/embeddings/generate")
async def generate_embeddings(request: EmbeddingRequest):
    """Generate embeddings for text"""
    pass

@app.post("/embeddings/search")
async def search_embeddings(request: SearchRequest):
    """Search for similar tokens"""
    pass

@app.get("/embeddings/stats")
async def get_stats():
    """Get vector database statistics"""
    pass
```

### 4.3 Frontend Integration

- [ ] Add embedding visualization
- [ ] Add similarity search UI
- [ ] Add embedding comparison tools

---

## Phase 5: Advanced Features (Week 5-6)

### 5.1 Learned Embeddings (Optional)

- [ ] Design neural network architecture
- [ ] Create training pipeline
- [ ] Add fine-tuning tools
- [ ] Benchmark against other strategies

### 5.2 Embedding Analytics

- [ ] Clustering analysis
- [ ] Dimensionality reduction visualization
- [ ] Embedding quality metrics
- [ ] Similarity distribution analysis

### 5.3 Performance Optimization

- [ ] Batch processing optimization
- [ ] Caching layer
- [ ] GPU acceleration
- [ ] Distributed storage support

---

## Quick Start Guide

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install vector database backends (choose one or both)
pip install chromadb
# OR
pip install faiss-cpu
```

### Basic Usage

```python
from src.core.core_tokenizer import TextTokenizer
from src.embeddings import SOMAEmbeddingGenerator, ChromaVectorStore, SOMAInferencePipeline

# Initialize components
tokenizer = TextTokenizer(seed=42, embedding_bit=False)
embedding_gen = SOMAEmbeddingGenerator(
    strategy="feature_based",
    embedding_dim=768
)
vector_store = ChromaVectorStore(
    collection_name="soma_embeddings",
    persist_directory="./vector_db"
)

# Create pipeline
pipeline = SOMAInferencePipeline(
    embedding_generator=embedding_gen,
    vector_store=vector_store,
    tokenizer=tokenizer
)

# Process text
result = pipeline.process_text("Hello world, this is SOMA!")
print(f"Generated {len(result['tokens'])} tokens")
print(f"Embedding shape: {result['embeddings'].shape}")

# Search for similar content
results = pipeline.similarity_search("artificial intelligence", top_k=5)
for r in results:
    print(f"Token: {r['text']}, Distance: {r['distance']}")
```

---

## Testing Checklist

### Unit Tests
- [ ] Feature extraction
- [ ] Embedding generation (all strategies)
- [ ] Vector store operations
- [ ] Pipeline processing

### Integration Tests
- [ ] End-to-end pipeline
- [ ] Vector database persistence
- [ ] Search functionality
- [ ] Batch processing

### Performance Tests
- [ ] Embedding generation speed
- [ ] Vector database insert/search speed
- [ ] Memory usage
- [ ] Scalability

---

## Success Metrics

1. **Embedding Quality**
   - Similar tokens have similar embeddings
   - Different tokens have different embeddings
   - Embeddings are normalized and stable

2. **Performance**
   - Generate embeddings at >10K tokens/sec
   - Search in <100ms for 1M tokens
   - Memory efficient (<1GB for 100K tokens)

3. **Usability**
   - Simple API
   - Good documentation
   - Working examples

---

## Next Steps

1. **Immediate**: Complete Phase 1 implementation
2. **Short-term**: Add vector database integration
3. **Medium-term**: Implement hybrid embeddings
4. **Long-term**: Add learned embeddings and analytics

---

## Resources

- [Embedding System Design](./EMBEDDING_SYSTEM_DESIGN.md) - Complete design document
- [ChromaDB Docs](https://docs.trychroma.com/)
- [FAISS Docs](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)

