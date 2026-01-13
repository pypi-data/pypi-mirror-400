# 🎌 Manga & Anime LLM Training Guide

## 🎯 Goal

Train an **ADVANCED SOMA LLM** specialized for **manga and anime** text generation.

**Configuration:**
- 32K vocabulary
- 1024 d_model (high-dimensional)
- 16 layers (deep)
- 16 attention heads
- 2048 context window
- Advanced training techniques

---

## 📋 Complete Process

### Step 1: Collect Manga/Anime Data

```powershell
# Collect from HuggingFace and local files
railway run python soma_cognitive/slm/MANGA_ANIME_DATA_COLLECTOR.py
```

**What this does:**
- Downloads light novels from HuggingFace (if available)
- Downloads anime subtitles
- Processes local manga/anime files
- Combines into training dataset

**Output:**
- `manga_anime_data/combined_manga_anime.txt`

---

### Step 2: Train Advanced Model

```powershell
# Train advanced model on manga/anime data
railway run python soma_cognitive/slm/TRAIN_ADVANCED_MANGA_ANIME.py
```

**What this does:**
- Loads manga/anime data
- Builds 32K vocabulary
- Creates advanced model (16 layers, 1024 dim)
- Trains with learning rate scheduling
- Saves trained model

**Output:**
- `soma_llm_advanced_manga_anime.pkl`

**Time:** 8-16 hours

---

## 📊 Advanced Configuration

### Model Specs

```python
config = SOMALGMConfig(
    vocab_size=32000,      # 32K vocabulary
    d_model=1024,          # 1024 dimensions
    n_layers=16,           # 16 layers
    n_heads=16,            # 16 attention heads
    d_ff=4096,             # 4096 feed-forward
    max_seq_len=2048,      # 2048 context window
    learning_rate=3e-4,    # Advanced LR
    batch_size=8           # Optimized batch size
)
```

### Advanced Features

1. **Learning Rate Scheduling:**
   - Warmup phase (10% of epochs)
   - Cosine annealing
   - Adaptive learning rate

2. **Deep Architecture:**
   - 16 layers (vs 4 in standard)
   - 1024 dimensions (vs 256)
   - 16 attention heads (vs 4)

3. **Long Context:**
   - 2048 token window (vs 512)
   - Better for long dialogues
   - Character relationship modeling

---

## 📚 Data Sources for Manga/Anime

### Option 1: HuggingFace Datasets

```python
# Light novels
dataset = load_dataset("light_novels", split="train")

# Anime subtitles
dataset = load_dataset("opensubtitles", split="train")
```

### Option 2: Local Files

**Supported formats:**
- `.txt` - Plain text files
- `.epub` - E-book format
- `.srt` - Subtitle files

**How to use:**
```python
# Edit MANGA_ANIME_DATA_COLLECTOR.py
local_files = [
    "path/to/manga1.txt",
    "path/to/light_novel1.epub",
    "path/to/subtitles.srt",
]
collector.collect_from_files(local_files)
```

### Option 3: Manual Collection

1. **Download legally:**
   - Project Gutenberg (some Japanese literature)
   - Official translations
   - Licensed content

2. **Organize files:**
   - Put all `.txt` files in one folder
   - Or use the collector script

3. **Process:**
   ```python
   collector = MangaAnimeDataCollector()
   collector.collect_from_files(["path/to/file1.txt", "path/to/file2.txt"])
   ```

---

## 🎯 Training Process

### Phase 1: Data Collection

```powershell
# Collect data
railway run python soma_cognitive/slm/MANGA_ANIME_DATA_COLLECTOR.py
```

**Expected:**
- 100K - 10M+ examples
- 50MB - 5GB of text
- Manga dialogues, light novel text, subtitles

### Phase 2: Advanced Training

```powershell
# Train advanced model
railway run python soma_cognitive/slm/TRAIN_ADVANCED_MANGA_ANIME.py
```

**What happens:**
1. Loads manga/anime data
2. Builds 32K vocabulary
3. Creates advanced model
4. Trains for 30 epochs
5. Uses learning rate scheduling
6. Saves model

