# 🚀 Real Data Training Guide - SOMA LLM

## 🎯 Goal

Train SOMA LLM on **REAL datasets**, not dummy data:
- Wikipedia (100M+ tokens)
- Common Crawl (billions of tokens)
- Code repositories
- Books
- Scientific papers

---

## 📋 Step-by-Step Process

### Step 1: Install Dependencies

```powershell
# Install HuggingFace datasets (for easy data download)
pip install datasets

# Or on Railway
railway run pip install datasets
```

---

### Step 2: Download Real Data

```powershell
# Download real datasets via HuggingFace
railway run python soma_cognitive/slm/REAL_DATA_PIPELINE.py
```

**What this does:**
- Downloads Wikipedia (English)
- Downloads Common Crawl (C4)
- Downloads Code (CodeSearchNet)
- Downloads Books (Project Gutenberg)
- Saves to `training_data/` directory

**Expected output:**
- `training_data/wikipedia/wikipedia_text.txt` (~100MB+)
- `training_data/commoncrawl/c4_text.txt` (~500MB+)
- `training_data/code/code_python.txt` (~50MB+)
- `training_data/books/*.txt` (~10MB+)

**Time:** 30 minutes - 2 hours (depending on data size)

---

### Step 3: Process Data

```powershell
# Process downloaded data
railway run python soma_cognitive/slm/PROCESS_REAL_DATA.py
```

**What this does:**
- Cleans text
- Splits into sentences
- Removes noise
- Saves processed data

**Output:**
- `processed_data/processed_training_data.txt`

**Time:** 10-30 minutes

---

### Step 4: Train on Real Data

```powershell
# Train model on REAL data
railway run python soma_cognitive/slm/TRAIN_WITH_REAL_DATA.py
```

**What this does:**
- Loads processed real data
- Builds vocabulary from real data
- Trains model on real examples
- Saves trained model

**Output:**
- `soma_llm_real_data.pkl`

**Time:** 2-8 hours (depending on data size)

---

## 📊 Data Sources

### 1. Wikipedia
- **Source:** HuggingFace Datasets
- **Size:** 100M+ tokens
- **Quality:** High (curated)
- **Use:** General knowledge

### 2. Common Crawl (C4)
- **Source:** HuggingFace Datasets
- **Size:** Billions of tokens
- **Quality:** Medium (web crawl)
- **Use:** Diverse language patterns

### 3. Code (CodeSearchNet)
- **Source:** HuggingFace Datasets
- **Size:** 50M+ tokens
- **Quality:** High (GitHub)
- **Use:** Programming knowledge

### 4. Books (Project Gutenberg)
- **Source:** Direct download
- **Size:** 10M+ tokens
- **Quality:** High (classic literature)
- **Use:** Literary language

### 5. Scientific Papers (arXiv)
- **Source:** HuggingFace Datasets
- **Size:** 20M+ tokens
- **Quality:** High (peer-reviewed)
- **Use:** Technical knowledge

---

## 🎯 Training Configuration

### Initial Training (Recommended)

```python
config = SOMALGMConfig(
    vocab_size=8000,      # Built from real data
    d_model=256,
    n_layers=4,
    n_heads=4,
    epochs=20,
    batch_size=16
)
```

**Resources:**
- RAM: 4-6 GB
- Time: 2-4 hours
- Data: 1M examples

### Scale Up Training

```python
config = SOMALGMConfig(
    vocab_size=60000,     # Full vocabulary
    d_model=768,
    n_layers=12,
    n_heads=12,
    epochs=50,
    batch_size=32
)
```

**Resources:**
- RAM: 12-16 GB
- Time: 8-16 hours
- Data: 10M+ examples

---

## 📈 Expected Results

### With Real Data:

| Metric | Dummy Data | Real Data |
|--------|-----------|-----------|
| **Vocabulary** | 576 tokens | 8K-60K tokens |
| **Training Examples** | 400 | 1M+ |
| **Loss** | 2.99 | 1.5-2.5 |
| **Generation Quality** | Basic | Much better |
| **Generalization** | Limited | Good |

---

## 🚀 Quick Start (All Steps)

```powershell
# 1. Download real data
railway run python soma_cognitive/slm/REAL_DATA_PIPELINE.py

# 2. Process data
railway run python soma_cognitive/slm/PROCESS_REAL_DATA.py

# 3. Train on real data
railway run python soma_cognitive/slm/TRAIN_WITH_REAL_DATA.py
```

---

## 📊 Data Statistics

After downloading, you should have:

```
training_data/
├── wikipedia/
│   └── wikipedia_text.txt      (~100-500 MB)
├── commoncrawl/
│   └── c4_text.txt             (~500 MB - 5 GB)
├── code/
│   └── code_python.txt         (~50-200 MB)
└── books/
    └── book_*.txt              (~10-50 MB)

processed_data/
└── processed_training_data.txt (~500 MB - 5 GB)
```

**Total:** 1-10 GB of real training data

---

## ⚙️ Customization

### Download More Data

Edit `REAL_DATA_PIPELINE.py`:

```python
# Increase limits
wiki_dataset = load_dataset("wikipedia", split="train", streaming=True)
# Remove .take(100000) to get all data
```

### Add More Sources

```python
# Add Reddit
reddit_dataset = load_dataset("reddit", split="train")

# Add Stack Overflow
stack_dataset = load_dataset("stackoverflow", split="train")

# Add more code
code_dataset = load_dataset("bigcode/the-stack", split="train")
```

---

## 🎯 Next Steps After Training

1. **Evaluate Model:**
   - Test on benchmarks
   - Compare with baseline
   - Measure improvement

2. **Scale Up:**
   - More data (10M+ examples)
   - Larger model (12 layers, 768 dim)
   - Longer training (50-100 epochs)

3. **Fine-tune:**
   - Domain-specific data
   - Task-specific fine-tuning
   - Specialized capabilities

---

## 📝 Notes

### Data Quality Matters

- **Clean data** > Large data
- **Diverse sources** > Single source
- **Curated** > Raw crawl

### Training Tips

- Start with 1M examples
- Validate training works
- Then scale to full dataset
- Monitor loss carefully

### Storage

- Real data is large (GBs)
- Railway Pro has storage limits
- Consider external storage (S3, etc.)
- Or process in batches

---

## 🚨 Troubleshooting

### Out of Memory

```python
# Reduce batch size
batch_size = 8  # Instead of 16

# Process data in chunks
# Don't load all at once
```

### Data Download Fails

```python
# Use smaller subset
dataset = load_dataset("wikipedia", split="train[:10000]")

# Or download manually
# Then process locally
```

### Training Too Slow

```python
# Reduce data size for testing
training_texts = training_texts[:100000]  # 100K examples

# Then scale up once working
```

---

## 🎉 Success Indicators

After training on real data, you should see:

✅ **Vocabulary:** 8K-60K tokens (not 576)
✅ **Training examples:** 1M+ (not 400)
✅ **Loss:** 1.5-2.5 (better than 2.99)
✅ **Generation:** More coherent, diverse
✅ **Model size:** 20-500 MB (depending on config)

---

**Ready to train on REAL data? Start with Step 1! 🚀**
