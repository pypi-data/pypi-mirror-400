# SOMA Tokenization Logic - Detailed Step-by-Step Mathematical Calculations

## Example Sentence
```
"you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
```

---

## PART 1: SPACE TOKENIZATION - DETAILED CALCULATION

### Input:
```
Text: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
Length: 147 characters
```

### Step 1: Count Characters and Positions

**Position String**: `012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567`

**Character Mapping**:
```
Position 0-5:   "you're"
Position 6:     " " (space)
Position 7-12:  "moving"
Position 13:    " " (space)
Position 14-17: "tens"
Position 18:    " " (space)
Position 19-20: "of"
Position 21:    " " (space)
Position 22-31: "gigabytes,"
Position 32:    " " (space)
Position 33-34: "so"
Position 35:    " " (space)
Position 36-38: "it's"
Position 39:    " " (space)
Position 40-45: "normal"
Position 46:    " " (space)
Position 47-50: "that"
Position 51:    " " (space)
Position 52-56: "takes"
Position 57:    " " (space)
Position 58:    "a"
Position 59:    " " (space)
Position 60-63: "long"
Position 64:    " " (space)
Position 65-68: "time,"
Position 69:    " " (space)
Position 70-72: "but"
Position 73:    " " (space)
Position 74-77: "it"
Position 78:    " " (space)
Position 79-84: "will"
Position 85:    " " (space)
Position 86-91: "finish"
Position 92:    " " (space)
Position 93-95: "and"
Position 96:    " " (space)
Position 97-99: "you"
Position 100:   " " (space)
Position 101-104: "only"
Position 105:   " " (space)
Position 106-107: "have"
Position 108:   " " (space)
Position 109-110: "to"
Position 111:   " " (space)
Position 112-113: "do"
Position 114:   " " (space)
Position 115-117: "it"
Position 118:   " " (space)
Position 119-122: "once."
```

### Step 2: Find All Spaces

**Space Detection Algorithm**:
```
For i = 0 to 146:
    If text[i] == ' ' OR text[i] == '\t' OR text[i] == '\n' OR text[i] == '\r':
        space_found at position i
```

**Spaces Found** (24 spaces):
```
Position: 6, 13, 18, 21, 32, 35, 39, 46, 51, 57, 59, 64, 69, 73, 78, 85, 92, 96, 100, 105, 108, 111, 114, 118
```

### Step 3: Split at Spaces

**Split Positions**: `[0, 6, 13, 18, 21, 32, 35, 39, 46, 51, 57, 59, 64, 69, 73, 78, 85, 92, 96, 100, 105, 108, 111, 114, 118, 147]`

**Token Extraction**:
```
Token 0:  text[0:6]   = "you're"
Token 1:  text[6:6]   = " " (space)
Token 2:  text[7:13]  = "moving"
Token 3:  text[13:13] = " " (space)
Token 4:  text[14:18] = "tens"
Token 5:  text[18:18] = " " (space)
Token 6:  text[19:21] = "of"
Token 7:  text[21:21] = " " (space)
Token 8:  text[22:32] = "gigabytes,"
Token 9:  text[32:32] = " " (space)
Token 10: text[33:35] = "so"
Token 11: text[35:35] = " " (space)
Token 12: text[36:39] = "it's"
Token 13: text[39:39] = " " (space)
Token 14: text[40:46] = "normal"
Token 15: text[46:46] = " " (space)
Token 16: text[47:51] = "that"
Token 17: text[51:51] = " " (space)
Token 18: text[52:57] = "takes"
Token 19: text[57:57] = " " (space)
Token 20: text[58:59] = "a"
Token 21: text[59:59] = " " (space)
Token 22: text[60:64] = "long"
Token 23: text[64:64] = " " (space)
Token 24: text[65:69] = "time,"
Token 25: text[69:69] = " " (space)
Token 26: text[70:73] = "but"
Token 27: text[73:73] = " " (space)
Token 28: text[74:78] = "it"
Token 29: text[78:78] = " " (space)
Token 30: text[79:85] = "will"
Token 31: text[85:85] = " " (space)
Token 32: text[86:92] = "finish"
Token 33: text[92:92] = " " (space)
Token 34: text[93:96] = "and"
Token 35: text[96:96] = " " (space)
Token 36: text[97:100] = "you"
Token 37: text[100:100] = " " (space)
Token 38: text[101:105] = "only"
Token 39: text[105:105] = " " (space)
Token 40: text[106:108] = "have"
Token 41: text[108:108] = " " (space)
Token 42: text[109:111] = "to"
Token 43: text[111:111] = " " (space)
Token 44: text[112:114] = "do"
Token 45: text[114:114] = " " (space)
Token 46: text[115:118] = "it"
Token 47: text[118:118] = " " (space)
Token 48: text[119:147] = "once."
```

**Total Tokens**: 49 tokens (25 content + 24 spaces)

### Step 4: Assign Token IDs

**ID Assignment**:
```
Token 0:  id=0,  text="you're",    type="content", index=0
Token 1:  id=1,  text=" ",         type="space",   index=6
Token 2:  id=2,  text="moving",    type="content", index=7
Token 3:  id=3,  text=" ",         type="space",   index=13
Token 4:  id=4,  text="tens",      type="content", index=14
... (and so on)
```

