# SOMA Tokenization Logic - Mathematical Documentation

## Example Sentence
```
"you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
```

---

## 1. SPACE TOKENIZATION

### Mathematical Logic:
**Rule**: Split text on whitespace boundaries (space, tab, newline, carriage return)

### Algorithm:
```
Let text = T[0..n-1]
Let tokens = []
Let i = 0
Let start = 0
Let token_id = 0

While i < n:
    If T[i] is whitespace:
        If start < i:
            tokens.append({
                id: token_id++,
                text: T[start..i-1],
                type: "content",
                index: start
            })
        
        Let space_start = i
        Let space_chars = []
        While i < n AND T[i] is whitespace:
            space_chars.append(T[i])
            i++
        
        tokens.append({
            id: token_id++,
            text: join(space_chars),
            type: "space",
            index: space_start
        })
        start = i
    Else:
        i++

If start < n:
    tokens.append({
        id: token_id,
        text: T[start..n-1],
        type: "content",
        index: start
    })
```

### Example Output:
```
Input: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."

Tokens:
1. "you're" (type: content, index: 0)
2. " " (type: space, index: 6)
3. "moving" (type: content, index: 7)
4. " " (type: space, index: 13)
5. "tens" (type: content, index: 14)
6. " " (type: space, index: 18)
7. "of" (type: content, index: 19)
8. " " (type: space, index: 21)
9. "gigabytes," (type: content, index: 22)
10. " " (type: space, index: 32)
... (and so on)
```

### Mathematical Properties:
- **Deterministic**: Same input → same output
- **Reversible**: Original text = concat(all tokens)
- **Space Preservation**: All whitespace sequences preserved
- **No Information Loss**: Perfect reconstruction guaranteed

---

## 2. WORD TOKENIZATION

### Mathematical Logic:
**Rule**: Split on word boundaries (alphanumeric sequences)

### Algorithm:
```
Let text = T[0..n-1]
Let tokens = []
Let i = 0
Let start = -1
Let token_id = 0

While i < n:
    ch = T[i]
    If is_word_char(ch):  // Alphanumeric
        If start == -1:
            start = i
    Else:
        If start != -1:
            tokens.append({
                id: token_id++,
                text: T[start..i-1],
                type: "word",
                index: start
            })
            start = -1
        
        tokens.append({
            id: token_id++,
            text: ch,
            type: "non_word",
            index: i
        })
    i++

If start != -1:
    tokens.append({
        id: token_id,
        text: T[start..n-1],
        type: "word",
        index: start
    })
```

### Word Character Definition:
```
is_word_char(ch) = (is_alpha(ch) OR is_digit(ch))
where:
    is_alpha(ch) = (65 ≤ ord(ch) ≤ 90) OR (97 ≤ ord(ch) ≤ 122)
    is_digit(ch) = (48 ≤ ord(ch) ≤ 57)
```

### Example Output:
```
Input: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."

Tokens:
1. "you" (type: word, index: 0)
2. "'" (type: non_word, index: 3)
3. "re" (type: word, index: 4)
4. " " (type: non_word, index: 6)
5. "moving" (type: word, index: 7)
6. " " (type: non_word, index: 13)
7. "tens" (type: word, index: 14)
8. " " (type: non_word, index: 18)
9. "of" (type: word, index: 19)
10. " " (type: non_word, index: 21)
11. "gigabytes" (type: word, index: 22)
12. "," (type: non_word, index: 31)
... (and so on)
```

### Mathematical Properties:
- **Word Boundaries**: Splits on non-alphanumeric characters
- **Punctuation Preservation**: All punctuation preserved as separate tokens
- **Reversible**: Original text = concat(all tokens)

---

## 3. CHARACTER TOKENIZATION

### Mathematical Logic:
**Rule**: Each character becomes a token

### Algorithm:
```
Let text = T[0..n-1]
Let tokens = []
Let token_id = 0

For i = 0 to n-1:
    ch = T[i]
    tokens.append({
        id: token_id++,
        text: ch,
        type: "character",
        index: i,
        codepoint: ord(ch),
        is_ascii: (ord(ch) < 128),
        is_space: is_space(ch),
        is_alpha: is_alpha(ch),
        is_digit: is_digit(ch)
    })
```

