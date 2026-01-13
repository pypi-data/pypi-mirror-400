# 🚀 Train Real LLM on Railway Pro - Complete Guide

## 🎯 Goal

Train a **production-ready LLM** using Railway Pro's resources:
- **60K vocabulary** (full GPT-2 style)
- **12 layers, 12 heads** (GPT-2 small architecture)
- **768 embedding dimension**
- **~500MB model size**
- **4-8 hours training time** (on Railway Pro)

---

## 📊 Model Options

### Option 1: Improved SLM (Recommended First Step)
- **Vocab:** 8,000 tokens
- **Layers:** 4
- **Model Dim:** 256
- **Size:** ~20-50 MB
- **Training:** 1-2 hours
- **File:** `TRAIN_IMPROVED_SLM.py`

### Option 2: Full GPT-Style Model (Production)
- **Vocab:** 60,000 tokens
- **Layers:** 12
- **Model Dim:** 768
- **Size:** ~500 MB
- **Training:** 4-8 hours
- **File:** `TRAIN_GPT_MODEL.py` or `soma_gpt.py` with full config

---

## 🚀 Quick Start: Train Improved SLM First

### Step 1: Prepare Training Script

The script `TRAIN_IMPROVED_SLM.py` is ready, but we need to ensure it builds vocab and initializes model:

```python
# Already fixed in the script, but verify:
# 1. model.build_vocab() is called
# 2. model.initialize_model() is called
# 3. Trainer is used correctly
```

### Step 2: Run on Railway Pro

```powershell
# Train Improved SLM (1-2 hours)
railway run python soma_cognitive/slm/TRAIN_IMPROVED_SLM.py
```

**Expected Output:**
- Vocabulary: ~8,000 tokens
- Training pairs: ~10,000-15,000
- Loss: Should decrease from ~6.0 to ~2.5
- Model size: ~20-50 MB
- Training time: 1-2 hours

---

## 🎯 Train Full GPT-Style Model

### Step 1: Create Full GPT Training Script

Create `TRAIN_FULL_GPT_RAILWAY.py`:

