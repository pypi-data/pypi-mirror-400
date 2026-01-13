# 🔧 Railway Backend Connection Fix - FINAL

## 🐛 Problem
Backend at `https://sbackend.up.railway.app` is not responding, causing frontend connection errors.

## ✅ Root Cause
CORS environment variable not set in Railway, AND backend might not be starting correctly.

## 🔧 FIXES TO APPLY

### Step 1: Set Environment Variables in Railway Backend Service

Go to: **Railway → keen-happiness → Backend Service → Variables**

Add/Update these **EXACT** variables:

```bash
CORS_ORIGINS=https://sfrontend.up.railway.app
PORT=8000
HOST=0.0.0.0
```

**CRITICAL:** No trailing slashes, no quotes, exact URLs.

### Step 2: Verify Backend is Starting

Check **Backend Service → Logs** after deploy. You should see:
```
[CORS] Configured origins: ['https://sfrontend.up.railway.app']
[CORS] CORS_ORIGINS env var: https://sfrontend.up.railway.app
[START] Starting SOMA API Server...
[INFO] Server will be available at: http://0.0.0.0:8000
```

If you see errors about missing modules or imports, the backend is not starting.

### Step 3: Check Railway Startup Command

Backend Service → Settings → **Start Command** should be:
```bash
python -m uvicorn src.servers.main_server:app --host 0.0.0.0 --port $PORT
```

OR if Railway auto-detects:
```bash
cd src/servers && python main_server.py
```

### Step 4: Verify Health Endpoint

Open in browser: `https://sbackend.up.railway.app/health`

Should return:
```json
{"status": "ok", "message": "SOMA API Server is running", "cors_configured": true}
```

If this fails, the backend is not running at all.

## 🚨 If Still Not Working

1. **Check Railway Backend Logs** - Look for Python errors
2. **Redeploy Backend** - Force a fresh deployment
3. **Check Railway Status** - Ensure backend service is "Active"
4. **Verify Port** - Railway sets `PORT` automatically, ensure code uses it

## 📝 Code Fixes Applied

I've updated the backend code to:
- ✅ Log CORS configuration on startup
- ✅ Use `PORT` and `HOST` from environment variables
- ✅ Better error handling for missing CORS configuration

## ⚠️ ACTION REQUIRED

**You MUST set `CORS_ORIGINS` in Railway Backend Service Variables, then redeploy.**

This cannot be fixed by code alone - it requires Railway environment variable configuration.