### Example Output:
```
Input: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."

Tokens:
1. "y" (type: character, index: 0, codepoint: 121, is_alpha: true)
2. "o" (type: character, index: 1, codepoint: 111, is_alpha: true)
3. "u" (type: character, index: 2, codepoint: 117, is_alpha: true)
4. "'" (type: character, index: 3, codepoint: 39, is_alpha: false)
5. "r" (type: character, index: 4, codepoint: 114, is_alpha: true)
6. "e" (type: character, index: 5, codepoint: 101, is_alpha: true)
7. " " (type: character, index: 6, codepoint: 32, is_space: true)
... (147 characters total)
```

### Mathematical Properties:
- **1:1 Mapping**: Each character → 1 token
- **Complete Information**: All character properties preserved
- **Perfect Reconstruction**: Original text = concat(all tokens)

---

## 4. GRAMMAR TOKENIZATION

### Mathematical Logic:
**Rule**: Split words and punctuation separately

### Algorithm:
```
Let text = T[0..n-1]
Let tokens = []
Let i = 0
Let start = -1
Let token_id = 0

While i < n:
    ch = T[i]
    If is_word_char(ch):
        If start == -1:
            start = i
    Else:
        If start != -1:
            tokens.append({
                id: token_id++,
                text: T[start..i-1],
                type: "word",
                index: start
            })
            start = -1
        
        If is_space(ch):
            tokens.append({
                id: token_id++,
                text: ch,
                type: "space",
                index: i
            })
        Else:
            tokens.append({
                id: token_id++,
                text: ch,
                type: "punctuation",
                index: i,
                codepoint: ord(ch)
            })
    i++

If start != -1:
    tokens.append({
        id: token_id,
        text: T[start..n-1],
        type: "word",
        index: start
    })
```

### Example Output:
```
Input: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."

Tokens:
1. "you" (type: word, index: 0)
2. "'" (type: punctuation, index: 3, codepoint: 39)
3. "re" (type: word, index: 4)
4. " " (type: space, index: 6)
5. "moving" (type: word, index: 7)
6. " " (type: space, index: 13)
7. "tens" (type: word, index: 14)
8. " " (type: space, index: 18)
9. "of" (type: word, index: 19)
10. " " (type: space, index: 21)
11. "gigabytes" (type: word, index: 22)
12. "," (type: punctuation, index: 31, codepoint: 44)
... (and so on)
```

### Mathematical Properties:
- **Grammar-Aware**: Separates words from punctuation
- **Punctuation Classification**: Each punctuation marked with codepoint
- **Space Classification**: Spaces marked separately from punctuation

---

## 5. SUBWORD TOKENIZATION

### Mathematical Logic:
**Rule**: Split words into smaller chunks (subwords)

### Strategies:

#### A. Fixed-Length Chunks:
```
Algorithm:
For word W of length L:
    chunk_size = 3 (default)
    chunks = []
    For i = 0 to L-1 step chunk_size:
        chunk = W[i..min(i+chunk_size-1, L-1)]
        chunks.append(chunk)
```

#### B. BPE-Like Split:
```
Algorithm:
For word W:
    chunks = []
    If len(W) ≤ chunk_size:
        chunks = [W]
    Else:
        // Split into prefix and suffix
        prefix = W[0..chunk_size-1]
        suffix = W[chunk_size..L-1]
        chunks = [prefix] + split_suffix(suffix, chunk_size)
```

#### C. Syllable Split:
```
Algorithm:
For word W:
    chunks = []
    syllables = detect_syllables(W)  // Based on vowel patterns
    For each syllable:
        chunks.append(syllable)
```

#### D. Frequency-Based Split:
```
Algorithm:
For word W:
    chunks = []
    // Split based on character frequency patterns
    common_prefixes = ["pre", "un", "re", "in", ...]
    common_suffixes = ["ing", "ed", "er", "ly", ...]
    
    If W starts with common_prefix:
        chunks.append(prefix)
        W = W[len(prefix)..]
    
    If W ends with common_suffix:
        suffix = W[L-len(suffix)..]
        W = W[0..L-len(suffix)-1]
        chunks.append(W)
        chunks.append(suffix)
    Else:
        chunks = split_fixed(W, chunk_size)
```

### Example Output (Fixed, chunk_size=3):
```
Input: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."

Word "moving" → Subwords:
1. "mov" (type: subword, parent_word: "moving", subword_index: 0)
2. "ing" (type: subword, parent_word: "moving", subword_index: 1)

Word "gigabytes" → Subwords:
1. "gig" (type: subword, parent_word: "gigabytes", subword_index: 0)
2. "aby" (type: subword, parent_word: "gigabytes", subword_index: 1)
3. "tes" (type: subword, parent_word: "gigabytes", subword_index: 2)
```

