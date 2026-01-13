# 🚀 Hostinger Business Hosting Deployment Guide

## ⚠️ **IMPORTANT: Challenges with Shared Hosting**

Your SOMA project has specific requirements that may be **challenging** on standard shared hosting:

### **Project Requirements:**
- ✅ Python 3.x with FastAPI/uvicorn (needs long-running process)
- ✅ Node.js for Next.js frontend (build + runtime)
- ✅ WebSocket support (for interactive terminal)
- ✅ Background job processing (async code execution)
- ✅ Heavy dependencies (numpy, pandas, sentence-transformers, chromadb)
- ✅ File system access for job files

### **Hostinger Business Hosting Limitations:**
- ❌ **No long-running processes** (scripts timeout after 30-60 seconds)
- ❌ **Limited Python support** (usually CGI/mod_wsgi, not FastAPI)
- ❌ **No WebSocket support** on shared hosting
- ❌ **No Node.js** (or very limited) on standard plans
- ❌ **Memory limits** (may not handle heavy ML libraries)
- ❌ **No SSH access** (on basic plans)

---

## ✅ **POSSIBLE SOLUTIONS:**

### **Option 1: Hostinger VPS (Recommended if Available)**

If Hostinger offers VPS hosting with your business plan:

**Advantages:**
- Full control (SSH access)
- Can run long-running processes
- Can install Node.js and Python
- No timeout restrictions

**Steps:**
1. Get VPS access from Hostinger
2. Install Python 3.x, Node.js, pip
3. Deploy backend and frontend separately
4. Use PM2 or systemd to keep processes running

**Deployment Script:**
```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && npm run build

# Start backend (with PM2 or systemd)
python backend/src/servers/main_server.py

# Start frontend
cd frontend && npm start
```

---

### **Option 2: Hybrid Approach (Frontend on Hostinger, Backend Elsewhere)**

**Best Solution for Shared Hosting:**

1. **Frontend (Next.js) → Hostinger:**
   - Build Next.js as static export
   - Upload to Hostinger via FTP/cPanel
   - Serve as static files

2. **Backend (FastAPI) → Railway/Render/Heroku:**
   - Deploy backend separately
   - Update frontend API URL to point to backend

**Steps:**

#### **Step 1: Build Frontend as Static Export**

```bash
cd frontend
# Update next.config.js to export static
npm run build
# Upload 'out' folder to Hostinger
```

#### **Step 2: Deploy Backend to Railway/Render**

- Use your existing `soma_railway.zip`
- Deploy backend separately
- Get backend URL (e.g., `https://soma-backend.railway.app`)

#### **Step 3: Update Frontend API URL**

In `frontend/.env.production`:
```
NEXT_PUBLIC_API_URL=https://soma-backend.railway.app
```

#### **Step 4: Upload to Hostinger**

- Upload `frontend/out` folder contents to `public_html/`
- Access via your domain

---

### **Option 3: Simplified Version (If Full Features Not Needed)**

If you can live without some features:

1. **Remove WebSocket/Interactive Terminal:**
   - Disable interactive code execution
   - Use only HTTP endpoints

2. **Remove Background Jobs:**
   - Disable async job manager
   - Use synchronous execution only

3. **Use Lighter Dependencies:**
   - Remove heavy ML libraries if not needed
   - Use minimal tokenization only

4. **Deploy as Python CGI:**
   - Convert FastAPI to Flask (lighter)
   - Use Hostinger's Python app support
   - Serve via mod_wsgi

---

### **Option 4: Use Hostinger's Python App Feature (If Available)**

Some Hostinger plans support Python apps:

1. **Check cPanel for "Python App" or "Python Selector"**
2. **Create Python App:**
   - Select Python version (3.8+)
   - Point to your project directory
   - Set startup file: `backend/src/servers/main_server.py`

3. **Install Dependencies:**
   - Use pip in Python app environment
   - May need to request specific packages

4. **Limitations:**
   - Still may have timeout issues
   - WebSocket may not work
   - Background jobs may not work

---

## 🎯 **RECOMMENDED APPROACH:**

### **For Hostinger Business Hosting:**

**Use Option 2 (Hybrid):**
1. ✅ Deploy **frontend** to Hostinger (static Next.js export)
2. ✅ Deploy **backend** to Railway/Render (free tier available)
3. ✅ Connect them via API URL

**Why This Works:**
- Frontend is just static files (works on any hosting)
- Backend gets proper environment (Railway/Render)
- No timeout or process restrictions
- WebSocket and background jobs work
- Cost-effective (Railway free tier + Hostinger)

---

## 📋 **STEP-BY-STEP: Hybrid Deployment**

### **Part 1: Prepare Frontend for Static Export**

1. **Update `frontend/next.config.js`:**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true
  },
  trailingSlash: true,
}

module.exports = nextConfig
```

2. **Build Frontend:**
```bash
cd frontend
npm install
npm run build
# Output will be in 'out' folder
```

3. **Update API URL:**
   - Set `NEXT_PUBLIC_API_URL` to your backend URL
   - Or create `.env.production` file

### **Part 2: Deploy Backend to Railway**

1. **Use `soma_railway.zip`** (already created!)
2. **Upload to Railway:**
   - Create new project
   - Upload ZIP or connect GitHub
   - Railway auto-detects and deploys
3. **Get Backend URL:**
   - Railway provides URL like `https://xxx.railway.app`
   - Update frontend API URL

### **Part 3: Upload Frontend to Hostinger**

1. **Via FTP/cPanel File Manager:**
   - Upload all files from `frontend/out/` to `public_html/`
   - Or create subdomain: `app.yourdomain.com`

2. **Access:**
   - Visit your domain
   - Frontend connects to Railway backend

---

## 🔧 **ALTERNATIVE: Full Hostinger Setup (If VPS Available)**

If you have Hostinger VPS access:

### **Setup Script:**

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.10+
sudo apt install python3.10 python3-pip python3-venv -y

# 3. Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 4. Install PM2 (process manager)
sudo npm install -g pm2

# 5. Upload project files
# (via FTP or git clone)

# 6. Setup backend
cd /path/to/project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 7. Setup frontend
cd frontend
npm install
npm run build

# 8. Start backend with PM2
cd /path/to/project
pm2 start backend/src/servers/main_server.py --name soma-backend --interpreter python3

# 9. Start frontend with PM2
cd frontend
pm2 start npm --name soma-frontend -- start

# 10. Save PM2 config
pm2 save
pm2 startup
```

---

## ❓ **CHECK YOUR HOSTINGER PLAN:**

Before proceeding, check:

1. **Do you have SSH access?**
   - If YES → Option 1 or 4 (VPS setup)
   - If NO → Option 2 (Hybrid)

2. **Do you have Python App support in cPanel?**
   - If YES → Option 4 (Python App)
   - If NO → Option 2 (Hybrid)

3. **Do you have Node.js support?**
   - If YES → Can build frontend on server
   - If NO → Build locally, upload static files

4. **What's your timeout limit?**
   - If 30-60 seconds → Can't run long processes
   - If unlimited → Can run backend

---

## 🎯 **QUICK DECISION GUIDE:**

```
Do you have SSH/VPS access?
├─ YES → Use Option 1 (Full VPS Setup)
└─ NO → Continue...

Do you have Python App in cPanel?
├─ YES → Try Option 4 (Python App)
└─ NO → Use Option 2 (Hybrid - Recommended)
```

---

## 📞 **NEXT STEPS:**

1. **Check your Hostinger plan features**
2. **Decide which option to use**
3. **I can help you set up whichever option you choose!**

**Most likely: Option 2 (Hybrid) is your best bet!** 🎯

