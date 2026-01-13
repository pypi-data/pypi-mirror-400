# 🚀 How to Execute SOMA Workflows

## After Importing Workflows

### Step 1: Activate Workflows
1. Open n8n: `http://localhost:5678` (or your n8n URL)
2. Go to **"Workflows"** section
3. For each workflow, click the **toggle switch** to activate it
4. ✅ Green = Active, ⚪ Gray = Inactive

### Step 2: Get Webhook URLs
1. Click on a workflow to open it
2. Click on the **Webhook node** (first node)
3. Copy the **Production URL** or **Test URL**
   - Example: `http://localhost:5678/webhook/tokenize`
   - Example: `http://localhost:5678/webhook/analyze`

### Step 3: Execute Workflows

## Method 1: Using cURL (Command Line)

### Tokenization Workflow:
```bash
curl -X POST http://localhost:5678/webhook/tokenize ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Hello World!\", \"tokenizer_type\": \"word\"}"
```

### Analysis Workflow:
```bash
curl -X POST http://localhost:5678/webhook/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"The quick brown fox jumps over the lazy dog.\", \"tokenizer_type\": \"word\"}"
```

### Batch Processing:
```bash
curl -X POST http://localhost:5678/webhook/batch-process ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Your large text here...\", \"batch_size\": 100, \"options\": {\"tokenizer_type\": \"word\"}}"
```

## Method 2: Using PowerShell

```powershell
# Tokenization
$body = @{
    text = "Hello World!"
    tokenizer_type = "word"
    lower = $false
    drop_specials = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/tokenize" -Method Post -Body $body -ContentType "application/json"
```

## Method 3: Using n8n UI (Test Mode)

1. Open the workflow in n8n
2. Click **"Execute Workflow"** button
3. Enter test data in the webhook node
4. Click **"Execute Node"** to test
5. See results in real-time

## Method 4: Using Postman or HTTP Client

1. Create a new POST request
2. URL: `http://localhost:5678/webhook/tokenize` (use your webhook URL)
3. Headers: `Content-Type: application/json`
4. Body (JSON):
```json
{
  "text": "Hello World!",
  "tokenizer_type": "word",
  "lower": false,
  "drop_specials": false
}
```
5. Click **Send**

## Method 5: From Another Application

### JavaScript/Node.js:
```javascript
const response = await fetch('http://localhost:5678/webhook/tokenize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "Hello World!",
    tokenizer_type: "word"
  })
});
const result = await response.json();
console.log(result);
```

### Python:
```python
import requests

response = requests.post(
    'http://localhost:5678/webhook/tokenize',
    json={
        'text': 'Hello World!',
        'tokenizer_type': 'word'
    }
)
print(response.json())
```

## 📋 Available Parameters

All workflows accept these parameters:

```json
{
  "text": "Your text here",
  "tokenizer_type": "word",  // Options: word, space, char, grammar, subword, bpe, syllable, frequency, byte
  "lower": false,             // Convert to lowercase
  "drop_specials": false,     // Remove special characters
  "collapse_repeats": 1,      // Collapse repeated characters
  "embedding": false,         // Enable embedding
  "seed": null,               // Random seed (optional)
  "embedding_bit": null       // Embedding bit size (optional)
}
```

## 🔍 Check Execution Status

1. In n8n, go to **"Executions"** section
2. See all workflow executions
3. Click on any execution to see details
4. View input/output data, errors, and timing

## 🆘 Troubleshooting

### Workflow Not Executing?
- ✅ Check workflow is activated (toggle switch)
- ✅ Verify webhook URL is correct
- ✅ Check SOMA API is running: `http://localhost:8000/health`
- ✅ Check n8n execution logs for errors

### Getting 404 Error?
- Check webhook path matches exactly
- Verify workflow is activated
- Check n8n is running

### Getting 500 Error?
- Check SOMA API is running
- Verify API URL in workflow node
- Check execution logs in n8n

## 🎯 Quick Test

Test if everything is working:

```bash
# Test SOMA API
curl http://localhost:8000/health

# Test n8n workflow
curl -X POST http://localhost:5678/webhook/tokenize \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"test\", \"tokenizer_type\": \"word\"}"
```

---

**That's it!** Your workflows are ready to use! 🎉

