# 🚀 Railway Pro - Quick Start for Real LLM Training

## ✅ Ready to Train!

You have Railway Pro and want to train a **real production LLM**. Here's the fastest path:

---

## 🎯 Option 1: Start with Improved SLM (Recommended)

**Best for:** Testing, validation, quick results
**Time:** 1-2 hours
**Size:** 20-50 MB

```powershell
# Train Improved SLM
railway run python soma_cognitive/slm/TRAIN_IMPROVED_SLM.py
```

**What you get:**
- 8,000 token vocabulary
- 4 layers, 256 dim
- Good quality for SOMA topics
- Fast training

---

## 🎯 Option 2: Train Full GPT Model (Production)

**Best for:** Production use, best quality
**Time:** 4-8 hours
**Size:** ~500 MB

```powershell
# Train Full GPT Model
railway run python soma_cognitive/slm/TRAIN_FULL_GPT_RAILWAY.py
```

**What you get:**
- 60,000 token vocabulary
- 12 layers, 768 dim
- Production-quality generation
- Full GPT-2 style architecture

---

## 📋 Pre-Flight Checklist

Before training, verify:

- [ ] Railway Pro subscription active
- [ ] Service linked: `railway link -p 468b8a56-fb43-4884-99cd-200a79eef113`
- [ ] Service has resources:
  - RAM: 12 GB (for full model) or 6 GB (for improved)
  - CPU: 8 cores (for full) or 4 cores (for improved)
  - Storage: 10 GB free
- [ ] Training script exists:
  - `TRAIN_IMPROVED_SLM.py` ✅
  - `TRAIN_FULL_GPT_RAILWAY.py` ✅

---

## 🚀 Training Commands

### Improved SLM (1-2 hours):
```powershell
railway run python soma_cognitive/slm/TRAIN_IMPROVED_SLM.py
```

### Full GPT Model (4-8 hours):
```powershell
railway run python soma_cognitive/slm/TRAIN_FULL_GPT_RAILWAY.py
```

---

## 📊 Monitor Training

### View Logs:
```powershell
# Check recent logs
railway logs --tail 50

# Or use Railway Dashboard
# https://railway.app → Your Project → Service → Logs
```

### Expected Output:
```
Building vocabulary from 1000 texts...
[OK] Vocabulary built: 60,000 tokens

Initializing model weights...
[OK] Model initialized: 124,000,000 parameters

Creating training pairs...
[OK] Created 50,000 training pairs

Training for 50 epochs...
Epoch 1/50 complete - Average Loss: 6.2542
...
Epoch 50/50 complete - Average Loss: 2.5000

[OK] Model saved: 485.23 MB
```

---

## ⚙️ Railway Pro Configuration

### Set Resources (Railway Dashboard):

1. Go to: https://railway.app
2. Select your project → Service
3. Settings → Resources:
   - **For Improved SLM:**
     - RAM: 6 GB
     - CPU: 4 cores
   - **For Full GPT:**
     - RAM: 12 GB
     - CPU: 8 cores

### Environment Variables (Optional):

```bash
# Set in Railway Dashboard → Variables
TRAINING_EPOCHS=50
BATCH_SIZE=32
LEARNING_RATE=0.0001
```

---

## 🎯 Recommended Training Path

### Path 1: Quick Validation
1. Train Improved SLM (1-2 hours)
2. Test generation
3. If good, train Full GPT

### Path 2: Direct Production
1. Train Full GPT directly (4-8 hours)
2. Monitor closely
3. Download when complete

---

## 📥 After Training

### Download Model:
```powershell
# Check model file
railway run ls -lh soma_full_gpt_model.pkl

# Download via Railway Dashboard
# Dashboard → Service → Files → Download
```

### Test Locally:
```python
import pickle

# Load model
model = pickle.load(open('soma_full_gpt_model.pkl', 'rb'))

# Generate
result = model.generate("SOMA is", max_tokens=100)
print(result)
```

---

## 🚨 Troubleshooting

### Out of Memory:
- Reduce batch size: `BATCH_SIZE=16`
- Or reduce model: `N_LAYERS=8`, `D_MODEL=512`

### Training Too Slow:
- Increase Railway resources
- Or reduce epochs: `EPOCHS=30`

### Model Not Learning:
- Check vocabulary built
- Verify training pairs > 0
- Check loss is decreasing

---

## 📚 Full Documentation

- **Complete Guide:** `TRAIN_REAL_LLM_RAILWAY_PRO.md`
- **Railway Operations:** `RAILWAY_OPERATIONS_GUIDE.md`
- **Training Analysis:** `TRAINING_SUCCESS_ANALYSIS.md`

---

## 🎉 Ready to Start!

**Recommended:** Start with Improved SLM, then move to Full GPT.

**Command:**
```powershell
railway run python soma_cognitive/slm/TRAIN_IMPROVED_SLM.py
```

**Or go straight to production:**
```powershell
railway run python soma_cognitive/slm/TRAIN_FULL_GPT_RAILWAY.py
```

---

**Let's train your real LLM! 🚀**