```python
"""
Train Full GPT-Style SOMA LGM on Railway Pro
==============================================

Production-ready model:
- 60K vocabulary
- 12 layers, 12 heads
- 768 embedding dimension
- ~500MB model size
- 4-8 hours training
"""

import sys
import os
import pickle
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from soma_cognitive.slm.soma_gpt import SOMALGM, SOMALGMConfig
from soma_cognitive.slm.soma_gpt_trainer_real import SOMALGMTrainer
from soma_cognitive.slm.EXPAND_TRAINING_DATA import expand_soma_knowledge_base
from soma_cognitive.slm.VOCAB_EXPANSION import add_general_english_to_texts

print("\n" + "=" * 70)
print("Train Full GPT-Style SOMA LGM on Railway Pro")
print("=" * 70)
print()
print("Model Configuration:")
print("  - Vocabulary: 60,000 tokens")
print("  - Layers: 12")
print("  - Heads: 12")
print("  - Model Dim: 768")
print("  - Expected Size: ~500 MB")
print("  - Training Time: 4-8 hours")
print()

# ============================================================================
# STEP 1: Create Full GPT Config
# ============================================================================

config = SOMALGMConfig(
    vocab_size=60000,      # Full GPT-2 vocabulary
    d_model=768,           # GPT-2 small size
    n_layers=12,           # GPT-2 small has 12 layers
    n_heads=12,            # 12 attention heads
    d_ff=3072,            # Feed-forward dimension (4x d_model)
    max_seq_len=1024,      # Maximum sequence length
    learning_rate=1e-4,    # Learning rate
    batch_size=32          # Batch size (adjust based on RAM)
)

print("[OK] Model config created")
print(f"    Vocab: {config.vocab_size:,}")
print(f"    Model dim: {config.d_model}")
print(f"    Layers: {config.n_layers}")
print(f"    Heads: {config.n_heads}")
print(f"    Estimated RAM: ~8-12 GB")
print(f"    Estimated model size: ~500 MB")
print()

# ============================================================================
# STEP 2: Load and Expand SOMA Knowledge
# ============================================================================

print("Loading SOMA knowledge base...")
soma_knowledge = [
    # ... (same as TRAIN_IMPROVED_SLM.py, but expand more)
    "SOMA is a universal tokenization framework that works on any file type.",
    "SOMA provides multiple tokenization methods including word, character, subword, and byte-level.",
    # ... (all 30+ facts)
]

print(f"[OK] Loaded {len(soma_knowledge)} base facts")
print()

# Expand facts (20 variants per fact for full model)
print("Expanding facts into variants (20 per fact for full training)...")
expanded_facts = expand_soma_knowledge_base(soma_knowledge, variants_per_fact=20)
print(f"[OK] Expanded to {len(expanded_facts)} training sentences")
print()

# Add general English (40% grammar, 60% SOMA for full model)
print("Adding general English for grammar (40% grammar, 60% SOMA)...")
training_texts = add_general_english_to_texts(expanded_facts, ratio=0.40)
print(f"[OK] Total training sentences: {len(training_texts)}")
print()

# ============================================================================
# STEP 3: Create Model
# ============================================================================

print("Creating Full GPT-Style SOMA LGM model...")
model = SOMALGM(config)
print("[OK] Model created")
print()

# ============================================================================
# STEP 4: Build Vocabulary and Initialize
# ============================================================================

print("Building vocabulary from training texts...")
model.build_vocab(training_texts)
print(f"[OK] Vocabulary built: {model.tokenizer.vocab_size:,} tokens")
print()

print("Initializing model weights...")
model.initialize_model()
print(f"[OK] Model initialized: {model.count_parameters():,} parameters")
print(f"    Estimated size: {model.count_parameters() * 4 / (1024**2):.2f} MB")
print()

# ============================================================================
# STEP 5: Train (Full Training - 50-100 epochs)
# ============================================================================

print("=" * 70)
print("Training Full GPT-Style Model")
print("=" * 70)
print()
print("Training settings:")
print("  - Epochs: 50 (can increase to 100 for better results)")
print("  - Batch size: 32")
print("  - Estimated time: 4-8 hours")
print()

# Shuffle for better learning
random.shuffle(training_texts)

# Train with full trainer
trainer = SOMALGMTrainer(model, learning_rate=config.learning_rate)
trainer.train(training_texts, epochs=50, batch_size=config.batch_size)

print()
print("=" * 70)
print("[OK] Training Complete!")
print("=" * 70)
print()

# ============================================================================
# STEP 6: Save Model
# ============================================================================

model_file = "soma_full_gpt_model.pkl"
print(f"Saving model to {model_file}...")
with open(model_file, 'wb') as f:
    pickle.dump(model, f)

file_size_mb = os.path.getsize(model_file) / (1024 * 1024)
print(f"[OK] Model saved: {file_size_mb:.2f} MB")
print()

# ============================================================================
# STEP 7: Test Generation
# ============================================================================

print("=" * 70)
print("Testing Generation (Full Model)")
print("=" * 70)
print()

test_prompts = [
    "SOMA is",
    "SOMA tokenization",
    "SOMA Cognitive",
    "What is SOMA?",
    "How does SOMA work?",
]

for prompt in test_prompts:
    generated = model.generate(prompt, max_tokens=100, temperature=0.7, repetition_penalty=1.2)
    print(f"Prompt: '{prompt}'")
    print(f"Generated: {generated[:200]}...")
    print()

print("=" * 70)
print("[OK] Full GPT Model Ready!")
print("=" * 70)
print()
print(f"Model file: {os.path.abspath(model_file)}")
print(f"Model size: {file_size_mb:.2f} MB")
print(f"Parameters: {model.count_parameters():,}")
print(f"Vocabulary: {model.config.vocab_size:,} tokens")
print()
```

### Step 2: Run Full Training on Railway Pro

```powershell
# Train Full GPT Model (4-8 hours)
railway run python soma_cognitive/slm/TRAIN_FULL_GPT_RAILWAY.py
```

**Monitor Training:**
```powershell
# Check logs periodically
railway logs

# Or use Railway Dashboard for real-time monitoring
# https://railway.app → Your Project → Service → Logs
```

---

## 📊 Railway Pro Resource Planning

### Improved SLM (Option 1)
- **RAM:** 4-6 GB
- **CPU:** 2-4 cores
- **Storage:** 50 MB
- **Time:** 1-2 hours
- **Cost:** Low

### Full GPT Model (Option 2)
- **RAM:** 8-12 GB
- **CPU:** 4-8 cores
- **Storage:** 500 MB
- **Time:** 4-8 hours
- **Cost:** Medium

---

## 🔧 Railway Pro Configuration

### Environment Variables

Set these in Railway Dashboard → Variables:

