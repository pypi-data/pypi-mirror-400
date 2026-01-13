# How to Run Semantic Embeddings

## Quick Start

### Step 1: Train Semantic Model

Train on your text corpus:

```bash
python examples/train_semantic_embeddings.py
```

Or use in your code:

```python
from examples.train_semantic_embeddings import train_semantic_embeddings

# Your text corpus
corpus = """
Your text data here. Can be multiple documents.
The more data, the better the semantic understanding.
"""

# Train
train_semantic_embeddings(
    text_corpus=corpus,
    output_model_path="soma_semantic_model.pkl",
    embedding_dim=768,
    epochs=10
)
```

### Step 2: Use Trained Embeddings

Generate embeddings:

```bash
python examples/use_semantic_embeddings.py
```

Or in your code:

```python
from embeddings import SOMAEmbeddingGenerator
from core.core_tokenizer import TextTokenizer

# Load trained model
generator = SOMAEmbeddingGenerator(
    strategy="semantic",
    semantic_model_path="soma_semantic_model.pkl"
)

# Tokenize and generate embeddings
tokenizer = TextTokenizer()
streams = tokenizer.build("Your text here")

for token in streams["word"].tokens:
    embedding = generator.generate(token)
    print(f"Token: {token.text}, Embedding: {embedding.shape}")
```

## Integration with API Server

### Option 1: Train Model First

1. Train model using the script above
2. Place model file in project root: `soma_semantic_model.pkl`
3. Use semantic strategy in API requests

### Option 2: Add Training Endpoint

Add to `main_server.py`:

```python
@app.post("/embeddings/train")
async def train_semantic_model(request: TrainingRequest):
    """Train semantic embeddings from provided corpus."""
    from embeddings.semantic_trainer import SOMASemanticTrainer
    from core.core_tokenizer import TextTokenizer
    
    # Tokenize corpus
    tokenizer = TextTokenizer()
    streams = tokenizer.build(request.corpus)
    
    # Collect tokens
    all_tokens = []
    for stream in streams.values():
        all_tokens.extend(stream.tokens)
    
    # Train
    trainer = SOMASemanticTrainer(
        embedding_dim=request.embedding_dim,
        epochs=request.epochs
    )
    trainer.build_vocab(all_tokens)
    trainer.build_cooccurrence(all_tokens)
    trainer.train(all_tokens)
    trainer.save(request.model_path)
    
    return {"status": "success", "model_path": request.model_path}
```

## Training Tips

### 1. Use Large Corpus

More data = better semantic understanding:

```python
# Read multiple documents
corpus = ""
for file in your_documents:
    with open(file, 'r') as f:
        corpus += f.read() + "\n"

train_semantic_embeddings(corpus, epochs=20)
```

### 2. Adjust Parameters

- **embedding_dim**: 768 (default) or 384, 512, 1024
- **window_size**: 5 (default) - context window size
- **epochs**: 10-20 for good results, 50+ for best results
- **min_count**: 2 (default) - minimum token frequency

### 3. Monitor Training

Watch the loss decrease:

```
Epoch 1/10, Loss: 0.5234
Epoch 2/10, Loss: 0.4123
Epoch 3/10, Loss: 0.3456
...
```

Lower loss = better embeddings.

## Using in Frontend

Update API request to use semantic strategy:

```typescript
const response = await api.post('/embeddings/generate', {
  text: "Your text",
  strategy: "semantic",  // Use semantic instead of feature_based
  embedding_dim: 768,
  tokenizer_seed: 42
});
```

**Note**: Model must be trained first and available at the server.

## File Structure

```
project/
├── soma_semantic_model.pkl  # Trained model (create by training)
├── examples/
│   ├── train_semantic_embeddings.py  # Training script
│   └── use_semantic_embeddings.py    # Usage script
└── src/
    └── embeddings/
        ├── semantic_trainer.py       # Training logic
        └── embedding_generator.py    # Embedding generation
```

## Troubleshooting

### "Model file not found"
- Train a model first using `train_semantic_embeddings.py`
- Check model path is correct

### "Token not in vocabulary"
- Token didn't appear in training corpus
- Falls back to feature-based embedding
- Train on larger corpus

### "Training is slow"
- Normal for large corpora
- Reduce `epochs` for faster training
- Use smaller `window_size`

## Summary

1. **Train**: `python examples/train_semantic_embeddings.py`
2. **Use**: Load model in `SOMAEmbeddingGenerator(strategy="semantic")`
3. **Generate**: Call `generator.generate(token)`

**Result**: NLP-understandable embeddings without pretrained models! 🎉

