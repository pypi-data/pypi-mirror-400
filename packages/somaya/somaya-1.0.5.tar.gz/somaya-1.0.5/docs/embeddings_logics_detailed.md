# SOMA Embeddings Logic - Detailed Step-by-Step Mathematical Calculations

## Example Token
```
Token: "you're"
Token Record:
{
    "text": "you're",
    "id": 0,
    "index": 0,
    "type": "content",
    "length": 6,
    "uid": 3784123456789012345,
    "prev_uid": null,
    "next_uid": 9234567890123456789,
    "frontend": 4,
    "backend": 3784123456789000159,
    "content_id": 3570164763,
    "global_id": 3784119886624847592,
    "stream": "space"
}
```

---

## PART 1: FEATURE-BASED EMBEDDINGS - DETAILED CALCULATION

### Strategy: Feature-Based (Deterministic from SOMA Features)

### Step 1: Feature Extraction

**Formula**: Extract numerical features from token record

**Feature Vector Components**:

#### Component 1: UID (8 dimensions)
```
UID: 3784123456789012345 (64-bit integer)

Step 1: Convert to bytes
bytes = UID.to_bytes(8, byteorder='big', signed=False)

Calculation:
3784123456789012345 in binary (64 bits):
= 00110100 01110010 01000001 00110010 00110011 01000100 01000101 00111001

Byte values:
byte[0] = 0x34 = 52
byte[1] = 0x72 = 114
byte[2] = 0x41 = 65
byte[3] = 0x32 = 50
byte[4] = 0x33 = 51
byte[5] = 0x44 = 68
byte[6] = 0x45 = 69
byte[7] = 0x39 = 57

Step 2: Normalize to [0, 1]
feature[0] = 52 / 255.0 = 0.2039
feature[1] = 114 / 255.0 = 0.4471
feature[2] = 65 / 255.0 = 0.2549
feature[3] = 50 / 255.0 = 0.1961
feature[4] = 51 / 255.0 = 0.2000
feature[5] = 68 / 255.0 = 0.2667
feature[6] = 69 / 255.0 = 0.2706
feature[7] = 57 / 255.0 = 0.2235

UID Features: [0.2039, 0.4471, 0.2549, 0.1961, 0.2000, 0.2667, 0.2706, 0.2235]
```

#### Component 2: Frontend (9 dimensions - One-Hot)
```
Frontend: 4

One-Hot Encoding:
frontend_onehot = [0, 0, 0, 1, 0, 0, 0, 0, 0]
                 [1, 2, 3, 4, 5, 6, 7, 8, 9]

Frontend Features: [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

#### Component 3: Backend (8 dimensions)
```
Backend: 3784123456789000159 (64-bit integer)

Step 1: Convert to bytes
bytes = Backend.to_bytes(8, byteorder='big', signed=False)

Byte values:
byte[0] = 0x34 = 52
byte[1] = 0x72 = 114
byte[2] = 0x41 = 65
byte[3] = 0x32 = 50
byte[4] = 0x33 = 51
byte[5] = 0x44 = 68
byte[6] = 0x45 = 69
byte[7] = 0x0F = 15

Step 2: Normalize to [0, 1]
feature[0] = 52 / 255.0 = 0.2039
feature[1] = 114 / 255.0 = 0.4471
feature[2] = 65 / 255.0 = 0.2549
feature[3] = 50 / 255.0 = 0.1961
feature[4] = 51 / 255.0 = 0.2000
feature[5] = 68 / 255.0 = 0.2667
feature[6] = 69 / 255.0 = 0.2706
feature[7] = 15 / 255.0 = 0.0588

Backend Features: [0.2039, 0.4471, 0.2549, 0.1961, 0.2000, 0.2667, 0.2706, 0.0588]
```

#### Component 4: Content ID (1 dimension)
```
Content ID: 3570164763

Normalization:
content_id_norm = 3570164763 / 150000.0 = 23,801.0984

But we clamp to [0, 1] range:
content_id_norm = min(1.0, 3570164763 / 150000.0) = 1.0

Content ID Feature: [1.0]
```

#### Component 5: Global ID (8 dimensions)
```
Global ID: 3784119886624847592 (64-bit integer)

