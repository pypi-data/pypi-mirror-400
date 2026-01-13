# Embeddings - Pure Mathematics

## FEATURE EXTRACTION

```
f_uid[i] = (UID >> (8×(7-i))) MOD 256 / 255,  i ∈ [0, 7]
f_frontend[i] = δ(i = frontend - 1),  i ∈ [0, 8]
f_backend[i] = (Backend >> (8×(7-i))) MOD 256 / 255,  i ∈ [0, 7]
f_content = min(1.0, Content_ID / 150000)
f_global[i] = (Global_ID >> (8×(7-i))) MOD 256 / 255,  i ∈ [0, 7]
f_prev[i] = (Prev_UID >> (8×(7-i))) MOD 256 / 255,  i ∈ [0, 7]
f_next[i] = (Next_UID >> (8×(7-i))) MOD 256 / 255,  i ∈ [0, 7]
f_index = Index / 10000
f_stream[i] = δ(stream = Streams[i]),  i ∈ [0, 8]

F = [f_uid, f_frontend, f_backend, f_content, f_global, f_prev, f_next, f_index, f_stream]
F ∈ ℝ^60
```

### Example: token = "you're"

```
UID = 3784123456789012345
byte[0] = ⌊3784123456789012345 / 256^7⌋ MOD 256 = 52
byte[1] = ⌊3784123456789012345 / 256^6⌋ MOD 256 = 114
byte[2] = ⌊3784123456789012345 / 256^5⌋ MOD 256 = 65
byte[3] = ⌊3784123456789012345 / 256^4⌋ MOD 256 = 50
byte[4] = ⌊3784123456789012345 / 256^3⌋ MOD 256 = 51
byte[5] = ⌊3784123456789012345 / 256^2⌋ MOD 256 = 68
byte[6] = ⌊3784123456789012345 / 256^1⌋ MOD 256 = 69
byte[7] = ⌊3784123456789012345 / 256^0⌋ MOD 256 = 57

f_uid = [52/255, 114/255, 65/255, 50/255, 51/255, 68/255, 69/255, 57/255]

frontend = 4
f_frontend = [0, 0, 0, 1, 0, 0, 0, 0, 0]

Backend = 3784123456789000159
f_backend = [0.2039, 0.4471, 0.2549, 0.1961, 0.2000, 0.2667, 0.2706, 0.0588]

Content_ID = 3570164763
f_content = min(1.0, 3570164763 / 150000) = 1.0

Global_ID = 3784119886624847592
f_global = [0.2039, 0.4471, 0.2549, 0.1961, 0.2000, 0.2667, 0.2706, 0.1569]

Prev_UID = 0
f_prev = [0, 0, 0, 0, 0, 0, 0, 0]

Next_UID = 9234567890123456789
f_next = [0.5020, 0.1176, 0.5216, 0.1176, 0.5216, 0.1176, 0.5216, 0.0824]

index = 0
f_index = 0

stream = "space"
f_stream = [1, 0, 0, 0, 0, 0, 0, 0, 0]

F ∈ ℝ^60
```

---

## PROJECTION

```
P ∈ ℝ^(60 × 768)
P[i,j] ~ N(0, 1/60)
P = P' / √60

E = F · P
E[j] = Σ(i=0 to 59) F[i] × P[i,j],  j ∈ [0, 767]
E ∈ ℝ^768
```

---

## NORMALIZATION

```
||E|| = √(Σ(j=0 to 767) E[j]²)

E_normalized[j] = E[j] / ||E||,  if ||E|| > 10^-8
E_normalized[j] = E[j],          otherwise

E_final = E_normalized
||E_final|| = 1
```

---

## SEMANTIC EMBEDDINGS

```
C[i,j] = Σ(k=0 to n-w) {
    1,  if t_k = i AND t_{k+m} = j for some m ∈ [1, w]
    0,  otherwise
}

L = Σ(i,j) (C[i,j] - E_token[i] · E_context[j])²

error = C[i,j] - E_token[i] · E_context[j]
E_token[i] ← E_token[i] + 2α × error × E_context[j]
E_context[j] ← E_context[j] + 2α × error × E_token[i]

E_semantic = E_token[vocab_index(uid)]
```

---

## HYBRID EMBEDDINGS

```
E_text = TextEncoder(text)
E_feature = FeatureBasedEmbedding(token)

P_align ∈ ℝ^(d_feature × d_text)
E_feature_proj = E_feature · P_align
E_feature_proj = E_feature_proj / ||E_feature_proj||

E_hybrid = 0.7 × E_text + 0.3 × E_feature_proj
```

---

## HASH EMBEDDINGS

```
hash_string = text || "_" || UID || "_" || Frontend || "_" || Backend || "_" || Content_ID || "_" || Global_ID
H = SHA256(hash_string)
H = [b₀, b₁, ..., b₃₁]

E_hash[i] = H[i MOD 32] / 255,  i ∈ [0, 767]
E_hash = E_hash / ||E_hash||
```

---

## BATCH PROCESSING

```
F_batch ∈ ℝ^(N × 60)
E_batch = F_batch · P
E_batch ∈ ℝ^(N × 768)

||E_batch[i]|| = √(Σ(j=0 to 767) E_batch[i,j]²)
E_batch_normalized[i,j] = E_batch[i,j] / ||E_batch[i]||
```
