# Fix WebSocket Connection Error

## The Problem

You're seeing this error in the browser console:
```
WebSocket connection to 'ws://localhost:8000/ws/execute' failed
```

## The Solution

The backend server with WebSocket support needs to be running. I've started it for you in the background.

## What I Did

1. ✅ Created `start_backend_server.ps1` - Script to start the server
2. ✅ Started the FastAPI server in the background
3. ✅ The server should now be running on `http://localhost:8000`

## Verify It's Working

1. **Check if server is running:**
   - Open: http://localhost:8000/health
   - Should return: `{"status":"healthy"}`

2. **Check API docs:**
   - Open: http://localhost:8000/docs
   - Should show FastAPI documentation

3. **Test WebSocket:**
   - Refresh your frontend page
   - Try the interactive execution feature
   - The WebSocket should now connect

## If It's Still Not Working

### Option 1: Restart the Server

```powershell
# Stop any existing server
Get-Process python | Where-Object {$_.Path -like "*python*"} | Stop-Process -Force

# Start the server
.\start_backend_server.ps1
```

### Option 2: Start Manually

```powershell
python src\servers\main_server.py
```

### Option 3: Check What's Running on Port 8000

```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess | ForEach-Object { Get-Process -Id $_.OwningProcess }
```

## Important Notes

- **Only `main_server.py` supports WebSocket** - The simple HTTP servers don't
- **The server must be FastAPI** - WebSocket requires FastAPI/uvicorn
- **Port 8000 must be available** - Or change the port in the code

## Quick Commands

```powershell
# Start server
.\start_backend_server.ps1

# OR
python src\servers\main_server.py

# Check if running
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
```

## Next Steps

1. ✅ Server should be running now
2. ✅ Refresh your frontend page
3. ✅ Try the interactive execution again
4. ✅ WebSocket should connect successfully!

If you still see errors, check the browser console for more details.

