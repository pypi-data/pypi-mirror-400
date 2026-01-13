# SOMA Embedding Generation System - Complete Design

## Executive Summary

This document outlines a comprehensive system to generate embeddings from SOMA tokens and make SOMA inference-ready. The system converts SOMA's mathematical token features (UIDs, frontend digits, backend numbers) into dense vector embeddings suitable for ML inference, similarity search, and semantic operations.

---

## 1. Problem Statement

### Current State
- ✅ SOMA generates rich token metadata (UIDs, digits, backend numbers)
- ❌ No embeddings exist - tokens are just IDs
- ❌ Cannot be used for inference without embeddings
- ❌ No vector database integration
- ❌ Vocabulary adapter discards SOMA features

### Goal
Transform SOMA tokens into **inference-ready embeddings** that:
1. Preserve SOMA's mathematical properties
2. Enable similarity search and retrieval
3. Support ML model inference
4. Work with vector databases
5. Maintain semantic meaning

---

## 2. System Architecture

### 2.1 High-Level Flow

```
Text Input
    ↓
SOMA Tokenization
    ↓
TokenRecord (with UID, frontend, backend, etc.)
    ↓
Embedding Generator (Multiple Strategies)
    ↓
Dense Vector Embedding (e.g., 768-dim)
    ↓
Vector Database Storage
    ↓
Inference/Retrieval
```

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│              SOMA Embedding System                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │   SOMA     │───▶│  Embedding   │───▶│  Vector  │ │
│  │ Tokenization │    │   Generator  │    │ Database  │ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│         │                    │                  │       │
│         │                    │                  │       │
│         ▼                    ▼                  ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │ TokenRecord  │    │   Strategy   │    │ Inference│ │
│  │  (Metadata)  │    │   Selector   │    │  Engine  │ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Embedding Generation Strategies

### 3.1 Strategy 1: Feature-Based Embedding (Deterministic)

**Concept**: Convert SOMA's mathematical features directly into embeddings.

**Features Used**:
- `uid` (64-bit) → split into 8 bytes → 8 dimensions
- `frontend` (1-9) → one-hot encoded → 9 dimensions
- `backend_huge` (64-bit) → split into 8 bytes → 8 dimensions
- `content_id` (1-150000) → normalized → 1 dimension
- `global_id` (64-bit) → split into 8 bytes → 8 dimensions
- `prev_uid`, `next_uid` → context features → 16 dimensions
- `index` → position encoding → 1 dimension
- `stream` → tokenization strategy → one-hot → 9 dimensions

**Total**: ~60 base dimensions → projected to target dimension (e.g., 768)

**Advantages**:
- ✅ Deterministic (same token → same embedding)
- ✅ Preserves all SOMA features
- ✅ Fast generation (no ML model needed)
- ✅ Perfect reproducibility

**Disadvantages**:
- ❌ No semantic meaning (purely mathematical)
- ❌ May not capture token relationships well

### 3.2 Strategy 2: Hybrid Embedding (Text + Features)

**Concept**: Combine text-based embeddings with SOMA features.

**Process**:
1. Generate text embedding using pre-trained model (e.g., sentence-transformers)
2. Generate feature embedding from SOMA metadata
3. Concatenate or weighted combine both

**Formula**:
```
embedding = α × text_embedding + (1-α) × feature_embedding
```

**Advantages**:
- ✅ Semantic meaning from text embeddings
- ✅ Preserves SOMA mathematical properties
- ✅ Better for similarity search
- ✅ Can leverage pre-trained models

**Disadvantages**:
- ❌ Requires external embedding model
- ❌ Slightly slower
- ❌ Less deterministic (depends on text embedding model)

### 3.3 Strategy 3: Learned Embedding (Trainable)

**Concept**: Train a neural network to map SOMA features → embeddings.

**Architecture**:
```
Input: SOMA Features (60-dim)
    ↓
Dense Layer 1 (256 units, ReLU)
    ↓
Dense Layer 2 (512 units, ReLU)
    ↓
Dense Layer 3 (768 units, Linear)
    ↓
Output: Embedding (768-dim)
```