---

## 📊 Expected Results

### Model Statistics

| Metric | Value |
|--------|-------|
| **Vocabulary** | 32,000 tokens |
| **Parameters** | ~50-100M |
| **Model Size** | 200-300 MB |
| **Context** | 2048 tokens |
| **Training Time** | 8-16 hours |

### Training Metrics

- **Loss:** Should decrease from ~6.0 to ~1.5-2.0
- **Vocabulary:** 32K tokens (built from data)
- **Training Examples:** 1M+ recommended
- **Epochs:** 30 (with LR scheduling)

---

## 🚀 Quick Start

### Complete Pipeline:

```powershell
# 1. Collect manga/anime data
railway run python soma_cognitive/slm/MANGA_ANIME_DATA_COLLECTOR.py

# 2. Train advanced model
railway run python soma_cognitive/slm/TRAIN_ADVANCED_MANGA_ANIME.py
```

---

## ⚙️ Resource Requirements

### Railway Pro Configuration

**For Advanced Training:**
- **RAM:** 16-24 GB
- **CPU:** 8+ cores
- **Storage:** 20+ GB (for data + model)
- **Time:** 8-16 hours

**Set in Railway Dashboard:**
- Service → Settings → Resources
- Increase RAM to 24 GB
- Increase CPU to 8 cores

---

## 🎌 Manga/Anime Specific Features

### What Makes This Specialized

1. **Character Dialogue:**
   - Trained on character conversations
   - Understands dialogue patterns
   - Generates character-appropriate speech

2. **Story Structure:**
   - Trained on manga/anime narratives
   - Understands story arcs
   - Generates plot-consistent text

3. **Terminology:**
   - Learns manga/anime vocabulary
   - Understands genre-specific terms
   - Generates appropriate language

---

## 📝 Data Preparation Tips

### For Best Results:

1. **Diverse Sources:**
   - Mix different manga/anime genres
   - Include various authors
   - Balance dialogue and narration

2. **Quality Over Quantity:**
   - Clean, well-translated text
   - Consistent formatting
   - Remove noise/errors

3. **Sufficient Data:**
   - Minimum: 100K examples
   - Recommended: 1M+ examples
   - Ideal: 10M+ examples

---

## 🎯 Next Steps After Training

1. **Test Generation:**
   ```python
   import pickle
   model = pickle.load(open('soma_llm_advanced_manga_anime.pkl', 'rb'))
   result = model.generate("The hero", max_tokens=100)
   print(result)
   ```

2. **Fine-tune:**
   - Add more specific manga/anime data
   - Fine-tune on particular genres
   - Specialize for specific characters

3. **Deploy:**
   - Create API endpoint
   - Serve via Railway
   - Build manga/anime text generator

---

## 🚨 Troubleshooting

### Out of Memory

```python
# Reduce batch size
batch_size = 4  # Instead of 8

# Or reduce model size
d_model = 512   # Instead of 1024
n_layers = 8    # Instead of 16
```

### Training Too Slow

```python
# Reduce epochs for testing
epochs = 10  # Instead of 30

# Or reduce data
training_texts = training_texts[:500000]  # 500K examples
```

### Not Enough Data

```python
# Collect more data
# Use multiple sources
# Combine different datasets
```

---

## 🎉 Success Indicators

After training, you should see:

✅ **Vocabulary:** 32K tokens (built from manga/anime data)
✅ **Model size:** 200-300 MB
✅ **Loss:** 1.5-2.0 (good convergence)
✅ **Generation:** Manga/anime style text
✅ **Context:** Handles 2048-token sequences

---

## 📚 Additional Resources

- **Data Collection:** `MANGA_ANIME_DATA_COLLECTOR.py`
- **Advanced Training:** `TRAIN_ADVANCED_MANGA_ANIME.py`
- **Real Data Guide:** `REAL_DATA_TRAINING_GUIDE.md`

---

**Ready to train your advanced manga/anime LLM? Start with data collection! 🎌**
