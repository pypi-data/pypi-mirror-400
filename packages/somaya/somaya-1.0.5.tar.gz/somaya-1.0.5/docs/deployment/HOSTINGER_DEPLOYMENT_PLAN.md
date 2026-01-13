# 🎯 Hostinger Deployment Plan - Based on Support Answers

## ✅ **WHAT WE CAN DO:**

Based on Hostinger's answers, here's what's **POSSIBLE**:

### ✅ **Available:**
- SSH access (good for file uploads)
- Static Node.js apps (frontend only)
- Basic Python scripts (cron jobs)
- File system access

### ❌ **NOT Available:**
- Python FastAPI backend
- Long-running processes
- WebSocket support
- Full-stack Node.js
- Backend services

---

## 🚀 **SOLUTION: Hybrid Deployment**

### **Frontend → Hostinger (Static Files)**
- Build Next.js as static export
- Upload via SSH/FTP
- Works perfectly!

### **Backend → Railway/Render (Free Tier)**
- Deploy Python FastAPI separately
- Full features (WebSocket, background jobs)
- Free tier available

---

## 📋 **STEP-BY-STEP DEPLOYMENT:**

### **PART 1: Prepare Frontend for Static Export**

#### Step 1: Update Next.js Config

Update `frontend/next.config.js` to support static export:

```javascript
/** @type {import('next').NextConfig} */
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
  runtimeCaching: [
    {
      urlPattern: /^https?.*/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'offlineCache',
        expiration: {
          maxEntries: 200,
        },
      },
    },
  ],
})

const nextConfig = {
  output: 'export', // Enable static export
  images: {
    unoptimized: true, // Required for static export
    domains: ['localhost', 'sbackend.up.railway.app', 'keen-happiness-production.up.railway.app'],
  },
  trailingSlash: true, // Better for static hosting
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  compress: true,
  poweredByHeader: false,
  reactStrictMode: true,
  swcMinify: true,
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
    }
    
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      }
    }
    
    return config
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          },
        ],
      },
    ]
  },
}

module.exports = withPWA(nextConfig)
```

#### Step 2: Create Environment File

Create `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

(We'll update this after backend is deployed)

#### Step 3: Build Frontend

```bash
cd frontend
npm install
npm run build
```

This creates `frontend/out/` folder with static files.

---

### **PART 2: Deploy Backend to Railway**

#### Step 1: Use Your Existing ZIP

You already have `soma_railway.zip` - perfect!

#### Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up/login (free tier available)
3. Click "New Project"
4. Choose "Deploy from GitHub" OR "Upload ZIP"
5. Upload `soma_railway.zip`
6. Railway auto-detects and deploys

#### Step 3: Get Backend URL

- Railway provides URL like: `https://xxx.up.railway.app`
- Copy this URL
- Update `frontend/.env.production` with this URL
- Rebuild frontend: `npm run build`

#### Step 4: Set Environment Variables (if needed)

In Railway dashboard:
- Go to your project → Variables
- Add any required env vars (API keys, etc.)

---

### **PART 3: Upload Frontend to Hostinger**

#### Option A: Via SSH (Recommended)

```bash
# Connect via SSH
ssh your-username@your-domain.com

# Navigate to public_html
cd public_html

# Upload files from frontend/out/ folder
# Use FTP client like FileZilla, or:
scp -r /path/to/frontend/out/* your-username@your-domain.com:~/public_html/
```

#### Option B: Via FTP/cPanel

1. Open FileZilla or FTP client
2. Connect to your Hostinger FTP
3. Navigate to `public_html/`
4. Upload ALL files from `frontend/out/` folder
5. Make sure `index.html` is in root

#### Option C: Via cPanel File Manager

1. Login to cPanel
2. Go to File Manager
3. Navigate to `public_html/`
4. Upload files from `frontend/out/`

---

### **PART 4: Configure CORS (Important!)**

Your backend needs to allow requests from your Hostinger domain.

Update `backend/src/servers/main_server.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-domain.com",  # Add your Hostinger domain
        "https://www.your-domain.com",  # Add www version
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Or allow all origins (for development):
```python
allow_origins=["*"]
```

---

## 🔧 **ALTERNATIVE: Use Subdomain**

If you want to keep main domain for something else:

1. **Create subdomain in Hostinger:**
   - `app.yourdomain.com` → points to `public_html/app/`

2. **Upload frontend to:**
   - `public_html/app/` folder

3. **Access via:**
   - `https://app.yourdomain.com`

---

## 📝 **FINAL CHECKLIST:**

- [ ] Updated `frontend/next.config.js` with `output: 'export'`
- [ ] Created `frontend/.env.production` with backend URL
- [ ] Built frontend: `npm run build`
- [ ] Deployed backend to Railway
- [ ] Got backend URL from Railway
- [ ] Updated frontend `.env.production` with backend URL
- [ ] Rebuilt frontend with correct backend URL
- [ ] Updated backend CORS to allow Hostinger domain
- [ ] Uploaded `frontend/out/` files to Hostinger `public_html/`
- [ ] Tested: Visit your domain → should see frontend
- [ ] Tested: Frontend should connect to Railway backend

---

## 🎯 **QUICK COMMANDS:**

```bash
# 1. Build frontend
cd frontend
npm install
npm run build

# 2. Upload to Hostinger (via SSH)
scp -r out/* your-username@your-domain.com:~/public_html/

# 3. Or use FTP client to upload out/ folder contents
```

---

## 🐛 **TROUBLESHOOTING:**

### **Frontend shows but API calls fail:**
- Check CORS settings in backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check browser console for errors

### **404 errors on routes:**
- Make sure `trailingSlash: true` in next.config.js
- Check `.htaccess` file (may need to add rewrite rules)

### **Backend not responding:**
- Check Railway logs
- Verify backend is running
- Check environment variables

---

## 💰 **COST:**

- **Hostinger:** Already paid (Business plan)
- **Railway:** Free tier (500 hours/month) or $5/month for more
- **Total:** $0-5/month

---

## ✅ **RESULT:**

- ✅ Frontend hosted on Hostinger (your domain)
- ✅ Backend hosted on Railway (reliable, fast)
- ✅ Full features working (WebSocket, background jobs)
- ✅ Professional setup
- ✅ Cost-effective

---

## 🚀 **READY TO DEPLOY?**

1. I can help you update the Next.js config
2. I can help you set up Railway deployment
3. I can create upload scripts

**Let me know when you're ready!** 🎯

