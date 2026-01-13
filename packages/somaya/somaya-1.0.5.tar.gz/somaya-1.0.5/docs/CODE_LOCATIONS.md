# 📁 Where is Your Code?

## 🎯 Current Status

**✅ Backend is DEPLOYED and RUNNING on Railway:**
- URL: https://keen-happiness-production.up.railway.app
- Status: ✅ LIVE and WORKING

**❌ Frontend is NOT deployed yet** (code exists locally)

---

## 📂 Backend Code Location

### Main Backend Server
**File:** `src/servers/main_server.py`
- This is the FastAPI server that's running on Railway
- Contains all API endpoints (`/tokenize`, `/decode`, `/analyze`, etc.)

### Backend Core Logic
**Directory:** `src/`
- `src/core/` - Core tokenization engine
- `src/compression/` - Compression algorithms
- `src/utils/` - Utility functions
- `src/integration/` - Integration modules

### Backend Entry Point (Local Development)
**File:** `start.py` (in root)
- Used to start the server locally
- Railway uses this to start the server in the cloud

### To Run Backend Locally:
```bash
# Option 1: Use start.py
python start.py

# Option 2: Use main.py
python main.py
# Then select option 2 (Server Mode)

# Option 3: Direct uvicorn
uvicorn src.servers.main_server:app --host 0.0.0.0 --port 8000
```

---

## 🎨 Frontend Code Location

### Frontend Application
**Directory:** `frontend/`
- `frontend/app/` - Next.js pages
- `frontend/components/` - React components
- `frontend/lib/api.ts` - API connection to backend
- `frontend/package.json` - Dependencies

### Frontend Entry Point
**File:** `frontend/package.json`
- Scripts: `npm run dev` (development), `npm start` (production)

### To Run Frontend Locally:
```bash
cd frontend
npm install  # First time only
npm run dev  # Development server (http://localhost:3000)
```

### Frontend API Connection
**File:** `frontend/lib/api.ts`
- This file connects frontend to backend
- Currently points to: `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'`
- **To connect to Railway backend:** Set environment variable:
  ```bash
  NEXT_PUBLIC_API_URL=https://keen-happiness-production.up.railway.app
  ```

---

## 🚀 What's Deployed vs What's Local

### ✅ DEPLOYED (On Railway)
- **Backend API:** https://keen-happiness-production.up.railway.app
  - Code: `src/servers/main_server.py` + all `src/` files
  - Running in Docker container
  - Accessible from anywhere

### ❌ NOT DEPLOYED (Local Only)
- **Frontend:** Still on your computer
  - Location: `frontend/` directory
  - Needs to be deployed separately
  - Currently only runs on `localhost:3000`

---

## 🔧 How to Deploy Frontend

### Option 1: Deploy Frontend to Railway (Recommended)

1. **Go to Railway Dashboard:**
   - https://railway.com/project/2a7fd91e-4260-44b2-b41e-a39d951fe026

2. **Create New Service:**
   - Click "New Service" → "GitHub Repo" or "Empty Service"
   - Set **Root Directory** to: `frontend`

3. **Add Environment Variable:**
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://keen-happiness-production.up.railway.app`

4. **Deploy:**
   - Railway will auto-detect Next.js and deploy

### Option 2: Run Frontend Locally (Connect to Railway Backend)

```bash
# Navigate to frontend
cd frontend

# Set environment variable
$env:NEXT_PUBLIC_API_URL="https://keen-happiness-production.up.railway.app"

# Start frontend
npm run dev
```

Then open: http://localhost:3000

---

## 📍 Quick Reference

| Component | Location | Status | URL |
|-----------|----------|--------|-----|
| **Backend API** | `src/servers/main_server.py` | ✅ Deployed | https://keen-happiness-production.up.railway.app |
| **Frontend** | `frontend/` | ❌ Local Only | http://localhost:3000 (when running) |
| **Backend Core** | `src/core/` | ✅ Deployed | Part of backend |
| **n8n** | `n8n/` | ❌ Not Deployed | - |

---

## 🎯 Summary

**Your backend code is:**
- ✅ Deployed and running on Railway
- 📁 Located in `src/` directory
- 🔗 Accessible at: https://keen-happiness-production.up.railway.app

**Your frontend code is:**
- ❌ Still on your computer
- 📁 Located in `frontend/` directory
- 🏠 Only runs locally (localhost:3000)
- ⚠️ Needs to be deployed separately to Railway

**To see the full app working:**
1. Deploy frontend to Railway (see instructions above)
2. OR run frontend locally and connect to Railway backend

