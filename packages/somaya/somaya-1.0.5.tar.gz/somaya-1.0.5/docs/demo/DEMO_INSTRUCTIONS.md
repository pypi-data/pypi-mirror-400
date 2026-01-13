# SOMA Demo Instructions

## 🚀 Quick Demo Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- numpy
- faiss-cpu (or faiss-gpu)
- fastapi
- uvicorn
- wikipedia (optional, for data)

### Step 2: Run Main Demo

#### Option A: Full Workflow (Recommended)
```bash
python examples/test_full_workflow_500k.py
```

This demonstrates:
1. ✅ Tokenization (500k tokens)
2. ✅ Embedding Generation
3. ✅ Semantic Training (optional)
4. ✅ Vector Store Creation
5. ✅ Similarity Search

**Output**: All results saved to `workflow_output/` directory

#### Option B: Quick Search Demo
```bash
python examples/search_examples.py
```

Interactive search interface for exploring tokens.

#### Option C: Embedding Demo
```bash
python examples/embedding_example.py
```

Shows embedding generation and usage.

### Step 3: Start API Server (Optional)

```bash
python main.py
# Select option 2 for Server Mode
```

Or directly:
```bash
python src/servers/main_server.py
```

Server runs on: `http://localhost:8000`

### Step 4: Test API (if server is running)

```bash
curl -X POST http://localhost:8000/tokenize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World!", "tokenizer_type": "word"}'
```

## 📁 Demo Files Explained

### Core Demo Scripts

1. **`examples/test_full_workflow_500k.py`**
   - Main comprehensive demo
   - Shows complete workflow
   - Generates all outputs

2. **`examples/search_examples.py`**
   - Interactive search interface
   - Vector similarity search
   - Token exploration

3. **`examples/embedding_example.py`**
   - Embedding generation
   - Feature-based embeddings
   - Embedding visualization

4. **`examples/use_vector_store.py`**
   - Vector store operations
   - FAISS integration
   - Batch processing

### Key Features to Highlight

1. **Tokenization**
   - Multiple strategies (word, char, subword, etc.)
   - Mathematical analysis
   - Statistical features

2. **Embeddings**
   - Feature-based (60 dimensions)
   - Semantic embeddings (optional)
   - Hybrid embeddings

3. **Vector Store**
   - FAISS-based similarity search
   - Fast nearest neighbor search
   - Batch processing support

4. **API Server**
   - RESTful API
   - Multiple endpoints
   - Real-time processing

## 🎯 Demo Talking Points

1. **"SOMA provides multiple tokenization strategies"**
   - Show different tokenization methods
   - Demonstrate mathematical features

2. **"Feature-based embeddings capture token structure"**
   - Show embedding generation
   - Explain 60-dimensional features

3. **"Vector store enables fast similarity search"**
   - Demonstrate search functionality
   - Show related tokens

4. **"API server provides easy integration"**
   - Show API endpoints
   - Demonstrate REST API usage

## 📊 Expected Outputs

After running `test_full_workflow_500k.py`:

```
workflow_output/
├── tokens.pkl                    # Tokenized data
├── embedding_batches/            # Embedding batches
├── embedding_batches_metadata.json
├── soma_semantic_model.pkl    # Semantic model (if trained)
├── vector_store.faiss           # Vector store index
├── similarity_search_results.json
└── tokenization_results.json
```

## ⚠️ Important Notes

1. **First Run**: Will take time to tokenize and generate embeddings
2. **Resume**: Script can resume from previous runs
3. **Memory**: Vector store loads first 30 batches by default
4. **Dependencies**: Make sure all packages are installed

## 🔧 Troubleshooting

### Issue: "No module named 'src'"
**Solution**: Run from project root directory

### Issue: "Memory error"
**Solution**: Reduce `max_batches_for_vector_store` in script

### Issue: "FAISS not found"
**Solution**: `pip install faiss-cpu` (or `faiss-gpu`)

### Issue: "Dependencies missing"
**Solution**: `pip install -r requirements.txt`

## 📝 Demo Checklist

- [ ] Dependencies installed
- [ ] Main demo script runs successfully
- [ ] Output files generated
- [ ] Search demo works
- [ ] API server starts (optional)
- [ ] Ready to present!

## 🎉 Success!

If all steps complete successfully, you're ready for the demo!

Check `workflow_output/` for all generated files and results.

