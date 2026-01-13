# How SOMA Embeddings Work (Feature-Based Strategy)

## Overview

SOMA's **feature-based embeddings** convert mathematical token features into dense vector embeddings through a deterministic mathematical process. **No machine learning or pretrained models are used.**

---

## Step-by-Step Process

### Step 1: Tokenization with SOMA

When you tokenize text, SOMA creates `TokenRecord` objects with mathematical features:

```python
TokenRecord(
    text="hello",
    uid=18446744073709551615,           # 64-bit unique ID
    frontend=7,                          # 1-9 digit
    backend_huge=9876543210987654321,   # 64-bit hash
    content_id=12345,                    # Content-based ID
    global_id=12345678901234567890,      # Global identifier
    prev_uid=11111111111111111111,       # Previous token's UID
    next_uid=22222222222222222222,       # Next token's UID
    index=0,                             # Position in sequence
    stream="word"                        # Tokenization strategy
)
```

---

### Step 2: Feature Extraction

The embedding generator extracts **~60 numerical features** from each token:

```python
def _extract_features(token):
    features = []
    
    # 1. UID → 8 bytes (normalized 0-1)
    uid_bytes = int64_to_bytes(token.uid)  # [0.123, 0.456, ...] (8 values)
    features.extend(uid_bytes)  # +8 features
    
    # 2. Frontend digit → one-hot encoding (1-9)
    frontend_onehot = [0,0,0,0,0,0,1,0,0]  # if frontend=7
    features.extend(frontend_onehot)  # +9 features
    
    # 3. Backend huge → 8 bytes
    backend_bytes = int64_to_bytes(token.backend_huge)  # 8 values
    features.extend(backend_bytes)  # +8 features
    
    # 4. Content ID → normalized (0-1)
    content_id_norm = token.content_id / 150000.0  # 1 value
    features.append(content_id_norm)  # +1 feature
    
    # 5. Global ID → 8 bytes
    global_bytes = int64_to_bytes(token.global_id)  # 8 values
    features.extend(global_bytes)  # +8 features
    
    # 6. Neighbor UIDs → 16 bytes (prev + next)
    prev_bytes = int64_to_bytes(token.prev_uid or 0)  # 8 values
    next_bytes = int64_to_bytes(token.next_uid or 0)   # 8 values
    features.extend(prev_bytes)  # +8 features
    features.extend(next_bytes)  # +8 features
    
    # 7. Index → normalized position
    index_norm = token.index / 10000.0  # 1 value
    features.append(index_norm)  # +1 feature
    
    # 8. Stream → one-hot encoding (9 strategies)
    stream_onehot = [1,0,0,0,0,0,0,0,0]  # if stream="space"
    features.extend(stream_onehot)  # +9 features
    
    # Total: ~60 features
    return np.array(features)  # Shape: (60,)
```

**Example Feature Vector:**
```
[0.123, 0.456, ..., 0.789,  # UID bytes (8)
 0, 0, 0, 0, 0, 0, 1, 0, 0,  # Frontend one-hot (9)
 0.234, 0.567, ..., 0.890,  # Backend bytes (8)
 0.0823,                     # Content ID norm (1)
 0.345, 0.678, ..., 0.901,  # Global ID bytes (8)
 0.111, 0.222, ..., 0.333,  # Prev UID bytes (8)
 0.444, 0.555, ..., 0.666,  # Next UID bytes (8)
 0.0001,                     # Index norm (1)
 1, 0, 0, 0, 0, 0, 0, 0, 0] # Stream one-hot (9)
```

---

### Step 3: Feature-to-Embedding Projection

The ~60 features are projected to the target embedding dimension (e.g., 768) using a **random projection matrix**:

```python
# Initialize projection matrix (once, then reused)
projection_matrix = np.random.randn(60, 768)  # Shape: (60, 768)
projection_matrix = projection_matrix / sqrt(60)  # Normalize

# Project features to embedding
embedding = features @ projection_matrix  # (60,) @ (60, 768) = (768,)
```

**Mathematical Operation:**
```
embedding[i] = Σ(features[j] * projection_matrix[j][i])
              for j in range(60)
```

This is a **linear transformation** - no neural networks, no training, just matrix multiplication.

---

### Step 4: Normalization

The embedding vector is L2-normalized to unit length:

```python
norm = sqrt(sum(embedding[i]^2 for i in range(768)))
embedding = embedding / norm
```

**Result:** Embedding vector with length = 1.0

---

## Complete Flow Diagram

```
Text: "Hello world"
    ↓
SOMA Tokenization
    ↓
TokenRecord {
    text: "Hello",
    uid: 18446744073709551615,
    frontend: 7,
    backend_huge: 9876543210987654321,
    ...
}
    ↓
Feature Extraction
    ↓
Feature Vector (60 dimensions):
[0.123, 0.456, ..., 0.789,  # UID
 0,0,0,0,0,0,1,0,0,          # Frontend
 0.234, 0.567, ...,          # Backend
 ...]
    ↓
Projection Matrix (60 × 768)
    ↓
Embedding Vector (768 dimensions):
[0.001, -0.023, 0.456, ..., 0.789]
    ↓
L2 Normalization
    ↓
Final Embedding (768-dim, unit vector):
[0.0001, -0.0023, 0.0456, ..., 0.0789]
```

---

## Key Points

### ✅ What It Uses:
- **SOMA's mathematical features only**
- **Deterministic projection matrix** (random but fixed)
- **Linear algebra** (matrix multiplication)
- **No machine learning**
- **No pretrained models**
- **No training data**

### ❌ What It Doesn't Use:
- ❌ BERT embeddings
- ❌ sentence-transformers
- ❌ Any pretrained models
- ❌ Neural networks
- ❌ Training data
- ❌ Learned weights

---

## Why This Works

1. **Rich Features**: SOMA tokens contain ~60 numerical features that capture:
   - Token identity (UID)
   - Content properties (content_id, frontend digit)
   - Context (neighbors, position)
   - Tokenization strategy (stream)

2. **Dimensionality Expansion**: Projection from 60 → 768 dimensions:
   - Spreads information across more dimensions
   - Creates dense representation
   - Enables similarity calculations

3. **Normalization**: Unit vectors enable:
   - Cosine similarity calculations
   - Consistent vector magnitudes
   - Better for similarity search

---

## Example Calculation

**Token:** "hello"

**SOMA Features:**
- UID: `18446744073709551615`
- Frontend: `7`
- Backend: `9876543210987654321`
- Content ID: `12345`
- Global ID: `12345678901234567890`
- Index: `0`
- Stream: `"word"`

**Feature Extraction:**
```python
# UID → 8 bytes
uid_bytes = [0.123, 0.456, 0.789, 0.012, 0.345, 0.678, 0.901, 0.234]

# Frontend 7 → one-hot
frontend = [0, 0, 0, 0, 0, 0, 1, 0, 0]

# ... (all other features)

# Total: 60 features
features = [0.123, 0.456, ..., 1, 0, 0, ...]  # 60 values
```

**Projection:**
```python
# Random projection matrix (60 × 768)
projection = np.random.randn(60, 768)

# Matrix multiplication
embedding = features @ projection  # (60,) @ (60, 768) = (768,)
```

**Normalization:**
```python
norm = sqrt(sum(embedding^2))
embedding = embedding / norm  # Unit vector
```

**Result:** 768-dimensional embedding vector, purely from SOMA math!

---

## Comparison with Pretrained Models

| Aspect | SOMA Feature-Based | BERT/sentence-transformers |
|--------|---------------------|---------------------------|
| **Source** | SOMA math features | Learned from billions of tokens |
| **Training** | None | Extensive pretraining |
| **Deterministic** | ✅ Yes | ⚠️ Mostly (model weights fixed) |
| **Semantic** | ❌ No | ✅ Yes |
| **Dependencies** | None | Requires model files |
| **Speed** | Very fast | Slower |
| **Size** | Small (just projection matrix) | Large (model weights) |

---

## Summary

**SOMA embeddings are:**
1. ✅ **Mathematically derived** from token features
2. ✅ **Deterministic** (same token → same embedding)
3. ✅ **No pretrained models** (pure math)
4. ✅ **Fast** (just matrix multiplication)
5. ✅ **No dependencies** (works without ML libraries)

**They are NOT:**
- ❌ Learned from data
- ❌ Using BERT or any pretrained model
- ❌ Semantic embeddings
- ❌ Trained on any corpus

It's a **mathematical transformation** of SOMA's internal features into dense vectors suitable for similarity search and inference.

