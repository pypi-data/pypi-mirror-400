# 🚂 Railway Operations Guide - Complete Reference

## 🎯 Your Railway Project

**Project ID:** `468b8a56-fb43-4884-99cd-200a79eef113`  
**Project Name:** SANTEK

---

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Deploying Code](#deploying-code)
3. [Running Commands](#running-commands)
4. [Service Management](#service-management)
5. [Training Models](#training-models)
6. [File Management](#file-management)
7. [Monitoring & Logs](#monitoring--logs)
8. [Environment Variables](#environment-variables)
9. [Quick Reference](#quick-reference)

---

## 🔧 Initial Setup

### Step 0: Login to Railway (REQUIRED FIRST!)

```powershell
# Login to Railway (opens browser)
railway login

# Verify login
railway whoami
```

**If you get "Unauthorized" error, you MUST login first!**

### Step 1: Link to Your Railway Project

```powershell
# Navigate to your project directory
cd "C:\Users\SCHAVALA\Downloads\SOMA-Extracted\SOMA-9a284bcf1b497d32e2041726fa2bba1e662d2770"

# Link to your Railway project
railway link -p 468b8a56-fb43-4884-99cd-200a79eef113
```

**Expected Output:**
```
✓ Linked to project SANTEK (468b8a56-fb43-4884-99cd-200a79eef113)
```

### Step 2: Verify Link

```powershell
# Check current project
railway status
```

**Expected Output:**
```
Project: SANTEK (468b8a56-fb43-4884-99cd-200a79eef113)
Service: (none)
Environment: production
```

### Step 3: Install Railway CLI (if not installed)

```powershell
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Or via npm
npm install -g @railway/cli

# Verify installation
railway --version
```

---

## 🚀 Deploying Code

### Method 1: Deploy All Files (Initial Deployment)

```powershell
# Deploy everything to Railway
railway up
```

**What this does:**
- Uploads your code to Railway
- Builds your project
- Deploys as a service
- Shows deployment logs

### Method 2: Deploy Specific Service

```powershell
# List services
railway service list

# Deploy specific service
railway up --service <service-name>
```

### Method 3: Connect to GitHub (Recommended)

```powershell
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit for Railway deployment"

# Push to GitHub
git remote add origin <your-github-repo-url>
git push -u origin main

# In Railway Dashboard:
# 1. Go to your project
# 2. Settings → Source
# 3. Connect GitHub
# 4. Select your repository
# 5. Auto-deploy on every push!
```

---

## ⚡ Running Commands

### Basic Command Execution

```powershell
# Run any command in Railway environment
railway run <command>

# Examples:
railway run python --version
railway run pip list
railway run ls -la
railway run pwd
```

### Run Python Scripts

```powershell
# Run a Python script
railway run python check_system.py

# Run with arguments
railway run python train_model.py --epochs 50 --batch-size 16

# Run from specific directory
railway run bash -c "cd soma_cognitive/slm && python SHOWCASE_SLM.py"
```

### Interactive Shell

```powershell
# Open interactive shell
railway shell

# Now you're in Railway environment
# Can run commands directly:
python --version
ls -la
cd soma_cognitive/slm
python SHOWCASE_SLM.py
exit
```

---

## 🎮 Service Management

### List Services

```powershell
# List all services in project
railway service list
```

### Create New Service

```powershell
# Create a new service
railway service create <service-name>

# Example: Create training service
railway service create soma-training
```

### Start/Stop Service

```powershell
# Stop a service
railway service stop <service-name>

# Start a service
railway service start <service-name>

# Restart a service
railway service restart <service-name>
```

### Delete Service

```powershell
# Delete a service (careful!)
railway service delete <service-name>
```

### View Service Details

```powershell
# View service info
railway service

# View specific service
railway service <service-name>
```

---

## 🤖 Training Models on Railway

### Quick Training (One-Time)

```powershell
# Train Showcase SLM
railway run python soma_cognitive/slm/SHOWCASE_SLM.py

# Train Improved SLM
railway run python soma_cognitive/slm/TRAIN_IMPROVED_SLM.py

# Train Full GPT-Style
railway run python soma_cognitive/slm/TRAIN_ON_SANTOK_DATA.py
```

### Training with Background Process

```powershell
# Run training in background (won't block terminal)
railway run nohup python soma_cognitive/slm/SHOWCASE_SLM.py > training.log 2>&1 &

# Check if still running
railway run ps aux | grep python
```

### Create Dedicated Training Service

```powershell
# 1. Create training service
railway service create soma-training

# 2. Set environment variables
railway variables set MODEL_TYPE=showcase --service soma-training
railway variables set EPOCHS=50 --service soma-training

# 3. Deploy training script
railway up --service soma-training
```

---

## 📁 File Management

### List Files

```powershell
# List files in root
railway run ls -la

# List files in specific directory
railway run ls -la soma_cognitive/slm/

# List with details
railway run ls -lh soma_cognitive/slm/*.pkl
```

### Download Files

```powershell
# Download a file
railway run cat soma_cognitive/slm/soma_showcase_slm.pkl > model.pkl

# Download directory (using tar)
railway run tar -czf models.tar.gz soma_cognitive/slm/*.pkl
railway run cat models.tar.gz > models.tar.gz
```

### Upload Files

```powershell
# Upload a file
railway run bash -c "cat > file.txt" < local_file.txt

# Or use Railway volumes (persistent storage)
railway volume create models-storage
railway volume mount models-storage /data/models
```

### Check File Sizes

```powershell
# Check file sizes
railway run du -sh soma_cognitive/slm/*.pkl

# Check directory size
railway run du -sh soma_cognitive/slm/
```

### Delete Files

```powershell
# Delete a file
railway run rm soma_cognitive/slm/old_model.pkl

# Delete directory
railway run rm -rf temp_directory/
```

---

## 📊 Monitoring & Logs

### View Logs

```powershell
# View logs for current service
railway logs

# View logs for specific service
railway logs --service <service-name>

# View logs (Railway CLI doesn't support --follow, use Dashboard instead)
# For real-time logs, use Railway Dashboard → Your Service → Logs tab

# View specific deployment logs
railway logs <deployment-id>
```

### View Metrics

```powershell
# View service metrics (CPU, RAM, Network)
# Go to Railway Dashboard → Your Service → Metrics tab
```

### Check Resource Usage

```powershell
# Check RAM usage
railway run free -h

# Check CPU usage
railway run top -bn1 | head -20

# Check disk usage
railway run df -h

# Check process list
railway run ps aux
```

---

## 🔐 Environment Variables

### List Variables

```powershell
# List all environment variables
railway variables

# List for specific service
railway variables --service <service-name>
```

### Set Variables

```powershell
# Set a variable
railway variables set KEY=value

# Set for specific service
railway variables set KEY=value --service <service-name>

# Set multiple variables
railway variables set MODEL_TYPE=showcase EPOCHS=50 BATCH_SIZE=16
```

### Get Variable Value

```powershell
# Get variable value
railway variables get KEY

# Get for specific service
railway variables get KEY --service <service-name>
```

### Delete Variable

```powershell
# Delete a variable
railway variables delete KEY

# Delete for specific service
railway variables delete KEY --service <service-name>
```

### Common Training Variables

```powershell
# Set training configuration
railway variables set MODEL_TYPE=showcase
railway variables set EPOCHS=50
railway variables set BATCH_SIZE=16
railway variables set LEARNING_RATE=0.0001
railway variables set MAX_RAM_GB=8
```

---

## 🎯 Complete Training Workflow

### Step-by-Step: Train Model on Railway

```powershell
# 1. Link to project (if not done)
railway link -p 468b8a56-fb43-4884-99cd-200a79eef113

# 2. Deploy code
railway up

# 3. Set training variables
railway variables set MODEL_TYPE=showcase
railway variables set EPOCHS=20

# 4. Run training
railway run python soma_cognitive/slm/SHOWCASE_SLM.py

# 5. Monitor logs (in another terminal)
railway logs --follow

# 6. Check if model was created
railway run ls -lh soma_cognitive/slm/*.pkl

# 7. Download model
railway run cat soma_cognitive/slm/soma_showcase_slm.pkl > model.pkl

# 8. Verify download
ls -lh model.pkl
```

---

## 🔄 Common Operations

### Check Project Status

```powershell
# Current project info
railway status

# List all projects
railway projects

# Switch project
railway link -p <project-id>
```

### View Deployment History

```powershell
# View deployments
# Go to Railway Dashboard → Your Service → Deployments tab
```

### Redeploy Service

```powershell
# Redeploy current service
railway up

# Redeploy specific service
railway up --service <service-name>
```

### View Service URL

```powershell
# Get service URL
railway domain

# Or check in Railway Dashboard
```

---

## 🛠️ Troubleshooting

### Service Won't Start

```powershell
# Check logs
railway logs --tail 100

# Check environment variables
railway variables

# Verify code deployed
railway run ls -la
```

### Command Not Found

```powershell
# Check if in Railway environment
railway run which python
railway run which pip

# Install dependencies
railway run pip install -r requirements.txt
```

### Out of Memory

```powershell
# Check RAM usage
railway run free -h

# Check process memory
railway run ps aux --sort=-%mem | head -10

# Reduce batch size in training
railway variables set BATCH_SIZE=8
```

### Files Not Persisting

```powershell
# Use Railway volumes for persistent storage
railway volume create persistent-storage
railway volume mount persistent-storage /data
```

---

## 📝 Quick Reference Card

### Essential Commands

```powershell
# Link to project
railway link -p 468b8a56-fb43-4884-99cd-200a79eef113

# Deploy
railway up

# Run command
railway run <command>

# View logs (use Dashboard for real-time)
railway logs

# Set variable
railway variables set KEY=value

# List services
railway service list

# Open shell
railway shell

# Check status
railway status
```

### Training Commands

```powershell
# Train Showcase SLM
railway run python soma_cognitive/slm/SHOWCASE_SLM.py

# Train Improved SLM
railway run python soma_cognitive/slm/TRAIN_IMPROVED_SLM.py

# Train Full GPT-Style
railway run python soma_cognitive/slm/TRAIN_ON_SANTOK_DATA.py

# Check trained models
railway run ls -lh soma_cognitive/slm/*.pkl

# Download model
railway run cat soma_cognitive/slm/soma_showcase_slm.pkl > model.pkl
```

### Service Management

```powershell
# Create service
railway service create <name>

# Start service
railway service start <name>

# Stop service
railway service stop <name>

# Restart service
railway service restart <name>

# Delete service
railway service delete <name>
```

---

## 🎓 Example Workflows

### Workflow 1: First Time Setup

```powershell
# 1. Link project
railway link -p 468b8a56-fb43-4884-99cd-200a79eef113

# 2. Verify
railway status

# 3. Deploy
railway up

# 4. Check logs
railway logs
```

### Workflow 2: Train Model

```powershell
# 1. Set variables
railway variables set MODEL_TYPE=showcase EPOCHS=20

# 2. Run training
railway run python soma_cognitive/slm/SHOWCASE_SLM.py

# 3. Monitor (new terminal)
railway logs --follow

# 4. Download model
railway run cat soma_cognitive/slm/soma_showcase_slm.pkl > model.pkl
```

### Workflow 3: Update Code

```powershell
# 1. Make changes locally
# ... edit files ...

# 2. Deploy changes
railway up

# 3. Verify deployment
railway logs --tail 50
```

---

## 💡 Pro Tips

1. **Use Railway Dashboard:**
   - Visual interface for everything
   - Easier to manage services
   - Better log viewing

2. **GitHub Integration:**
   - Connect to GitHub for auto-deploy
   - Every push = automatic deployment
   - No need for `railway up`

3. **Environment Variables:**
   - Set in Railway Dashboard (easier)
   - Or use CLI for automation

4. **Logs:**
   - Use `--follow` for real-time monitoring
   - Use Dashboard for better log viewing

5. **Volumes:**
   - Use volumes for persistent storage
   - Models won't be lost on redeploy

6. **Background Jobs:**
   - Use `nohup` for long-running tasks
   - Or create dedicated service

---

## 🚀 Next Steps

1. ✅ **Link to Project:** `railway link -p 468b8a56-fb43-4884-99cd-200a79eef113`
2. 🚀 **Deploy Code:** `railway up`
3. 🎯 **Train Model:** `railway run python soma_cognitive/slm/SHOWCASE_SLM.py`
4. 📊 **Monitor:** `railway logs --follow`
5. 💾 **Download:** `railway run cat soma_cognitive/slm/soma_showcase_slm.pkl > model.pkl`

---

**Ready to start? Run:**
```powershell
railway link -p 468b8a56-fb43-4884-99cd-200a79eef113
railway up
```
