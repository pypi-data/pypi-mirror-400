# WebSocket Connection Fix

## Problem
The frontend is trying to connect to `ws://localhost:8000/ws/execute` but getting a connection error.

## Solution

The backend server needs to be running with **FastAPI** (which supports WebSocket), not the simple HTTP server.

### Step 1: Check if Server is Running

```powershell
# Check if port 8000 is in use
Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet
```

### Step 2: Start the Correct Server

The WebSocket endpoint `/ws/execute` is only available in the **FastAPI server** (`main_server.py`), not the simple HTTP server.

**Option A: Use the PowerShell script (Recommended)**
```powershell
.\start_backend_server.ps1
```

**Option B: Start manually**
```powershell
# From project root
python src\servers\main_server.py

# OR from backend directory
cd backend
python src\servers\main_server.py
```

**Option C: Use the batch file**
```cmd
QUICK_START_SERVER.bat
```

### Step 3: Verify WebSocket Endpoint

Once the server is running, you should see:
- `[START] Starting SOMA API Server...`
- `[INFO] Server will be available at: http://localhost:8000`
- `[INFO] API Documentation at: http://localhost:8000/docs`

The WebSocket endpoint will be available at:
- `ws://localhost:8000/ws/execute`

### Step 4: Test the Connection

1. Open your browser's developer console (F12)
2. Try to use the interactive execution feature in the frontend
3. The WebSocket should now connect successfully

## Troubleshooting

### If port 8000 is already in use:

1. **Find what's using it:**
   ```powershell
   netstat -ano | findstr :8000
   ```

2. **Kill the process (if it's not the right server):**
   ```powershell
   # Get the PID from netstat output, then:
   Stop-Process -Id <PID> -Force
   ```

3. **Or change the port** in `main_server.py` line 4310:
   ```python
   port = int(os.getenv("PORT", "8001"))  # Change to 8001
   ```

### If you get import errors:

```powershell
# Install dependencies
pip install -r requirements.txt

# Or install FastAPI and uvicorn specifically
pip install fastapi uvicorn websockets
```

### If WebSocket still doesn't work:

1. **Check the server logs** - you should see WebSocket connection attempts
2. **Verify the endpoint exists** - check `src/servers/main_server.py` line 2878 for `@app.websocket("/ws/execute")`
3. **Check CORS settings** - the server should allow WebSocket connections from your frontend origin

## Quick Test

After starting the server, test the WebSocket endpoint:

```powershell
# Test HTTP endpoint (should work)
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Test WebSocket (requires a WebSocket client)
# You can use the browser console or a tool like wscat
```

## Important Notes

- The **simple HTTP server** (`simple_server.py` or `lightweight_server.py`) does **NOT** support WebSocket
- Only the **FastAPI server** (`main_server.py`) supports WebSocket
- Make sure you're running `main_server.py`, not `simple_server.py`