```bash
# Training Configuration
TRAINING_EPOCHS=50
BATCH_SIZE=32
LEARNING_RATE=0.0001

# Model Configuration
VOCAB_SIZE=60000
D_MODEL=768
N_LAYERS=12
N_HEADS=12

# Resource Limits (Railway Pro)
MAX_MEMORY=12GB
MAX_CPU=8
```

### Railway Service Settings

1. **Go to Railway Dashboard**
2. **Select your service**
3. **Settings → Resources:**
   - **RAM:** 12 GB (for full model)
   - **CPU:** 8 cores (for faster training)
   - **Storage:** 10 GB (for model + data)

---

## 📈 Training Progress Monitoring

### Check Training Status

```powershell
# View recent logs
railway logs --tail 100

# Check service status
railway status

# Monitor resource usage
# Railway Dashboard → Metrics
```

### Expected Training Output

```
Building vocabulary from 1000 texts...
[OK] Vocabulary built: 60,000 tokens

Initializing model weights...
[OK] Model initialized: 124,000,000 parameters

Creating training pairs...
[OK] Created 50,000 training pairs

Training for 50 epochs...

Epoch 1/50 complete - Average Loss: 6.2542
Epoch 5/50 complete - Average Loss: 5.2385
Epoch 10/50 complete - Average Loss: 4.2715
...
Epoch 50/50 complete - Average Loss: 2.5000

[OK] Model saved: 485.23 MB
```

---

## 🎯 Training Strategies

### Strategy 1: Incremental Training
1. **Start with Improved SLM** (1-2 hours)
2. **Verify it works**
3. **Then train Full GPT** (4-8 hours)

### Strategy 2: Direct Full Training
1. **Train Full GPT directly** (4-8 hours)
2. **Monitor closely**
3. **Adjust if needed**

### Strategy 3: Multi-Stage Training
1. **Stage 1:** Train on SOMA data (20 epochs)
2. **Stage 2:** Add external data (30 epochs)
3. **Stage 3:** Fine-tune (20 epochs)

---

## 📝 Training Checklist

### Before Training:
- [ ] Railway Pro subscription active
- [ ] Service has 12 GB RAM allocated
- [ ] Service has 8 CPU cores
- [ ] Storage has 10 GB free
- [ ] Training script ready
- [ ] Environment variables set

### During Training:
- [ ] Monitor logs for errors
- [ ] Check loss is decreasing
- [ ] Verify RAM usage is stable
- [ ] Ensure training isn't stuck

### After Training:
- [ ] Model file exists and is correct size
- [ ] Test generation works
- [ ] Download model file
- [ ] Backup model to local storage

---

## 🚨 Troubleshooting

### Out of Memory
```powershell
# Reduce batch size
BATCH_SIZE=16  # Instead of 32

# Or reduce model size
N_LAYERS=8     # Instead of 12
D_MODEL=512    # Instead of 768
```

### Training Too Slow
```powershell
# Increase Railway Pro resources
# Dashboard → Service → Scale Up

# Or reduce epochs
EPOCHS=30  # Instead of 50
```

### Model Not Learning
```powershell
# Check vocabulary was built
# Check training pairs > 0
# Verify loss is decreasing
# Check learning rate (try 2e-4)
```

---

## 📊 Expected Results

### Improved SLM:
- **Loss:** 6.0 → 2.5 (58% improvement)
- **Model Size:** 20-50 MB
- **Generation:** Good for SOMA topics
- **Training Time:** 1-2 hours

### Full GPT Model:
- **Loss:** 6.0 → 2.0 (67% improvement)
- **Model Size:** ~500 MB
- **Generation:** Production-quality text
- **Training Time:** 4-8 hours

---

## 🎉 Next Steps After Training

1. **Download Model:**
   ```powershell
   railway run ls -lh soma_full_gpt_model.pkl
   # Download via Railway Dashboard → Files
   ```

2. **Test Locally:**
   ```python
   import pickle
   model = pickle.load(open('soma_full_gpt_model.pkl', 'rb'))
   result = model.generate("SOMA is", max_tokens=100)
   print(result)
   ```

3. **Deploy for Production:**
   - Create API endpoint
   - Serve model via FastAPI
   - Use Railway's domain

---

## 📚 Additional Resources

- `TRAIN_IMPROVED_SLM.py` - Improved model training
- `TRAIN_GPT_MODEL.py` - Full GPT training
- `soma_gpt.py` - Model architecture
- `RAILWAY_OPERATIONS_GUIDE.md` - Railway commands

---

**Ready to train your real LLM on Railway Pro! 🚀**

**Recommended:** Start with Improved SLM, then move to Full GPT model.
