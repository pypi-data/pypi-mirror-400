# 🚀 START - 3 Simple Steps

## Step 1: Start SOMA Backend

**Option A - Double-click:**
```
Double-click: START.bat
```

**Option B - Manual:**
```bash
python src/servers/main_server.py
```

✅ Wait until you see: "SOMA API Server... running"

---

## Step 2: Import Workflows to n8n

1. **Open n8n** in browser: `http://localhost:5678`

2. **Click "Workflows"** (left sidebar)

3. **Click "Import from File"**

4. **Go to this folder:** `n8n\workflows\`

5. **Select ALL 6 files:**
   - soma-tokenization-workflow.json
   - soma-analysis-workflow.json
   - soma-batch-processing-workflow.json
   - soma-scheduled-analysis-workflow.json
   - soma-webhook-integration-workflow.json
   - soma-slack-integration-workflow.json

6. **Click "Import"**

7. **Activate each workflow** (click the toggle switch - make it green)

---

## Step 3: Test It

**Double-click:**
```
test-workflow.bat
```

**OR use PowerShell:**
```powershell
cd n8n
.\test-workflow.ps1
```

**OR test manually:**
```bash
curl -X POST http://localhost:5678/webhook/tokenize -H "Content-Type: application/json" -d "{\"text\": \"Hello!\", \"tokenizer_type\": \"word\"}"
```

---

## ✅ Done!

Your workflows are now running!

**To use them:**
- Get webhook URL from n8n (click workflow → webhook node → copy URL)
- Send POST requests to that URL with your text

**See `HOW-TO-EXECUTE.md` for more examples!**