**Training**:
- Use contrastive learning (similar tokens → similar embeddings)
- Train on large corpus
- Optimize for downstream tasks (classification, retrieval, etc.)

**Advantages**:
- ✅ Learns optimal feature combinations
- ✅ Can be fine-tuned for specific tasks
- ✅ Best performance potential

**Disadvantages**:
- ❌ Requires training data and compute
- ❌ Not deterministic (model weights vary)
- ❌ Most complex to implement

### 3.4 Strategy 4: Hash-Based Embedding (Fast & Deterministic)

**Concept**: Use cryptographic hashing to create fixed-size embeddings.

**Process**:
1. Concatenate all SOMA features into string
2. Hash using SHA-256 or similar
3. Convert hash bytes to embedding vector
4. Normalize to unit vector

**Advantages**:
- ✅ Extremely fast
- ✅ Deterministic
- ✅ Fixed size output
- ✅ No external dependencies

**Disadvantages**:
- ❌ No semantic meaning
- ❌ Poor similarity properties (hash collisions rare but possible)

---

## 4. Implementation Design

### 4.1 Core Classes

#### `SOMAEmbeddingGenerator`

```python
class SOMAEmbeddingGenerator:
    """
    Generates embeddings from SOMA TokenRecord objects.
    """
    
    def __init__(
        self,
        strategy: str = "feature_based",
        embedding_dim: int = 768,
        text_model: Optional[str] = None,
        feature_weights: Optional[Dict] = None
    ):
        """
        Args:
            strategy: One of ["feature_based", "hybrid", "learned", "hash"]
            embedding_dim: Target embedding dimension
            text_model: Model name for text embeddings (if hybrid)
            feature_weights: Custom weights for feature combination
        """
        self.strategy = strategy
        self.embedding_dim = embedding_dim
        self.text_model = text_model
        self.feature_weights = feature_weights or self._default_weights()
        
    def generate(self, token_record: TokenRecord) -> np.ndarray:
        """Generate embedding for a single token."""
        if self.strategy == "feature_based":
            return self._feature_based_embedding(token_record)
        elif self.strategy == "hybrid":
            return self._hybrid_embedding(token_record)
        elif self.strategy == "learned":
            return self._learned_embedding(token_record)
        elif self.strategy == "hash":
            return self._hash_embedding(token_record)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def generate_batch(self, token_records: List[TokenRecord]) -> np.ndarray:
        """Generate embeddings for multiple tokens (batched)."""
        # Implementation with batching optimization
        pass
    
    def _feature_based_embedding(self, token: TokenRecord) -> np.ndarray:
        """Strategy 1: Feature-based deterministic embedding."""
        # Extract features
        features = self._extract_features(token)
        
        # Project to target dimension
        embedding = self._project_features(features)
        
        # Normalize
        return self._normalize(embedding)
    
    def _extract_features(self, token: TokenRecord) -> np.ndarray:
        """Extract numerical features from TokenRecord."""
        features = []
        
        # UID (64-bit → 8 bytes)
        uid_bytes = self._int64_to_bytes(token.uid)
        features.extend(uid_bytes)
        
        # Frontend (1-9 → one-hot)
        frontend_onehot = np.zeros(9)
        if 1 <= token.frontend <= 9:
            frontend_onehot[token.frontend - 1] = 1.0
        features.extend(frontend_onehot)
        
        # Backend (64-bit → 8 bytes)
        backend_bytes = self._int64_to_bytes(token.backend_huge)
        features.extend(backend_bytes)
        
        # Content ID (normalized)
        content_id_norm = token.content_id / 150000.0
        features.append(content_id_norm)
        
        # Global ID (64-bit → 8 bytes)
        global_bytes = self._int64_to_bytes(token.global_id)
        features.extend(global_bytes)
        
        # Neighbor UIDs
        prev_bytes = self._int64_to_bytes(token.prev_uid or 0)
        next_bytes = self._int64_to_bytes(token.next_uid or 0)
        features.extend(prev_bytes)
        features.extend(next_bytes)
        
        # Index (normalized)
        index_norm = token.index / 10000.0  # Assuming max 10k tokens
        features.append(index_norm)
        
        # Stream (one-hot: 9 tokenization strategies)
        stream_onehot = self._stream_to_onehot(token.stream)
        features.extend(stream_onehot)
        
        return np.array(features, dtype=np.float32)
    
    def _project_features(self, features: np.ndarray) -> np.ndarray:
        """Project feature vector to target embedding dimension."""
        # Use learned projection matrix or simple MLP
        if hasattr(self, '_projection_matrix'):
            return features @ self._projection_matrix
        else:
            # Simple linear projection with random initialization
            if not hasattr(self, '_random_projection'):
                np.random.seed(42)  # For reproducibility
                self._random_projection = np.random.randn(
                    len(features), self.embedding_dim
                ).astype(np.float32)
            return features @ self._random_projection
    
    def _normalize(self, embedding: np.ndarray) -> np.ndarray:
        """L2 normalize embedding."""
        norm = np.linalg.norm(embedding)
        if norm > 0:
            return embedding / norm
        return embedding
```

