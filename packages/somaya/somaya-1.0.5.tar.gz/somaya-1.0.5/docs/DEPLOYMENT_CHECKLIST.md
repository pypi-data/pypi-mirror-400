# 🚀 Railway Deployment Checklist

## Pre-Deployment

### Backend
- [x] ✅ `Dockerfile` exists and is configured
- [x] ✅ `railway.json` exists with Dockerfile config
- [x] ✅ `start.py` exists (starts server correctly)
- [x] ✅ `Procfile` exists (web: python start.py)
- [x] ✅ `requirements.txt` has all dependencies
- [x] ✅ Security: File access restrictions enforced
- [x] ✅ Security: Admin authentication implemented
- [x] ✅ Security: CORS configurable via environment variables
- [x] ✅ Security: JWT authentication configured

### Frontend
- [x] ✅ `frontend/railway.json` exists with Nixpacks config
- [x] ✅ `frontend/package.json` has all dependencies
- [x] ✅ `frontend/next.config.js` configured for production
- [x] ✅ `NEXT_PUBLIC_API_URL` uses environment variable
- [x] ✅ Build process works locally: `npm run build`

## Railway Setup

### 1. Create Railway Project
- [ ] Go to https://railway.app
- [ ] Click "New Project"
- [ ] Connect your GitHub repository

### 2. Deploy Backend Service
- [ ] Add new service → Select backend code
- [ ] Railway auto-detects Dockerfile
- [ ] **Set Environment Variables:**
  - [ ] `PORT=8000` (usually auto-set by Railway)
  - [ ] `HOST=0.0.0.0`
  - [ ] `JWT_SECRET_KEY=<generate-strong-key>` ⚠️ **CRITICAL**
  - [ ] `CORS_ORIGINS=<frontend-url>` ⚠️ **CRITICAL**
  - [ ] `ALLOWED_USERS=admin:password123` ⚠️ **CRITICAL**
  - [ ] `RAILWAY_ENVIRONMENT=production`
  - [ ] `NODE_ENV=production`
- [ ] Generate domain for backend
- [ ] Verify backend is running: `/health` endpoint

### 3. Deploy Frontend Service
- [ ] Add new service → Select frontend code (frontend/ directory)
- [ ] Railway auto-detects Next.js
- [ ] **Set Environment Variables:**
  - [ ] `NODE_ENV=production`
  - [ ] `NEXT_PUBLIC_API_URL=<backend-railway-url>` ⚠️ **CRITICAL**
- [ ] Generate domain for frontend
- [ ] Update backend `CORS_ORIGINS` with frontend URL

### 4. Update Backend CORS
- [ ] Go to Backend Service → Variables
- [ ] Update `CORS_ORIGINS` with actual frontend URL
- [ ] Format: `https://your-frontend.up.railway.app`
- [ ] Service will restart automatically

## Verification

### Backend Tests
- [ ] Health check: `curl https://backend.up.railway.app/health`
- [ ] API docs: `https://backend.up.railway.app/docs`
- [ ] Authentication: Try login at `/admin`

### Frontend Tests
- [ ] Open frontend URL in browser
- [ ] Check console: Should see API URL logged
- [ ] Test authentication: Login works
- [ ] Test code execution: Run Python code
- [ ] Test file browser: Admin can access files

### Security Verification
- [ ] Regular users cannot access SOMA files
- [ ] Admin login required for file access
- [ ] CORS errors don't appear in console
- [ ] JWT tokens work correctly

## Post-Deployment

### Monitoring
- [ ] Set up Railway alerts for failures
- [ ] Monitor CPU/Memory usage
- [ ] Check logs regularly

### Documentation
- [ ] Save production URLs
- [ ] Document environment variables
- [ ] Update README with production URLs

## Quick Commands

### Generate JWT Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Test Backend Health
```bash
curl https://your-backend.up.railway.app/health
```

### Test Frontend Connection
Open browser console and check:
```
🔗 API Base URL: https://your-backend.up.railway.app
```

## Troubleshooting

**Backend won't start:**
- Check Railway logs
- Verify `PORT` is set (Railway auto-sets)
- Verify `start.py` exists

**CORS errors:**
- Verify `CORS_ORIGINS` matches frontend URL exactly
- Check backend logs for CORS warnings

**Authentication fails:**
- Verify `JWT_SECRET_KEY` is set
- Check `ALLOWED_USERS` format: `username:password`

**Frontend can't connect:**
- Verify `NEXT_PUBLIC_API_URL` is set
- Check if backend is running
- Verify backend URL is correct

---

## ✅ Ready to Deploy!

Once all checkboxes are checked, your application is ready for Railway production deployment! 🎉

