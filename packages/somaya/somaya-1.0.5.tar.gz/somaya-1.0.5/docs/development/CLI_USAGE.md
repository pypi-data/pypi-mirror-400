# SOMA CLI - Complete Usage Guide

## One Clean Entry Point for Everything

The `soma_cli.py` file is your single entry point for ALL SOMA operations.

## Commands

### 1. Tokenize

Tokenize text, files, or URLs.

```bash
# Tokenize text
python soma_cli.py tokenize --text "Hello world" --method word

# Tokenize file
python soma_cli.py tokenize --file data.txt --method word --output tokens.json

# Tokenize from URL
python soma_cli.py tokenize --url https://example.com/text.txt --method word

# Options:
#   --text TEXT        Input text
#   --file PATH        Input file path
#   --url URL          Input URL
#   --method METHOD    Tokenization method (word, char, subword, etc.)
#   --seed SEED        Random seed (default: 42)
#   --output PATH      Output file path
#   --format FORMAT    Output format (json, txt)
```

### 2. Train

Train semantic embeddings on your data.

```bash
# Train on text
python soma_cli.py train --text "Your corpus here..." --model-path model.pkl

# Train on file
python soma_cli.py train --file corpus.txt --model-path model.pkl --epochs 20

# Train from URL
python soma_cli.py train --url https://example.com/corpus.txt --model-path model.pkl

# Use enhanced trainer
python soma_cli.py train --file corpus.txt --enhanced --epochs 10

# Options:
#   --text TEXT           Training text
#   --file PATH           Training file path
#   --url URL             Training URL
#   --model-path PATH     Model output path (default: soma_model.pkl)
#   --embedding-dim DIM   Embedding dimension (default: 768)
#   --epochs EPOCHS       Training epochs (default: 10)
#   --window-size SIZE    Context window size (default: 5)
#   --enhanced            Use enhanced trainer (multi-stream, temporal, etc.)
```

### 3. Embed

Generate embeddings for text or files.

```bash
# Generate embeddings from text
python soma_cli.py embed --text "Hello world" --model-path model.pkl

# Generate embeddings from file
python soma_cli.py embed --file data.txt --model-path model.pkl --output embeddings.npy

# Use different strategy
python soma_cli.py embed --text "Hello" --strategy feature_based

# Options:
#   --text TEXT        Input text
#   --file PATH        Input file path
#   --model-path PATH  Trained model path (default: soma_model.pkl)
#   --output PATH      Output file path (.npy format)
#   --strategy STR     Strategy: feature_based, hash_based, semantic, hybrid
```

### 4. Test

Run tests to verify everything works.

```bash
# Full test suite
python soma_cli.py test

# Quick smoke tests
python soma_cli.py test --quick
```

### 5. Info

Show system information.

```bash
python soma_cli.py info
```

## Complete Workflow Examples

### Example 1: Basic Tokenization

```bash
# Tokenize a file
python soma_cli.py tokenize --file document.txt --method word --output tokens.json
```

### Example 2: Train and Use Embeddings

```bash
# Step 1: Train on corpus
python soma_cli.py train --file corpus.txt --model-path my_model.pkl --epochs 15

# Step 2: Generate embeddings
python soma_cli.py embed --file new_text.txt --model-path my_model.pkl --output embeddings.npy
```

### Example 3: Enhanced Training

```bash
# Train with enhanced features (multi-stream, temporal, etc.)
python soma_cli.py train \
    --file large_corpus.txt \
    --enhanced \
    --embedding-dim 768 \
    --epochs 20 \
    --model-path enhanced_model.pkl
```

### Example 4: Online Data

```bash
# Train on data from URL
python soma_cli.py train --url https://example.com/corpus.txt --model-path model.pkl
```

## All Features in One Place

✅ **Tokenization** - 9 methods (word, char, subword, byte, etc.)
✅ **Training** - Basic and enhanced semantic trainers
✅ **Embeddings** - Multiple strategies
✅ **File Support** - Text files, any file type
✅ **URL Support** - Load data from URLs
✅ **Testing** - Built-in test suite
✅ **Info** - System information

## Priority Order

1. **Tokenize** - Most common operation
2. **Train** - For custom embeddings
3. **Embed** - Generate embeddings
4. **Test** - Verify system
5. **Info** - Check capabilities

## Tips

- Use `--help` with any command for detailed options
- Start with `tokenize` to test your setup
- Use `test` to verify everything works
- Use `--enhanced` for best quality embeddings
- Save outputs with `--output` for later use

## That's It!

One file (`soma_cli.py`) handles everything. Clean, simple, complete.

