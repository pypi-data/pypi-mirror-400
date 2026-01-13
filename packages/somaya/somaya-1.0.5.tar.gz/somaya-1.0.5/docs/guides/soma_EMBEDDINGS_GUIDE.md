# SOMA Embeddings Guide - Complete Reference

## Table of Contents
1. [Overview](#overview)
2. [Embedding Strategies](#embedding-strategies)
3. [Feature-Based Embeddings](#feature-based-embeddings)
4. [Semantic Embeddings](#semantic-embeddings)
5. [Hybrid Embeddings](#hybrid-embeddings)
6. [Hash-Based Embeddings](#hash-based-embeddings)
7. [Embedding Pipeline](#embedding-pipeline)
8. [Feature Extraction](#feature-extraction)
9. [Complete Example](#complete-example)
10. [Summary](#summary)

---

## Overview

SOMA embeddings convert tokens into high-dimensional vector representations that capture semantic and structural information. These embeddings enable similarity search, clustering, and other downstream tasks.

### What are Embeddings?

**Embeddings** are numerical vector representations of tokens (words or subwords). Each token is mapped to a fixed-size vector (e.g., 768 dimensions) where similar tokens have similar vector representations.

### Key Concepts

- **Embedding Dimension**: The size of the vector (default: 768)
- **Normalization**: L2 normalization to unit length
- **Feature Extraction**: Converting token properties to numerical features
- **Projection**: Mapping features to target embedding dimension

### Embedding Strategies

SOMA supports **4 different embedding strategies**:

1. **feature_based**: Deterministic embedding from SOMA token features
2. **semantic**: Self-trained semantic embeddings (learned from co-occurrence)
3. **hybrid**: Combines text embeddings with SOMA features
4. **hash**: Fast hash-based embedding

---

## Embedding Strategies

### Summary of All 4 Strategies

| # | Strategy | Description | Deterministic | Requires Training | Use Case |
|---|----------|-------------|---------------|------------------|----------|
| 1 | **feature_based** | Based on SOMA token features | Yes | No | Fast, reproducible embeddings |
| 2 | **semantic** | Learned semantic relationships | Yes (after training) | Yes | Semantic similarity search |
| 3 | **hybrid** | Text + SOMA features | No | No (uses pretrained) | Best semantic understanding |
| 4 | **hash** | Hash-based fast embedding | Yes | No | Ultra-fast, simple embeddings |

---

## Feature-Based Embeddings

### What is Feature-Based Embedding?

Feature-based embeddings generate deterministic vectors from SOMA's token features (UID, frontend digit, backend number, etc.). This strategy requires no training and produces reproducible embeddings.

### Algorithm

1. **Extract Features**: Convert token properties to numerical features
2. **Project**: Multiply features by projection matrix
3. **Normalize**: L2 normalization to unit length

### Feature Extraction

Features are extracted from token properties:

1. **UID** (8 bytes): 64-bit unique identifier → normalized to [0, 1]
2. **Frontend Digit** (9 values): One-hot encoded (1-9)
3. **Backend Huge** (8 bytes): 64-bit number → normalized to [0, 1]
4. **Content ID** (1 value): Normalized to [0, 1]
5. **Global ID** (8 bytes): 64-bit identifier → normalized to [0, 1]
6. **Previous UID** (8 bytes): Context information
7. **Next UID** (8 bytes): Context information
8. **Index** (1 value): Token position, normalized
9. **Stream Type** (9 values): One-hot encoded tokenization type

**Total Feature Dimension**: ~60 features (8+9+8+1+8+8+8+1+9 = 60)

### Projection Matrix

Features are projected to target embedding dimension using a random projection matrix:

```
projection_matrix = random_matrix(feature_dim, embedding_dim)
projection_matrix = projection_matrix / sqrt(feature_dim)  # Normalized
embedding = features @ projection_matrix
```

### Normalization

Final embedding is L2-normalized to unit length:

```
norm = sqrt(sum(embedding²))
embedding = embedding / norm
```

### Properties

- **Deterministic**: Same token always produces same embedding (same seed)
- **Fast**: No model inference required
- **Reproducible**: Uses fixed random seed
- **Feature-Rich**: Captures all SOMA token properties

---

## Semantic Embeddings

### What is Semantic Embedding?

Semantic embeddings are learned from token co-occurrence patterns. The model is trained on text data to learn which tokens appear together, creating embeddings that capture semantic relationships.

### Key Characteristics

- **Self-Trained**: No pretrained models, learns from data
- **Co-occurrence Based**: Learns from tokens appearing together
- **Requires Training**: Must train model before use
- **Semantic Understanding**: Captures meaning relationships

### Training Process

1. **Data Collection**: Gather text data
2. **Tokenization**: Convert text to tokens using SOMA
3. **Co-occurrence Learning**: Learn which tokens appear together
4. **Embedding Update**: Update embeddings based on context
5. **Model Save**: Save trained model for reuse

### Usage

After training, semantic embeddings provide:
- Similar tokens have similar embeddings
- Related concepts are close in embedding space
- Better semantic search than feature-based

---

## Hybrid Embeddings

### What is Hybrid Embedding?

Hybrid embeddings combine text-based embeddings (from sentence-transformers) with SOMA feature-based embeddings. This combines the best of both worlds: semantic understanding from text models and structural information from SOMA features.

### Algorithm

1. **Text Embedding**: Generate embedding from token text using pretrained model
2. **Feature Embedding**: Generate feature-based embedding
3. **Dimension Alignment**: Ensure both have same dimension
4. **Weighted Combination**: Combine with weights (default: 70% text, 30% features)
5. **Project & Normalize**: Project to target dimension and normalize

### Formula

```
text_embedding = sentence_transformer(token.text)
feature_embedding = feature_based_embedding(token)
combined = (0.7 * text_embedding) + (0.3 * feature_embedding)
final = normalize(project(combined, target_dim))
```

### Properties

- **Semantic Rich**: Uses pretrained text models
- **Structure Aware**: Includes SOMA features
- **Configurable Weights**: Can adjust text/feature balance
- **Requires Dependencies**: Needs sentence-transformers library

---

## Hash-Based Embeddings

### What is Hash-Based Embedding?

Hash-based embeddings generate deterministic embeddings using cryptographic hashing. This is the fastest method but provides less semantic information.

### Algorithm

1. **Create Hash String**: Concatenate all token properties
2. **SHA-256 Hash**: Generate hash bytes
3. **Convert to Vector**: Map hash bytes to embedding dimensions
4. **Normalize**: L2 normalization

### Hash String Construction

```
hash_string = f"{text}_{uid}_{frontend}_{backend_huge}_{content_id}_{global_id}"
hash_bytes = SHA256(hash_string)
```

### Vector Generation

Hash bytes are repeated to fill embedding dimension:

```
for i in range(embedding_dim):
    byte_idx = i % len(hash_bytes)
    embedding[i] = hash_bytes[byte_idx] / 255.0
```

### Properties

- **Fastest**: Very quick computation
- **Deterministic**: Same input → same output
- **Fixed Size**: Always produces embedding_dim sized vector
- **Less Semantic**: Primarily for indexing, not semantic search

---

## Embedding Pipeline

### Complete Process Flow

```
Input Text
    ↓
[1. Tokenization]
    └─ Convert text to tokens (using one of 9 tokenization methods)
    ↓
[2. Token Records]
    └─ Create TokenRecord objects with:
       - UID, frontend, backend_huge, content_id, global_id
       - prev_uid, next_uid, index, stream
    ↓
[3. Feature Extraction] (for feature_based/hybrid/hash)
    └─ Extract numerical features from token properties
    ↓
[4. Embedding Generation]
    ├─ feature_based: features @ projection_matrix
    ├─ semantic: lookup in trained model
    ├─ hybrid: combine text + features
    └─ hash: SHA-256 hash → vector
    ↓
[5. Normalization]
    └─ L2 normalize to unit length
    ↓
Output: Embedding Vectors
```

---

## Feature Extraction

### Detailed Feature Breakdown

For a token, features are extracted as follows:

#### 1. UID (8 bytes)

```
uid = token.uid  # 64-bit integer
bytes = int64_to_bytes(uid)  # Convert to 8 bytes
normalized = [b / 255.0 for b in bytes]  # Normalize to [0, 1]
Features: 8 values
```

#### 2. Frontend Digit (9 values, one-hot)

```
frontend = token.frontend  # 1-9
onehot = [0, 0, 0, 0, 0, 0, 0, 0, 0]
onehot[frontend - 1] = 1.0  # Set position to 1
Features: 9 values
```

#### 3. Backend Huge (8 bytes)

```
backend_huge = token.backend_huge  # 64-bit integer
bytes = int64_to_bytes(backend_huge)
normalized = [b / 255.0 for b in bytes]
Features: 8 values
```

#### 4. Content ID (1 value)

```
content_id = token.content_id
normalized = content_id / 150000.0  # Normalize
Features: 1 value
```

#### 5. Global ID (8 bytes)

```
global_id = token.global_id  # 64-bit integer
bytes = int64_to_bytes(global_id)
normalized = [b / 255.0 for b in bytes]
Features: 8 values
```

#### 6. Previous UID (8 bytes)

```
prev_uid = token.prev_uid or 0
bytes = int64_to_bytes(prev_uid)
normalized = [b / 255.0 for b in bytes]
Features: 8 values
```

#### 7. Next UID (8 bytes)

```
next_uid = token.next_uid or 0
bytes = int64_to_bytes(next_uid)
normalized = [b / 255.0 for b in bytes]
Features: 8 values
```

#### 8. Index (1 value)

```
index = token.index
normalized = index / 10000.0  # Assuming max 10k tokens
Features: 1 value
```

#### 9. Stream Type (9 values, one-hot)

```
stream = token.stream  # "space", "word", "char", etc.
streams = ["space", "word", "char", "grammar", "subword",
           "subword_bpe", "subword_syllable", "subword_frequency", "byte"]
onehot = [0, 0, 0, 0, 0, 0, 0, 0, 0]
onehot[streams.index(stream)] = 1.0
Features: 9 values
```

**Total**: 8 + 9 + 8 + 1 + 8 + 8 + 8 + 1 + 9 = **60 features**

---

## Complete Example

### Example: "I LOVE BEING ALONE"

Let's demonstrate feature-based embedding generation:

#### Step 1: Tokenization

```
Input: "I LOVE BEING ALONE"
After preprocessing: "i love being alone"
Tokens: ["i", "love", "being", "alone"]
```

#### Step 2: Token Properties (Example for "love")

```
Token: "love"
UID: 1234567890123456789 (example)
Frontend: 9
Backend Huge: 9876543210987654321 (example)
Content ID: 45231
Global ID: 1122334455667788990 (example)
Previous UID: 1111111111111111111 (for "i")
Next UID: 2222222222222222222 (for "being")
Index: 1
Stream: "word"
```

#### Step 3: Feature Extraction

```
Features (60 values):
- UID bytes (8): [0.48, 0.21, 0.35, ...]  # Normalized bytes
- Frontend one-hot (9): [0, 0, 0, 0, 0, 0, 0, 0, 1]  # Position 8 = 1
- Backend bytes (8): [0.38, 0.52, 0.67, ...]
- Content ID (1): 0.3015  # 45231 / 150000
- Global ID bytes (8): [0.43, 0.28, 0.51, ...]
- Prev UID bytes (8): [0.41, 0.44, 0.44, ...]
- Next UID bytes (8): [0.51, 0.51, 0.51, ...]
- Index (1): 0.0001  # 1 / 10000
- Stream one-hot (9): [0, 1, 0, 0, 0, 0, 0, 0, 0]  # "word" at index 1
```

#### Step 4: Projection

```
Feature vector: shape (60,)
Projection matrix: shape (60, 768)  # Random, normalized
Embedding = features @ projection_matrix  # shape (768,)
```

#### Step 5: Normalization

```
Norm = sqrt(sum(embedding²))
Embedding = embedding / norm
Final embedding: shape (768,) with L2 norm = 1.0
```

---

## Summary

This guide covers SOMA's embedding system:

### Key Takeaways

1. **4 Embedding Strategies**: feature_based, semantic, hybrid, hash
2. **Feature-Based (Default)**: Deterministic, fast, no training needed
3. **Semantic**: Learned embeddings, requires training
4. **Hybrid**: Best semantic understanding, combines text + features
5. **Hash**: Fastest, simple indexing

### Feature Extraction

- **60 Features** extracted from token properties
- Includes: UID, frontend, backend, content_id, global_id, neighbors, index, stream
- All features normalized to [0, 1] range

### Embedding Process

1. Extract features from tokens
2. Project to target dimension (default: 768)
3. L2 normalize to unit length
4. Result: Fixed-size vector representation

### Use Cases

- **Feature-Based**: General purpose, reproducible embeddings
- **Semantic**: Semantic similarity search
- **Hybrid**: Best semantic understanding
- **Hash**: Fast indexing and retrieval

---

*This guide provides a complete reference for understanding and implementing SOMA embeddings. All strategies have been verified against the actual implementation.*
