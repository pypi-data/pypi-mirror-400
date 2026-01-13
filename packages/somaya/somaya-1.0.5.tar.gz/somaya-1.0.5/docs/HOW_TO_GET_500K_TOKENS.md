# How to Get 500k Tokens for Testing

This guide shows you how to get 500,000 tokens to test the complete SOMA workflow:
**Tokenization → Embedding → Semantic → Model Outcome**

## Quick Start

Run the test script:
```bash
python examples/test_full_workflow_500k.py
```

## Option 1: Use the Test Script (Recommended)

The script `examples/test_full_workflow_500k.py` provides multiple options:

### 1. Download Wikipedia Articles
```bash
pip install wikipedia-api
python examples/test_full_workflow_500k.py
# Choose option 1
```

### 2. Generate Synthetic Text
```bash
python examples/test_full_workflow_500k.py
# Choose option 2 (default)
```

### 3. Use Your Own File
```bash
python examples/test_full_workflow_500k.py
# Choose option 3
# Enter path to your text file
```

## Option 2: Download Real Datasets

### Wikipedia Dump
```bash
# Download Wikipedia articles
wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2

# Extract and convert to text (requires wikiextractor)
pip install wikiextractor
wikiextractor enwiki-latest-pages-articles.xml.bz2 -o wiki_text
```

### Project Gutenberg Books
```bash
# Download free books
wget https://www.gutenberg.org/files/1342/1342-0.txt  # Pride and Prejudice
wget https://www.gutenberg.org/files/11/11-0.txt      # Alice in Wonderland
# ... download more books to reach 500k tokens
```

### Common Crawl
```bash
# Download web crawl data
# Visit: https://commoncrawl.org/
```

## Option 3: Use Public APIs

### Wikipedia API
```python
import wikipedia
wikipedia.set_lang("en")

articles = []
topics = ["Artificial Intelligence", "Machine Learning", ...]
for topic in topics:
    page = wikipedia.page(topic)
    articles.append(page.content)

text = "\n\n".join(articles)
```

### News APIs
- **NewsAPI**: https://newsapi.org/
- **Guardian API**: https://open-platform.theguardian.com/

## Option 4: Generate Synthetic Text

The test script includes a synthetic text generator that creates varied text to reach your target token count.

## What the Test Script Does

1. **Tokenization**: Tokenizes your text with SOMA
2. **Embedding Generation**: Creates feature-based embeddings
3. **Semantic Training**: Trains semantic embeddings from SOMA structure
4. **Model Outcome**: Performs similarity search to demonstrate the full pipeline

## Output Files

All results are saved to `workflow_output/`:
- `tokenization_results.json` - Tokenization statistics
- `embedding_stats.json` - Embedding information
- `soma_semantic_model.pkl` - Trained semantic model
- `similarity_search_results.json` - Search results

## Example Usage

```python
from examples.test_full_workflow_500k import test_full_workflow

# Load your text
with open("your_text_file.txt", "r") as f:
    text = f.read()

# Run full workflow
test_full_workflow(text, output_dir="my_results")
```

## Tips

1. **For faster testing**: Use option 4 (sample text) for quick validation
2. **For realistic testing**: Use Wikipedia articles or real datasets
3. **For production**: Use your actual domain-specific text data
4. **Token count**: ~500k tokens ≈ 2.5M characters (roughly 5 chars per token)

## Troubleshooting

**Not enough tokens?**
- Download more articles/books
- Increase the number of Wikipedia articles
- Use longer text files

**Too slow?**
- Process in batches
- Use smaller embedding dimensions
- Reduce training epochs

**Memory issues?**
- Process text in chunks
- Use streaming tokenization
- Reduce batch sizes

