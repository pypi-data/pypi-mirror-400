# API V2 Debug Guide

## Common Issues

### 500 Error on /api/tokenize

**Problem**: TextTokenizer requires both `seed` and `embedding_bit` parameters.

**Fix**: All TextTokenizer instantiations have been updated to:
```python
tokenizer = TextTokenizer(seed=42, embedding_bit=16)
```

### Import Errors

**Check**: Make sure the backend server can import TextTokenizer:
```python
from core.core_tokenizer import TextTokenizer
```

**If that fails**, try:
```python
from src.core.core_tokenizer import TextTokenizer
```

### Testing the API

1. **Check if backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test tokenize endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/tokenize \
     -F "text=Hello world" \
     -F "method=word" \
     -F "seed=42"
   ```

3. **Check backend logs** for detailed error messages

### Error Logging

The API now includes detailed error logging:
- Check console output for `[ERROR]` messages
- Check logs for full tracebacks
- All exceptions are logged with full stack traces

