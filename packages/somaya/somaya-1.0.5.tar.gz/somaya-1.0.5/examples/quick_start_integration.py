"""
Quick Start: SOMA + Pretrained Models

This is the fastest way to get started using SOMA with pretrained models.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.core_tokenizer import run_once
from src.integration.vocabulary_adapter import quick_convert_SOMA_to_model_ids

# Your text
text = "Hello world! SOMA is amazing."

# Step 1: Tokenize with SOMA
SOMA_result = run_once(text, seed=42, embedding_bit=False)

# Step 2: Extract tokens
tokens = [rec["text"] for rec in SOMA_result["word"]["records"]]
print(f"SOMA tokens: {tokens}")

# Step 3: Convert to model vocabulary IDs
model_ids = quick_convert_SOMA_to_model_ids(tokens, model_name="bert-base-uncased")
print(f"BERT vocabulary IDs: {model_ids}")

# That's it! Now you can use model_ids with any BERT model.
# The IDs are compatible with BERT's embedding layer.
