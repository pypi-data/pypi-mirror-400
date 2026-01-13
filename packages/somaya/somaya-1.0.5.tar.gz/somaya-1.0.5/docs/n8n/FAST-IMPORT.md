# ⚡ FAST IMPORT - 30 Seconds

## For Existing n8n Installation

### Windows:
```batch
cd n8n
quick-import.bat
```

### Linux/Mac:
```bash
cd n8n
chmod +x quick-import.sh
./quick-import.sh
```

**That's it!** Open `http://localhost:5678` and activate your workflows.

---

## Manual Import (if script doesn't work)

1. Open n8n: `http://localhost:5678`
2. Click **"Workflows"** in left sidebar
3. Click **"Import from File"** button
4. Select ALL files from `n8n/workflows/` folder:
   - `soma-tokenization-workflow.json`
   - `soma-analysis-workflow.json`
   - `soma-batch-processing-workflow.json`
   - `soma-scheduled-analysis-workflow.json`
   - `soma-webhook-integration-workflow.json`
   - `soma-slack-integration-workflow.json`
5. Click **"Import"**
6. **Activate** each workflow (toggle switch)
7. **Done!** 🎉

---

## Test Immediately

```bash
curl -X POST http://localhost:5678/webhook/tokenize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World!", "tokenizer_type": "word"}'
```

---

**Need help?** Check `README-EXISTING-N8N.md` for detailed instructions.

