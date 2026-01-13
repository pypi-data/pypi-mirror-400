# Vocabulary Compatibility Issue: SOMA ↔ Pretrained Models

## The Critical Problem

**SOMA can tokenize perfectly — even more precisely than BPE — but if you feed its IDs into a pretrained Transformer, the embedding layer will interpret them under a different vocabulary mapping.**

### The Core Issue

1. **SOMA generates its own token IDs:**
   - UIDs (64-bit unique identifiers)
   - Frontend digits (1-9)
   - Backend numbers (64-bit hashes)
   - Global IDs (combined identifiers)

2. **Pretrained models have their own vocabularies:**
   - BERT: ~30,000 tokens with specific ID mappings
   - GPT-2/3/4: ~50,000-100,000 tokens with specific ID mappings
   - T5: ~32,000 tokens with specific ID mappings
   - Each model's embedding layer expects **its own vocabulary IDs**

3. **The Mismatch:**
   - SOMA's token ID `12345` ≠ BERT's token ID `12345`
   - Feeding SOMA IDs directly to a pretrained model will produce **garbage embeddings**
   - The model interprets SOMA's ID `12345` as whatever token BERT has at index 12345 (likely a completely different token)

### Why This Matters

```
SOMA Tokenization:
Text: "hello world"
SOMA IDs: [98765, 43210]  ← These are SOMA's internal IDs

Pretrained Model (BERT):
BERT Vocabulary ID 98765 = "##ing"  ← Different token!
BERT Vocabulary ID 43210 = "the"    ← Different token!

Result: Model thinks you're saying "##ing the" instead of "hello world"
```

## Solutions

### Solution 1: Use SOMA Tokenization + Model Vocabulary Mapping (Recommended)

**Use SOMA to tokenize, then map token strings to model vocabulary IDs.**

```python
from src.core.core_tokenizer import run_once
from src.integration.vocabulary_adapter import SOMAToModelConverter

# 1. Tokenize with SOMA
text = "Hello world! SOMA is amazing."
soma_result = run_once(text, seed=42, embedding_bit=False)

# 2. Convert to model vocabulary IDs
converter = SOMAToModelConverter(model_name="bert-base-uncased")
model_ready = converter.convert_soma_result(soma_result, tokenizer_type="word")

# 3. Use with pretrained model
model_input_ids = model_ready["model_input_ids"]
# Now safe to feed to BERT's embedding layer!
```

**Pros:**
- ✅ Leverages SOMA's superior tokenization
- ✅ Compatible with any pretrained model
- ✅ Preserves SOMA metadata (frontend digits, backend numbers)
- ✅ No model retraining required

**Cons:**
- ⚠️ Model tokenizer may split tokens differently (subword tokenization)
- ⚠️ Alignment between SOMA tokens and model tokens may not be 1:1

### Solution 2: Train New Model with SOMA from Day One

**Build a new model using SOMA's vocabulary system from scratch.**

```python
# This requires training a new model
# 1. Create vocabulary from SOMA tokenization of training corpus
# 2. Initialize embedding layer with SOMA vocabulary size
# 3. Train model from scratch

# Pros: Perfect alignment, no mapping needed
# Cons: Requires full model training (expensive, time-consuming)
```

**Pros:**
- ✅ Perfect vocabulary alignment
- ✅ No mapping/adapter needed
- ✅ Full control over tokenization

**Cons:**
- ❌ Requires training from scratch (expensive)
- ❌ Lose benefits of pretrained models
- ❌ Time-consuming

### Solution 3: Re-embed Existing Model (Advanced)

**Replace the embedding layer of a pretrained model with one aligned to SOMA's vocabulary.**

This is complex and generally not recommended unless you have specific requirements.

## Implementation Guide

### Basic Usage

```python
from src.core.core_tokenizer import run_once
from src.integration.vocabulary_adapter import quick_convert_soma_to_model_ids

# Tokenize with SOMA
text = "Hello world"
soma_result = run_once(text, seed=42, embedding_bit=False)

# Extract tokens
tokens = [rec["text"] for rec in soma_result["word"]["records"]]

# Convert to model IDs
model_ids = quick_convert_soma_to_model_ids(tokens, model_name="bert-base-uncased")
print(f"Model vocabulary IDs: {model_ids}")
```

