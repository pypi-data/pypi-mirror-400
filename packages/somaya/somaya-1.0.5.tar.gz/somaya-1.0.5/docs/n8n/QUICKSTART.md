# n8n Quick Start Guide for SOMA

Get up and running with n8n workflows for SOMA in minutes!

## ⚡ FASTEST Setup (30 seconds) - Existing n8n

**If you already have n8n running:**

```bash
# Windows
cd n8n
quick-import.bat

# Linux/Mac
cd n8n
chmod +x quick-import.sh
./quick-import.sh
```

Then open `http://localhost:5678` and activate your workflows! Done! 🎉

---

## ⚡ Quick Setup (5 minutes) - New Installation

### Step 1: Start SOMA Backend
```bash
# Make sure SOMA API is running
python src/servers/main_server.py
# Or use the provided script
python scripts/setup/start_main_server.py
```

### Step 2: Start n8n
```bash
# Windows
cd n8n
start.bat

# Linux/Mac
cd n8n
chmod +x start.sh
./start.sh
```

### Step 3: Import Workflows (FASTEST)
```bash
# Windows
cd n8n
quick-import.bat

# Linux/Mac
cd n8n
./quick-import.sh
```

Or manually:
1. Open browser: `http://localhost:5678`
2. Go to Workflows → Import from File
3. Select files from `workflows/` folder

### Step 4: Test a Workflow
```bash
# Test tokenization
curl -X POST http://localhost:5678/webhook/tokenize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World!", "tokenizer_type": "word"}'
```

## 🎯 Common Use Cases

### 1. Simple Text Tokenization
```bash
curl -X POST http://localhost:5678/webhook/tokenize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here",
    "tokenizer_type": "word",
    "lower": false,
    "drop_specials": false
  }'
```

### 2. Text Analysis
```bash
curl -X POST http://localhost:5678/webhook/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Analyze this text",
    "tokenizer_type": "word"
  }'
```

### 3. Batch Processing
```bash
curl -X POST http://localhost:5678/webhook/batch-process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Large text content...",
    "batch_size": 100,
    "options": {
      "tokenizer_type": "word"
    }
  }'
```

## 🔧 Configuration

### Update SOMA API URL
If your SOMA API is not on `localhost:8000`, update the workflows:

1. Open workflow in n8n UI
2. Find "SOMA API" HTTP Request node
3. Update URL field
4. Save workflow

### Change n8n Credentials
1. Edit `.env` file (or create from `.env.example`)
2. Set `N8N_USER` and `N8N_PASSWORD`
3. Restart n8n: `docker-compose restart`

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Explore workflow files in `workflows/` directory
- Customize workflows in n8n UI
- Create your own workflows using n8n's visual editor

## 🆘 Troubleshooting

**n8n won't start?**
```bash
# Check Docker
docker ps

# Check logs
docker-compose logs n8n
```

**Can't connect to SOMA API?**
```bash
# Check if SOMA is running
curl http://localhost:8000/health

# Start SOMA if needed
python src/servers/main_server.py
```

**Workflow not executing?**
- Check workflow is activated (toggle in n8n UI)
- Verify webhook URL is correct
- Check n8n execution logs

## 🎓 Learn More

- [n8n Documentation](https://docs.n8n.io/)
- [SOMA Documentation](../README.md)
- [SOMA API Docs](http://localhost:8000/docs)

---

**Happy Automating! 🚀**

