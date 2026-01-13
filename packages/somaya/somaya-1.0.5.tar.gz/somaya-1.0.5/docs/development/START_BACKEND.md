# How to Start the Backend Server

The frontend requires the backend API server to be running on `http://localhost:8000`.

## Quick Start

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Start the server:**
   ```bash
   python -m src.servers.main_server
   ```

   Or if you're in the root directory:
   ```bash
   python -m backend.src.servers.main_server
   ```

3. **Verify it's running:**
   - You should see: `[OK] API V2 routes loaded`
   - Server will be available at: `http://localhost:8000`
   - API docs at: `http://localhost:8000/docs`

## Alternative: Using uvicorn directly

```bash
cd backend
uvicorn src.servers.main_server:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

- **Port 8000 already in use?** 
  - Change the port in `main_server.py` (line 2414) or kill the process using port 8000

- **Import errors?**
  - Make sure you're in the correct directory
  - Check that all dependencies are installed: `pip install -r requirements.txt`

- **CORS errors?**
  - The server is configured to allow all origins in development
  - Check `main_server.py` line 170

## What the Backend Provides

- `/api/tokenize` - Tokenization endpoint
- `/api/train` - Training endpoint  
- `/api/embed` - Embedding generation
- `/api/process-file` - Universal file processing
- `/api/health` - Health check
- `/api/train-enhanced` - Enhanced training

All endpoints are prefixed with `/api` and registered in `backend/src/servers/api_v2_routes.py`

