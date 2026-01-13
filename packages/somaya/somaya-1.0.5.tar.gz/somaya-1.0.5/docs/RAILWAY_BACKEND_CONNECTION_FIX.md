# 🔧 Railway Backend Connection Fix

## 🐛 Problem
Frontend cannot connect to backend on Railway:
```
Cannot connect to backend server at https://sbackend.up.railway.app
```

## 🔍 Root Cause
The `NEXT_PUBLIC_API_URL` environment variable is **not set** in the Railway frontend service.

## ✅ Fix: Set Environment Variable in Railway

### Step 1: Get Your Backend URL
1. Go to Railway dashboard: https://railway.app
2. Select your **Backend service**
3. Go to **Settings** → **Generate Domain** (if not already done)
4. Copy the backend URL (e.g., `https://sbackend-production.up.railway.app`)

### Step 2: Set Environment Variable in Frontend Service

1. **In Railway Dashboard:**
   - Select your **Frontend service**
   - Go to **Variables** tab
   - Click **"New Variable"**

2. **Add this variable:**
   ```
   Variable Name: NEXT_PUBLIC_API_URL
   Value: https://sbackend.up.railway.app
   ```
   (Replace with your actual backend URL from Step 1)

3. **Click "Save"** or "Deploy" to apply changes

### Step 3: Verify Backend is Running

1. **Check Backend Service:**
   - Go to Backend service in Railway
   - Check **Deployments** tab - should show "Active"
   - Check **Logs** - should show server started

2. **Test Backend Health:**
   - Open: `https://sbackend.up.railway.app/health`
   - Should return: `{"status": "ok", ...}`

### Step 4: Verify CORS is Configured

In **Backend service** → **Variables**, ensure:
```
CORS_ORIGINS=https://your-frontend-url.up.railway.app
```

Replace `your-frontend-url` with your actual frontend Railway URL.

### Step 5: Redeploy Frontend

After setting `NEXT_PUBLIC_API_URL`:
1. Railway will auto-redeploy, OR
2. Manually trigger redeploy: **Frontend service** → **Deployments** → **"Redeploy"**

## 🧪 Testing

After redeploy:
1. Open your frontend URL
2. Check browser console - should show: `🔗 API Base URL: https://sbackend.up.railway.app`
3. Try executing code - should work now

## 📝 Quick Checklist

- [ ] Backend service is deployed and running on Railway
- [ ] Backend health endpoint works: `https://your-backend-url/health`
- [ ] `NEXT_PUBLIC_API_URL` is set in Frontend service variables
- [ ] `CORS_ORIGINS` includes your frontend URL in Backend service
- [ ] Frontend is redeployed after setting environment variable
- [ ] Browser console shows correct API URL

## 🔗 Railway Environment Variables Reference

**Frontend Service:**
```
NEXT_PUBLIC_API_URL=https://sbackend.up.railway.app
NODE_ENV=production
```

**Backend Service:**
```
PORT=8000
JWT_SECRET_KEY=<your-secret-key>
ALLOWED_USERS=admin:your-secure-password
CORS_ORIGINS=https://your-frontend-url.up.railway.app
```

