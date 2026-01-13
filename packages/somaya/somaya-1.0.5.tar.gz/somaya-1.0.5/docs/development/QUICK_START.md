# SOMA Quick Start Guide

Get up and running in 5 minutes!

## Fastest Setup (Choose One)

### Option 1: Automated Script

**Windows:**
```powershell
.\setup.bat
.\run.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

### Option 2: Docker

```bash
docker-compose up
```

### Option 3: Manual (3 Steps)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate and install
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# 3. Run
python start.py
```

## Access the Server

Once running, open in browser:
- **API Docs**: http://localhost:8000/docs
- **Server**: http://localhost:8000

## Quick Test

**Tokenize text:**
```bash
curl -X POST "http://localhost:8000/api/v1/tokenize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "method": "word"}'
```

**Or use CLI:**
```bash
python soma_cli.py tokenize --text "Hello world" --method word
```

## Common Commands

| Task | Command |
|------|---------|
| Start server | `./run.sh` (Linux/Mac) or `run.bat` (Windows) |
| Verify setup | `python verify_installation.py` |
| Tokenize text | `python soma_cli.py tokenize --text "text" --method word` |
| Train model | `python soma_cli.py train --file data.txt --model-path model.pkl` |
| Generate embeddings | `python soma_cli.py embed --text "text" --model-path model.pkl` |

## Change Port

```bash
PORT=8001 python start.py
```

## Troubleshooting

**Port in use?** Change port: `PORT=8001 python start.py`

**Python not found?** Use `python3` instead of `python`

**Dependencies fail?** Upgrade pip: `pip install --upgrade pip`

**Need help?** See [INSTALLATION.md](INSTALLATION.md) for detailed guide

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [CLI_USAGE.md](CLI_USAGE.md) for CLI commands
- Explore API at http://localhost:8000/docs

