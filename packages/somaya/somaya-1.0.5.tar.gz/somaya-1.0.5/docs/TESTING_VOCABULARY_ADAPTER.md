# Testing Vocabulary Adapter in Backend

This guide shows you how to test the vocabulary adapter integration in the SOMA backend.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install transformers
   ```

2. **Start the backend server:**
   ```bash
   python src/servers/main_server.py
   ```
   
   The server will start at `http://localhost:8000`

## Testing Methods

### Method 1: Interactive API Documentation (Easiest)

1. Open your browser and go to: `http://localhost:8000/docs`
2. Find the `/test/vocabulary-adapter` endpoint
3. Click "Try it out"
4. Enter your test data (or use defaults)
5. Click "Execute"

**Quick Test:**
- Go to `/test/vocabulary-adapter/quick` endpoint
- Click "Try it out" → "Execute"
- No parameters needed!

### Method 2: Python Test Script

Run the comprehensive test script:

```bash
python tests/test_vocabulary_adapter_backend.py
```

This script will:
- ✅ Check if server is running
- ✅ Test quick endpoint
- ✅ Test custom requests
- ✅ Compare different models
- ✅ Show usage instructions

### Method 3: curl (Command Line)

**Quick Test:**
```bash
curl http://localhost:8000/test/vocabulary-adapter/quick
```

**Custom Test:**
```bash
curl -X POST http://localhost:8000/test/vocabulary-adapter \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world! SOMA is amazing.",
    "model_name": "bert-base-uncased",
    "tokenizer_type": "word"
  }'
```

### Method 4: Test Scripts (Windows/Linux)

**Windows:**
```bash
scripts\test_vocabulary_adapter.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/test_vocabulary_adapter.sh
./scripts/test_vocabulary_adapter.sh
```

### Method 5: Python requests

```python
import requests

# Quick test
response = requests.get("http://localhost:8000/test/vocabulary-adapter/quick")
print(response.json())

# Custom test
response = requests.post(
    "http://localhost:8000/test/vocabulary-adapter",
    json={
        "text": "Hello world! SOMA is amazing.",
        "model_name": "bert-base-uncased",
        "tokenizer_type": "word"
    }
)
data = response.json()
print(f"SOMA tokens: {data['soma']['tokens']}")
print(f"Model IDs: {data['model']['input_ids']}")
```

## Endpoint Details

### POST `/test/vocabulary-adapter`

**Request Body:**
```json
{
  "text": "Hello world! SOMA is amazing.",
  "model_name": "bert-base-uncased",
  "tokenizer_type": "word",
  "seed": 42,
  "embedding_bit": false
}
```

**Parameters:**
- `text` (string, optional): Text to tokenize (default: "Hello world! SOMA is amazing.")
- `model_name` (string, optional): HuggingFace model name (default: "bert-base-uncased")
- `tokenizer_type` (string, optional): SOMA tokenizer type (default: "word")
- `seed` (int, optional): Random seed (default: 42)
- `embedding_bit` (bool, optional): Embedding bit flag (default: false)

**Response:**
```json
{
  "success": true,
  "input": {
    "text": "...",
    "model_name": "bert-base-uncased",
    "tokenizer_type": "word"
  },
  "soma": {
    "tokens": ["Hello", "world", "!", ...],
    "token_count": 5,
    "frontend_digits": [3, 5, 7, ...]
  },
  "model": {
    "input_ids": [7592, 2088, 999, ...],
    "tokens": ["hello", "world", "!", ...],
    "token_count": 6,
    "vocab_size": 30522
  },
  "mapping": {
    "soma_to_model": {
      "0": [1, 2],
      "1": [3],
      ...
    }
  },
  "comparison": {
    "soma_token_count": 5,
    "model_token_count": 6,
    "ratio": 1.2
  }
}
```

### GET `/test/vocabulary-adapter/quick`

Quick test with default values. No parameters needed.

## Supported Models

Test with any HuggingFace model:

- `bert-base-uncased`
- `bert-large-uncased`
- `distilbert-base-uncased`
- `gpt2`
- `gpt2-medium`
- `gpt2-large`
- `roberta-base`
- `roberta-large`
- `t5-small`
- `t5-base`
- `t5-large`
- And 100+ more...

## Expected Output

When successful, you should see:

```json
{
  "success": true,
  "soma": {
    "tokens": ["Hello", "world", "!", "SOMA", "is", "amazing", "."],
    "token_count": 7
  },
  "model": {
    "input_ids": [7592, 2088, 999, ...],
    "tokens": ["hello", "world", "!", ...],
    "token_count": 8
  },
  "comparison": {
    "ratio": 1.14,
    "note": "Model may split tokens into subwords (ratio > 1)"
  }
}
```

## Troubleshooting

### "Vocabulary adapter not available"

**Error:**
```json
{
  "detail": "Vocabulary adapter not available. Install transformers: pip install transformers"
}
```

**Solution:**
```bash
pip install transformers
```

### "Cannot connect to server"

**Error:** Connection refused or timeout

**Solution:**
1. Make sure the server is running:
   ```bash
   python src/servers/main_server.py
   ```
2. Check that it's running on port 8000
3. Try accessing `http://localhost:8000/` in your browser

### Model not found

**Error:**
```
OSError: Model 'xxx' not found
```

**Solution:**
- Use a valid HuggingFace model name
- Make sure you have internet connection (first download requires it)
- Check model name spelling

### Slow response / Timeout

**First request may take 10-30 seconds** because the model needs to be downloaded from HuggingFace. This is normal!

- The first request downloads the model tokenizer files (~1-2 MB)
- Subsequent requests will be much faster (< 1 second)
- If you get a timeout, increase the timeout value or wait for the first download to complete
- Once downloaded, models are cached locally in `~/.cache/huggingface/`

## Example Test Scenarios

### Test 1: Basic BERT Integration
```bash
curl -X POST http://localhost:8000/test/vocabulary-adapter \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world!",
    "model_name": "bert-base-uncased",
    "tokenizer_type": "word"
  }'
```

### Test 2: GPT-2 Integration
```bash
curl -X POST http://localhost:8000/test/vocabulary-adapter \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox",
    "model_name": "gpt2",
    "tokenizer_type": "word"
  }'
```

### Test 3: Character Tokenization
```bash
curl -X POST http://localhost:8000/test/vocabulary-adapter \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello",
    "model_name": "bert-base-uncased",
    "tokenizer_type": "char"
  }'
```

### Test 4: Different Models Comparison
```python
import requests

models = ["bert-base-uncased", "distilbert-base-uncased", "gpt2"]
text = "SOMA provides superior tokenization."

for model in models:
    response = requests.post(
        "http://localhost:8000/test/vocabulary-adapter",
        json={"text": text, "model_name": model, "tokenizer_type": "word"}
    )
    data = response.json()
    print(f"{model}: {data['comparison']['ratio']:.2f}x tokens")
```

## Next Steps

After testing, you can:

1. **Use in your application:** Integrate the vocabulary adapter into your NLP pipeline
2. **See examples:** Check `examples/integration_with_transformers.py`
3. **Read documentation:** See `docs/VOCABULARY_COMPATIBILITY_ISSUE.md`
4. **API reference:** See `src/integration/README.md`

## Support

If you encounter issues:
1. Check the server logs for detailed error messages
2. Verify transformers is installed: `pip list | grep transformers`
3. Test with the quick endpoint first
4. Check the API documentation at `http://localhost:8000/docs`

