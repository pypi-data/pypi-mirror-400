# Tokenization Mathematics

## SPACE TOKENIZATION

```
T = [t₀, t₁, ..., tₙ₋₁]
n = |T|

is_space(c) = {
    1,  if c ∈ {' ', '\t', '\n', '\r'}
    0,  otherwise
}

S = {i : is_space(T[i]) = 1, i ∈ [0, n-1]}
P = {0} ∪ S ∪ {n}

For each consecutive pair (pᵢ, pᵢ₊₁) in sorted P:
    tokenᵢ = substring(T, pᵢ, pᵢ₊₁)

|tokens| = |P| - 1
```

---

## WORD TOKENIZATION

```
is_word_char(c) = {
    1,  if (65 ≤ ord(c) ≤ 90) OR (97 ≤ ord(c) ≤ 122) OR (48 ≤ ord(c) ≤ 57)
    0,  otherwise
}

B = {i : is_word_char(T[i]) ≠ is_word_char(T[i-1]), i ∈ [1, n-1]} ∪ {0, n}

For each consecutive pair (bᵢ, bᵢ₊₁) in sorted B:
    tokenᵢ = substring(T, bᵢ, bᵢ₊₁)

|tokens| = |B| - 1
```

---

## CHARACTER TOKENIZATION

```
tokenᵢ = T[i],  i ∈ [0, n-1]
|tokens| = n
```

---

## GRAMMAR TOKENIZATION

```
classify(c) = {
    "word",        if is_word_char(c) = 1
    "punctuation", if is_space(c) = 0 AND is_word_char(c) = 0
    "space",       if is_space(c) = 1
}

For each position i where classify(T[i]) ≠ classify(T[i-1]) OR i = 0:
    tokenᵢ = substring(T, start, end)
    type(tokenᵢ) = classify(T[start])
```

---

## SUBWORD TOKENIZATION

### Fixed-Length
```
k = 3
|chunks| = ⌈L / k⌉
chunkᵢ = substring(W, i×k, min((i+1)×k, L)),  i ∈ [0, ⌈L/k⌉-1]
```

### BPE-Like
```
P = {common_patterns of length 2-3}

chunk₁ = prefix_match(W, P)
W' = W \ prefix(chunk₁)
chunk₂ = suffix_match(W', P)
```

### Syllable
```
V = {'a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'}

For each c in W:
    If c ∈ V:
        syllable_boundary
```

### Frequency-Based
```
P_prefix = {"pre", "un", "re", "in", ...}
P_suffix = {"ing", "ed", "er", "ly", ...}

chunk₁ = prefix_match(W, P_prefix)
W' = W \ prefix(chunk₁)
chunk₂ = suffix_match(W', P_suffix)
```

---

## BYTE TOKENIZATION

```
cp = ord(c)

encode_utf8(cp) = {
    [cp],                    if cp < 128
    [0xC0 | (cp >> 6), 0x80 | (cp & 0x3F)],  if cp < 2048
    [0xE0 | (cp >> 12), 0x80 | ((cp >> 6) & 0x3F), 0x80 | (cp & 0x3F)],  if cp < 65536
}

For each byte b in encode_utf8(ord(c)):
    token_text = decimal_string(b)
    token_byte = b
    token_codepoint = ord(c)
```

---

## UID GENERATION

```
S₀ = seed
x₀ = S
x₁ = x₀ XOR (x₀ >> 12)
x₂ = x₁ XOR (x₁ << 25)
x₃ = x₂ XOR (x₂ >> 27)
x₄ = (x₃ × 2685821657736338717) MOD 2^64
UID = x₄
```

---

## FRONTEND

```
weighted_sum = Σ(i=1 to L) ord(token[i-1]) × i

digital_root_9(n) = {
    ((n - 1) MOD 9) + 1,  if n > 0
    9,                     if n ≤ 0
}

hash_token(token):
    h₀ = 0
    hᵢ = hᵢ₋₁ × 31 + ord(token[i-1]),  i ∈ [1, L]
    hash = h_L

hash_digit = hash MOD 10
weighted_digit = digital_root_9(weighted_sum)
frontend = ((weighted_digit × 9 + hash_digit) MOD 9) + 1
```

