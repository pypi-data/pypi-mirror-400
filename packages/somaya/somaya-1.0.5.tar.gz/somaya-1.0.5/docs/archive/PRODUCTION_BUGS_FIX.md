# Production Bugs Found on https://sfrontend.up.railway.app/

## 🐛 Critical Bugs

### 1. **API URL Configuration Missing** ✅ FIXED (with fallback)
**Issue**: Frontend defaults to `http://localhost:8000` if `NEXT_PUBLIC_API_URL` is not set in Railway environment variables.

**Location**: `frontend/lib/api.ts:7-11`
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (
  typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? `https://${window.location.hostname.replace('sfrontend', 'sbackend')}` // Auto-detect backend URL in production
    : 'http://localhost:8000' // Fallback to localhost for local dev
)
```

**Impact**: All API calls will fail in production if environment variable is not set (now has auto-detection fallback).

**Fix Applied**: Added auto-detection that converts `sfrontend` to `sbackend` in the hostname.

**Still Recommended**: Set Railway environment variable explicitly:
- **Variable**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://sbackend.up.railway.app` (or your backend URL)

---

### 2. **CORS Security Warning**
**Issue**: Backend is using `CORS_ORIGINS="*"` in production, which is insecure.

**Location**: `src/servers/main_server.py:185-190`

**Impact**: Security risk + potential CORS issues if browser blocks wildcard.

**Fix**: Set Railway environment variable on backend:
- **Variable**: `CORS_ORIGINS`
- **Value**: `https://sfrontend.up.railway.app,https://sfrontend.up.railway.app/`

---

### 3. **Webpack Cache Disabled in Dev (Not Production Issue)**
**Status**: ✅ This is fine - only affects dev mode, not production builds.

---

## 🔧 Required Railway Environment Variables

### Frontend Service (`sfrontend`)
```
NEXT_PUBLIC_API_URL=https://sbackend.up.railway.app
```

### Backend Service (`sbackend`)
```
CORS_ORIGINS=https://sfrontend.up.railway.app
WEAVIATE_URL=<your-weaviate-url>
WEAVIATE_API_KEY=<your-api-key>
```

---

## 🚨 Immediate Actions Required

1. **Set `NEXT_PUBLIC_API_URL` in Railway frontend service**
2. **Set `CORS_ORIGINS` in Railway backend service**
3. **Redeploy both services**

---

## 📝 Additional Checks Needed

1. **Check browser console** for API connection errors
2. **Verify backend is running** at `https://sbackend.up.railway.app/health`
3. **Check Network tab** for failed API requests
4. **Verify environment variables** are set correctly in Railway dashboard

---

## 🔍 How to Verify Fixes

1. Open browser console on https://sfrontend.up.railway.app/
2. Look for API configuration debug logs:
   ```
   🔗 API Configuration Debug:
     NEXT_PUBLIC_API_URL (env var): https://sbackend.up.railway.app
     API_BASE_URL (final): https://sbackend.up.railway.app
   ```
3. Check for CORS errors in console
4. Test API calls (e.g., health check, tokenization)