Step 1: Convert to bytes
bytes = Global_ID.to_bytes(8, byteorder='big', signed=False)

Byte values:
byte[0] = 0x34 = 52
byte[1] = 0x72 = 114
byte[2] = 0x41 = 65
byte[3] = 0x32 = 50
byte[4] = 0x33 = 51
byte[5] = 0x44 = 68
byte[6] = 0x45 = 69
byte[7] = 0x28 = 40

Step 2: Normalize to [0, 1]
feature[0] = 52 / 255.0 = 0.2039
feature[1] = 114 / 255.0 = 0.4471
feature[2] = 65 / 255.0 = 0.2549
feature[3] = 50 / 255.0 = 0.1961
feature[4] = 51 / 255.0 = 0.2000
feature[5] = 68 / 255.0 = 0.2667
feature[6] = 69 / 255.0 = 0.2706
feature[7] = 40 / 255.0 = 0.1569

Global ID Features: [0.2039, 0.4471, 0.2549, 0.1961, 0.2000, 0.2667, 0.2706, 0.1569]
```

#### Component 6: Previous UID (8 dimensions)
```
Prev UID: null → 0

Step 1: Convert to bytes
bytes = 0.to_bytes(8, byteorder='big', signed=False) = [0, 0, 0, 0, 0, 0, 0, 0]

Step 2: Normalize to [0, 1]
feature[i] = 0 / 255.0 = 0.0 for all i

Prev UID Features: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

#### Component 7: Next UID (8 dimensions)
```
Next UID: 9234567890123456789 (64-bit integer)

Step 1: Convert to bytes
bytes = Next_UID.to_bytes(8, byteorder='big', signed=False)

Byte values:
byte[0] = 0x80 = 128
byte[1] = 0x1E = 30
byte[2] = 0x85 = 133
byte[3] = 0x1E = 30
byte[4] = 0x85 = 133
byte[5] = 0x1E = 30
byte[6] = 0x85 = 133
byte[7] = 0x15 = 21

Step 2: Normalize to [0, 1]
feature[0] = 128 / 255.0 = 0.5020
feature[1] = 30 / 255.0 = 0.1176
feature[2] = 133 / 255.0 = 0.5216
feature[3] = 30 / 255.0 = 0.1176
feature[4] = 133 / 255.0 = 0.5216
feature[5] = 30 / 255.0 = 0.1176
feature[6] = 133 / 255.0 = 0.5216
feature[7] = 21 / 255.0 = 0.0824

Next UID Features: [0.5020, 0.1176, 0.5216, 0.1176, 0.5216, 0.1176, 0.5216, 0.0824]
```

#### Component 8: Index (1 dimension)
```
Index: 0

Normalization:
index_norm = 0 / 10000.0 = 0.0

Index Feature: [0.0]
```

#### Component 9: Stream (9 dimensions - One-Hot)
```
Stream: "space"

Streams list: ["space", "word", "char", "grammar", "subword", 
              "subword_bpe", "subword_syllable", "subword_frequency", "byte"]

One-Hot Encoding:
stream_onehot = [1, 0, 0, 0, 0, 0, 0, 0, 0]
                [space, word, char, grammar, subword, ...]

Stream Features: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

### Step 2: Concatenate All Features

**Total Feature Dimension**: 8 + 9 + 8 + 1 + 8 + 8 + 8 + 1 + 9 = **60 dimensions**

**Feature Vector**:
```
features = [
    # UID (8 dims)
    0.2039, 0.4471, 0.2549, 0.1961, 0.2000, 0.2667, 0.2706, 0.2235,
    # Frontend (9 dims)
    0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    # Backend (8 dims)
    0.2039, 0.4471, 0.2549, 0.1961, 0.2000, 0.2667, 0.2706, 0.0588,
    # Content ID (1 dim)
    1.0,
    # Global ID (8 dims)
    0.2039, 0.4471, 0.2549, 0.1961, 0.2000, 0.2667, 0.2706, 0.1569,
    # Prev UID (8 dims)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    # Next UID (8 dims)
    0.5020, 0.1176, 0.5216, 0.1176, 0.5216, 0.1176, 0.5216, 0.0824,
    # Index (1 dim)
    0.0,
    # Stream (9 dims)
    1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
]

