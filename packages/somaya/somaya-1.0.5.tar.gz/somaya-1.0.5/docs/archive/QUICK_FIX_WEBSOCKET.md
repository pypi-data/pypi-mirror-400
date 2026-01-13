# Quick Fix: WebSocket Connection Error

## The Error
```
WebSocket connection to 'ws://localhost:8000/ws/execute' failed
```

## The Fix

**The backend server needs to be running!** The WebSocket endpoint is only available when the FastAPI server is running.

## Quick Start (3 Steps)

### 1. Start the Server

**Option A: PowerShell Script (Easiest)**
```powershell
.\START_SERVER.ps1
```

**Option B: Direct Command**
```powershell
python src\servers\main_server.py
```

**Option C: Batch File**
```cmd
QUICK_START_SERVER.bat
```

### 2. Wait for Server to Start

You should see:
```
[START] Starting SOMA API Server...
[INFO] Server will be available at: http://localhost:8000
[INFO] API Documentation at: http://localhost:8000/docs
```

### 3. Refresh Your Frontend

- Refresh the browser page
- Try the interactive execution again
- WebSocket should now connect! ✅

## Verify It's Working

1. **Check health endpoint:**
   - Open: http://localhost:8000/health
   - Should return JSON with status

2. **Check API docs:**
   - Open: http://localhost:8000/docs
   - Should show FastAPI Swagger UI

3. **Test in frontend:**
   - Use the interactive code execution
   - WebSocket should connect without errors

## Troubleshooting

### Port 8000 Already in Use?

```powershell
# Find what's using it
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
    Select-Object OwningProcess | 
    ForEach-Object { Get-Process -Id $_.OwningProcess }

# Kill it (if it's not the right server)
Stop-Process -Id <PID> -Force
```

### Import Errors?

```powershell
# Install dependencies
pip install fastapi uvicorn websockets
```

### Still Not Working?

1. Check browser console for detailed error
2. Check server logs for connection attempts
3. Verify the server file exists: `src\servers\main_server.py`
4. Make sure you're running the FastAPI server, not the simple HTTP server

## Important

- ✅ **FastAPI server** (`main_server.py`) = Has WebSocket support
- ❌ **Simple HTTP server** (`simple_server.py`) = No WebSocket support

Make sure you're running `main_server.py`!