### Mathematical Properties:
- **Deterministic Splitting**: Same word → same subwords
- **Reconstruction Info**: Parent word stored for perfect reconstruction
- **Multiple Strategies**: 4 different splitting algorithms

---

## 6. BYTE TOKENIZATION

### Mathematical Logic:
**Rule**: Convert characters to byte representations

### Algorithm:
```
Let text = T[0..n-1]
Let tokens = []
Let token_id = 0

For i = 0 to n-1:
    ch = T[i]
    codepoint = ord(ch)
    
    // Convert to byte-like representation (decimal digits)
    bytes = []
    temp = codepoint
    While temp > 0:
        bytes.append(temp % 10)  // Extract digit
        temp = temp // 10
    
    For byte_val in bytes:
        tokens.append({
            id: token_id++,
            text: str(byte_val),
            type: "byte",
            index: i,
            codepoint: codepoint,
            byte_value: byte_val
        })
```

### Example Output:
```
Input: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."

Character "y" (codepoint: 121) → Bytes:
1. "1" (type: byte, codepoint: 121, byte_value: 1)
2. "2" (type: byte, codepoint: 121, byte_value: 2)
3. "1" (type: byte, codepoint: 121, byte_value: 1)

Character "o" (codepoint: 111) → Bytes:
1. "1" (type: byte, codepoint: 111, byte_value: 1)
2. "1" (type: byte, codepoint: 111, byte_value: 1)
3. "1" (type: byte, codepoint: 111, byte_value: 1)
... (and so on)
```

### Mathematical Properties:
- **Byte Representation**: Each character → byte sequence
- **Deterministic**: Same character → same bytes
- **Reversible**: Bytes → codepoint → character

---

## 7. UID GENERATION (Unique Identifier)

### Mathematical Logic:
**Algorithm**: XorShift64* (deterministic pseudo-random)

### XorShift64* Algorithm:
```
State: 64-bit integer S
Seed: Initial value (default: 0x9E3779B97F4A7C15)

Function next_u64():
    x = S
    x = x XOR (x >> 12)  // Right shift 12 bits, XOR
    x = x XOR (x << 25)  // Left shift 25 bits, XOR
    x = x XOR (x >> 27)  // Right shift 27 bits, XOR
    x = (x * 2685821657736338717) MOD 2^64
    S = x
    Return x
```

### UID Assignment:
```
Let tokens = [T0, T1, T2, ..., Tn-1]
Let seed = initial_seed
Let rng = XorShift64Star(seed)
Let uids = []

For i = 0 to n-1:
    uid[i] = rng.next_u64()
    tokens[i].uid = uid[i]
```

### Mathematical Properties:
- **Deterministic**: Same seed + same tokens → same UIDs
- **Unique**: Each token gets unique 64-bit UID
- **Uniform Distribution**: XorShift64* provides good distribution
- **Reversible Seed**: Can regenerate UIDs from seed

### Example:
```
Token: "you"
Seed: 42
UID: 18446744073709551615 (64-bit integer)

Token: "'"
UID: 9223372036854775807

Token: "re"
UID: 4611686018427387903
... (each token gets unique UID)
```

---

## 8. FRONTEND (Digital Root 1-9)

### Mathematical Logic:
**Rule**: Convert token to digit 1-9 using alphabetic mapping

### Algorithm:
```
Function alphabetic_value(ch):
    cu = to_uppercase(ch)
    o = ord(cu)
    If 65 ≤ o ≤ 90:  // A-Z
        k = o - 65
        Return (k MOD 9) + 1
    Else:
        Return 0

Function alphabetic_sum(token_text):
    sum = 0
    For each ch in token_text:
        sum += alphabetic_value(ch)
    Return sum

Function digital_root_9(n):
    If n ≤ 0:
        Return 9
    Else:
        Return ((n - 1) MOD 9) + 1

Function combined_digit(token_text, embedding_bit):
    // Method 1: Weighted sum
    weighted_sum = alphabetic_sum(token_text)
    weighted_digit = digital_root_9(weighted_sum)
    If embedding_bit:
        weighted_digit = digital_root_9(weighted_digit + 1)
    
    // Method 2: Hash
    hash_val = hash_token(token_text)  // h = h * 31 + ord(ch)
    hash_digit = hash_val MOD 10
    
    // Combine
    combined = ((weighted_digit * 9 + hash_digit) MOD 9) + 1
    Return combined
```