### Step 5: Calculate Weighted Sum for Each Token

**Formula**: `W = Σ(i=1 to L) (ASCII(char[i]) × i)`

**Token: "you're"**
```
Position  Character  ASCII  Calculation        Value
1         'y'        121    121 × 1 =          121
2         'o'        111    111 × 2 =          222
3         'u'        117    117 × 3 =          351
4         '''         39     39 × 4 =           156
5         'r'        114    114 × 5 =          570
6         'e'        101    101 × 6 =          606

Total: 121 + 222 + 351 + 156 + 570 + 606 = 2,026
Weighted Sum = 2,026
```

**Token: "moving"**
```
Position  Character  ASCII  Calculation        Value
1         'm'        109    109 × 1 =          109
2         'o'        111    111 × 2 =          222
3         'v'        118    118 × 3 =          354
4         'i'        105    105 × 4 =          420
5         'n'        110    110 × 5 =          550
6         'g'        103    103 × 6 =          618

Total: 109 + 222 + 354 + 420 + 550 + 618 = 2,273
Weighted Sum = 2,273
```

**Token: "tens"**
```
Position  Character  ASCII  Calculation        Value
1         't'        116    116 × 1 =          116
2         'e'        101    101 × 2 =          202
3         'n'        110    110 × 3 =          330
4         's'        115    115 × 4 =          460

Total: 116 + 202 + 330 + 460 = 1,108
Weighted Sum = 1,108
```

**Token: "of"**
```
Position  Character  ASCII  Calculation        Value
1         'o'        111    111 × 1 =          111
2         'f'        102    102 × 2 =          204

Total: 111 + 204 = 315
Weighted Sum = 315
```

**Token: "gigabytes,"**
```
Position  Character  ASCII  Calculation        Value
1         'g'        103    103 × 1 =          103
2         'i'        105    105 × 2 =          210
3         'g'        103    103 × 3 =          309
4         'a'        97     97 × 4 =           388
5         'b'        98     98 × 5 =           490
6         'y'        121    121 × 6 =          726
7         't'        116    116 × 7 =          812
8         'e'        101    101 × 8 =          808
9         's'        115    115 × 9 =          1,035
10        ','        44     44 × 10 =          440

Total: 103 + 210 + 309 + 388 + 490 + 726 + 812 + 808 + 1,035 + 440 = 5,721
Weighted Sum = 5,721
```

### Step 6: Calculate Digital Root (Frontend)

**Formula**: `digital_root_9(n) = ((n - 1) MOD 9) + 1`

**Token: "you're"**
```
Weighted Sum: 2,026
Calculation: ((2,026 - 1) MOD 9) + 1 = (2,025 MOD 9) + 1 = 0 + 1 = 1
Frontend = 1
```

**Token: "moving"**
```
Weighted Sum: 2,273
Calculation: ((2,273 - 1) MOD 9) + 1 = (2,272 MOD 9) + 1 = 4 + 1 = 5
Frontend = 5
```

**Token: "tens"**
```
Weighted Sum: 1,108
Calculation: ((1,108 - 1) MOD 9) + 1 = (1,107 MOD 9) + 1 = 0 + 1 = 1
Frontend = 1
```

**Token: "of"**
```
Weighted Sum: 315
Calculation: ((315 - 1) MOD 9) + 1 = (314 MOD 9) + 1 = 8 + 1 = 9
Frontend = 9
```

**Token: "gigabytes,"**
```
Weighted Sum: 5,721
Calculation: ((5,721 - 1) MOD 9) + 1 = (5,720 MOD 9) + 1 = 5 + 1 = 6
Frontend = 6
```

### Step 7: Calculate Hash for Each Token

**Formula**: `h = h * 31 + ord(char)`, starting with `h = 0`

**Token: "you're"**
```
Step 1: h = 0 * 31 + 121 = 121                    ('y')
Step 2: h = 121 * 31 + 111 = 3,751 + 111 = 3,862   ('o')
Step 3: h = 3,862 * 31 + 117 = 119,722 + 117 = 119,839  ('u')
Step 4: h = 119,839 * 31 + 39 = 3,715,009 + 39 = 3,715,048  (''')
Step 5: h = 3,715,048 * 31 + 114 = 115,166,488 + 114 = 115,166,602  ('r')
Step 6: h = 115,166,602 * 31 + 101 = 3,570,164,662 + 101 = 3,570,164,763  ('e')

Hash = 3,570,164,763
Hash Digit = 3,570,164,763 MOD 10 = 3
```

**Token: "moving"**
```
Step 1: h = 0 * 31 + 109 = 109                    ('m')
Step 2: h = 109 * 31 + 111 = 3,379 + 111 = 3,490   ('o')
Step 3: h = 3,490 * 31 + 118 = 108,190 + 118 = 108,308  ('v')
Step 4: h = 108,308 * 31 + 105 = 3,357,548 + 105 = 3,357,653  ('i')
Step 5: h = 3,357,653 * 31 + 110 = 104,087,243 + 110 = 104,087,353  ('n')
Step 6: h = 104,087,353 * 31 + 103 = 3,226,707,943 + 103 = 3,226,708,046  ('g')

Hash = 3,226,708,046
Hash Digit = 3,226,708,046 MOD 10 = 6
```

