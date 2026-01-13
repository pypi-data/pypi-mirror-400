# 🚂 Railway Deployment - Complete Setup Guide

## ✅ Railway Configuration Files Checked

### Files Present:
- ✅ `Procfile` - Correct startup command
- ✅ `railway.json` - Correct build and deploy config
- ✅ `runtime.txt` - Python 3.11 specified
- ✅ `deploy.ps1` / `deploy.sh` - Deployment helper scripts

## 🔧 Required Railway Environment Variables

### Backend Service Variables (CRITICAL):

```bash
# CORS Configuration (REQUIRED for frontend connection)
CORS_ORIGINS=https://sfrontend.up.railway.app

# Server Configuration
PORT=8000
HOST=0.0.0.0

# Authentication (REQUIRED for admin access)
JWT_SECRET_KEY=<generate-a-secure-random-string>
ALLOWED_USERS=admin:your-secure-password-hash

# Optional: Railway Environment Detection
RAILWAY_ENVIRONMENT=production
```

### Frontend Service Variables:

```bash
# Backend API URL (REQUIRED)
NEXT_PUBLIC_API_URL=https://sbackend.up.railway.app

# Node Environment
NODE_ENV=production
```

### How to Generate JWT_SECRET_KEY:

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use openssl
openssl rand -base64 32
```

### How to Generate ALLOWED_USERS Hash:

```bash
python -c "import hashlib; print(hashlib.sha256('your-password'.encode()).hexdigest())"
```

Example:
- Password: `admin123`
- Hash: `240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9`
- Format: `admin:240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9`

## 📋 Railway Setup Steps

### Step 1: Set Backend Environment Variables

1. Go to Railway: https://railway.app
2. Select project: **keen-happiness**
3. Select **Backend Service**
4. Go to **Variables** tab
5. Add these variables (one by one):

```
CORS_ORIGINS=https://sfrontend.up.railway.app
PORT=8000
HOST=0.0.0.0
JWT_SECRET_KEY=<your-generated-secret>
ALLOWED_USERS=admin:<your-password-hash>
RAILWAY_ENVIRONMENT=production
```

### Step 2: Set Frontend Environment Variables

1. Select **Frontend Service**
2. Go to **Variables** tab
3. Add:

```
NEXT_PUBLIC_API_URL=https://sbackend.up.railway.app
NODE_ENV=production
```

### Step 3: Verify Configuration

Check **Backend Service → Logs** after deploy. You should see:

```
[CORS] Configured origins: ['https://sfrontend.up.railway.app']
[CORS] CORS_ORIGINS env var: https://sfrontend.up.railway.app
[START] Starting SOMA API Server...
[INFO] Server will be available at: http://0.0.0.0:8000
[INFO] Health check at: http://0.0.0.0:8000/health
[INFO] CORS Origins: https://sfrontend.up.railway.app
[INFO] Allowed Origins: ['https://sfrontend.up.railway.app']
```

### Step 4: Test Health Endpoint

Open: `https://sbackend.up.railway.app/health`

Should return:
```json
{
  "status": "ok",
  "message": "SOMA API Server is running",
  "cors_configured": true,
  "cors_origins": ["https://sfrontend.up.railway.app"],
  "backend_url": "http://0.0.0.0:8000"
}
```

## 🚨 Troubleshooting

### Issue: "Cannot connect to backend server"

**Causes:**
1. CORS_ORIGINS not set → Set in Backend Service Variables
2. Backend not running → Check Backend Service → Logs
3. Backend crashed → Check logs for Python errors

**Fix:**
- Set `CORS_ORIGINS=https://sfrontend.up.railway.app` in Backend Variables
- Redeploy backend service
- Check backend logs for errors

### Issue: Backend logs show CORS errors

**Fix:**
- Verify `CORS_ORIGINS` is exactly: `https://sfrontend.up.railway.app`
- No trailing slash
- No quotes
- Redeploy backend

### Issue: Health endpoint returns 404

**Fix:**
- Check Backend Service → Settings → Start Command
- Should be: `uvicorn src.servers.main_server:app --host 0.0.0.0 --port $PORT`
- Or Railway should auto-detect from `Procfile`

## ✅ Verification Checklist

- [ ] Backend Service Variables set (CORS_ORIGINS, PORT, HOST, JWT_SECRET_KEY, ALLOWED_USERS)
- [ ] Frontend Service Variables set (NEXT_PUBLIC_API_URL)
- [ ] Backend Service deployed and running
- [ ] Frontend Service deployed and running
- [ ] Health endpoint returns `{"status": "ok", "cors_configured": true}`
- [ ] Frontend can connect to backend (no CORS errors)
- [ ] Backend logs show CORS configuration correctly

## 📝 Notes

- Railway automatically sets `PORT` - but we can override it
- Railway automatically detects Python from `runtime.txt`
- Railway uses `Procfile` or `railway.json` for startup command
- CORS_ORIGINS must match frontend URL exactly (no trailing slash)

