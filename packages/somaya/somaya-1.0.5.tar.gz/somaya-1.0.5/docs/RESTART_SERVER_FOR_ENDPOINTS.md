# Important: Restart Server for New Endpoints

## The Issue

If you're getting **404 errors** when testing the vocabulary adapter endpoints, it means the server needs to be **restarted** to pick up the new endpoints.

## Solution

### Step 1: Stop the Current Server

If the server is running, stop it:
- Press `Ctrl+C` in the terminal where the server is running

### Step 2: Restart the Server

```bash
python src/servers/main_server.py
```

You should see output like:
```
✅ Successfully imported vocabulary adapter
🚀 Starting SOMA API Server...
📡 Server will be available at: http://localhost:8000
```

### Step 3: Verify Endpoints

Run the verification script:
```bash
python scripts/verify_endpoints.py
```

Or test manually:
```bash
# Quick test
curl http://localhost:8000/test/vocabulary-adapter/quick
```

## Why This Happens

FastAPI registers endpoints when the application starts. If you add new endpoints to the code while the server is running, they won't be available until you restart.

## Quick Check

After restarting, you should see the endpoints in the API docs:
1. Open: http://localhost:8000/docs
2. Look for:
   - `POST /test/vocabulary-adapter`
   - `GET /test/vocabulary-adapter/quick`

If you don't see them, the server hasn't picked up the changes yet.

## Verification

The verification script will tell you:
- ✅ Server is running
- ✅ Endpoints are available
- ❌ Endpoints not found (need restart)
- ❌ Vocabulary adapter not installed

Run it with:
```bash
python scripts/verify_endpoints.py
```