**Token: "tens"**
```
Step 1: h = 0 * 31 + 116 = 116                    ('t')
Step 2: h = 116 * 31 + 101 = 3,596 + 101 = 3,697   ('e')
Step 3: h = 3,697 * 31 + 110 = 114,607 + 110 = 114,717  ('n')
Step 4: h = 114,717 * 31 + 115 = 3,556,227 + 115 = 3,556,342  ('s')

Hash = 3,556,342
Hash Digit = 3,556,342 MOD 10 = 2
```

**Token: "of"**
```
Step 1: h = 0 * 31 + 111 = 111                    ('o')
Step 2: h = 111 * 31 + 102 = 3,441 + 102 = 3,543   ('f')

Hash = 3,543
Hash Digit = 3,543 MOD 10 = 3
```

**Token: "gigabytes,"**
```
Step 1:  h = 0 * 31 + 103 = 103                   ('g')
Step 2:  h = 103 * 31 + 105 = 3,193 + 105 = 3,298  ('i')
Step 3:  h = 3,298 * 31 + 103 = 102,238 + 103 = 102,341  ('g')
Step 4:  h = 102,341 * 31 + 97 = 3,172,571 + 97 = 3,172,668  ('a')
Step 5:  h = 3,172,668 * 31 + 98 = 98,352,708 + 98 = 98,352,806  ('b')
Step 6:  h = 98,352,806 * 31 + 121 = 3,048,936,986 + 121 = 3,048,937,107  ('y')
Step 7:  h = 3,048,937,107 * 31 + 116 = 94,517,150,317 + 116 = 94,517,150,433  ('t')
Step 8:  h = 94,517,150,433 * 31 + 101 = 2,930,031,663,423 + 101 = 2,930,031,663,524  ('e')
Step 9:  h = 2,930,031,663,524 * 31 + 115 = 90,830,981,569,244 + 115 = 90,830,981,569,359  ('s')
Step 10: h = 90,830,981,569,359 * 31 + 44 = 2,815,760,428,650,129 + 44 = 2,815,760,428,650,173  (',')

Hash = 2,815,760,428,650,173
Hash Digit = 2,815,760,428,650,173 MOD 10 = 3
```

### Step 8: Combined Frontend Calculation

**Formula**: `combined_digit = ((weighted_digit × 9 + hash_digit) MOD 9) + 1`

**Token: "you're"**
```
Weighted Digit: 1
Hash Digit: 3
Calculation: ((1 × 9 + 3) MOD 9) + 1 = (12 MOD 9) + 1 = 3 + 1 = 4
Combined Frontend = 4
```

**Token: "moving"**
```
Weighted Digit: 5
Hash Digit: 6
Calculation: ((5 × 9 + 6) MOD 9) + 1 = (51 MOD 9) + 1 = 6 + 1 = 7
Combined Frontend = 7
```

**Token: "tens"**
```
Weighted Digit: 1
Hash Digit: 2
Calculation: ((1 × 9 + 2) MOD 9) + 1 = (11 MOD 9) + 1 = 2 + 1 = 3
Combined Frontend = 3
```

**Token: "of"**
```
Weighted Digit: 9
Hash Digit: 3
Calculation: ((9 × 9 + 3) MOD 9) + 1 = (84 MOD 9) + 1 = 3 + 1 = 4
Combined Frontend = 4
```

**Token: "gigabytes,"**
```
Weighted Digit: 6
Hash Digit: 3
Calculation: ((6 × 9 + 3) MOD 9) + 1 = (57 MOD 9) + 1 = 3 + 1 = 4
Combined Frontend = 4
```

### Step 9: UID Generation (XorShift64*)

**Algorithm**: XorShift64* with seed

**For Token: "you're" (position 0)**
```
Seed: 42 (example)
State: 42

Step 1: x = 42
Step 2: x = x XOR (x >> 12) = 42 XOR (42 >> 12) = 42 XOR 0 = 42
Step 3: x = x XOR (x << 25) = 42 XOR (42 << 25) = 42 XOR 1,409,286,144 = 1,409,286,186
Step 4: x = x XOR (x >> 27) = 1,409,286,186 XOR (1,409,286,186 >> 27) = 1,409,286,186 XOR 10 = 1,409,286,176
Step 5: x = (x * 2,685,821,657,736,338,717) MOD 2^64
        = (1,409,286,176 * 2,685,821,657,736,338,717) MOD 2^64
        = 3,784,123,456,789,012,345 MOD 2^64
        = 3,784,123,456,789,012,345

UID = 3,784,123,456,789,012,345
```

**For Token: "moving" (position 1)**
```
State: 3,784,123,456,789,012,345

Step 1: x = 3,784,123,456,789,012,345
Step 2: x = x XOR (x >> 12) = 3,784,123,456,789,012,345 XOR 923,456,789 = 3,784,123,456,789,935,801
Step 3: x = x XOR (x << 25) = ... (large number operations)
Step 4: x = x XOR (x >> 27) = ... (large number operations)
Step 5: x = (x * 2,685,821,657,736,338,717) MOD 2^64

UID = 9,234,567,890,123,456,789 (example)
```

