# 🧠 SOMA-LLM v1 Specification — Bridge Model

## 🎯 Mission

Build the **bridge model** that proves SOMA can scale to real LLM territory while keeping its identity.

---

## 📊 Architecture Specification

### Core Parameters

| Component | Value | Rationale |
|-----------|-------|-----------|
| **Layers** | 12 | GPT-2 class depth |
| **Heads** | 8 | Balanced attention |
| **d_model** | 512 | Memory-efficient, trainable |
| **d_ff** | 2048 | 4x d_model (standard) |
| **Vocab** | 16,384 | Real LLM threshold |
| **Context** | 1024 | Long-context capable |
| **Params** | ~90M | Trainable on 1-2 GPUs |

### Memory Profile

- **Model Size:** ~360 MB (90M params × 4 bytes)
- **Training RAM:** ~8-12 GB (with gradients)
- **Inference RAM:** ~2-4 GB

---

## 🧩 What Makes This "SOMA" (Not GPT Clone)

### 1. Token Identity System
- Tokens carry **structural roles** (not just string fragments)
- UID-based token identification
- Frontend/backend composition

### 2. Structure-Aware Embeddings
- Embeddings encode **function, not just frequency**
- 60+ features from TokenRecord
- Semantic grouping signals

### 3. Hierarchy-Aware Attention
- Attention respects **token relationships**
- Tree/graph structure signals
- Neighbor-aware processing

### 4. SOMA-Specific Objectives (Future)
- Structure prediction
- Hierarchy learning
- Semantic coherence

---

## 📈 Training Targets

### Data Requirements

- **Minimum:** 5M tokens
- **Target:** 10M tokens
- **Optimal:** 50M tokens

### Training Metrics

- **Loss Target:** < 2.0 (from ~6.0 baseline)
- **Epochs:** 50-100
- **Time:** 8-16 hours (Railway Pro / GPU)

---

## 🚀 Implementation Phases

### Phase 1: Vocabulary Scaling ✅ (Next)
- Expand to 16K tokens
- Add general English
- Add technical text
- Keep SOMA identity

### Phase 2: Architecture Upgrade ✅ (Next)
- 12 layers, 8 heads
- 512 d_model
- 1024 context

### Phase 3: Data Collection ⏳
- Wikipedia dump
- Technical docs
- SOMA-specific text

### Phase 4: Training ⏳
- Multi-stage training
- Stability checks
- SOMA specialization

---

## 🎯 Success Criteria

**This model is "real LLM" when:**

- ✅ Generates coherent 500+ token passages
- ✅ Maintains context across 1024 tokens
- ✅ Shows SOMA-specific knowledge
- ✅ Loss converges < 2.0
- ✅ Inference < 100ms per token

---

**Status:** Ready to implement Phase 1 & 2
