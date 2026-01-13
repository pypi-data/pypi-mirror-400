# 🔧 CORS Fix for Railway

## 🐛 Problem
CORS error blocking frontend requests:
```
Access to fetch at 'https://sbackend.up.railway.app/health' from origin 'https://sfrontend.up.railway.app' has been blocked by CORS policy
```

**Note**: Other endpoints (`/auth/verify`, `/execute/files`) work fine (200 OK), but `/health` fails.

## ✅ Fix: Set CORS_ORIGINS in Railway Backend

### Step 1: Set Environment Variable in Railway Backend Service

1. Go to Railway: https://railway.app
2. Select your project: **keen-happiness**
3. Select **Backend Service**
4. Go to **Variables** tab
5. Click **"New Variable"** or edit existing
6. Add/Update:
   ```
   Variable Name: CORS_ORIGINS
   Value: https://sfrontend.up.railway.app
   ```

**IMPORTANT**: Use exact URL with `https://` prefix

### Step 2: Verify Other Required Variables

Make sure these are also set in Backend Service:

```
CORS_ORIGINS=https://sfrontend.up.railway.app
PORT=8000
JWT_SECRET_KEY=<your-secret-key>
ALLOWED_USERS=admin:your-secure-password
```

### Step 3: Redeploy Backend

After setting `CORS_ORIGINS`:
1. Railway will auto-redeploy, OR
2. Manually: Backend Service → Deployments → "Redeploy"

### Step 4: Check Backend Logs

After redeploy, check Backend Service → Logs. You should see:
```
[CORS] Configured origins: ['https://sfrontend.up.railway.app']
[CORS] CORS_ORIGINS env var: https://sfrontend.up.railway.app
```

### Step 5: Test

1. Open frontend: https://sfrontend.up.railway.app
2. Open browser console (F12)
3. Should NOT see CORS errors anymore
4. Health check should work: `/health` endpoint

## 🧪 Debugging

If still not working:

1. **Check Railway Variables:**
   - Backend Service → Variables
   - Verify `CORS_ORIGINS` is exactly: `https://sfrontend.up.railway.app`
   - No trailing slash, no spaces

2. **Check Backend Logs:**
   - Look for `[CORS] Configured origins:` message
   - Should show your frontend URL

3. **Test Backend Health Directly:**
   - Open: https://sbackend.up.railway.app/health
   - Should return: `{"status": "ok", ...}`

4. **Clear Browser Cache:**
   - Sometimes cached CORS errors persist
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

## 📝 Quick Checklist

- [ ] `CORS_ORIGINS=https://sfrontend.up.railway.app` is set in Backend Service
- [ ] Backend is redeployed after setting variable
- [ ] Backend logs show correct CORS origins
- [ ] Frontend refreshed (hard refresh)
- [ ] No CORS errors in browser console