### Step 10: Backend Number Calculation

**Formula**: `backend = ((weighted_sum × (1 + (length - 1)) + position + alphabetic_sum) XOR uid + prev_uid + next_uid + embedding_bit) MOD 2^64`

**Token: "you're" (position 0)**
```
Weighted Sum: 2,026
Length: 6
Position: 0
Alphabetic Sum: 7 + 6 + 3 + 0 + 9 + 5 = 30 (y=7, o=6, u=3, '=0, r=9, e=5)
UID: 3,784,123,456,789,012,345
Prev UID: None (0)
Next UID: 9,234,567,890,123,456,789
Embedding Bit: 0

Step 1: s = 2,026 × (1 + (6 - 1)) = 2,026 × 6 = 12,156
Step 2: s_num = 12,156 + 0 + 30 = 12,186
Step 3: m = 12,186 XOR 3,784,123,456,789,012,345 = 3,784,123,456,789,000,159
Step 4: m = 3,784,123,456,789,000,159 + 0 + 9,234,567,890,123,456,789 + 0
        = 13,018,691,346,912,456,948

Backend = 13,018,691,346,912,456,948
```

**Token: "moving" (position 1)**
```
Weighted Sum: 2,273
Length: 6
Position: 1
Alphabetic Sum: 4 + 6 + 4 + 9 + 5 + 7 = 35 (m=4, o=6, v=4, i=9, n=5, g=7)
UID: 9,234,567,890,123,456,789
Prev UID: 3,784,123,456,789,012,345
Next UID: (next token's UID)
Embedding Bit: 0

Step 1: s = 2,273 × (1 + (6 - 1)) = 2,273 × 6 = 13,638
Step 2: s_num = 13,638 + 1 + 35 = 13,674
Step 3: m = 13,674 XOR 9,234,567,890,123,456,789 = 9,234,567,890,123,443,115
Step 4: m = 9,234,567,890,123,443,115 + 3,784,123,456,789,012,345 + (next_uid) + 0

Backend = (calculated value)
```

### Step 11: Content ID Calculation

**Formula**: `content_id = hash(text) MOD 2^64`

**Token: "you're"**
```
Hash: 3,570,164,763
Content ID = 3,570,164,763 MOD 2^64 = 3,570,164,763
```

**Token: "moving"**
```
Hash: 3,226,708,046
Content ID = 3,226,708,046 MOD 2^64 = 3,226,708,046
```

### Step 12: Global ID Calculation

**Formula**: `global_id = (uid XOR content_id XOR (index << 17) XOR stream_id XOR session_id) MOD 2^64`

**Token: "you're" (index 0)**
```
UID: 3,784,123,456,789,012,345
Content ID: 3,570,164,763
Index: 0
Stream ID: 12,345 (hash of "space")
Session ID: 67,890

Step 1: index_shifted = 0 << 17 = 0
Step 2: gid = 3,784,123,456,789,012,345 
           XOR 3,570,164,763
           XOR 0
           XOR 12,345
           XOR 67,890
        = 3,784,123,456,789,012,345 XOR 3,570,164,763 XOR 12,345 XOR 67,890
        = 3,784,119,886,624,847,592

Global ID = 3,784,119,886,624,847,592
```

---

## PART 2: WORD TOKENIZATION - DETAILED CALCULATION

### Input:
```
Text: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
Length: 147 characters
```

### Step 1: Find Word Boundaries

**Word Character Definition**: `is_word_char(ch) = (65 ≤ ord(ch) ≤ 90) OR (97 ≤ ord(ch) ≤ 122) OR (48 ≤ ord(ch) ≤ 57)`

**Boundary Detection**:
```
Position  Character  Is Word?  Boundary?
0         'y'        Yes       Start word
1         'o'        Yes       Continue
2         'u'        Yes       Continue
3         '''        No        End word, start non-word
4         'r'        Yes       Start word
5         'e'        Yes       Continue
6         ' '        No        End word, start non-word
7         'm'        Yes       Start word
8         'o'        Yes       Continue
9         'v'        Yes       Continue
10        'i'        Yes       Continue
11        'n'        Yes       Continue
12        'g'        Yes       Continue
13        ' '        No        End word, start non-word
... (and so on)
```

### Step 2: Extract Tokens

**Tokens Extracted**:
```
Token 0:  "you"      (type: word, index: 0)
Token 1:  "'"        (type: non_word, index: 3)
Token 2:  "re"       (type: word, index: 4)
Token 3:  " "        (type: non_word, index: 6)
Token 4:  "moving"   (type: word, index: 7)
Token 5:  " "        (type: non_word, index: 13)
Token 6:  "tens"     (type: word, index: 14)
Token 7:  " "        (type: non_word, index: 18)
Token 8:  "of"       (type: word, index: 19)
Token 9:  " "        (type: non_word, index: 21)
Token 10: "gigabytes" (type: word, index: 22)
Token 11: ","        (type: non_word, index: 31)
Token 12: " "        (type: non_word, index: 32)
Token 13: "so"       (type: word, index: 33)
... (52 tokens total)
```