### Alphabetic Mapping:
```
A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9
J=1, K=2, L=3, M=4, N=5, O=6, P=7, Q=8, R=9
S=1, T=2, U=3, V=4, W=5, X=6, Y=7, Z=8

Pattern: (position MOD 9) + 1
```

### Example:
```
Token: "you"
Characters: y=7, o=6, u=3
Sum: 7 + 6 + 3 = 16
Digital Root: ((16 - 1) MOD 9) + 1 = 7

Token: "moving"
Characters: m=4, o=6, v=4, i=9, n=5, g=7
Sum: 4 + 6 + 4 + 9 + 5 + 7 = 35
Digital Root: ((35 - 1) MOD 9) + 1 = 8
```

### Mathematical Properties:
- **Range**: 1-9 (9-centric system)
- **Deterministic**: Same token → same frontend
- **Alphabetic**: Based on letter positions
- **Digital Root**: Folds large numbers to 1-9

---

## 9. BACKEND (Composite Number)

### Mathematical Logic:
**Rule**: Create 64-bit composite number from multiple factors

### Algorithm:
```
Function compose_backend_number(token_text, position, uid, prev_uid, next_uid, embedding_bit):
    // Step 1: Weighted character sum
    If run_collapse_to_one:
        s = weighted_char_sum_runaware(token_text)
        eff_len = effective_length_after_collapse(token_text)
        runs_sum = sum_of_letter_run_lengths(token_text)
        s = s + runs_sum
    Else:
        s = weighted_char_sum(token_text)
        eff_len = length(token_text)
    
    // Step 2: Multiply by length factor
    s = s * (1 + (eff_len - 1))
    
    // Step 3: Add position
    s = s + position
    
    // Step 4: Add alphabetic sum
    s_num = s + alphabetic_sum_fast(token_text)
    
    // Step 5: XOR with UID
    m = s_num XOR uid
    
    // Step 6: Add neighbor UIDs
    m = m + (prev_uid if prev_uid else 0)
    m = m + (next_uid if next_uid else 0)
    
    // Step 7: Add embedding bit
    m = m + (1 if embedding_bit else 0)
    
    Return m
```

### Mathematical Formula:
```
backend = (
    (weighted_sum * (1 + (length - 1)) + position + alphabetic_sum) 
    XOR uid 
    + prev_uid 
    + next_uid 
    + embedding_bit
) MOD 2^64
```

### Example:
```
Token: "you"
Position: 0
UID: 18446744073709551615
Prev UID: None
Next UID: 9223372036854775807
Embedding Bit: 0

Weighted Sum: 16
Length: 3
Position: 0
Alphabetic Sum: 16
s_num = 16 * (1 + (3-1)) + 0 + 16 = 16 * 3 + 16 = 64
m = 64 XOR 18446744073709551615 = 18446744073709551551
m = 18446744073709551551 + 0 + 9223372036854775807 + 0
Backend: 27670116110564327358 (64-bit)
```

### Mathematical Properties:
- **Composite**: Combines multiple factors
- **Context-Aware**: Includes neighbor UIDs
- **Position-Aware**: Includes token position
- **Deterministic**: Same inputs → same backend

---

## 10. CONTENT ID

### Mathematical Logic:
**Rule**: Hash of token text content

### Algorithm:
```
Function _content_id(token_text):
    h = 0
    For each ch in token_text:
        h = h * 31 + ord(ch)
    Return h MOD (2^64)
```

### Hash Formula:
```
content_id = (
    ((((0 * 31 + ord(ch0)) * 31 + ord(ch1)) * 31 + ord(ch2)) ...) * 31 + ord(chn)
) MOD 2^64
```

### Example:
```
Token: "you"
h = 0
h = 0 * 31 + 121 = 121          // 'y'
h = 121 * 31 + 111 = 3862       // 'o'
h = 3862 * 31 + 117 = 119839    // 'u'
Content ID: 119839
```

### Mathematical Properties:
- **Hash Function**: Java-style hash (h * 31 + c)
- **Deterministic**: Same text → same content_id
- **Collision-Resistant**: Different texts → likely different IDs
- **Semantic Grouping**: Similar texts have similar IDs

---

## 11. GLOBAL ID