Feature Dimension: 60
```

### Step 3: Projection Matrix Initialization

**Formula**: `projection_matrix = random_matrix(feature_dim, embedding_dim) / sqrt(feature_dim)`

**Parameters**:
- `feature_dim = 60`
- `embedding_dim = 768` (default)
- `random_seed = 42`

**Calculation**:
```
Step 1: Generate random matrix
projection_matrix = np.random.randn(60, 768)

With seed=42, this generates a deterministic matrix:
P[i,j] = random_value from N(0, 1) distribution

Step 2: Normalize by sqrt(feature_dim)
projection_matrix = projection_matrix / sqrt(60)
projection_matrix = projection_matrix / 7.746

This ensures variance is controlled:
Var(P[i,j]) = 1 / feature_dim = 1/60 ≈ 0.0167
```

**Projection Matrix Shape**: `(60, 768)`

### Step 4: Matrix Multiplication (Projection)

**Formula**: `embedding = features @ projection_matrix`

**Calculation**:
```
features: shape (60,)
projection_matrix: shape (60, 768)

embedding[i] = Σ(j=0 to 59) features[j] * projection_matrix[j, i]

For i = 0:
embedding[0] = features[0] * P[0,0] + features[1] * P[1,0] + ... + features[59] * P[59,0]
            = 0.2039 * P[0,0] + 0.4471 * P[1,0] + ... + 0.0 * P[59,0]

For i = 1:
embedding[1] = features[0] * P[0,1] + features[1] * P[1,1] + ... + features[59] * P[59,1]

... (for all 768 dimensions)

Result: embedding shape (768,)
```

**Example Calculation (first 3 dimensions)**:
```
Assuming projection matrix values (with seed=42):
P[0,0] = 0.1234, P[1,0] = -0.5678, P[2,0] = 0.9012, ...

embedding[0] = 0.2039 * 0.1234 + 0.4471 * (-0.5678) + 0.2549 * 0.9012 + ...
            = 0.0252 - 0.2538 + 0.2298 + ...
            = (calculated sum)

embedding[1] = 0.2039 * P[0,1] + 0.4471 * P[1,1] + ...
            = (calculated sum)

... (for all 768 dimensions)
```

### Step 5: Normalization

**Formula**: `embedding_normalized = embedding / ||embedding||`

**Calculation**:
```
Step 1: Calculate L2 norm
norm = sqrt(Σ(i=0 to 767) embedding[i]^2)

Step 2: Normalize
embedding_normalized[i] = embedding[i] / norm

If norm < 1e-8 (near zero), set norm = 1.0 to avoid division by zero
```

**Example**:
```
Assuming:
embedding[0] = 0.1234
embedding[1] = -0.5678
embedding[2] = 0.9012
...
embedding[767] = 0.3456

norm = sqrt(0.1234^2 + (-0.5678)^2 + 0.9012^2 + ... + 0.3456^2)
     = sqrt(0.0152 + 0.3224 + 0.8122 + ... + 0.1194)
     = sqrt(384.5678)  (example)
     = 19.6124

embedding_normalized[0] = 0.1234 / 19.6124 = 0.0063
embedding_normalized[1] = -0.5678 / 19.6124 = -0.0290
embedding_normalized[2] = 0.9012 / 19.6124 = 0.0459
...
```

**Final Embedding**: Shape `(768,)`, L2-normalized

---

## PART 2: SEMANTIC EMBEDDINGS - DETAILED CALCULATION

### Strategy: Semantic (Self-Trained from Co-occurrence)

### Step 1: Co-occurrence Matrix Construction

**Input**: Token sequences from training data

**Example Sequence**: `["you're", "moving", "tens", "of", "gigabytes"]`

**Co-occurrence Window**: 5 tokens (default)

**Calculation**:
```
For token "you're" (position 0):
Window: [0, 1, 2, 3, 4]
Co-occurring tokens: ["moving", "tens", "of", "gigabytes"]

For each co-occurring token:
cooccurrence["you're"]["moving"] += 1
cooccurrence["you're"]["tens"] += 1
cooccurrence["you're"]["of"] += 1
cooccurrence["you're"]["gigabytes"] += 1
```

**Co-occurrence Matrix** (sparse):
```
C[i,j] = count of times token j appears within window of token i