#### `SOMAVectorStore`

```python
class SOMAVectorStore:
    """
    Vector database interface for SOMA embeddings.
    Supports multiple backends: Chroma, FAISS, Qdrant, etc.
    """
    
    def __init__(
        self,
        backend: str = "chroma",
        collection_name: str = "soma_embeddings",
        embedding_dim: int = 768,
        persist_directory: Optional[str] = None
    ):
        self.backend = backend
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.persist_directory = persist_directory
        
        if backend == "chroma":
            self._init_chroma()
        elif backend == "faiss":
            self._init_faiss()
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def add_tokens(
        self,
        token_records: List[TokenRecord],
        embeddings: np.ndarray,
        metadata: Optional[List[Dict]] = None
    ):
        """Add tokens and their embeddings to the store."""
        pass
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar tokens."""
        pass
    
    def get_token_embedding(self, token_id: str) -> Optional[np.ndarray]:
        """Retrieve embedding for a specific token."""
        pass
```

---

## 5. Vector Database Integration

### 5.1 Chroma Integration (Recommended)

**Why Chroma**:
- ✅ Easy to use Python API
- ✅ Built-in persistence
- ✅ Metadata filtering
- ✅ Good performance

**Implementation**:
```python
import chromadb
from chromadb.config import Settings

class ChromaVectorStore(SOMAVectorStore):
    def _init_chroma(self):
        self.client = chromadb.Client(
            Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"embedding_dim": self.embedding_dim}
        )
    
    def add_tokens(self, token_records, embeddings, metadata=None):
        ids = [f"token_{i}" for i in range(len(token_records))]
        texts = [token.text for token in token_records]
        metadatas = metadata or [
            {
                "text": token.text,
                "stream": token.stream,
                "uid": str(token.uid),
                "frontend": token.frontend,
                "index": token.index
            }
            for token in token_records
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query_embedding, top_k=10, filter=None):
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filter
        )
        return results
```

### 5.2 FAISS Integration (High Performance)

**Why FAISS**:
- ✅ Extremely fast similarity search
- ✅ GPU support
- ✅ Memory efficient
- ✅ Facebook/Meta maintained

**Implementation**:
```python
import faiss
import numpy as np

class FAISSVectorStore(SOMAVectorStore):
    def _init_faiss(self):
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.token_map = {}  # Map index → TokenRecord
    
    def add_tokens(self, token_records, embeddings, metadata=None):
        start_idx = self.index.ntotal
        self.index.add(embeddings.astype('float32'))
        
        # Store token mapping
        for i, token in enumerate(token_records):
            self.token_map[start_idx + i] = token
    
    def search(self, query_embedding, top_k=10, filter=None):
        query = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx in self.token_map:
                results.append({
                    "token": self.token_map[idx],
                    "distance": float(dist),
                    "index": int(idx)
                })
        return results
```

---