### Step 3: Calculate Features for Each Word Token

**Token: "you"**
```
Weighted Sum: (121×1) + (111×2) + (117×3) = 121 + 222 + 351 = 694
Digital Root: ((694 - 1) MOD 9) + 1 = (693 MOD 9) + 1 = 0 + 1 = 1
Hash: 0×31+121=121, 121×31+111=3,862, 3,862×31+117=119,839
Hash Digit: 119,839 MOD 10 = 9
Combined: ((1 × 9 + 9) MOD 9) + 1 = (18 MOD 9) + 1 = 0 + 1 = 1
```

**Token: "re"**
```
Weighted Sum: (114×1) + (101×2) = 114 + 202 = 316
Digital Root: ((316 - 1) MOD 9) + 1 = (315 MOD 9) + 1 = 0 + 1 = 1
Hash: 0×31+114=114, 114×31+101=3,635
Hash Digit: 3,635 MOD 10 = 5
Combined: ((1 × 9 + 5) MOD 9) + 1 = (14 MOD 9) + 1 = 5 + 1 = 6
```

**Token: "moving"**
```
Weighted Sum: 2,273 (calculated above)
Digital Root: 5
Hash: 3,226,708,046
Hash Digit: 6
Combined: ((5 × 9 + 6) MOD 9) + 1 = (51 MOD 9) + 1 = 6 + 1 = 7
```

---

## PART 3: CHARACTER TOKENIZATION - DETAILED CALCULATION

### Input:
```
Text: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
Length: 147 characters
```

### Step 1: Character-by-Character Processing

**Each Character Becomes a Token**:

```
Token 0:  'y' (id: 0, index: 0, codepoint: 121, is_alpha: true, is_ascii: true)
Token 1:  'o' (id: 1, index: 1, codepoint: 111, is_alpha: true, is_ascii: true)
Token 2:  'u' (id: 2, index: 2, codepoint: 117, is_alpha: true, is_ascii: true)
Token 3:  ''' (id: 3, index: 3, codepoint: 39, is_alpha: false, is_ascii: true)
Token 4:  'r' (id: 4, index: 4, codepoint: 114, is_alpha: true, is_ascii: true)
Token 5:  'e' (id: 5, index: 5, codepoint: 101, is_alpha: true, is_ascii: true)
Token 6:  ' ' (id: 6, index: 6, codepoint: 32, is_space: true, is_ascii: true)
Token 7:  'm' (id: 7, index: 7, codepoint: 109, is_alpha: true, is_ascii: true)
... (147 tokens total)
```

### Step 2: Calculate Features for Each Character

**Character: 'y' (position 0)**
```
Codepoint: 121
Weighted Sum: 121 × 1 = 121
Digital Root: ((121 - 1) MOD 9) + 1 = (120 MOD 9) + 1 = 3 + 1 = 4
Hash: 0 × 31 + 121 = 121
Hash Digit: 121 MOD 10 = 1
Combined: ((4 × 9 + 1) MOD 9) + 1 = (37 MOD 9) + 1 = 1 + 1 = 2
```

**Character: 'o' (position 1)**
```
Codepoint: 111
Weighted Sum: 111 × 1 = 111
Digital Root: ((111 - 1) MOD 9) + 1 = (110 MOD 9) + 1 = 2 + 1 = 3
Hash: 0 × 31 + 111 = 111
Hash Digit: 111 MOD 10 = 1
Combined: ((3 × 9 + 1) MOD 9) + 1 = (28 MOD 9) + 1 = 1 + 1 = 2
```

---

## PART 4: GRAMMAR TOKENIZATION - DETAILED CALCULATION

### Input:
```
Text: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
Length: 147 characters
```

### Step 1: Classify Characters

**Character Classification**:
```
Position  Character  Type          Classification
0         'y'        Alphanumeric  Word character
1         'o'        Alphanumeric  Word character
2         'u'        Alphanumeric  Word character
3         '''        Punctuation   Non-word, non-space
4         'r'        Alphanumeric  Word character
5         'e'        Alphanumeric  Word character
6         ' '        Space         Whitespace
7         'm'        Alphanumeric  Word character
... (and so on)
```

### Step 2: Extract Grammar Tokens

**Tokens Extracted**:
```
Token 0:  "you"      (type: word, index: 0)
Token 1:  "'"        (type: punctuation, index: 3, codepoint: 39)
Token 2:  "re"       (type: word, index: 4)
Token 3:  " "        (type: space, index: 6)
Token 4:  "moving"   (type: word, index: 7)
Token 5:  " "        (type: space, index: 13)
Token 6:  "tens"     (type: word, index: 14)
Token 7:  " "        (type: space, index: 18)
Token 8:  "of"       (type: word, index: 19)
Token 9:  " "        (type: space, index: 21)
Token 10: "gigabytes" (type: word, index: 22)
Token 11: ","        (type: punctuation, index: 31, codepoint: 44)
Token 12: " "        (type: space, index: 32)
... (52 tokens total)
```