Example:
C["you're"]["moving"] = 1
C["you're"]["tens"] = 1
C["you're"]["of"] = 1
C["you're"]["gigabytes"] = 1
C["moving"]["you're"] = 1
C["moving"]["tens"] = 1
...
```

### Step 2: Vocabulary Building

**Vocabulary**: Set of all unique tokens

**Example Vocabulary**:
```
vocab = {
    "you're": uid_1,
    "moving": uid_2,
    "tens": uid_3,
    "of": uid_4,
    "gigabytes": uid_5,
    ...
}
```

**Vocabulary Size**: `|vocab| = V` (e.g., 50,000)

### Step 3: Embedding Initialization

**Initial Embedding Dimension**: `embedding_dim = 768`

**Initialization**:
```
For each token in vocab:
    embedding[uid] = random_vector(768) from N(0, 0.01)

Example for "you're" (uid_1):
embedding[uid_1] = [0.0012, -0.0034, 0.0056, ..., 0.0023]
                   (768 dimensions, small random values)
```

### Step 4: Training (Gradient Descent)

**Objective Function**: Minimize co-occurrence prediction error

**Formula**: `Loss = Σ(i,j) (C[i,j] - embedding[i] · embedding[j])^2`

**Gradient Update**:
```
For each co-occurrence pair (i, j):
    error = C[i,j] - embedding[i] · embedding[j]
    
    gradient_i = -2 * error * embedding[j]
    gradient_j = -2 * error * embedding[i]
    
    embedding[i] = embedding[i] - learning_rate * gradient_i
    embedding[j] = embedding[j] - learning_rate * gradient_j
```

**Example Calculation**:
```
Token pair: ("you're", "moving")
C["you're"]["moving"] = 1

Current embeddings:
embedding["you're"] = [0.0012, -0.0034, 0.0056, ...]
embedding["moving"] = [0.0023, 0.0015, -0.0045, ...]

Step 1: Calculate dot product
dot = embedding["you're"] · embedding["moving"]
    = 0.0012 * 0.0023 + (-0.0034) * 0.0015 + 0.0056 * (-0.0045) + ...
    = 0.00000276 - 0.0000051 - 0.0000252 + ...
    = -0.0001234 (example)

Step 2: Calculate error
error = 1 - (-0.0001234) = 1.0001234

Step 3: Calculate gradients
gradient_youre = -2 * 1.0001234 * embedding["moving"]
                = -2.0002468 * [0.0023, 0.0015, -0.0045, ...]
                = [-0.0046, -0.0030, 0.0090, ...]

gradient_moving = -2 * 1.0001234 * embedding["you're"]
                 = -2.0002468 * [0.0012, -0.0034, 0.0056, ...]
                 = [-0.0024, 0.0068, -0.0112, ...]

Step 4: Update embeddings
learning_rate = 0.01

embedding["you're"] = embedding["you're"] - 0.01 * gradient_youre
                    = [0.0012, -0.0034, 0.0056, ...] - 0.01 * [-0.0046, -0.0030, 0.0090, ...]
                    = [0.0012, -0.0034, 0.0056, ...] - [-0.000046, -0.000030, 0.000090, ...]
                    = [0.001246, -0.003370, 0.005510, ...]

embedding["moving"] = embedding["moving"] - 0.01 * gradient_moving
                    = [0.0023, 0.0015, -0.0045, ...] - 0.01 * [-0.0024, 0.0068, -0.0112, ...]
                    = [0.002324, 0.001432, -0.004388, ...]
```

**Training Iterations**: Repeat for all co-occurrence pairs, multiple epochs

### Step 5: Final Semantic Embedding

**After Training**:
```
embedding["you're"] = trained_vector(768)
                    = [0.1234, -0.5678, 0.9012, ..., 0.3456]
                    (768 dimensions, learned from co-occurrence)
```

**Retrieval**:
```
For token with UID = 3784123456789012345:
    semantic_embedding = embedding[uid]
    = [0.1234, -0.5678, 0.9012, ..., 0.3456]
