# SOMA Demo - Complete Workflow

## Quick Start for Demo

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Main Demo (Full Workflow)
```bash
python examples/test_full_workflow_500k.py
```

This will:
- Tokenize 500k tokens
- Generate embeddings
- Train semantic embeddings (optional)
- Create vector store
- Perform similarity search

### 3. Run Search Examples
```bash
python examples/search_examples.py
```

### 4. Run Embedding Example
```bash
python examples/embedding_example.py
```

### 5. Start API Server
```bash
python main.py
# Select option 2 for Server Mode
```

Or directly:
```bash
python src/servers/main_server.py
```

## Project Structure

```
demo_soma/
├── src/                    # Core source code
│   ├── core/              # Tokenization engine
│   ├── embeddings/        # Embedding generation
│   ├── servers/           # API servers
│   └── integration/       # Transformer integration
├── examples/              # Demo scripts
│   ├── test_full_workflow_500k.py  # Main demo
│   └── search_examples.py          # Search demo
├── soma/                # Package code
├── main.py                # Entry point
├── setup.py               # Setup script
└── requirements.txt       # Dependencies
```

## Key Features to Demo

1. **Tokenization**: Multiple strategies (word, char, subword, etc.)
2. **Embeddings**: Feature-based and semantic embeddings
3. **Vector Store**: FAISS-based similarity search
4. **API Server**: RESTful API for tokenization
5. **Integration**: Works with transformers (BERT, GPT, etc.)

## Demo Scripts

- `test_full_workflow_500k.py` - Complete workflow demo
- `search_examples.py` - Vector search examples
- `embedding_example.py` - Embedding generation
- `use_vector_store.py` - Vector store operations

## API Endpoints

Once server is running:
- `POST /tokenize` - Tokenize text
- `POST /analyze` - Analyze text
- `GET /health` - Health check

## Notes

- All outputs are saved to `workflow_output/` directory
- You can resume from previous runs
- Vector store supports up to 30 batches by default (configurable)