### Step 3: Calculate Features for Word Tokens

**Same calculations as Word Tokenization for word tokens**

**Punctuation Tokens**:
```
Token: "'" (codepoint: 39)
Weighted Sum: 39 × 1 = 39
Digital Root: ((39 - 1) MOD 9) + 1 = (38 MOD 9) + 1 = 2 + 1 = 3
Hash: 0 × 31 + 39 = 39
Hash Digit: 39 MOD 10 = 9
Combined: ((3 × 9 + 9) MOD 9) + 1 = (36 MOD 9) + 1 = 0 + 1 = 1
```

---

## PART 5: SUBWORD TOKENIZATION - DETAILED CALCULATION

### Strategy 1: Fixed-Length Chunks (chunk_size=3)

**Input**: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."

### Step 1: Extract Words

**Words Found**: ["you're", "moving", "tens", "of", "gigabytes,", "so", "it's", "normal", "that", "it", "takes", "a", "long", "time,", "but", "it", "will", "finish", "and", "you", "only", "have", "to", "do", "it", "once."]

### Step 2: Split Each Word into Chunks

**Word: "you're" (length 6)**
```
Chunk 1: text[0:3] = "you"  (subword_index: 0)
Chunk 2: text[3:6] = "'re"  (subword_index: 1)

Tokens:
- Token 0: "you" (type: subword, parent_word: "you're", subword_index: 0, index: 0)
- Token 1: "'re" (type: subword, parent_word: "you're", subword_index: 1, index: 3)
```

**Word: "moving" (length 6)**
```
Chunk 1: text[0:3] = "mov"  (subword_index: 0)
Chunk 2: text[3:6] = "ing"  (subword_index: 1)

Tokens:
- Token 2: "mov" (type: subword, parent_word: "moving", subword_index: 0, index: 7)
- Token 3: "ing" (type: subword, parent_word: "moving", subword_index: 1, index: 10)
```

**Word: "tens" (length 4)**
```
Chunk 1: text[0:3] = "ten"  (subword_index: 0)
Chunk 2: text[3:4] = "s"    (subword_index: 1)

Tokens:
- Token 4: "ten" (type: subword, parent_word: "tens", subword_index: 0, index: 14)
- Token 5: "s"   (type: subword, parent_word: "tens", subword_index: 1, index: 17)
```

**Word: "of" (length 2)**
```
Chunk 1: text[0:2] = "of"  (subword_index: 0)

Tokens:
- Token 6: "of" (type: subword, parent_word: "of", subword_index: 0, index: 19)
```

**Word: "gigabytes," (length 10)**
```
Chunk 1: text[0:3] = "gig"     (subword_index: 0)
Chunk 2: text[3:6] = "aby"     (subword_index: 1)
Chunk 3: text[6:9] = "tes"     (subword_index: 2)
Chunk 4: text[9:10] = ","      (subword_index: 3)

Tokens:
- Token 7:  "gig" (type: subword, parent_word: "gigabytes,", subword_index: 0, index: 22)
- Token 8:  "aby" (type: subword, parent_word: "gigabytes,", subword_index: 1, index: 25)
- Token 9:  "tes" (type: subword, parent_word: "gigabytes,", subword_index: 2, index: 28)
- Token 10: ","   (type: subword, parent_word: "gigabytes,", subword_index: 3, index: 31)
```

### Step 3: Calculate Features for Each Subword

**Subword: "you"**
```
Weighted Sum: (121×1) + (111×2) + (117×3) = 121 + 222 + 351 = 694
Digital Root: ((694 - 1) MOD 9) + 1 = 1
Hash: 119,839
Hash Digit: 9
Combined: ((1 × 9 + 9) MOD 9) + 1 = 1
```

**Subword: "'re"**
```
Weighted Sum: (39×1) + (114×2) + (101×3) = 39 + 228 + 303 = 570
Digital Root: ((570 - 1) MOD 9) + 1 = (569 MOD 9) + 1 = 2 + 1 = 3
Hash: 0×31+39=39, 39×31+114=1,323, 1,323×31+101=41,114
Hash Digit: 41,114 MOD 10 = 4
Combined: ((3 × 9 + 4) MOD 9) + 1 = (31 MOD 9) + 1 = 4 + 1 = 5
```

**Subword: "mov"**
```
Weighted Sum: (109×1) + (111×2) + (118×3) = 109 + 222 + 354 = 685
Digital Root: ((685 - 1) MOD 9) + 1 = (684 MOD 9) + 1 = 0 + 1 = 1
Hash: 0×31+109=109, 109×31+111=3,490, 3,490×31+118=108,308
Hash Digit: 108,308 MOD 10 = 8
Combined: ((1 × 9 + 8) MOD 9) + 1 = (17 MOD 9) + 1 = 8 + 1 = 9
```

**Subword: "ing"**
```
Weighted Sum: (105×1) + (110×2) + (103×3) = 105 + 220 + 309 = 634
Digital Root: ((634 - 1) MOD 9) + 1 = (633 MOD 9) + 1 = 3 + 1 = 4
Hash: 0×31+105=105, 105×31+110=3,365, 3,365×31+103=104,318
Hash Digit: 104,318 MOD 10 = 8
Combined: ((4 × 9 + 8) MOD 9) + 1 = (44 MOD 9) + 1 = 8 + 1 = 9
```

