# ✅ Correct SOMA Tokenizer Names

## ⚠️ Important: Use Lowercase and Correct Spelling

The API is case-sensitive and requires exact spelling. Use these names:

### ✅ Correct Names:
- `'word'` ✅
- `'char'` ✅
- `'space'` ✅
- `'grammar'` ✅ (not "grammer")
- `'subword'` ✅
- `'bpe'` ✅ (lowercase, not "BPE")
- `'syllable'` ✅
- `'frequency'` ✅
- `'byte'` ✅

### ❌ Common Mistakes:
- ❌ `'character'` → Use `'char'`
- ❌ `'whitespace'` → Use `'space'`
- ❌ `'grammer'` → Use `'grammar'`
- ❌ `'BPE'` → Use `'bpe'` (lowercase)
- ❌ `'Byte'` → Use `'byte'` (lowercase)

---

## Example Configuration:

```javascript
const config = {
  tokenizerTypes: ['word', 'char', 'space'],  // ✅ Correct
  // NOT: ['word', 'character', 'BPE']  // ❌ Wrong
};
```

---

## How to Check Available Tokenizers:

Run this command:
```powershell
curl.exe http://127.0.0.1:8000/
```

You'll see:
```json
{
  "message": "SOMA API is running!",
  "version": "1.0.0",
  "available_tokenizers": [
    "space",
    "word",
    "char",
    "grammar",
    "subword",
    "bpe",
    "syllable",
    "frequency",
    "byte"
  ]
}
```

---

**Always use the exact names from the API response!**

