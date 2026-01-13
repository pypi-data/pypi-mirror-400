# 🚂 Railway Training Guide for SOMA LLM Development

## 🎯 Why Use Railway for Training?

### Advantages Over Local Training:

✅ **Better Resources:**
- Railway provides dedicated CPU resources
- More RAM available (depending on your plan)
- No impact on your local machine
- Can run training 24/7 without keeping your laptop on

✅ **No Local RAM Constraints:**
- Your local machine: 2.1 GB free (87% used)
- Railway: Can allocate more resources
- No need to close applications

✅ **Reliable & Scalable:**
- Railway handles resource management
- Can scale up if needed
- Automatic restarts on failure

✅ **Background Processing:**
- Train models while using your laptop normally
- No performance impact on local machine
- Can monitor via Railway dashboard

---

## 📊 Railway Resource Options

### Railway Plans (Check Your Subscription):

| Plan | RAM | CPU | Best For |
|------|-----|-----|----------|
| **Hobby** | 512 MB - 8 GB | Shared | Showcase SLM |
| **Pro** | Up to 32 GB | Dedicated | Improved SLM, Full GPT-Style |
| **Team** | Up to 64 GB | Dedicated | Large models, multiple services |

**Note:** Check your Railway dashboard to see your current plan and available resources.

---

## 🚀 Setting Up Training on Railway

### Option 1: Create a Training Service (Recommended)

#### Step 1: Create New Service in Railway

1. Go to Railway Dashboard: https://railway.app
2. Open your project (or create new one)
3. Click **"+ New"** → **"Empty Service"**
4. Name it: **"soma-training"** or **"llm-trainer"**

#### Step 2: Configure the Service

**Environment Variables:**
```bash
# Training Configuration
TRAINING_MODE=railway
MODEL_TYPE=showcase  # or "improved" or "full"
EPOCHS=50
BATCH_SIZE=16
LEARNING_RATE=0.0001

# Resource Limits (adjust based on your plan)
MAX_RAM_GB=8
MAX_CPU_CORES=4
```

**Build Configuration:**
- **Builder:** Nixpacks (auto-detects Python)
- **Start Command:** `python train_on_railway.py`

#### Step 3: Create Training Script

Create `train_on_railway.py` in project root:

```python
#!/usr/bin/env python3
"""
Railway Training Script for SOMA SLM
Optimized for cloud deployment
"""

import os
import sys
import psutil

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'soma_cognitive/slm'))

print("=" * 70)
print("SOMA SLM Training on Railway")
print("=" * 70)
print()

# Check resources
ram = psutil.virtual_memory()
print(f"Available RAM: {ram.total / (1024**3):.2f} GB")
print(f"Free RAM: {ram.available / (1024**3):.2f} GB")
print()

# Get model type from environment
model_type = os.getenv('MODEL_TYPE', 'showcase').lower()
epochs = int(os.getenv('EPOCHS', '50'))
batch_size = int(os.getenv('BATCH_SIZE', '16'))

print(f"Model Type: {model_type}")
print(f"Epochs: {epochs}")
print(f"Batch Size: {batch_size}")
print()

# Import and train
try:
    from soma_cognitive.slm.soma_gpt import SOMALGM, SOMALGMConfig
    
    if model_type == 'showcase':
        from soma_cognitive.slm.SHOWCASE_SLM import train_showcase_model
        print("Training Showcase SLM...")
        train_showcase_model()
        
    elif model_type == 'improved':
        from soma_cognitive.slm.TRAIN_IMPROVED_SLM import train_improved_model
        print("Training Improved SLM...")
        train_improved_model(epochs=epochs, batch_size=batch_size)
        
    elif model_type == 'full':
        from soma_cognitive.slm.TRAIN_ON_SANTOK_DATA import train_full_model
        print("Training Full GPT-Style Model...")
        train_full_model(epochs=epochs, batch_size=batch_size)
        
    else:
        print(f"Unknown model type: {model_type}")
        print("Available: showcase, improved, full")
        sys.exit(1)
        
    print()
    print("=" * 70)
    print("[OK] Training Complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"[ERROR] Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
```

#### Step 4: Deploy and Train

1. **Push to Railway:**
   ```bash
   railway up
   ```

2. **Or connect to GitHub:**
   - Connect Railway to your GitHub repo
   - Push code: `git push`
   - Railway auto-deploys

3. **Monitor Training:**
   - Go to Railway Dashboard
   - Click on your training service
   - View **Logs** tab to see training progress

4. **Download Model:**
   - After training, model is saved in Railway filesystem
   - Use Railway CLI to download:
     ```bash
     railway run ls -lh soma_cognitive/slm/*.pkl
     railway run cat soma_cognitive/slm/soma_showcase_slm.pkl > model.pkl
     ```

---

### Option 2: Use Railway CLI for One-Time Training

#### Quick Training Command:

```bash
# Train Showcase SLM
railway run python soma_cognitive/slm/SHOWCASE_SLM.py

# Train Improved SLM
railway run python soma_cognitive/slm/TRAIN_IMPROVED_SLM.py

# Train Full GPT-Style
railway run python soma_cognitive/slm/TRAIN_ON_SANTOK_DATA.py
```

