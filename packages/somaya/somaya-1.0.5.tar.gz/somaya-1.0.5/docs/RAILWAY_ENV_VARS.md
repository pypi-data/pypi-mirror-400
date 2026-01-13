# Railway Environment Variables - REQUIRED FOR PRODUCTION

## CRITICAL: Set these environment variables in Railway before deployment

### Backend (Python/FastAPI)

1. **JWT_SECRET_KEY** (REQUIRED)
   - Description: Secret key for JWT token signing
   - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Example: `xK8PmN2qR5sT7vW9yZ0bC1dE3fG4hI5jK6lM7nO8pQ9r`
   - **DO NOT SHARE OR COMMIT THIS VALUE**

2. **ALLOWED_USERS** (REQUIRED)
   - Description: Comma-separated list of username:password pairs for admin access
   - Format: `username1:password1,username2:password2`
   - Example: `admin:SecurePassword123,admin2:AnotherSecurePassword`
   - **DO NOT USE DEFAULT PASSWORD**

3. **CORS_ORIGINS** (REQUIRED)
   - Description: Comma-separated list of allowed frontend origins
   - Format: `https://yourdomain.com,https://www.yourdomain.com`
   - Example: `https://soma-frontend.up.railway.app`
   - **DO NOT USE "*" IN PRODUCTION**

4. **PORT** (Optional - Railway sets this automatically)
   - Description: Port number for the server
   - Default: 8000
   - Railway sets this automatically

5. **NODE_ENV** or **RAILWAY_ENVIRONMENT** (Optional)
   - Description: Environment indicator
   - Railway sets this automatically

### Frontend (Next.js)

1. **NEXT_PUBLIC_API_URL** (REQUIRED)
   - Description: Backend API URL
   - Format: `https://your-backend-url.up.railway.app`
   - Example: `https://soma-backend.up.railway.app`
   - **MUST BE HTTPS IN PRODUCTION**

## How to Set in Railway

1. Go to your Railway project
2. Select the service (backend or frontend)
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable with its value
6. Click "Deploy" to apply changes

## Security Checklist

- [ ] JWT_SECRET_KEY is set and secure (32+ characters, random)
- [ ] ALLOWED_USERS is set with strong passwords (no default "admin123")
- [ ] CORS_ORIGINS is restricted to your frontend domain (not "*")
- [ ] NEXT_PUBLIC_API_URL points to your backend HTTPS URL
- [ ] All passwords are strong (12+ characters, mixed case, numbers, symbols)
- [ ] Environment variables are NOT committed to git

## Testing After Deployment

1. Test health endpoint: `https://your-backend-url/health`
2. Test login: Use admin credentials from ALLOWED_USERS
3. Verify CORS: Frontend should be able to call backend
4. Check logs for any warnings about missing environment variables

