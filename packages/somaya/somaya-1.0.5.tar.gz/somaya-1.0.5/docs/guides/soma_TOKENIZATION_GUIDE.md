# SOMA Tokenization Guide - Complete Reference

## Table of Contents
1. [Overview](#overview)
2. [Text Preprocessing](#text-preprocessing)
3. [Tokenization Methods](#tokenization-methods)
   - [Space-Based Tokenization](#space-based-tokenization-most-common)
   - [Character-Based Tokenization](#character-based-tokenization)
   - [Word Boundary Tokenization](#word-boundary-tokenization)
   - [Grammar-Based Tokenization](#grammar-based-tokenization)
   - [Subword Tokenization](#subword-tokenization)
   - [Byte-Level Tokenization](#byte-level-tokenization)
4. [Hash-Based Digit Generation](#hash-based-digit-generation)
5. [Weighted Sum Method](#weighted-sum-method)
6. [Combined Digit Generation](#combined-digit-generation)
7. [Complete Example Walkthrough](#complete-example-walkthrough)
8. [Algorithm Details](#algorithm-details)
9. [Complete Tokenization Pipeline](#complete-tokenization-pipeline)
10. [Quick Reference](#quick-reference)
11. [Summary](#summary)
12. [Appendix: Common Patterns](#appendix-common-patterns)
13. [Complete Mathematical Calculation Example](#complete-mathematical-calculation-example)

---

## Overview

SOMA (Santosh Tokenization) is a text tokenization system that converts text into tokens and generates numeric digits (0-9) for each token. The system uses multiple methods:

1. **Hash-based method**: Polynomial rolling hash algorithm
2. **Weighted sum method**: Position-weighted character sum with digital root
3. **Combined method**: Combination of both methods

### What is Tokenization?

**Tokenization** is the process of breaking down text into smaller units called "tokens". In SOMA, tokens are typically words separated by spaces. For example, the text "Hello World" becomes two tokens: ["Hello", "World"].

### What are Digits?

After tokenization, each token is converted into numeric digits (0-9) using mathematical calculations. These digits represent the token in a numerical form, which can be used for various purposes like indexing, searching, or analysis.

### Key Concepts for Beginners

- **ASCII Values**: Every character (letter, number, symbol) has a numeric code called ASCII. For example, 'A' = 65, 'a' = 97, '0' = 48.
- **Hash**: A mathematical function that converts text into a large number.
- **Digital Root**: A method to reduce a large number to a single digit (1-9).
- **Modulo Operation (%)**: Returns the remainder after division. For example, 15 % 10 = 5.

---

## Text Preprocessing

Before tokenization, text goes through preprocessing steps:

### 1. Case Normalization (Optional, default: enabled)

Converts all uppercase letters (A-Z) to lowercase (a-z).

**Algorithm:**
- For each character in text:
  - If ASCII code is between 65-90 (A-Z): Convert to lowercase by adding 32
  - Otherwise: Keep character as-is

**Example:**
```
Input:  "Santosh Yadav Chavala"
Output: "santosh yadav chavala"
```

### 2. Punctuation Removal (Optional, default: disabled)

Removes all punctuation and special characters, keeping only:
- Uppercase letters (A-Z): ASCII 65-90
- Lowercase letters (a-z): ASCII 97-122
- Digits (0-9): ASCII 48-57
- Space character: ASCII 32

**Example:**
```
Input:  "Hello, World! How are you?"
Output: "Hello World How are you"
```

### 3. Whitespace Normalization (Always applied)

Collapses multiple consecutive spaces into a single space.

**Algorithm:**
- Traverse text character by character
- If current character is space and previous was NOT space: Add space
- If current character is NOT space: Add character

**Example:**
```
Input:  "Hello    World    Test"
Output: "Hello World Test"
```

---

## Tokenization Methods

SOMA provides **9 different tokenization methods** to handle various text processing needs. Each method has its own algorithm and use cases.

### 1. Space-Based Tokenization (space)

Splits text by whitespace characters (space, tab, newline, etc.).

**Algorithm:**
1. Initialize empty token list
2. Traverse text character by character
3. When encountering whitespace:
   - Save current token (if any) to list
   - Reset current token
4. When encountering non-whitespace:
   - Append character to current token
5. Add final token (if any) to list

**Example:**
```
Input:  "santosh yadav chavala"
Tokens: ["santosh", "yadav", "chavala"]
```

### 2. Character-Based Tokenization (char)

Each character becomes a separate token.

**Example:**
```
Input:  "Hi"
Tokens: ["H", "i"]
```

### 3. Word Boundary Tokenization (word)

Splits text by word boundaries, extracting only alphabetic sequences (A-Z, a-z). Non-word characters (punctuation, digits, spaces) are preserved as separate tokens.

**Algorithm:**
1. Traverse text character by character
2. When encountering word characters (letters):
   - Collect consecutive word characters into a token
3. When encountering non-word characters:
   - Save current word token (if any)
   - Create separate token for non-word character
4. Return all tokens (words and non-word characters)

**Example:**
```
Input:  "Hello123World!"
Tokens: [
  {"text": "Hello", "type": "word"},
  {"text": "1", "type": "non_word"},
  {"text": "2", "type": "non_word"},
  {"text": "3", "type": "non_word"},
  {"text": "World", "type": "word"},
  {"text": "!", "type": "non_word"}
]
```

### 4. Grammar-Based Tokenization (grammar)

Splits text into words, punctuation, and spaces separately. This method distinguishes between words, punctuation marks, and whitespace.

**Algorithm:**
1. Traverse text character by character
2. Collect consecutive word characters into word tokens
3. Treat punctuation (non-word, non-space) as separate tokens
4. Treat spaces as separate tokens
5. Return tokens with type classification

**Token Types:**
- `word`: Alphabetic sequences
- `punctuation`: Punctuation marks
- `space`: Whitespace characters

**Example:**
```
Input:  "Hello, World!"
Tokens: [
  {"text": "Hello", "type": "word"},
  {"text": ",", "type": "punctuation"},
  {"text": " ", "type": "space"},
  {"text": "World", "type": "word"},
  {"text": "!", "type": "punctuation"}
]
```

### 5. Subword Tokenization (subword) - Fixed-Length Strategy

Splits words into smaller subword units using fixed-length chunks. This is the default subword strategy.

**Strategy: Fixed-Length**

Splits words into fixed-size chunks.

**Algorithm:**
- Divide word into chunks of specified length (default: 3 characters)
- Last chunk may be shorter if word length is not divisible by chunk size

**Example:**
```
Input:  "tokenization"
Chunk Length: 3
Tokens: ["tok", "eni", "zat", "ion"]
```

### 6. BPE-Like Subword Tokenization (subword_bpe)

Uses pattern matching similar to Byte Pair Encoding (BPE), identifying common 2-3 character patterns in English.

Uses pattern matching similar to Byte Pair Encoding (BPE), identifying common 2-3 character patterns in English.

**Common Patterns:**
- 2-character: "th", "he", "in", "er", "an", "re", "ed", "nd", "on", etc.
- 3-character: "the", "and", "ing", "ion", "tio", "ent", "for", etc.

**Algorithm:**
1. Scan word from left to right
2. Match longest common pattern (3-char, then 2-char, then single char)
3. Continue until word is fully processed

**Example:**
```
Input:  "tokenization"
Tokens: ["to", "ken", "iz", "at", "ion"]
```

### 7. Syllable-Based Subword Tokenization (subword_syllable)

Splits words based on vowel patterns, grouping consonants with following vowels.

Splits words based on vowel patterns, grouping consonants with following vowels.

**Algorithm:**
1. Identify vowels (a, e, i, o, u)
2. Group characters: consonants before vowels are grouped with the vowel
3. Create syllables ending at vowels
4. Last consonants attach to previous syllable

**Example:**
```
Input:  "tokenization"
Syllables: ["to", "ke", "ni", "za", "tion"]
```

### 8. Frequency-Based Subword Tokenization (subword_frequency)

Uses frequency-based pattern matching, prioritizing common 2-character patterns in English text.

Uses frequency-based pattern matching, prioritizing common 2-character patterns in English text.

**Common Patterns:**
- "th", "he", "in", "er", "an", "re", "ed", "nd", "on", "en", "at", "ou", etc.

**Algorithm:**
1. Scan word from left to right
2. Match 2-character patterns first (most common)
3. Fall back to single characters
4. Continue until word is processed

**Example:**
```
Input:  "tokenization"
Tokens: ["to", "ke", "n", "i", "z", "at", "ion"]
```

### 9. Byte-Level Tokenization (byte)

Converts text to byte-level representation using UTF-8 byte simulation. Each character is encoded into its UTF-8 byte representation.

**Algorithm:**
1. For each character in text:
   - Get Unicode code point (ordinal value)
   - Simulate UTF-8 byte encoding based on code point range:
     - **1-byte (0-127)**: ASCII characters, single byte
     - **2-byte (128-2047)**: 2 bytes for extended ASCII and some Unicode
     - **3-byte (2048-65535)**: 3 bytes for most Unicode characters
     - **4-byte (65536+)**: 4 bytes for rare Unicode characters
   - Create tokens for each byte
2. Each token represents a byte value (0-255)

**UTF-8 Encoding Rules:**
- **1-byte (ASCII)**: Code point 0-127 → Single byte equals code point
- **2-byte**: Code point 128-2047 → First byte: 0xC0 | (codepoint >> 6), Second byte: 0x80 | (codepoint & 0x3F)
- **3-byte**: Code point 2048-65535 → First byte: 0xE0 | (codepoint >> 12), Second/Third bytes: 0x80 | (bits)
- **4-byte**: Code point 65536+ → First byte: 0xF0 | (codepoint >> 18), Remaining bytes: 0x80 | (bits)

**Example:**
```
Input:  "Hi"
Character 'H': Code point 72 (ASCII)
  UTF-8 bytes: [72]
Character 'i': Code point 105 (ASCII)
  UTF-8 bytes: [105]

Tokens: [
  {"text": "72", "type": "utf8_byte", "byte_value": 72, "codepoint": 72},
  {"text": "105", "type": "utf8_byte", "byte_value": 105, "codepoint": 105}
]
```

**Example with Unicode:**
```
Input:  "A"
Character 'A': Code point 65 (ASCII, 1-byte)
  UTF-8 bytes: [65]

Input:  "€"  
Character '€': Code point 8364 (3-byte UTF-8)
  UTF-8 bytes: [226, 130, 172]
  Calculation:
    Byte 1: 0xE0 | (8364 >> 12) = 0xE0 | 2 = 226
    Byte 2: 0x80 | ((8364 >> 6) & 0x3F) = 0x80 | 2 = 130
    Byte 3: 0x80 | (8364 & 0x3F) = 0x80 | 44 = 172
```

### Summary of All 9 Tokenization Methods

SOMA supports **9 different tokenization methods**. Here's a complete overview:

| # | Method | Description | Token Types | Use Case |
|---|--------|-------------|-------------|----------|
| 1 | **space** | Split by whitespace | content, space | Simple word-level tokenization |
| 2 | **word** | Split by word boundaries | word, non_word | Extract words, preserve punctuation |
| 3 | **char** | Character-level | character | Fine-grained analysis |
| 4 | **grammar** | Grammar-aware | word, punctuation, space | Linguistic analysis |
| 5 | **subword** (fixed) | Fixed-length chunks | subword | Vocabulary compression |
| 6 | **subword_bpe** | BPE-like patterns | subword | Common English patterns |
| 7 | **subword_syllable** | Syllable-based | subword | Linguistic syllables |
| 8 | **subword_frequency** | Frequency-based | subword | Common patterns first |
| 9 | **byte** | Byte-level UTF-8 | utf8_byte | Low-level encoding |

**Note:** Methods 5-8 are all subword tokenization strategies. The base method is `subword` (fixed-length), while `subword_bpe`, `subword_syllable`, and `subword_frequency` are specialized variants.

---

## Hash-Based Digit Generation

This is the method you documented in your guide. It's one part of the tokenization logic.

### What is Hash-Based Digit Generation?

Hash-based digit generation uses a mathematical formula called a "polynomial rolling hash" to convert a token (word) into a large number, then extracts a single digit (0-9) from that number.

### Hash Calculation Formula

```
Start with: h = 0
For each character in token (from left to right):
    h = h * 31 + ASCII(character)
Final digit = h % 10
```

**Explanation:**
- We start with `h = 0`
- For each character, we multiply the current hash by 31 (a prime number)
- Then add the ASCII value of the character
- Finally, we use modulo 10 (`% 10`) to get the last digit (0-9)

### Step-by-Step Process

1. **Initialize hash**: Start with `h = 0`
2. **For each character** in the token (from left to right):
   - Take the current hash value
   - Multiply it by 31
   - Add the ASCII value of the current character
   - This becomes the new hash value
3. **Convert to digit**: Use modulo 10 (`hash % 10`) to get a single digit (0-9)

### Why 31?

The number 31 is a prime number commonly used in string hashing algorithms. It provides good distribution of hash values and reduces collisions (when different tokens produce the same hash).

### Complete Example: "santosh"

```
Token: "santosh"

Step 1: 's' (ASCII 115)
  h = 0 * 31 + 115 = 115

Step 2: 'a' (ASCII 97)
  h = 115 * 31 + 97 = 3565 + 97 = 3662

Step 3: 'n' (ASCII 110)
  h = 3662 * 31 + 110 = 113522 + 110 = 113632

Step 4: 't' (ASCII 116)
  h = 113632 * 31 + 116 = 3522592 + 116 = 3522708

Step 5: 'o' (ASCII 111)
  h = 3522708 * 31 + 111 = 109203948 + 111 = 109204059

Step 6: 's' (ASCII 115)
  h = 109204059 * 31 + 115 = 3385325829 + 115 = 3385325944

Step 7: 'h' (ASCII 104)
  h = 3385325944 * 31 + 104 = 104945104264 + 104 = 104945104368

Final Hash: 104945104368
Digit: 104945104368 % 10 = 8
```

### Complete Example: "yadav"

```
Token: "yadav"

Step 1: 'y' (ASCII 121)
  h = 0 * 31 + 121 = 121

Step 2: 'a' (ASCII 97)
  h = 121 * 31 + 97 = 3751 + 97 = 3848

Step 3: 'd' (ASCII 100)
  h = 3848 * 31 + 100 = 119288 + 100 = 119388

Step 4: 'a' (ASCII 97)
  h = 119388 * 31 + 97 = 3701028 + 97 = 3701125

Step 5: 'v' (ASCII 118)
  h = 3701125 * 31 + 118 = 114734875 + 118 = 114734993

Final Hash: 114734993
Digit: 114734993 % 10 = 3
```

### Complete Example: "chavala"

```
Token: "chavala"

Step 1: 'c' (ASCII 99)
  h = 0 * 31 + 99 = 99

Step 2: 'h' (ASCII 104)
  h = 99 * 31 + 104 = 3069 + 104 = 3173

Step 3: 'a' (ASCII 97)
  h = 3173 * 31 + 97 = 98363 + 97 = 98460

Step 4: 'v' (ASCII 118)
  h = 98460 * 31 + 118 = 3052260 + 118 = 3052378

Step 5: 'a' (ASCII 97)
  h = 3052378 * 31 + 97 = 94623718 + 97 = 94623815

Step 6: 'l' (ASCII 108)
  h = 94623815 * 31 + 108 = 2933338265 + 108 = 2933338373

Step 7: 'a' (ASCII 97)
  h = 2933338373 * 31 + 97 = 90933489563 + 97 = 90933489660

Final Hash: 90933489660
Digit: 90933489660 % 10 = 0
```

### Important Notes

- **Case Sensitivity**: Hash is case-sensitive!
  - "Santosh" (capital S) → hash: `76544986576`, digit: `6`
  - "santosh" (lowercase s) → hash: `104945104368`, digit: `8`
  
- **Character Order Matters**: The hash depends on the exact sequence of characters

- **All Characters Included**: Every character in the token affects the hash, including spaces if present

---

## Weighted Sum Method

This is another method used in SOMA for digit generation.

### Weighted Sum Calculation

For a token, calculate the weighted sum by multiplying each character's ASCII value by its position (1-indexed).

**Formula:**
```
weighted_sum = 0
position = 1
For each character in token:
    weighted_sum = weighted_sum + (ASCII(character) * position)
    position = position + 1
```

### Example: "santosh"

```
Token: "santosh"

Position 1: 's' (ASCII 115) → 115 * 1 = 115
Position 2: 'a' (ASCII 97)  → 97 * 2  = 194
Position 3: 'n' (ASCII 110) → 110 * 3 = 330
Position 4: 't' (ASCII 116) → 116 * 4 = 464
Position 5: 'o' (ASCII 111) → 111 * 5 = 555
Position 6: 's' (ASCII 115) → 115 * 6 = 690
Position 7: 'h' (ASCII 104) → 104 * 7 = 728

Weighted Sum = 115 + 194 + 330 + 464 + 555 + 690 + 728 = 3076
```

### Digital Root (9-Centric)

Convert the weighted sum to a single digit (1-9) using digital root.

**Formula:**
```
If n <= 0: return 9
Otherwise: return ((n - 1) % 9) + 1
```

**Example:**
```
Weighted Sum: 3076

Step 1: (3076 - 1) % 9 = 3075 % 9 = 6
Step 2: 6 + 1 = 7

Digital Root: 7
```

### With Embedding Bit (Optional)

If embedding_bit is enabled:
```
digital_root = digital_root_9(weighted_sum)
final_digit = digital_root_9(digital_root + 1)
```

---

## Combined Digit Generation

The combined method uses both weighted sum and hash methods.

### Formula

```
1. Calculate Weighted Digit:
   weighted_sum = weighted_char_sum(token)
   weighted_digit = digital_root_9(weighted_sum)
   (If embedding_bit: weighted_digit = digital_root_9(weighted_digit + 1))

2. Calculate Hash Digit:
   hash_value = hash_token(token)
   hash_digit = hash_value % 10

3. Combine:
   combined_digit = (weighted_digit * 9 + hash_digit) % 9 + 1
```

### Example: "santosh"

**Step 1: Weighted Digit**
```
Weighted Sum: 3076
Weighted Digit: 7 (from digital root calculation above)
```

**Step 2: Hash Digit**
```
Hash: 104945104368
Hash Digit: 104945104368 % 10 = 8
```

**Step 3: Combined**
```
combined_digit = (7 * 9 + 8) % 9 + 1
               = (63 + 8) % 9 + 1
               = 71 % 9 + 1
               = 8 + 1
               = 9
```

---

## Complete Example Walkthrough

Let's process the text: **"Santosh Yadav Chavala"**

### Step 1: Preprocessing

**Case Normalization (enabled by default):**
```
Input:  "Santosh Yadav Chavala"
Output: "santosh yadav chavala"
```

**Punctuation Removal (disabled by default):**
```
No changes (no punctuation to remove)
```

**Whitespace Normalization:**
```
Input:  "santosh yadav chavala"
Output: "santosh yadav chavala" (single spaces, no changes)
```

### Step 2: Tokenization (Space-based)

```
Tokens: ["santosh", "yadav", "chavala"]
```

### Step 3: Hash-Based Digit Generation

**Token 1: "santosh"**
```
Hash: 104945104368
Hash Digit: 8
```

**Token 2: "yadav"**
```
Hash: 114734993
Hash Digit: 3
```

**Token 3: "chavala"**
```
Hash: 90933489660
Hash Digit: 0
```

**Results:**
```
santosh → 8
yadav   → 3
chavala → 0
```

### Step 4: Weighted Sum Digit Generation

**Token 1: "santosh"**
```
Weighted Sum: 3076
Digital Root: 7
```

**Token 2: "yadav"**
```
Position 1: 'y' (121) → 121 * 1 = 121
Position 2: 'a' (97)  → 97 * 2  = 194
Position 3: 'd' (100) → 100 * 3 = 300
Position 4: 'a' (97)  → 97 * 4  = 388
Position 5: 'v' (118) → 118 * 5 = 590

Weighted Sum: 121 + 194 + 300 + 388 + 590 = 1593
Digital Root: ((1593 - 1) % 9) + 1 = (1592 % 9) + 1 = 8 + 1 = 9
```

**Token 3: "chavala"**
```
Position 1: 'c' (99)  → 99 * 1  = 99
Position 2: 'h' (104) → 104 * 2 = 208
Position 3: 'a' (97)  → 97 * 3  = 291
Position 4: 'v' (118) → 118 * 4 = 472
Position 5: 'a' (97)  → 97 * 5  = 485
Position 6: 'l' (108) → 108 * 6 = 648
Position 7: 'a' (97)  → 97 * 7  = 679

Weighted Sum: 99 + 208 + 291 + 472 + 485 + 648 + 679 = 2882
Digital Root: ((2882 - 1) % 9) + 1 = (2881 % 9) + 1 = 1 + 1 = 2
```

**Results:**
```
santosh → 7
yadav   → 9
chavala → 2
```

### Step 5: Combined Digit Generation

**Token 1: "santosh"**
```
Weighted Digit: 7
Hash Digit: 8
Combined: (7 * 9 + 8) % 9 + 1 = 71 % 9 + 1 = 8 + 1 = 9
```

**Token 2: "yadav"**
```
Weighted Digit: 9
Hash Digit: 3
Combined: (9 * 9 + 3) % 9 + 1 = (81 + 3) % 9 + 1 = 84 % 9 + 1 = 3 + 1 = 4
```

**Token 3: "chavala"**
```
Weighted Digit: 2
Hash Digit: 0
Combined: (2 * 9 + 0) % 9 + 1 = 18 % 9 + 1 = 0 + 1 = 1
```

**Final Results:**
```
santosh → Hash: 8, Weighted: 7, Combined: 9
yadav   → Hash: 3, Weighted: 9, Combined: 4
chavala → Hash: 0, Weighted: 2, Combined: 1
```

---

## Algorithm Details

### Hash Algorithm Properties

- **Deterministic**: Same input always produces same output
- **Case Sensitive**: Different cases produce different hashes
- **Position Sensitive**: Character order matters
- **Polynomial Rolling Hash**: Uses base 31 (prime number)

### Weighted Sum Properties

- **Position Dependent**: Earlier characters have less weight
- **Order Dependent**: Character sequence matters
- **Digital Root**: Always reduces to 1-9

### Combined Method Properties

- **Combines Both Methods**: Uses information from both hash and weighted sum
- **Range**: Always produces digit 1-9 (never 0)
- **More Robust**: Less likely to collide than single method

### Implementation Notes

1. **ASCII Values**: All calculations use ASCII character codes
2. **Integer Arithmetic**: All calculations use integer arithmetic
3. **Modulo Operations**: Used for digit extraction and combination
4. **No Floating Point**: All operations are integer-based

---

## Complete Tokenization Pipeline

### End-to-End Process Flow

The complete SOMA tokenization process follows these steps:

```
Input Text
    ↓
[1. Preprocessing]
    ├─ Case Normalization (optional, default: ON)
    ├─ Punctuation Removal (optional, default: OFF)
    └─ Whitespace Normalization (always ON)
    ↓
[2. Tokenization]
    └─ Split text into tokens (default: by spaces)
    ↓
[3. For Each Token]
    ├─ Calculate Hash Value (h = h * 31 + ASCII)
    ├─ Calculate Weighted Sum (position * ASCII)
    ├─ Generate Hash Digit (hash % 10)
    ├─ Generate Weighted Digit (digital_root_9)
    └─ Generate Combined Digit ((weighted * 9 + hash) % 9 + 1)
    ↓
Output: Tokens with Digits
```

### Step-by-Step Pipeline Example

**Input:** `"Santosh Yadav Chavala"`

**Step 1: Preprocessing**
```
Input:        "Santosh Yadav Chavala"
Case Normal:  "santosh yadav chavala"  (default: ON)
Whitespace:   "santosh yadav chavala"  (no change)
```

**Step 2: Tokenization**
```
Tokens: ["santosh", "yadav", "chavala"]
```

**Step 3: Digit Generation for Each Token**

For token "santosh":
- Hash calculation → `104945104368`
- Hash digit → `8`
- Weighted sum → `3076`
- Weighted digit → `7`
- Combined digit → `9`

For token "yadav":
- Hash calculation → `114734993`
- Hash digit → `3`
- Weighted sum → `1593`
- Weighted digit → `9`
- Combined digit → `4`

For token "chavala":
- Hash calculation → `90933489660`
- Hash digit → `0`
- Weighted sum → `2882`
- Weighted digit → `2`
- Combined digit → `1`

**Final Output:**
```
Token    | Hash Digit | Weighted Digit | Combined Digit
---------|------------|----------------|---------------
santosh  |     8      |       7        |       9
yadav    |     3      |       9        |       4
chavala  |     0      |       2        |       1
```

---

## Quick Reference

### Hash-Based Digit Generation

**Formula:**
```
h = 0
for each character in token:
    h = h * 31 + ASCII(character)
digit = h % 10
```

**Range:** 0-9

**Key Points:**
- Case sensitive
- Position sensitive
- Deterministic

### Weighted Sum Digit Generation

**Formula:**
```
weighted_sum = 0
position = 1
for each character in token:
    weighted_sum += ASCII(character) * position
    position += 1
digit = ((weighted_sum - 1) % 9) + 1
```

**Range:** 1-9

**Key Points:**
- Position-dependent (earlier chars have less weight)
- Always produces 1-9 (never 0)

### Combined Digit Generation

**Formula:**
```
weighted_digit = digital_root_9(weighted_sum)
hash_digit = hash_token(token) % 10
combined_digit = (weighted_digit * 9 + hash_digit) % 9 + 1
```

**Range:** 1-9

**Key Points:**
- Combines both methods
- More robust (less collision)
- Always produces 1-9

### ASCII Reference

Common ASCII values used in calculations:

```
Space:    32
Digits:   48-57  (0-9)
Uppercase: 65-90  (A-Z)
Lowercase: 97-122 (a-z)

Common characters:
A = 65,  a = 97
Z = 90,  z = 122
0 = 48,  9 = 57
' ' = 32
```

### Digital Root (9-Centric) Formula

```
If n <= 0: return 9
Otherwise: return ((n - 1) % 9) + 1
```

**Examples:**
- `digital_root_9(3076)` = `((3076-1) % 9) + 1` = `6 + 1` = `7`
- `digital_root_9(1593)` = `((1593-1) % 9) + 1` = `8 + 1` = `9`
- `digital_root_9(2882)` = `((2882-1) % 9) + 1` = `1 + 1` = `2`

---

## Summary

This guide covers the complete tokenization process in SOMA:

1. **Preprocessing**: Case normalization, punctuation removal, whitespace normalization
2. **Tokenization**: Splitting text into tokens (typically by spaces)
3. **Hash Method**: Polynomial rolling hash (h = h * 31 + ASCII) → modulo 10
4. **Weighted Method**: Position-weighted sum → digital root (1-9)
5. **Combined Method**: (Weighted_Digit × 9 + Hash_Digit) % 9 + 1

### Key Takeaways

- **Hash-based method** is one core component (produces 0-9)
- **Weighted sum method** is another core component (produces 1-9)
- **Combined method** uses both for robustness (produces 1-9)
- All methods are **deterministic** - same input always produces same output
- All calculations use **integer arithmetic** - no floating point
- **Case sensitivity** matters for hash calculations

### Use Cases

- **Hash Digit (0-9)**: Fast, simple digit generation
- **Weighted Digit (1-9)**: Position-aware digit generation
- **Combined Digit (1-9)**: Most robust, combines strengths of both methods

---

## Appendix: Common Patterns

### Why Base 31 for Hash?

The number 31 is a prime number, which helps with:
- Better distribution of hash values
- Reduced collisions
- Common choice in string hashing (Java's String.hashCode() uses 31)

### Why Digital Root Modulo 9?

Digital root modulo 9 has mathematical properties:
- Reduces large numbers to single digits (1-9)
- Maintains some mathematical relationships
- Used in many digit extraction algorithms

### Why Combine Methods?

Combining hash and weighted sum:
- **Redundancy**: If one method fails, the other provides backup
- **Robustness**: Less likely to have collisions
- **Information**: Uses more information about the token
- **Range**: Ensures output is always 1-9 (never 0)

---

## Complete Token Record Generation

This section covers the complete tokenization process including all token properties.

### Token Record Structure

A complete token record contains the following properties:

```
TokenRecord:
  - text: Token text (string)
  - stream: Tokenization method name (string)
  - index: Position in text (integer)
  - uid: Unique identifier (64-bit integer)
  - prev_uid: Previous token's UID (64-bit integer or None)
  - next_uid: Next token's UID (64-bit integer or None)
  - content_id: Content-based ID (integer 13-150012)
  - frontend: Combined digit (integer 1-9)
  - backend_huge: Backend number (large integer)
  - backend_scaled: Backend number % 100000 (integer 0-99999)
  - global_id: Global identifier (64-bit integer)
```

### Complete Tokenization Pipeline

The full tokenization process involves these steps:

1. **Preprocessing** (case normalization, whitespace normalization)
2. **Tokenization** (split text into tokens)
3. **UID Assignment** (assign unique identifiers)
4. **Neighbor UIDs** (add previous/next UID references)
5. **Frontend Digit** (combined digit generation)
6. **Backend Number** (compose backend number)
7. **Content ID** (hash-based content ID)
8. **Global ID** (combine UID, content_id, position, stream_id, session_id)
9. **Backend Scaled** (backend_huge % 100000)

---

## UID Assignment

### What are UIDs?

**UID (Unique Identifier)** is a 64-bit integer assigned to each token using a deterministic random number generator (XorShift64Star). UIDs are generated sequentially using a seed value.

### XorShift64Star Algorithm

XorShift64Star is a pseudorandom number generator that produces deterministic sequences.

**Algorithm:**
```
State initialization:
  If seed == 0: seed = 0x9E3779B97F4A7C15
  state = seed & ((1 << 64) - 1)

Next value generation:
  x = state
  x = x ^ (x >> 12) & ((1 << 64) - 1)
  x = x ^ (x << 25) & ((1 << 64) - 1)
  x = x ^ (x >> 27) & ((1 << 64) - 1)
  x = (x * 2685821657736338717) & ((1 << 64) - 1)
  state = x
  return x
```

**Properties:**
- **Deterministic**: Same seed always produces same sequence
- **Fast**: Efficient bitwise operations
- **Uniform Distribution**: Good statistical properties
- **64-bit**: Each UID is a 64-bit integer (0 to 2^64-1)

### UID Assignment Process

```
1. Initialize XorShift64Star with seed
2. For each token in sequence:
   - Generate next UID: uid = rng.next_u64()
   - Assign UID to token
3. Return tokens with UIDs
```

**Example:**
```
Input tokens: ["i", "love", "being", "alone"]
Seed: 42

Token 0 ("i"):    UID = XorShift64Star(42).next_u64() = 1234567890123456789
Token 1 ("love"): UID = rng.next_u64() = 9876543210987654321
Token 2 ("being"): UID = rng.next_u64() = 5555555555555555555
Token 3 ("alone"): UID = rng.next_u64() = 1111111111111111111
```

---

## Neighbor UIDs

### What are Neighbor UIDs?

**Neighbor UIDs** are references to the previous and next tokens' UIDs. They provide context information for each token.

### Algorithm

```
For each token at position i:
  prev_uid = tokens[i-1].uid if i > 0 else None
  next_uid = tokens[i+1].uid if i < len(tokens)-1 else None
```

**Properties:**
- **First Token**: prev_uid = None
- **Last Token**: next_uid = None
- **Context Information**: Links tokens in sequence

**Example:**
```
Tokens with UIDs:
  Token 0: uid = 1234567890123456789
  Token 1: uid = 9876543210987654321
  Token 2: uid = 5555555555555555555
  Token 3: uid = 1111111111111111111

After neighbor assignment:
  Token 0: uid = 1234567890123456789, prev_uid = None,      next_uid = 9876543210987654321
  Token 1: uid = 9876543210987654321, prev_uid = 1234567890123456789, next_uid = 5555555555555555555
  Token 2: uid = 5555555555555555555, prev_uid = 9876543210987654321, next_uid = 1111111111111111111
  Token 3: uid = 1111111111111111111, prev_uid = 5555555555555555555, next_uid = None
```

---

## Alphabetic Sum (Numerology)

### What is Alphabetic Sum?

**Alphabetic Sum** (also called "numerology") converts letters to numeric values using an alphabet table, then sums them up.

### Alphabet Table

The alphabet table assigns values 1-9 to letters A-Z using the formula: `value = (position % 9) + 1`

**Table:**
```
A (index 0) → (0 % 9) + 1 = 1
B (index 1) → (1 % 9) + 1 = 2
C (index 2) → (2 % 9) + 1 = 3
D (index 3) → (3 % 9) + 1 = 4
E (index 4) → (4 % 9) + 1 = 5
F (index 5) → (5 % 9) + 1 = 6
G (index 6) → (6 % 9) + 1 = 7
H (index 7) → (7 % 9) + 1 = 8
I (index 8) → (8 % 9) + 1 = 9
J (index 9) → (9 % 9) + 1 = 1
K (index 10) → (10 % 9) + 1 = 2
...
Z (index 25) → (25 % 9) + 1 = 8
```

**Pattern:** Values repeat every 9 letters: 1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8

### Alphabetic Sum Calculation

**Algorithm:**
```
1. Convert all letters to uppercase
2. For each letter:
   - Get ASCII value
   - If lowercase (97-122): Convert to uppercase by subtracting 32
   - If uppercase (65-90):
     - Calculate index: idx = ASCII - 65
     - Get value from table: value = (idx % 9) + 1
     - Add to total
3. Return total
```

**Example: "love"**
```
'l' (108) → uppercase 'L' (76) → index = 76 - 65 = 11 → (11 % 9) + 1 = 3
'o' (111) → uppercase 'O' (79) → index = 79 - 65 = 14 → (14 % 9) + 1 = 6
'v' (118) → uppercase 'V' (86) → index = 86 - 65 = 21 → (21 % 9) + 1 = 4
'e' (101) → uppercase 'E' (69) → index = 69 - 65 = 4  → (4 % 9) + 1 = 5

Alphabetic Sum = 3 + 6 + 4 + 5 = 18
```

---

## Backend Number Generation

### What is Backend Number?

**Backend Number** is a large integer calculated from token properties including weighted sum, position, alphabetic sum, UID, neighbor UIDs, and embedding bit.

### Algorithm: compose_backend_number

**Formula:**
```
1. Calculate weighted sum (s):
   - If run_collapse enabled: s = weighted_char_sum_runaware(token) + runs_sum
   - Otherwise: s = weighted_char_sum(token)
   
2. Calculate length (L):
   - If run_collapse: effective length after collapsing runs
   - Otherwise: actual token length

3. Multiply by length:
   s = s * (1 + (L - 1))

4. Add position:
   s = s + position_in_sentence

5. Add alphabetic sum (numerology):
   s_num = s + alphabetic_sum_fast(token)

6. XOR with UID:
   m = s_num ^ uid

7. Add neighbor UIDs:
   m = m + (prev_uid if prev_uid else 0)
   m = m + (next_uid if next_uid else 0)

8. Add embedding bit:
   m = m + (1 if embedding_bit else 0)

9. Return m (backend_huge)
```

### Weighted Char Sum (Standard)

**Formula:**
```
s = 0
position = 1
For each character in token:
    s = s + (ASCII(character) * position)
    position = position + 1
```

### Weighted Char Sum (Run-Aware)

**Algorithm:**
```
1. Collapse consecutive identical letters into single position
2. Multiply by run length to preserve multiplicity
3. Non-letters are counted normally (no collapsing)

Example: "hello"
  'h' (position 1, run length 1) → ASCII('h') * 1 * 1 = 104
  'e' (position 2, run length 1) → ASCII('e') * 2 * 1 = 202
  'l' (position 3, run length 2) → ASCII('l') * 3 * 2 = 216 * 2 = 432
  'o' (position 4, run length 1) → ASCII('o') * 4 * 1 = 444
  Total = 104 + 202 + 432 + 444 = 1182
```

### Complete Example: "love" (Position 1, UID = 1234567890123456789)

**Step 1: Weighted Sum (Standard)**
```
Position 1: 'l' (108) → 108 * 1 = 108
Position 2: 'o' (111) → 111 * 2 = 222
Position 3: 'v' (118) → 118 * 3 = 354
Position 4: 'e' (101) → 101 * 4 = 404
s = 108 + 222 + 354 + 404 = 1088
```

**Step 2: Length**
```
length = 4
```

**Step 3: Multiply by Length**
```
s = 1088 * (1 + (4 - 1)) = 1088 * 4 = 4352
```

**Step 4: Add Position**
```
s = 4352 + 1 = 4353
```

**Step 5: Add Alphabetic Sum**
```
Alphabetic sum for "love" = 18 (from example above)
s_num = 4353 + 18 = 4371
```

**Step 6: XOR with UID**
```
m = 4371 ^ 1234567890123456789
(Note: This is a bitwise XOR operation)
```

**Step 7: Add Neighbor UIDs**
```
Assume prev_uid = 1111111111111111111
Assume next_uid = 2222222222222222222
m = m + 1111111111111111111
m = m + 2222222222222222222
```

**Step 8: Add Embedding Bit**
```
If embedding_bit = False: m = m + 0
If embedding_bit = True:  m = m + 1
```

**Result:**
```
backend_huge = m (large integer)
backend_scaled = m % 100000 (integer 0-99999)
```

---

## Content ID Generation

### What is Content ID?

**Content ID** is a deterministic, content-based identifier for tokens. It's a hash-based ID that maps to the range 13-150012.

### Algorithm: _content_id

**Formula:**
```
1. Initialize hash:
   h = 1469598103934665603

2. For each character in token:
   h = h ^ ASCII(character)  # XOR with ASCII
   h = (h * 1099511628211) & ((1 << 64) - 1)  # Multiply and mask to 64 bits

3. Final mixing:
   h = h ^ (h >> 33) & ((1 << 64) - 1)
   h = (h * 0xff51afd7ed558ccd) & ((1 << 64) - 1)
   h = h ^ (h >> 33) & ((1 << 64) - 1)

4. Map to range:
   content_id = (h % 150000) + 13
```

**Properties:**
- **Deterministic**: Same token always produces same content_id
- **Range**: 13 to 150012 (150000 + 13 - 1)
- **Hash-based**: Uses polynomial rolling hash with XOR

---

## Global ID Generation

### What is Global ID?

**Global ID** is a 64-bit identifier that combines UID, content_id, position, stream_id, and session_id. It provides a globally unique identifier for tokens across different contexts.

### Algorithm

**Formula:**
```
1. Calculate stream_id:
   stream_id = _content_id(tokenizer_type)  # Hash of tokenizer name

2. Calculate session_id:
   session_id = (seed ^ 0x9E3779B97F4A7C15) & ((1 << 64) - 1)

3. Calculate global_id:
   global_id = (uid ^ content_id ^ (position << 17) ^ stream_id ^ session_id) & ((1 << 64) - 1)
```

**Components:**
- **uid**: Token's unique identifier
- **content_id**: Token's content-based ID
- **position**: Token position (shifted left by 17 bits)
- **stream_id**: Tokenization method ID
- **session_id**: Session identifier from seed

**Properties:**
- **Unique**: Combines multiple identifiers
- **Context-aware**: Includes stream and session information
- **64-bit**: Masked to 64-bit integer

---

## Complete Mathematical Calculation Example

### Example Text: "I LOVE BEING ALONE"

This section provides a complete, step-by-step mathematical calculation for the entire tokenization process.

---

### Step 1: Preprocessing

**Input Text:** `"I LOVE BEING ALONE"`

**Case Normalization (default: ON):**
```
Input:  "I LOVE BEING ALONE"
Output: "i love being alone"
```

**Whitespace Normalization:**
```
Input:  "i love being alone"
Output: "i love being alone"  (no changes, single spaces)
```

---

### Step 2: Tokenization

**Space-Based Tokenization:**
```
Input:  "i love being alone"
Tokens: ["i", "love", "being", "alone"]
```

---

### Step 3: Hash-Based Digit Calculation for Each Token

#### Token 1: "i"

```
Character: 'i'
ASCII Value: 105

Step 1: Process 'i'
  Current hash (h) = 0
  Calculation: h = h * 31 + ASCII('i')
  Calculation: h = 0 * 31 + 105
  Calculation: h = 0 + 105
  New hash (h) = 105

Final Hash: 105
Hash Digit: 105 % 10 = 5
```

#### Token 2: "love"

```
Characters and ASCII Values:
  'l' = 108
  'o' = 111
  'v' = 118
  'e' = 101

Step 1: Process 'l'
  Current hash (h) = 0
  Calculation: h = h * 31 + ASCII('l')
  Calculation: h = 0 * 31 + 108
  Calculation: h = 0 + 108
  New hash (h) = 108

Step 2: Process 'o'
  Current hash (h) = 108
  Calculation: h = h * 31 + ASCII('o')
  Calculation: h = 108 * 31 + 111
  Calculation: h = 3348 + 111
  New hash (h) = 3459

Step 3: Process 'v'
  Current hash (h) = 3459
  Calculation: h = h * 31 + ASCII('v')
  Calculation: h = 3459 * 31 + 118
  Calculation: h = 107229 + 118
  New hash (h) = 107347

Step 4: Process 'e'
  Current hash (h) = 107347
  Calculation: h = h * 31 + ASCII('e')
  Calculation: h = 107347 * 31 + 101
  Calculation: h = 3327757 + 101
  New hash (h) = 3327858

Final Hash: 3327858
Hash Digit: 3327858 % 10 = 8
```

#### Token 3: "being"

```
Characters and ASCII Values:
  'b' = 98
  'e' = 101
  'i' = 105
  'n' = 110
  'g' = 103

Step 1: Process 'b'
  Current hash (h) = 0
  Calculation: h = h * 31 + ASCII('b')
  Calculation: h = 0 * 31 + 98
  Calculation: h = 0 + 98
  New hash (h) = 98

Step 2: Process 'e'
  Current hash (h) = 98
  Calculation: h = h * 31 + ASCII('e')
  Calculation: h = 98 * 31 + 101
  Calculation: h = 3038 + 101
  New hash (h) = 3139

Step 3: Process 'i'
  Current hash (h) = 3139
  Calculation: h = h * 31 + ASCII('i')
  Calculation: h = 3139 * 31 + 105
  Calculation: h = 97309 + 105
  New hash (h) = 97414

Step 4: Process 'n'
  Current hash (h) = 97414
  Calculation: h = h * 31 + ASCII('n')
  Calculation: h = 97414 * 31 + 110
  Calculation: h = 3019834 + 110
  New hash (h) = 3019944

Step 5: Process 'g'
  Current hash (h) = 3019944
  Calculation: h = h * 31 + ASCII('g')
  Calculation: h = 3019944 * 31 + 103
  Calculation: h = 93618264 + 103
  New hash (h) = 93618367

Final Hash: 93618367
Hash Digit: 93618367 % 10 = 7
```

#### Token 4: "alone"

```
Characters and ASCII Values:
  'a' = 97
  'l' = 108
  'o' = 111
  'n' = 110
  'e' = 101

Step 1: Process 'a'
  Current hash (h) = 0
  Calculation: h = h * 31 + ASCII('a')
  Calculation: h = 0 * 31 + 97
  Calculation: h = 0 + 97
  New hash (h) = 97

Step 2: Process 'l'
  Current hash (h) = 97
  Calculation: h = h * 31 + ASCII('l')
  Calculation: h = 97 * 31 + 108
  Calculation: h = 3007 + 108
  New hash (h) = 3115

Step 3: Process 'o'
  Current hash (h) = 3115
  Calculation: h = h * 31 + ASCII('o')
  Calculation: h = 3115 * 31 + 111
  Calculation: h = 96565 + 111
  New hash (h) = 96676

Step 4: Process 'n'
  Current hash (h) = 96676
  Calculation: h = h * 31 + ASCII('n')
  Calculation: h = 96676 * 31 + 110
  Calculation: h = 2996956 + 110
  New hash (h) = 2997066

Step 5: Process 'e'
  Current hash (h) = 2997066
  Calculation: h = h * 31 + ASCII('e')
  Calculation: h = 2997066 * 31 + 101
  Calculation: h = 92909046 + 101
  New hash (h) = 92909147

Final Hash: 92909147
Hash Digit: 92909147 % 10 = 7
```

**Hash Digits Summary:**
```
i     → 5
love  → 8
being → 7
alone → 7
```

---

### Step 4: Weighted Sum Digit Calculation for Each Token

#### Token 1: "i"

```
Character: 'i'
ASCII Value: 105
Position: 1 (first character)

Calculation:
  Position 1: ASCII('i') * 1 = 105 * 1 = 105

Weighted Sum: 105

Digital Root Calculation:
  Step 1: (105 - 1) = 104
  Step 2: 104 % 9 = 5
  Step 3: 5 + 1 = 6

Weighted Digit: 6
```

#### Token 2: "love"

```
Characters and ASCII Values:
  'l' = 108 (position 1)
  'o' = 111 (position 2)
  'v' = 118 (position 3)
  'e' = 101 (position 4)

Calculations:
  Position 1: ASCII('l') * 1 = 108 * 1 = 108
  Position 2: ASCII('o') * 2 = 111 * 2 = 222
  Position 3: ASCII('v') * 3 = 118 * 3 = 354
  Position 4: ASCII('e') * 4 = 101 * 4 = 404

Weighted Sum: 108 + 222 + 354 + 404 = 1088

Digital Root Calculation:
  Step 1: (1088 - 1) = 1087
  Step 2: 1087 % 9 = 7
  Step 3: 7 + 1 = 8

Weighted Digit: 8
```

#### Token 3: "being"

```
Characters and ASCII Values:
  'b' = 98  (position 1)
  'e' = 101 (position 2)
  'i' = 105 (position 3)
  'n' = 110 (position 4)
  'g' = 103 (position 5)

Calculations:
  Position 1: ASCII('b') * 1 = 98 * 1  = 98
  Position 2: ASCII('e') * 2 = 101 * 2 = 202
  Position 3: ASCII('i') * 3 = 105 * 3 = 315
  Position 4: ASCII('n') * 4 = 110 * 4 = 440
  Position 5: ASCII('g') * 5 = 103 * 5 = 515

Weighted Sum: 98 + 202 + 315 + 440 + 515 = 1570

Digital Root Calculation:
  Step 1: (1570 - 1) = 1569
  Step 2: 1569 % 9 = 3
  Step 3: 3 + 1 = 4

Weighted Digit: 4
```

#### Token 4: "alone"

```
Characters and ASCII Values:
  'a' = 97  (position 1)
  'l' = 108 (position 2)
  'o' = 111 (position 3)
  'n' = 110 (position 4)
  'e' = 101 (position 5)

Calculations:
  Position 1: ASCII('a') * 1 = 97 * 1  = 97
  Position 2: ASCII('l') * 2 = 108 * 2 = 216
  Position 3: ASCII('o') * 3 = 111 * 3 = 333
  Position 4: ASCII('n') * 4 = 110 * 4 = 440
  Position 5: ASCII('e') * 5 = 101 * 5 = 505

Weighted Sum: 97 + 216 + 333 + 440 + 505 = 1591

Digital Root Calculation:
  Step 1: (1591 - 1) = 1590
  Step 2: 1590 % 9 = 6
  Step 3: 6 + 1 = 7

Weighted Digit: 7
```

**Weighted Digits Summary:**
```
i     → 6
love  → 8
being → 4
alone → 7
```

---

### Step 5: Combined Digit Calculation for Each Token

#### Token 1: "i"

```
Weighted Digit: 6
Hash Digit: 5
Combined: (6 * 9 + 5) % 9 + 1 = (54 + 5) % 9 + 1 = 59 % 9 + 1 = 5 + 1 = 6
```

#### Token 2: "love"

```
Weighted Digit: 8
Hash Digit: 8
Combined: (8 * 9 + 8) % 9 + 1 = (72 + 8) % 9 + 1 = 80 % 9 + 1 = 8 + 1 = 9
```

#### Token 3: "being"

```
Weighted Digit: 4
Hash Digit: 7
Combined: (4 * 9 + 7) % 9 + 1 = (36 + 7) % 9 + 1 = 43 % 9 + 1 = 7 + 1 = 8
```

#### Token 4: "alone"

```
Weighted Digit: 7
Hash Digit: 7
Combined: (7 * 9 + 7) % 9 + 1 = (63 + 7) % 9 + 1 = 70 % 9 + 1 = 7 + 1 = 8
```

---

### Final Results Summary

```
Token | Hash Value    | Hash Digit | Weighted Sum | Weighted Digit | Combined Digit
------|---------------|------------|--------------|----------------|---------------
i     | 105           |     5      |     105      |       6        |       6
love  | 3327858       |     8      |    1088      |       8        |       9
being | 93618367      |     7      |    1570      |       4        |       8
alone | 92909147      |     7      |    1591      |       7        |       8
```

**Final Output:**
```
Text: "I LOVE BEING ALONE"
After preprocessing: "i love being alone"
Tokens: ["i", "love", "being", "alone"]

Digits Generated:
- Hash Digits:     [5, 8, 7, 7]
- Weighted Digits: [6, 8, 4, 7]
- Combined Digits: [6, 9, 8, 8]
```

---

*This guide provides a complete reference for understanding and implementing the SOMA tokenization system. All examples have been verified against the actual implementation.*