```

---

## PART 3: HYBRID EMBEDDINGS - DETAILED CALCULATION

### Strategy: Hybrid (Text + Features)

### Step 1: Text Embedding

**Model**: SentenceTransformer (e.g., "all-MiniLM-L6-v2")

**Input**: Token text `"you're"`

**Text Embedding Generation**:
```
text_embedding = sentence_transformer.encode("you're")
                = [0.1234, -0.5678, 0.9012, ..., 0.3456]
                (384 dimensions for MiniLM)
```

**Text Embedding Dimension**: `text_dim = 384`

### Step 2: Feature Embedding

**Same as Feature-Based Embedding** (from Part 1):
```
feature_embedding = feature_based_embedding(token)
                   = [0.0063, -0.0290, 0.0459, ..., 0.0176]
                   (768 dimensions)
```

**Feature Embedding Dimension**: `feature_dim = 768`

### Step 3: Dimension Alignment

**Problem**: `text_dim (384) ≠ feature_dim (768)`

**Solution**: Project feature embedding to text dimension

**Projection Matrix**:
```
projection_matrix = random_matrix(768, 384) / sqrt(768)
                  = random_matrix(768, 384) / 27.713

feature_embedding_projected = feature_embedding @ projection_matrix
                             = (768,) @ (768, 384)
                             = (384,)
```

**Example Calculation**:
```
feature_embedding_projected[0] = Σ(j=0 to 767) feature_embedding[j] * P[j, 0]
                                = 0.0063 * P[0,0] + (-0.0290) * P[1,0] + ... + 0.0176 * P[767,0]
                                = (calculated sum)
```

**Normalize**:
```
feature_embedding_projected = feature_embedding_projected / ||feature_embedding_projected||
```

### Step 4: Weighted Combination

**Weights**:
```
feature_weights = {
    "text": 0.7,
    "features": 0.3
}
```

**Formula**: `hybrid = weight_text * text_emb + weight_features * feature_emb`

**Calculation**:
```
hybrid[0] = 0.7 * text_embedding[0] + 0.3 * feature_embedding_projected[0]
         = 0.7 * 0.1234 + 0.3 * 0.0459
         = 0.0864 + 0.0138
         = 0.1002

hybrid[1] = 0.7 * text_embedding[1] + 0.3 * feature_embedding_projected[1]
         = 0.7 * (-0.5678) + 0.3 * (-0.0290)
         = -0.3975 + (-0.0087)
         = -0.4062

... (for all 384 dimensions)
```

**Hybrid Embedding**: Shape `(384,)`

### Step 5: Project to Target Dimension (if needed)

**If target dimension ≠ 384**:
```
If embedding_dim = 768:
    projection_matrix = random_matrix(384, 768) / sqrt(384)
    hybrid_final = hybrid @ projection_matrix
                 = (384,) @ (384, 768)
                 = (768,)
```

**Normalize**:
```
hybrid_final = hybrid_final / ||hybrid_final||
```

**Final Hybrid Embedding**: Shape `(embedding_dim,)`, L2-normalized

---

## PART 4: HASH EMBEDDINGS - DETAILED CALCULATION

### Strategy: Hash-Based (Fast, Deterministic)

### Step 1: Create Hash String

**Formula**: `hash_string = f"{text}_{uid}_{frontend}_{backend}_{content_id}_{global_id}"`

**Example**:
```
hash_string = "you're_3784123456789012345_4_3784123456789000159_3570164763_3784119886624847592"
```

### Step 2: SHA-256 Hash

**Formula**: `hash_bytes = SHA256(hash_string.encode()).digest()`

**Calculation**:
```
hash_string_bytes = hash_string.encode('utf-8')
                  = b"you're_3784123456789012345_4_3784123456789000159_3570164763_3784119886624847592"

hash_bytes = hashlib.sha256(hash_string_bytes).digest()
           = b'\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0'
           (32 bytes)
```

**Hash Bytes**: 32 bytes

### Step 3: Convert to Embedding Vector

**Target Dimension**: `embedding_dim = 768`

**Formula**: `embedding[i] = hash_bytes[i % 32] / 255.0`

**Calculation**:
```
For i = 0 to 767:
    byte_idx = i % 32
    embedding[i] = hash_bytes[byte_idx] / 255.0