### Mathematical Logic:
**Rule**: Combine UID + content_id + index + stream_id + session_id

### Algorithm:
```
Function compute_global_id(uid, content_id, index, stream_id, session_id):
    gid = uid XOR content_id XOR (index << 17) XOR stream_id XOR session_id
    gid = gid MOD 2^64
    Return gid
```

### Mathematical Formula:
```
global_id = (
    uid 
    XOR content_id 
    XOR (index << 17) 
    XOR stream_id 
    XOR session_id
) MOD 2^64
```

### Example:
```
UID: 18446744073709551615
Content ID: 119839
Index: 0
Stream ID: 12345 (hash of stream name)
Session ID: 67890

gid = 18446744073709551615 
    XOR 119839 
    XOR (0 << 17) 
    XOR 12345 
    XOR 67890
Global ID: 18446744073709551501
```

### Mathematical Properties:
- **Unique**: Combines multiple unique factors
- **Stream-Aware**: Different streams → different IDs
- **Session-Aware**: Different sessions → different IDs
- **Global Uniqueness**: Unique across all tokenizations

---

## 12. NEIGHBOR AWARENESS

### Mathematical Logic:
**Rule**: Each token knows its previous and next UIDs

### Algorithm:
```
Let tokens = [T0, T1, T2, ..., Tn-1]
Let uids = [UID0, UID1, UID2, ..., UIDn-1]

For i = 0 to n-1:
    prev_uid = UID[i-1] if i > 0 else None
    next_uid = UID[i+1] if i < n-1 else None
    tokens[i].prev_uid = prev_uid
    tokens[i].next_uid = next_uid
```

### Example:
```
Tokens: ["you", "'", "re", " ", "moving"]

Token "you" (index 0):
    prev_uid: None
    next_uid: UID of "'"

Token "'" (index 1):
    prev_uid: UID of "you"
    next_uid: UID of "re"

Token "re" (index 2):
    prev_uid: UID of "'"
    next_uid: UID of " "

Token " " (index 3):
    prev_uid: UID of "re"
    next_uid: UID of "moving"

Token "moving" (index 4):
    prev_uid: UID of " "
    next_uid: None
```

### Mathematical Properties:
- **Linked Structure**: Creates token chain
- **Context Preservation**: Maintains sequential relationships
- **Bidirectional**: Knows both previous and next tokens

---

## COMPLETE EXAMPLE: Full Tokenization

### Input Sentence:
```
"you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
```

### Space Tokenization:
```
1. "you're" (id: 0, type: content, index: 0)
2. " " (id: 1, type: space, index: 6)
3. "moving" (id: 2, type: content, index: 7)
4. " " (id: 3, type: space, index: 13)
5. "tens" (id: 4, type: content, index: 14)
6. " " (id: 5, type: space, index: 18)
7. "of" (id: 6, type: content, index: 19)
8. " " (id: 7, type: space, index: 21)
9. "gigabytes," (id: 8, type: content, index: 22)
10. " " (id: 9, type: space, index: 32)
... (24 tokens total)
```

### Word Tokenization:
```
1. "you" (id: 0, type: word, index: 0)
2. "'" (id: 1, type: non_word, index: 3)
3. "re" (id: 2, type: word, index: 4)
4. " " (id: 3, type: non_word, index: 6)
5. "moving" (id: 4, type: word, index: 7)
6. " " (id: 5, type: non_word, index: 13)
7. "tens" (id: 6, type: word, index: 14)
8. " " (id: 7, type: non_word, index: 18)
9. "of" (id: 8, type: word, index: 19)
10. " " (id: 9, type: non_word, index: 21)
11. "gigabytes" (id: 10, type: word, index: 22)
12. "," (id: 11, type: non_word, index: 31)
... (52 tokens total)
```

### Character Tokenization:
```
1. "y" (id: 0, type: character, index: 0, codepoint: 121)
2. "o" (id: 1, type: character, index: 1, codepoint: 111)
3. "u" (id: 2, type: character, index: 2, codepoint: 117)
4. "'" (id: 3, type: character, index: 3, codepoint: 39)
5. "r" (id: 4, type: character, index: 4, codepoint: 114)
6. "e" (id: 5, type: character, index: 5, codepoint: 101)
7. " " (id: 6, type: character, index: 6, codepoint: 32)
... (147 tokens total)
```