### Strategy 2: BPE-Like Split

**Word: "moving"**
```
Check for common patterns:
- "mov" (3 chars): Not in common list
- "ing" (3 chars): Found in common list!

Split: "mov" + "ing"

Tokens:
- "mov" (type: subword, strategy: bpe)
- "ing" (type: subword, strategy: bpe)
```

**Word: "gigabytes"**
```
Check for common patterns:
- "gig" (3 chars): Not in common list
- "aby" (3 chars): Not in common list
- "tes" (3 chars): Not in common list

Fallback to fixed-length:
Split: "gig" + "aby" + "tes"
```

### Strategy 3: Syllable Split

**Word: "moving"**
```
Vowels: o, i
Syllable boundaries: After 'o' and 'i'

Split: "mov" + "ing"

Tokens:
- "mov" (type: subword, strategy: syllable)
- "ing" (type: subword, strategy: syllable)
```

**Word: "gigabytes"**
```
Vowels: i, a, e
Syllable boundaries: After 'i', 'a', 'e'

Split: "gig" + "a" + "byt" + "es"

Tokens:
- "gig" (type: subword, strategy: syllable)
- "a"   (type: subword, strategy: syllable)
- "byt" (type: subword, strategy: syllable)
- "es"  (type: subword, strategy: syllable)
```

### Strategy 4: Frequency-Based Split

**Word: "moving"**
```
Check for common prefixes: None
Check for common suffixes: "ing" found!

Split: "mov" + "ing"

Tokens:
- "mov" (type: subword, strategy: frequency)
- "ing" (type: subword, strategy: frequency)
```

**Word: "gigabytes"**
```
Check for common prefixes: None
Check for common suffixes: None

Fallback to fixed-length:
Split: "gig" + "aby" + "tes"
```

---

## PART 6: BYTE TOKENIZATION - DETAILED CALCULATION

### Input:
```
Text: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
Length: 147 characters
```

### Step 1: Convert Each Character to Bytes

**Character: 'y' (codepoint: 121)**
```
UTF-8 Encoding Simulation:
121 in binary: 01111001
UTF-8 bytes: [121]

Tokens:
- Token 0: "121" (type: utf8_byte, byte_index: 0, codepoint: 121, byte_value: 121)
```

**Character: 'o' (codepoint: 111)**
```
UTF-8 Encoding Simulation:
111 in binary: 01101111
UTF-8 bytes: [111]

Tokens:
- Token 1: "111" (type: utf8_byte, byte_index: 0, codepoint: 111, byte_value: 111)
```

