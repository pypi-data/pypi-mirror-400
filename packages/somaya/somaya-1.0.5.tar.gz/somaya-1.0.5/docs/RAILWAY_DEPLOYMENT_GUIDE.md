# Railway Production Deployment Guide

This guide covers deploying both **Backend** and **Frontend** to Railway production.

## 📋 Prerequisites

1. Railway account (https://railway.app)
2. Railway CLI installed (optional): `npm i -g @railway/cli`
3. Git repository pushed to GitHub/GitLab

## 🚀 Deployment Steps

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo" or "Empty Project"

### Step 2: Deploy Backend

#### Option A: Using Dockerfile (Recommended)

1. **Add Backend Service:**
   - Click "New" → "Service" → "GitHub Repo"
   - Select your repository
   - Railway will auto-detect `railway.json` and `Dockerfile`

2. **Set Environment Variables** (Critical!):
   
   ```
   PORT=8000
   HOST=0.0.0.0
   JWT_SECRET_KEY=<generate-a-strong-random-secret-key>
   CORS_ORIGINS=<your-frontend-railway-url>
   ALLOWED_USERS=admin:your-secure-password
   RAILWAY_ENVIRONMENT=production
   NODE_ENV=production
   ```

   **To generate JWT_SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Backend will start automatically** using `start.py`

#### Option B: Using Nixpacks (Alternative)

1. Railway will auto-detect Python project
2. It will use `requirements.txt` and `start.py`
3. Set same environment variables as above

### Step 3: Deploy Frontend

1. **Add Frontend Service:**
   - Click "New" → "Service" → "GitHub Repo" (same repo)
   - OR add as second service in same project

2. **Configure Build Settings:**
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`
   - Or Railway will auto-detect from `frontend/railway.json`

3. **Set Environment Variables:**
   
   ```
   NODE_ENV=production
   NEXT_PUBLIC_API_URL=<your-backend-railway-url>
   ```

   **Example:**
   ```
   NEXT_PUBLIC_API_URL=https://sbackend-production.up.railway.app
   ```

4. **Generate Domain:**
   - Go to Settings → Generate Domain
   - Railway will provide: `https://your-frontend.up.railway.app`

### Step 4: Configure CORS

**IMPORTANT:** Update backend `CORS_ORIGINS` with your frontend URL:

```
CORS_ORIGINS=https://your-frontend.up.railway.app,https://www.your-custom-domain.com
```

**Backend Environment Variables:**
- Go to Backend Service → Variables
- Update `CORS_ORIGINS` with your actual frontend URL(s)

### Step 5: Verify Deployment

1. **Backend Health Check:**
   ```
   curl https://your-backend.up.railway.app/health
   ```

2. **Frontend Access:**
   ```
   https://your-frontend.up.railway.app
   ```

3. **Test API Connection:**
   - Open frontend URL
   - Check browser console for API connection
   - Should see: `🔗 API Base URL: https://your-backend.up.railway.app`

## 🔒 Security Checklist

### Backend Security

- [x] `JWT_SECRET_KEY` is set (strong random key)
- [x] `ALLOWED_USERS` is set (format: `username:password`)
- [x] `CORS_ORIGINS` is restricted (not `*`)
- [x] `RAILWAY_ENVIRONMENT=production` is set
- [x] File access restrictions are enforced (automatic)

### Frontend Security

- [x] `NEXT_PUBLIC_API_URL` points to backend
- [x] No hardcoded API URLs
- [x] Authentication tokens stored securely (localStorage)

## 📝 Environment Variables Reference

### Backend Environment Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `PORT` | Yes | `8000` | Server port (Railway auto-sets) |
| `HOST` | Yes | `0.0.0.0` | Server host |
| `JWT_SECRET_KEY` | **CRITICAL** | `random-key-here` | JWT signing key |
| `CORS_ORIGINS` | **CRITICAL** | `https://frontend.up.railway.app` | Allowed frontend origins |
| `ALLOWED_USERS` | **CRITICAL** | `admin:password123` | Admin credentials |
| `RAILWAY_ENVIRONMENT` | Yes | `production` | Marks production environment |
| `NODE_ENV` | Yes | `production` | Node environment |

### Frontend Environment Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `NODE_ENV` | Yes | `production` | Node environment |
| `NEXT_PUBLIC_API_URL` | **CRITICAL** | `https://backend.up.railway.app` | Backend API URL |

## 🔧 Troubleshooting

### Backend Issues

**Issue: 502 Bad Gateway**
- Check if backend is running: View logs in Railway
- Verify `PORT` and `HOST` are set correctly
- Check if `start.py` is in root directory

**Issue: CORS Errors**
- Verify `CORS_ORIGINS` includes your frontend URL (exact match)
- Check backend logs for CORS warnings
- Ensure frontend `NEXT_PUBLIC_API_URL` is correct

**Issue: Authentication Fails**
- Verify `JWT_SECRET_KEY` is set
- Check `ALLOWED_USERS` format: `username:password`
- Check backend logs for authentication errors

**Issue: File Access Denied**
- This is expected for regular users (security feature)
- Only admin users can access files
- Verify you're logged in as admin

### Frontend Issues

**Issue: Cannot Connect to Backend**
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify backend URL is accessible
- Check browser console for connection errors

**Issue: Build Fails**
- Check Node.js version (should be 18+)
- Verify all dependencies in `package.json`
- Check build logs in Railway

**Issue: WebSocket Connection Fails**
- Verify backend URL supports WebSocket (`ws://` or `wss://`)
- Check Railway proxy configuration
- Test WebSocket endpoint directly

## 📊 Monitoring

1. **View Logs:**
   - Railway Dashboard → Service → Logs
   - Real-time logs available

2. **Metrics:**
   - CPU usage
   - Memory usage
   - Request count
   - Response times

3. **Alerts:**
   - Configure alerts in Railway dashboard
   - Set up notifications for failures

## 🔄 Updating Deployment

1. **Push Changes to Git:**
   ```bash
   git add .
   git commit -m "Update code"
   git push
   ```

2. **Railway Auto-Deploys:**
   - Railway watches your repository
   - Auto-deploys on push to main branch
   - Manual redeploy available in dashboard

3. **Rollback:**
   - Go to Deployments tab
   - Click "Rollback" on previous deployment

## 📦 File Structure for Railway

```
project-root/
├── Dockerfile              # Backend Dockerfile
├── railway.json            # Backend Railway config
├── Procfile                # Backend process file
├── start.py                # Backend start script
├── requirements.txt        # Backend dependencies
├── src/                    # Backend source code
├── examples/               # Example files
├── config/                 # Admin config (created at runtime)
│   └── admin_users.json    # Admin users (auto-generated)
└── frontend/               # Frontend directory
    ├── railway.json        # Frontend Railway config
    ├── package.json        # Frontend dependencies
    ├── next.config.js      # Next.js config
    └── ...                 # Next.js app files
```

## ✅ Post-Deployment Verification

1. **Backend Health:**
   - ✅ Health endpoint responds: `/health`
   - ✅ API docs accessible: `/docs`
   - ✅ Authentication works: `/auth/login`

2. **Frontend:**
   - ✅ Page loads without errors
   - ✅ API connection successful
   - ✅ Authentication flow works
   - ✅ Code execution works
   - ✅ File browser works (admin only)

3. **Security:**
   - ✅ Admin login required for file access
   - ✅ Regular users cannot access SOMA files
   - ✅ CORS restricted to frontend URL only
   - ✅ JWT tokens working correctly

## 🎯 Production URLs

After deployment, save these URLs:

- **Backend API:** `https://your-backend.up.railway.app`
- **Frontend App:** `https://your-frontend.up.railway.app`
- **Backend Docs:** `https://your-backend.up.railway.app/docs`

## 📞 Support

If you encounter issues:
1. Check Railway logs first
2. Verify all environment variables are set
3. Check this deployment guide
4. Review error messages in browser console / backend logs

---

**Ready to Deploy! 🚀**

Follow these steps carefully, especially the security checklist, to ensure a secure and successful deployment.

