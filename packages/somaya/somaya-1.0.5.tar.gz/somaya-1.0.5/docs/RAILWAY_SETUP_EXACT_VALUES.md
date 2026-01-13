# Railway Setup - Exact Configuration Values

## Your Railway Services
- **Project**: keen-happiness
- **Frontend**: https://sfrontend.up.railway.app
- **Backend**: https://sbackend.up.railway.app
- **n8n**: https://snin.up.railway.app

## Step 1: Set Frontend Environment Variables

Go to **Frontend Service** → **Variables** → Add:

```
NEXT_PUBLIC_API_URL=https://sbackend.up.railway.app
```

That's it. One variable.

## Step 2: Set Backend Environment Variables

Go to **Backend Service** → **Variables** → Add/Update:

```
CORS_ORIGINS=https://sfrontend.up.railway.app
PORT=8000
JWT_SECRET_KEY=<generate-your-own-secret-key>
ALLOWED_USERS=admin:your-secure-password
```

**To generate JWT_SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Redeploy Both Services

1. After setting variables, Railway auto-redeploys
2. OR manually: Each service → Deployments → "Redeploy"

## Step 4: Test

1. **Test Backend:**
   - Open: https://sbackend.up.railway.app/health
   - Should show: `{"status": "ok", ...}`

2. **Test Frontend:**
   - Open: https://sfrontend.up.railway.app
   - Open browser console (F12)
   - Should see: `🔗 API Base URL: https://sbackend.up.railway.app`
   - If you see `http://localhost:8000`, the environment variable isn't set

## Quick Checklist

- [ ] Frontend has `NEXT_PUBLIC_API_URL=https://sbackend.up.railway.app`
- [ ] Backend has `CORS_ORIGINS=https://sfrontend.up.railway.app`
- [ ] Backend has `JWT_SECRET_KEY` set
- [ ] Backend has `ALLOWED_USERS` set
- [ ] Both services are redeployed
- [ ] Backend health check works
- [ ] Frontend console shows correct API URL

## That's It!

These are the ONLY environment variables you need to set. Everything else is handled automatically.

