# Troubleshooting: Frontend Cannot Connect to Backend

## Quick Fixes

### 1. Check if Backend is Running
```bash
# Check if server is running on port 8000
# You should see: "Uvicorn running on http://0.0.0.0:8000"
```

### 2. Check Frontend is Running
```bash
cd frontend
npm run dev
# Should see: "Ready on http://localhost:3000"
```

### 3. Test Backend Directly
Open in browser: `http://localhost:8000/health`
Should return: `{"status": "ok", "message": "SOMA API Server is running"}`

### 4. Check CORS Settings
- Backend CORS is now set to allow all origins (`allow_origins=["*"]`)
- This should fix connection issues

### 5. Check API URL
Frontend uses: `http://localhost:8000` (from `NEXT_PUBLIC_API_URL`)

### 6. Common Issues

**Issue: "Cannot connect to backend server"**
- **Solution**: Make sure backend is running on port 8000
- **Check**: Open `http://localhost:8000/health` in browser

**Issue: CORS errors**
- **Solution**: CORS is now set to allow all origins
- **Check**: Restart backend server after CORS change

**Issue: Port already in use**
- **Solution**: Kill process on port 8000 or use different port
- **Windows**: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F`

**Issue: Frontend can't find backend**
- **Solution**: Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- **Check**: Restart frontend after changing env vars

## Step-by-Step Debugging

1. **Start Backend:**
   ```bash
   python src/servers/main_server.py
   ```
   Should see: "Uvicorn running on http://0.0.0.0:8000"

2. **Test Backend:**
   - Open: `http://localhost:8000/health`
   - Should return JSON with status "ok"

3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   Should see: "Ready on http://localhost:3000"

4. **Test Connection:**
   - Open: `http://localhost:3000`
   - Check browser console for errors
   - Try making a request from frontend

## Still Not Working?

1. **Check Firewall**: Windows Firewall might be blocking port 8000
2. **Check Antivirus**: Some antivirus software blocks localhost connections
3. **Try Different Port**: Change backend to port 8001 and update frontend
4. **Check Network**: Make sure no proxy is interfering

## Health Check Endpoint

Added `/health` endpoint to test if backend is accessible:
- URL: `http://localhost:8000/health`
- Response: `{"status": "ok", "message": "SOMA API Server is running"}`