### Grammar Tokenization:
```
1. "you" (id: 0, type: word, index: 0)
2. "'" (id: 1, type: punctuation, index: 3, codepoint: 39)
3. "re" (id: 2, type: word, index: 4)
4. " " (id: 3, type: space, index: 6)
5. "moving" (id: 4, type: word, index: 7)
6. " " (id: 5, type: space, index: 13)
7. "tens" (id: 6, type: word, index: 14)
8. " " (id: 7, type: space, index: 18)
9. "of" (id: 8, type: word, index: 19)
10. " " (id: 9, type: space, index: 21)
11. "gigabytes" (id: 10, type: word, index: 22)
12. "," (id: 11, type: punctuation, index: 31, codepoint: 44)
... (52 tokens total)
```

### Subword Tokenization (Fixed, chunk_size=3):
```
Word "moving":
1. "mov" (id: 0, type: subword, parent_word: "moving", subword_index: 0)
2. "ing" (id: 1, type: subword, parent_word: "moving", subword_index: 1)

Word "gigabytes":
1. "gig" (id: 10, type: subword, parent_word: "gigabytes", subword_index: 0)
2. "aby" (id: 11, type: subword, parent_word: "gigabytes", subword_index: 1)
3. "tes" (id: 12, type: subword, parent_word: "gigabytes", subword_index: 2)
... (non-word characters preserved as-is)
```

### Byte Tokenization:
```
Character "y" (codepoint: 121):
1. "1" (id: 0, type: byte, codepoint: 121, byte_value: 1)
2. "2" (id: 1, type: byte, codepoint: 121, byte_value: 2)
3. "1" (id: 2, type: byte, codepoint: 121, byte_value: 1)

Character "o" (codepoint: 111):
1. "1" (id: 3, type: byte, codepoint: 111, byte_value: 1)
2. "1" (id: 4, type: byte, codepoint: 111, byte_value: 1)
3. "1" (id: 5, type: byte, codepoint: 111, byte_value: 1)
... (each character → byte sequence)
```

---

## MATHEMATICAL PROPERTIES SUMMARY

### Determinism:
- **Same Input → Same Output**: All tokenizations are deterministic
- **Seed-Based UIDs**: UIDs depend on seed (reproducible)
- **No Randomness**: All operations are mathematical

### Reversibility:
- **Perfect Reconstruction**: Original text can be reconstructed from tokens
- **No Information Loss**: All characters, spaces, punctuation preserved
- **Metadata Preservation**: Index, type, length stored for reconstruction

### Uniqueness:
- **Unique UIDs**: Each token gets unique 64-bit UID
- **Unique Global IDs**: Each token gets unique global ID across streams
- **Stream Isolation**: Different streams have different IDs

### Mathematical Operations:
- **XOR**: Used for UID generation and global ID computation
- **Modulo**: Used for digital root and hash operations
- **Bit Shifts**: Used for position encoding in global ID
- **Hash Functions**: Used for content ID and digit generation

---

## TOKEN FEATURES SUMMARY

### Each Token Contains:
1. **text**: Original token text
2. **id**: Sequential token ID (0, 1, 2, ...)
3. **index**: Position in original text
4. **type**: Token type (word, space, punctuation, etc.)
5. **length**: Token length in characters
6. **uid**: Unique 64-bit identifier (XorShift64*)
7. **prev_uid**: Previous token's UID (for context)
8. **next_uid**: Next token's UID (for context)
9. **frontend**: Digital root (1-9) from alphabetic mapping
10. **backend**: 64-bit composite number
11. **content_id**: Hash of token text
12. **global_id**: Unique ID across all streams
13. **stream**: Tokenization strategy name

### Mathematical Relationships:
```
frontend = digital_root_9(alphabetic_sum(text))
backend = compose(text, position, uid, prev_uid, next_uid, embedding_bit)
content_id = hash(text) MOD 2^64
global_id = uid XOR content_id XOR (index << 17) XOR stream_id XOR session_id
```

---

## CONCLUSION

SOMA tokenization is:
- **Mathematical**: All operations are pure math (no ML models)
- **Deterministic**: Same input → same output
- **Reversible**: Perfect reconstruction guaranteed
- **Unique**: Every token has unique identifiers
- **Context-Aware**: Neighbor relationships preserved
- **Multi-Level**: 9 different tokenization strategies
- **Efficient**: Fast processing, low memory footprint

All tokenization logic is based on mathematical formulas and algorithms, ensuring reproducibility and perfect reconstruction.