### Full Integration Example

```python
from src.core.core_tokenizer import TextTokenizer
from src.integration.vocabulary_adapter import SOMAToModelConverter
from transformers import AutoModel

# 1. Tokenize with SOMA
tokenizer = TextTokenizer(seed=42, embedding_bit=False)
streams = tokenizer.build("Hello world! SOMA is amazing.")

# 2. Get word tokenization
word_stream = streams["word"]
tokens = [tok.text for tok in word_stream.tokens]

# 3. Convert to model format
converter = SOMAToModelConverter(model_name="bert-base-uncased")
model_inputs = converter.prepare_for_inference(
    {"word": {"records": [{"text": t} for t in tokens]}},
    tokenizer_type="word",
    return_tensors="pt"
)

# 4. Use with pretrained model
model = AutoModel.from_pretrained("bert-base-uncased")
outputs = model(**model_inputs)
```

### Supported Models

The vocabulary adapter works with any HuggingFace model:

- **BERT**: `bert-base-uncased`, `bert-large-uncased`, etc.
- **GPT**: `gpt2`, `gpt2-medium`, `gpt2-large`, etc.
- **T5**: `t5-small`, `t5-base`, `t5-large`, etc.
- **RoBERTa**: `roberta-base`, `roberta-large`, etc.
- **DistilBERT**: `distilbert-base-uncased`
- **And any other HuggingFace model**

## Technical Details

### How the Adapter Works

1. **SOMA Tokenization**: SOMA tokenizes text into token strings
2. **Text Reconstruction**: Token strings are joined back into text
3. **Model Tokenization**: Model's tokenizer processes the text
4. **ID Mapping**: Model's tokenizer assigns vocabulary IDs
5. **Alignment**: Approximate mapping between SOMA tokens and model tokens

### Important Notes

⚠️ **Subword Tokenization Mismatch**: If the model uses subword tokenization (BPE, WordPiece, SentencePiece), a single SOMA token may map to multiple model tokens.

Example:
```
SOMA: ["tokenization"]
Model: ["token", "##ization"]  ← Split into subwords
```

⚠️ **Reconstruction**: When converting back, you may get slightly different text due to subword tokenization differences.

✅ **SOMA Metadata Preserved**: SOMA's frontend digits, backend numbers, and UIDs are preserved in the conversion result.

## Best Practices

1. **Use SOMA's tokenization strategies that align with your model:**
   - For BPE-based models (GPT): Use `subword_bpe`
   - For WordPiece models (BERT): Use `word` or `subword`
   - For character-level models: Use `char`

2. **Always check the mapping:**
   ```python
   result = converter.convert_soma_result(soma_result, "word")
   print(result["token_mapping"])  # Check SOMA → Model token alignment
   ```

3. **Preserve SOMA metadata:**
   ```python
   # Access SOMA's original data
   frontend_digits = result["soma_frontend_digits"]
   backend_scaled = result["soma_backend_scaled"]
   ```

4. **For new projects: Consider training with SOMA from scratch** if you have the resources.

## FAQ

**Q: Can I use SOMA IDs directly with pretrained models?**  
A: No. SOMA IDs are not compatible with pretrained model vocabularies. Use the vocabulary adapter.

**Q: Will I lose SOMA's precision by using the adapter?**  
A: You keep SOMA's tokenization precision, but the model may split tokens differently during subword tokenization.

**Q: Can I fine-tune a model to use SOMA's vocabulary?**  
A: Yes, but you'd need to retrain the embedding layer, which is essentially training a new model.

**Q: Which tokenization strategy should I use?**  
A: Match SOMA's strategy to your model's tokenization type (BPE, WordPiece, etc.) for best alignment.

## Conclusion

SOMA's tokenization is superior, but **vocabulary compatibility is essential** for using pretrained models. The vocabulary adapter provides a bridge between SOMA's tokenization and model vocabularies, allowing you to leverage both:

- ✅ SOMA's superior tokenization
- ✅ Pretrained models' powerful embeddings and representations

For new projects with sufficient resources, training from scratch with SOMA's vocabulary system provides the best long-term solution.