**Note:** This runs training in Railway's environment but doesn't persist the service.

---

### Option 3: Add Training Endpoint to Existing Service

Add a training endpoint to your existing Railway backend service:

**In `src/servers/main_server.py` (or your main server):**

```python
from fastapi import BackgroundTasks
import os

@app.post("/api/v1/train-model")
async def train_model(
    model_type: str = "showcase",
    epochs: int = 50,
    background_tasks: BackgroundTasks = None
):
    """
    Start model training in background
    """
    def train():
        if model_type == "showcase":
            os.system("python soma_cognitive/slm/SHOWCASE_SLM.py")
        elif model_type == "improved":
            os.system("python soma_cognitive/slm/TRAIN_IMPROVED_SLM.py")
        # ... etc
    
    background_tasks.add_task(train)
    return {"status": "training_started", "model_type": model_type}

@app.get("/api/v1/training-status")
async def training_status():
    """
    Check training status
    """
    # Check if training process is running
    # Return status
    pass
```

Then trigger training via API:
```bash
curl -X POST "https://your-railway-app.up.railway.app/api/v1/train-model?model_type=showcase"
```

---

## 📋 Railway Training Configuration

### Recommended Settings by Model:

#### Showcase SLM:
```bash
MODEL_TYPE=showcase
EPOCHS=20
BATCH_SIZE=8
RAM_LIMIT=2GB
```

#### Improved SLM:
```bash
MODEL_TYPE=improved
EPOCHS=50
BATCH_SIZE=16
RAM_LIMIT=4GB
```

#### Full GPT-Style:
```bash
MODEL_TYPE=full
EPOCHS=10
BATCH_SIZE=32
RAM_LIMIT=8GB
```

---

## 🔍 Monitoring Training on Railway

### View Logs:
1. Railway Dashboard → Your Service
2. Click **"Logs"** tab
3. Real-time training output

### Check Resource Usage:
1. Railway Dashboard → Your Service
2. Click **"Metrics"** tab
3. Monitor CPU, RAM, Network

### Download Model After Training:
```bash
# List trained models
railway run ls -lh soma_cognitive/slm/*.pkl

# Download model
railway run cat soma_cognitive/slm/soma_showcase_slm.pkl > model.pkl
```

---

## 💡 Best Practices

### 1. **Start Small:**
   - Begin with Showcase SLM
   - Verify training works
   - Then scale up

### 2. **Monitor Resources:**
   - Watch RAM usage in Railway dashboard
   - Adjust batch size if needed
   - Railway may auto-scale if on Pro plan

### 3. **Save Models:**
   - Models are saved to Railway filesystem
   - Download after training completes
   - Or use Railway volumes for persistence

### 4. **Use Background Jobs:**
   - Training can take hours
   - Use Railway's background job feature
   - Or run as separate service

### 5. **Cost Management:**
   - Monitor usage in Railway dashboard
   - Stop service when not training
   - Use scheduled deployments for overnight training

---

## 🆚 Railway vs Local Training Comparison

| Aspect | Local (Your Machine) | Railway |
|--------|---------------------|---------|
| **RAM Available** | 2.1 GB (need to free) | 2-32 GB (plan dependent) |
| **CPU** | 12 cores (shared) | Dedicated (Pro plan) |
| **Training Time** | Same | Same (depends on resources) |
| **Cost** | Free | Subscription cost |
| **Convenience** | Need to free RAM | Just deploy |
| **Monitoring** | Local logs | Railway dashboard |
| **Background** | Uses your machine | Runs in cloud |

---

## 🎯 Recommended Approach

### For Quick Testing:
- **Use Local:** Showcase SLM (10-30 min)
- Free up RAM first

### For Production Training:
- **Use Railway:** Improved SLM or Full GPT-Style
- Better resources
- No local impact
- Can run overnight

### Hybrid Approach:
- **Local:** Development, testing, small models
- **Railway:** Production training, large models, scheduled jobs

---

## 🚀 Quick Start on Railway

1. **Create Training Service:**
   ```bash
   railway service create soma-training
   ```

2. **Set Environment Variables:**
   ```bash
   railway variables set MODEL_TYPE=showcase
   railway variables set EPOCHS=20
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

4. **Monitor:**
   - Railway Dashboard → Logs

5. **Download Model:**
   ```bash
   railway run cat soma_cognitive/slm/soma_showcase_slm.pkl > model.pkl
   ```

---

## 📝 Next Steps

1. ✅ **Check Railway Plan** - See available resources
2. 🎯 **Choose Training Method** - Service, CLI, or API endpoint
3. 🚀 **Deploy Training Script** - Set up on Railway
4. 📊 **Monitor Training** - Watch logs and metrics
5. 💾 **Download Models** - Get trained models after completion

---

**Status:** Railway is an excellent option for training, especially for larger models!

**Recommendation:** Use Railway for Improved SLM and Full GPT-Style models, use local for quick Showcase SLM testing.