### Example: "Hi"
```
weighted_sum = (72×1) + (105×2) = 282
weighted_digit = ((282-1) MOD 9) + 1 = 3
h₀ = 0
h₁ = 0 × 31 + 72 = 72
h₂ = 72 × 31 + 105 = 2337
hash_digit = 2337 MOD 10 = 7
frontend = ((3 × 9 + 7) MOD 9) + 1 = 8
```

### Example: "there"
```
weighted_sum = (116×1) + (104×2) + (101×3) + (114×4) + (101×5) = 1588
weighted_digit = ((1588-1) MOD 9) + 1 = 4
h₀ = 0
h₁ = 0 × 31 + 116 = 116
h₂ = 116 × 31 + 104 = 3700
h₃ = 3700 × 31 + 101 = 114801
h₄ = 114801 × 31 + 114 = 3558835
h₅ = 3558835 × 31 + 101 = 110323986
hash_digit = 110323986 MOD 10 = 6
frontend = ((4 × 9 + 6) MOD 9) + 1 = 7
```

### Example: "my"
```
weighted_sum = (109×1) + (121×2) = 351
weighted_digit = ((351-1) MOD 9) + 1 = 9
h₀ = 0
h₁ = 0 × 31 + 109 = 109
h₂ = 109 × 31 + 121 = 3500
hash_digit = 3500 MOD 10 = 0
frontend = ((9 × 9 + 0) MOD 9) + 1 = 1
```

### Example: "friend"
```
weighted_sum = (102×1) + (114×2) + (105×3) + (101×4) + (110×5) + (100×6) = 2199
weighted_digit = ((2199-1) MOD 9) + 1 = 3
h₀ = 0
h₁ = 0 × 31 + 102 = 102
h₂ = 102 × 31 + 114 = 3276
h₃ = 3276 × 31 + 105 = 101661
h₄ = 101661 × 31 + 101 = 3151492
h₅ = 3151492 × 31 + 110 = 97696242
h₆ = 97696242 × 31 + 100 = 3028583602
hash_digit = 3028583602 MOD 10 = 2
frontend = ((3 × 9 + 2) MOD 9) + 1 = 3
```

---

## BACKEND

```
weighted_sum = Σ(i=1 to L) ord(token[i-1]) × i
s = weighted_sum × (1 + (L - 1))
s_num = s + position + alphabetic_sum
m = s_num XOR uid
m = m + prev_uid + next_uid + embedding_bit
backend = m MOD 2^64
```

### Example: "hi", position = 0
```
weighted_sum = (104×1) + (105×2) = 314
s = 314 × (1 + (2 - 1)) = 628
s_num = 628 + 0 + 17 = 645
m = 645 XOR uid + prev_uid + next_uid + embedding_bit
backend = m MOD 2^64
```

### Example: "there", position = 3
```
weighted_sum = (116×1) + (104×2) + (101×3) + (114×4) + (101×5) = 1588
s = 1588 × (1 + (5 - 1)) = 7940
s_num = 7940 + 3 + 29 = 7972
m = 7972 XOR uid + prev_uid + next_uid + embedding_bit
backend = m MOD 2^64
```

---

## CONTENT ID

```
content_id = hash_token(token) MOD 2^64
```

---

## GLOBAL ID

```
global_id = (uid XOR content_id XOR (index << 17) XOR stream_id XOR session_id) MOD 2^64
```

---

## NEIGHBOR AWARENESS

```
prev_uid(token_i) = {
    uid(token_{i-1}),  if i > 0
    0,                 if i = 0
}

next_uid(token_i) = {
    uid(token_{i+1}),  if i < n-1
    0,                 if i = n-1
}
```
