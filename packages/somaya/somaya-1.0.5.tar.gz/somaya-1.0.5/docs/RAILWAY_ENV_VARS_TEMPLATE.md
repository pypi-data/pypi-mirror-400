# Railway Environment Variables Template

Copy these environment variables to your Railway project settings.

## 🔐 Backend Environment Variables

### Required Variables (Set these first!)

```bash
# Server Configuration
PORT=8000
HOST=0.0.0.0

# Security - CRITICAL!
JWT_SECRET_KEY=<generate-strong-random-key>
CORS_ORIGINS=https://your-frontend.up.railway.app
ALLOWED_USERS=admin:your-secure-password-here

# Environment
RAILWAY_ENVIRONMENT=production
NODE_ENV=production
```

### Generate JWT_SECRET_KEY

Run this command to generate a secure random key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as `JWT_SECRET_KEY`.

### ALLOWED_USERS Format

Format: `username:password,username2:password2`

Example:
```
ALLOWED_USERS=admin:SecurePassword123,john:AnotherSecurePassword456
```

**Important:** Passwords should be at least 8 characters. Railway will hash them automatically.

### CORS_ORIGINS Format

Format: `https://domain1.com,https://domain2.com`

Example:
```
CORS_ORIGINS=https://soma-frontend.up.railway.app,https://www.soma.com
```

**Security:** Never use `*` in production! Always specify exact frontend URLs.

## 🎨 Frontend Environment Variables

```bash
# Environment
NODE_ENV=production

# Backend API URL (CRITICAL!)
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

### Get Your Backend URL

1. Deploy backend first
2. Go to Backend Service → Settings → Generate Domain
3. Copy the URL (e.g., `https://sbackend-production.up.railway.app`)
4. Use it as `NEXT_PUBLIC_API_URL`

## 📋 Complete Setup Checklist

### Backend Service
- [ ] `PORT=8000` (Railway sets automatically, but good to have)
- [ ] `HOST=0.0.0.0`
- [ ] `JWT_SECRET_KEY` (generated secure random key)
- [ ] `CORS_ORIGINS` (your frontend Railway URL)
- [ ] `ALLOWED_USERS` (at least one admin user)
- [ ] `RAILWAY_ENVIRONMENT=production`
- [ ] `NODE_ENV=production`

### Frontend Service
- [ ] `NODE_ENV=production`
- [ ] `NEXT_PUBLIC_API_URL` (your backend Railway URL)

## 🔍 Verification Commands

After setting environment variables:

### Test Backend
```bash
# Health check
curl https://your-backend.up.railway.app/health

# Should return: {"status":"healthy",...}
```

### Test Frontend
```bash
# Open in browser
https://your-frontend.up.railway.app

# Check browser console for:
# 🔗 API Base URL: https://your-backend.up.railway.app
```

## ⚠️ Security Warnings

Railway will show warnings if these are missing:
- ❌ `JWT_SECRET_KEY` not set → Authentication will fail
- ❌ `CORS_ORIGINS` is `*` or not set → Security vulnerability
- ❌ `ALLOWED_USERS` not set → No admin access possible

## 🔄 Updating Environment Variables

1. Go to Railway Dashboard
2. Select Service (Backend or Frontend)
3. Go to Variables tab
4. Add/Edit variables
5. Service will automatically restart

---

**Copy the template above and fill in your actual values!**