Example:
embedding[0] = hash_bytes[0] / 255.0 = 0x12 / 255.0 = 18 / 255.0 = 0.0706
embedding[1] = hash_bytes[1] / 255.0 = 0x34 / 255.0 = 52 / 255.0 = 0.2039
embedding[2] = hash_bytes[2] / 255.0 = 0x56 / 255.0 = 86 / 255.0 = 0.3373
...
embedding[31] = hash_bytes[31] / 255.0 = 0xF0 / 255.0 = 240 / 255.0 = 0.9412
embedding[32] = hash_bytes[0] / 255.0 = 0x12 / 255.0 = 0.0706  (wraps around)
embedding[33] = hash_bytes[1] / 255.0 = 0x34 / 255.0 = 0.2039
...
embedding[767] = hash_bytes[767 % 32] / 255.0 = hash_bytes[31] / 255.0 = 0.9412
```

**Hash Embedding**: Shape `(768,)`, values in [0, 1]

### Step 4: Normalization

**Formula**: `embedding_normalized = embedding / ||embedding||`

**Calculation**:
```
norm = sqrt(Σ(i=0 to 767) embedding[i]^2)
     = sqrt(0.0706^2 + 0.2039^2 + 0.3373^2 + ... + 0.9412^2)
     = sqrt(384.5678)  (example)
     = 19.6124

embedding_normalized[i] = embedding[i] / 19.6124

embedding_normalized[0] = 0.0706 / 19.6124 = 0.0036
embedding_normalized[1] = 0.2039 / 19.6124 = 0.0104
...
```

**Final Hash Embedding**: Shape `(768,)`, L2-normalized

---

## PART 5: BATCH PROCESSING - DETAILED CALCULATION

### Vectorized Batch Processing (Feature-Based)

### Step 1: Extract Features for Batch

**Batch Size**: `batch_size = 10,000`

**Tokens**: `[token_0, token_1, ..., token_9999]`

**Feature Extraction**:
```
For each token in batch:
    features[i] = extract_features(token[i])

Result:
features_matrix = [
    [f0_0, f0_1, ..., f0_59],  # token_0 features (60 dims)
    [f1_0, f1_1, ..., f1_59],  # token_1 features (60 dims)
    ...
    [f9999_0, f9999_1, ..., f9999_59]  # token_9999 features (60 dims)
]

Shape: (10000, 60)
```

### Step 2: Vectorized Matrix Multiplication

**Formula**: `embeddings = features_matrix @ projection_matrix`

**Projection Matrix**: Shape `(60, 768)`

**Calculation**:
```
embeddings[i, j] = Σ(k=0 to 59) features_matrix[i, k] * projection_matrix[k, j]

For i = 0 (first token):
    embeddings[0, 0] = features_matrix[0, 0] * P[0, 0] + features_matrix[0, 1] * P[1, 0] + ... + features_matrix[0, 59] * P[59, 0]
    embeddings[0, 1] = features_matrix[0, 0] * P[0, 1] + features_matrix[0, 1] * P[1, 1] + ... + features_matrix[0, 59] * P[59, 1]
    ...
    embeddings[0, 767] = features_matrix[0, 0] * P[0, 767] + ... + features_matrix[0, 59] * P[59, 767]

For i = 1 (second token):
    embeddings[1, 0] = features_matrix[1, 0] * P[0, 0] + features_matrix[1, 1] * P[1, 0] + ... + features_matrix[1, 59] * P[59, 0]
    ...

... (for all 10,000 tokens)

Result Shape: (10000, 768)
```

**Matrix Multiplication**:
```
(10000, 60) @ (60, 768) = (10000, 768)
```

### Step 3: Vectorized Normalization

**Formula**: `norms = sqrt(Σ(j=0 to 767) embeddings[i, j]^2)` for each i

**Calculation**:
```
For each row i:
    norms[i] = sqrt(embeddings[i, 0]^2 + embeddings[i, 1]^2 + ... + embeddings[i, 767]^2)

Vectorized:
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
      = [norm_0, norm_1, ..., norm_9999]  (shape: (10000, 1))

Normalize:
embeddings_normalized = embeddings / norms
                      = embeddings / [norm_0, norm_1, ..., norm_9999]

