# Quick Start: Weaviate + SOMA

## 1. Install Dependencies

```bash
pip install weaviate-client python-dotenv
```

Or from the weaviate folder:
```bash
pip install -r weaviate/requirements.txt
```

## 2. Setup Environment Variables

Create a `.env` file in your project root:

```env
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-api-key-here
```

## 3. Test Connection

```bash
python weaviate/test_connection.py
```

Should see: ✅ Connection successful!

## 4. Run Example

```bash
python weaviate/example_usage.py
```

This will:
- Tokenize text with SOMA
- Generate embeddings
- Store in Weaviate
- Search for similar tokens

## 5. Use in Your Code

```python
from weaviate.weaviate_vector_store import WeaviateVectorStore
from src.tokenization.text_tokenizer import TextTokenizer
from src.embeddings.embedding_generator import SOMAEmbeddingGenerator

# Initialize
tokenizer = TextTokenizer()
embedding_gen = SOMAEmbeddingGenerator()
vector_store = WeaviateVectorStore()

# Tokenize and embed
text = "Your text here"
streams = tokenizer.build(text)
tokens = streams["word"].tokens
embeddings = embedding_gen.generate_batch(tokens)

# Store
vector_store.add_tokens(tokens, embeddings)

# Search
results = vector_store.search(embeddings[0], top_k=10)

# Clean up
vector_store.close()
```

## Troubleshooting

**Connection fails?**
- Check your `.env` file has correct URL and API key
- Verify your Weaviate cluster is running
- Check network connectivity

**Import errors?**
- Make sure you installed: `pip install weaviate-client`
- Check Python version (3.8+)

**Collection errors?**
- Collection might already exist with different schema
- Delete it in Weaviate dashboard or use a different collection name