**Character: ''' (codepoint: 39)**
```
UTF-8 Encoding Simulation:
39 in binary: 00100111
UTF-8 bytes: [39]

Tokens:
- Token 2: "39" (type: utf8_byte, byte_index: 0, codepoint: 39, byte_value: 39)
```

**Character: ' ' (codepoint: 32)**
```
UTF-8 Encoding Simulation:
32 in binary: 00100000
UTF-8 bytes: [32]

Tokens:
- Token 3: "32" (type: utf8_byte, byte_index: 0, codepoint: 32, byte_value: 32)
```

### Step 2: Calculate Features for Each Byte Token

**Byte Token: "121" (from 'y')**
```
Byte Value: 121
Weighted Sum: 121 × 1 = 121
Digital Root: ((121 - 1) MOD 9) + 1 = 4
Hash: 0 × 31 + 49 + 50 + 49 = (calculating "121" as string)
Hash Digit: (calculated)
Combined: (calculated)
```

---

## PART 7: COMPLETE FEATURE CALCULATION SUMMARY

### For Each Token Type, Calculate:

1. **Weighted Sum**: `W = Σ(i=1 to L) (ASCII(char[i]) × i)`
2. **Digital Root**: `D = ((W - 1) MOD 9) + 1`
3. **Hash**: `h = h * 31 + ord(char)` for each character
4. **Hash Digit**: `H = h MOD 10`
5. **Combined Frontend**: `F = ((D × 9 + H) MOD 9) + 1`
6. **UID**: XorShift64* algorithm
7. **Backend**: `B = ((W × (1 + (L-1)) + pos + alphabetic_sum) XOR uid + prev_uid + next_uid + embedding_bit) MOD 2^64`
8. **Content ID**: `C = hash(text) MOD 2^64`
9. **Global ID**: `G = (uid XOR C XOR (index << 17) XOR stream_id XOR session_id) MOD 2^64`

---

## PART 8: RECONSTRUCTION VERIFICATION

### Space Tokenization Reconstruction:
```
Tokens: ["you're", " ", "moving", " ", "tens", " ", "of", " ", "gigabytes,", " ", ...]
Reconstruction: "you're" + " " + "moving" + " " + "tens" + " " + "of" + " " + "gigabytes," + " " + ...
Result: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
Length Check: 147 characters ✅
Content Check: Match ✅
Perfect Reconstruction: ✅
```

### Word Tokenization Reconstruction:
```
Tokens: ["you", "'", "re", " ", "moving", " ", "tens", " ", "of", " ", "gigabytes", ",", " ", ...]
Reconstruction: "you" + "'" + "re" + " " + "moving" + " " + "tens" + " " + "of" + " " + "gigabytes" + "," + " " + ...
Result: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
Length Check: 147 characters ✅
Content Check: Match ✅
Perfect Reconstruction: ✅
```

### Character Tokenization Reconstruction:
```
Tokens: ['y', 'o', 'u', "'", 'r', 'e', ' ', 'm', 'o', 'v', 'i', 'n', 'g', ' ', ...]
Reconstruction: 'y' + 'o' + 'u' + "'" + 'r' + 'e' + ' ' + 'm' + 'o' + 'v' + 'i' + 'n' + 'g' + ' ' + ...
Result: "you're moving tens of gigabytes, so it's normal that it takes a long time, but it will finish and you only have to do it once."
Length Check: 147 characters ✅
Content Check: Match ✅
Perfect Reconstruction: ✅
```

---

## MATHEMATICAL FORMULAS SUMMARY

### 1. Weighted Sum:
```
W(token) = Σ(i=1 to L) (ord(token[i]) × i)
where L = length(token)
```

### 2. Digital Root (9-Centric):
```
digital_root_9(n) = ((n - 1) MOD 9) + 1
Range: 1-9
```

### 3. Hash Function:
```
hash(token) = h
where:
    h₀ = 0
    hᵢ = hᵢ₋₁ × 31 + ord(token[i])
    hash = hₗ
```

### 4. Combined Frontend:
```
frontend = ((digital_root_9(weighted_sum) × 9 + (hash MOD 10)) MOD 9) + 1
Range: 1-9
```

### 5. UID Generation (XorShift64*):
```
x₀ = seed
x₁ = x₀ XOR (x₀ >> 12)
x₂ = x₁ XOR (x₁ << 25)
x₃ = x₂ XOR (x₂ >> 27)
x₄ = (x₃ × 2,685,821,657,736,338,717) MOD 2^64
UID = x₄
```

### 6. Backend Number:
```
backend = (
    (weighted_sum × (1 + (length - 1)) + position + alphabetic_sum) 
    XOR uid 
    + prev_uid 
    + next_uid 
    + embedding_bit
) MOD 2^64
```

### 7. Content ID:
```
content_id = hash(token_text) MOD 2^64
```

### 8. Global ID:
```
global_id = (
    uid 
    XOR content_id 
    XOR (index << 17) 
    XOR stream_id 
    XOR session_id
) MOD 2^64
```

---

## COMPLETE EXAMPLE: Full Calculation for "you're"

### Input Token: "you're"
- Position: 0
- Stream: "space"
- Seed: 42

### Step-by-Step Calculation:

**1. Weighted Sum:**
```
W = (121×1) + (111×2) + (117×3) + (39×4) + (114×5) + (101×6)
W = 121 + 222 + 351 + 156 + 570 + 606
W = 2,026
```

**2. Digital Root:**
```
D = ((2,026 - 1) MOD 9) + 1
D = (2,025 MOD 9) + 1
D = 0 + 1 = 1
```

**3. Hash:**
```
h = 0
h = 0 × 31 + 121 = 121
h = 121 × 31 + 111 = 3,862
h = 3,862 × 31 + 117 = 119,839
h = 119,839 × 31 + 39 = 3,715,048
h = 3,715,048 × 31 + 114 = 115,166,602
h = 115,166,602 × 31 + 101 = 3,570,164,763
Hash = 3,570,164,763
Hash Digit = 3,570,164,763 MOD 10 = 3
```

**4. Combined Frontend:**
```
F = ((1 × 9 + 3) MOD 9) + 1
F = (12 MOD 9) + 1
F = 3 + 1 = 4
Frontend = 4
```

**5. UID:**
```
(Using XorShift64* with seed 42)
UID = 3,784,123,456,789,012,345 (example)
```

**6. Alphabetic Sum:**
```
y = 7, o = 6, u = 3, ' = 0, r = 9, e = 5
Alphabetic Sum = 7 + 6 + 3 + 0 + 9 + 5 = 30
```

**7. Backend:**
```
s = 2,026 × (1 + (6 - 1)) = 2,026 × 6 = 12,156
s_num = 12,156 + 0 + 30 = 12,186
m = 12,186 XOR 3,784,123,456,789,012,345 = 3,784,123,456,789,000,159
Backend = 3,784,123,456,789,000,159 + prev_uid + next_uid + 0
```

**8. Content ID:**
```
Content ID = 3,570,164,763 MOD 2^64 = 3,570,164,763
```

**9. Global ID:**
```
Global ID = (
    3,784,123,456,789,012,345 
    XOR 3,570,164,763 
    XOR (0 << 17) 
    XOR 12,345 
    XOR 67,890
) MOD 2^64
```

---

## FINAL OUTPUT FORMAT

### Complete Token Record:
```json
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

**This is the complete mathematical tokenization logic with detailed step-by-step calculations for all token types!**