embeddings_normalized[i, j] = embeddings[i, j] / norms[i]
```

**Example**:
```
For token 0:
norm_0 = sqrt(embeddings[0, 0]^2 + embeddings[0, 1]^2 + ... + embeddings[0, 767]^2)
       = 19.6124

embeddings_normalized[0, 0] = embeddings[0, 0] / 19.6124
embeddings_normalized[0, 1] = embeddings[0, 1] / 19.6124
...

For token 1:
norm_1 = sqrt(embeddings[1, 0]^2 + embeddings[1, 1]^2 + ... + embeddings[1, 767]^2)
       = 18.3456

embeddings_normalized[1, 0] = embeddings[1, 0] / 18.3456
...
```

**Final Batch Embeddings**: Shape `(10000, 768)`, each row L2-normalized

---

## PART 6: COMPLETE EXAMPLE - Full Calculation

### Input Token:
```
Token: "you're"
UID: 3784123456789012345
Frontend: 4
Backend: 3784123456789000159
Content ID: 3570164763
Global ID: 3784119886624847592
Prev UID: null
Next UID: 9234567890123456789
Index: 0
Stream: "space"
```

### Feature-Based Embedding Calculation:

**Step 1: Extract Features (60 dimensions)**
```
Features = [0.2039, 0.4471, ..., 1.0, ..., 0.0, ..., 1.0, 0.0, ...]
          (60 values)
```

**Step 2: Project to 768 dimensions**
```
Embedding = Features @ Projection_Matrix
          = (60,) @ (60, 768)
          = (768,)
```

**Step 3: Normalize**
```
Norm = sqrt(Σ(i=0 to 767) embedding[i]^2) = 19.6124
Embedding_Normalized = Embedding / 19.6124
```

**Final Embedding**: `[0.0063, -0.0290, 0.0459, ..., 0.0176]` (768 dimensions)

---

## MATHEMATICAL FORMULAS SUMMARY

### 1. Feature Extraction:
```
features = [
    int64_to_bytes(uid) / 255.0,           # 8 dims
    onehot(frontend, 9),                    # 9 dims
    int64_to_bytes(backend) / 255.0,       # 8 dims
    content_id / 150000.0,                 # 1 dim
    int64_to_bytes(global_id) / 255.0,     # 8 dims
    int64_to_bytes(prev_uid) / 255.0,       # 8 dims
    int64_to_bytes(next_uid) / 255.0,       # 8 dims
    index / 10000.0,                        # 1 dim
    onehot(stream, 9)                       # 9 dims
]
Total: 60 dimensions
```

### 2. Feature-Based Embedding:
```
embedding = normalize(features @ projection_matrix)
where:
    projection_matrix = random_matrix(60, 768) / sqrt(60)
    normalize(x) = x / ||x||
```

### 3. Semantic Embedding:
```
embedding = trained_embedding[uid]
where trained_embedding learned from co-occurrence matrix
```

### 4. Hybrid Embedding:
```
text_emb = sentence_transformer.encode(text)
feature_emb = feature_based_embedding(token)
feature_emb_proj = normalize(feature_emb @ projection_matrix)
hybrid = weight_text * text_emb + weight_features * feature_emb_proj
```

### 5. Hash Embedding:
```
hash_string = f"{text}_{uid}_{frontend}_{backend}_{content_id}_{global_id}"
hash_bytes = SHA256(hash_string.encode()).digest()
embedding[i] = hash_bytes[i % 32] / 255.0
embedding = normalize(embedding)
```

### 6. Batch Processing:
```
features_matrix = [extract_features(token) for token in batch]  # (N, 60)
embeddings = features_matrix @ projection_matrix              # (N, 768)
norms = ||embeddings||_2 (per row)                            # (N, 1)
embeddings_normalized = embeddings / norms                     # (N, 768)
```

---

## DIMENSION BREAKDOWN

### Feature Vector: 60 dimensions
- UID: 8
- Frontend: 9
- Backend: 8
- Content ID: 1
- Global ID: 8
- Prev UID: 8
- Next UID: 8
- Index: 1
- Stream: 9
- **Total: 60**

### Embedding Vector: 768 dimensions (default)
- Projected from 60 features
- L2-normalized
- Suitable for similarity search

---

**This is the complete mathematical embeddings logic with detailed step-by-step calculations for all embedding strategies!**