## 6. Inference Pipeline

### 6.1 Complete Inference Flow

```python
class SOMAInferencePipeline:
    """
    End-to-end inference pipeline using SOMA embeddings.
    """
    
    def __init__(
        self,
        embedding_generator: SOMAEmbeddingGenerator,
        vector_store: SOMAVectorStore,
        tokenizer: TextTokenizer
    ):
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.tokenizer = tokenizer
    
    def process_text(self, text: str) -> Dict:
        """
        Process text through complete pipeline:
        1. Tokenize with SOMA
        2. Generate embeddings
        3. Store in vector database
        4. Return results
        """
        # Step 1: Tokenize
        streams = self.tokenizer.build(text)
        
        # Step 2: Generate embeddings for all tokens
        all_embeddings = []
        all_tokens = []
        
        for stream_name, token_stream in streams.items():
            for token in token_stream.tokens:
                embedding = self.embedding_generator.generate(token)
                all_embeddings.append(embedding)
                all_tokens.append(token)
        
        embeddings_array = np.array(all_embeddings)
        
        # Step 3: Store in vector database
        self.vector_store.add_tokens(all_tokens, embeddings_array)
        
        return {
            "tokens": all_tokens,
            "embeddings": embeddings_array,
            "streams": {name: len(stream.tokens) for name, stream in streams.items()}
        }
    
    def similarity_search(
        self,
        query_text: str,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Search for similar tokens using query text.
        """
        # Tokenize query
        query_streams = self.tokenizer.build(query_text)
        
        # Generate query embedding (average of token embeddings)
        query_embeddings = []
        for stream_name, token_stream in query_streams.items():
            for token in token_stream.tokens:
                embedding = self.embedding_generator.generate(token)
                query_embeddings.append(embedding)
        
        if not query_embeddings:
            return []
        
        # Average query embeddings
        query_embedding = np.mean(query_embeddings, axis=0)
        
        # Search
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        return results
```

---

## 7. Implementation Plan

### Phase 1: Core Embedding Generation (Week 1-2)

**Tasks**:
1. ✅ Implement `SOMAEmbeddingGenerator` class
2. ✅ Implement feature extraction from TokenRecord
3. ✅ Implement feature-based embedding strategy
4. ✅ Add unit tests
5. ✅ Create embedding visualization tools

**Deliverables**:
- `src/embeddings/embedding_generator.py`
- `src/embeddings/feature_extractor.py`
- `tests/test_embedding_generator.py`

### Phase 2: Vector Database Integration (Week 2-3)

**Tasks**:
1. ✅ Implement Chroma backend
2. ✅ Implement FAISS backend
3. ✅ Create unified `SOMAVectorStore` interface
4. ✅ Add persistence support
5. ✅ Performance benchmarking

**Deliverables**:
- `src/embeddings/vector_store.py`
- `src/embeddings/backends/chroma_store.py`
- `src/embeddings/backends/faiss_store.py`

### Phase 3: Hybrid Embedding Strategy (Week 3-4)

**Tasks**:
1. ✅ Integrate sentence-transformers
2. ✅ Implement hybrid embedding combination
3. ✅ Add configuration for weight tuning
4. ✅ Benchmark against feature-based

**Deliverables**:
- `src/embeddings/strategies/hybrid_embedding.py`
- `src/embeddings/text_embedders.py`

### Phase 4: Inference Pipeline (Week 4-5)

**Tasks**:
1. ✅ Implement `SOMAInferencePipeline`
2. ✅ Add batch processing
3. ✅ Create API endpoints
4. ✅ Add similarity search API
5. ✅ Performance optimization

**Deliverables**:
- `src/embeddings/inference_pipeline.py`
- `src/servers/embedding_server.py`
- API documentation

### Phase 5: Advanced Features (Week 5-6)

**Tasks**:
1. ✅ Implement learned embedding strategy (optional)
2. ✅ Add embedding fine-tuning tools
3. ✅ Create embedding visualization dashboard
4. ✅ Add embedding export/import
5. ✅ Comprehensive documentation

**Deliverables**:
- `src/embeddings/strategies/learned_embedding.py`
- `src/embeddings/training/embedding_trainer.py`
- Frontend embedding visualization

---

## 8. Usage Examples

### Example 1: Basic Embedding Generation

```python
from src.core.core_tokenizer import TextTokenizer
from src.embeddings.embedding_generator import SOMAEmbeddingGenerator

# Initialize
tokenizer = TextTokenizer(seed=42, embedding_bit=False)
embedding_gen = SOMAEmbeddingGenerator(
    strategy="feature_based",
    embedding_dim=768
)

# Tokenize text
text = "Hello world, this is SOMA!"
streams = tokenizer.build(text)

# Generate embeddings
for stream_name, token_stream in streams.items():
    for token in token_stream.tokens:
        embedding = embedding_gen.generate(token)
        print(f"Token: {token.text}")
        print(f"Embedding shape: {embedding.shape}")
        print(f"Embedding norm: {np.linalg.norm(embedding)}")
```

### Example 2: Vector Database Storage and Search

```python
from src.embeddings.vector_store import ChromaVectorStore
from src.embeddings.inference_pipeline import SOMAInferencePipeline

# Initialize pipeline
vector_store = ChromaVectorStore(
    backend="chroma",
    collection_name="soma_embeddings",
    persist_directory="./vector_db"
)

pipeline = SOMAInferencePipeline(
    embedding_generator=embedding_gen,
    vector_store=vector_store,
    tokenizer=tokenizer
)

# Process and store documents
documents = [
    "Machine learning is fascinating",
    "Natural language processing enables AI",
    "SOMA provides perfect tokenization"
]

for doc in documents:
    pipeline.process_text(doc)

# Search for similar content
results = pipeline.similarity_search(
    query_text="artificial intelligence",
    top_k=5
)

for result in results:
    print(f"Token: {result['token'].text}")
    print(f"Distance: {result['distance']}")
```

### Example 3: Hybrid Embedding

```python
# Use hybrid strategy with semantic understanding
hybrid_gen = SOMAEmbeddingGenerator(
    strategy="hybrid",
    embedding_dim=768,
    text_model="sentence-transformers/all-MiniLM-L6-v2",
    feature_weights={"text": 0.7, "features": 0.3}
)

# Generate embeddings with both semantic and mathematical features
embedding = hybrid_gen.generate(token_record)
```

---

## 9. Performance Considerations

### 9.1 Embedding Generation Speed

| Strategy | Speed (tokens/sec) | Memory (MB) |
|----------|-------------------|-------------|
| Feature-based | ~100K | ~50 |
| Hybrid | ~10K | ~200 |
| Learned | ~50K | ~100 |
| Hash | ~200K | ~20 |

### 9.2 Vector Database Performance

| Backend | Insert (tokens/sec) | Search (QPS) | Memory |
|---------|---------------------|--------------|--------|
| Chroma | ~5K | ~1K | Medium |
| FAISS | ~50K | ~10K | Low |

### 9.3 Optimization Strategies

1. **Batch Processing**: Generate embeddings in batches
2. **Caching**: Cache embeddings for repeated tokens
3. **GPU Acceleration**: Use GPU for learned embeddings
4. **Indexing**: Build FAISS indices for fast search

---

## 10. Future Enhancements

1. **Multi-Modal Embeddings**: Support for images, audio, etc.
2. **Fine-Tuning Tools**: GUI for embedding strategy tuning
3. **Embedding Analytics**: Clustering, visualization, analysis
4. **Distributed Storage**: Support for distributed vector databases
5. **Real-Time Updates**: Streaming embedding generation

---

## 11. Conclusion

This design provides a complete path from SOMA tokens to inference-ready embeddings. The system:

- ✅ Preserves SOMA's mathematical properties
- ✅ Enables similarity search and retrieval
- ✅ Supports multiple embedding strategies
- ✅ Integrates with vector databases
- ✅ Provides end-to-end inference pipeline

**Next Steps**: Begin Phase 1 implementation.

