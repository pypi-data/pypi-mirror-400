"""
Train Semantic Embeddings from soma Tokens

This script trains NLP-understandable embeddings WITHOUT using pretrained models.
It learns semantic relationships from soma's structure.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings.semantic_trainer import somaSemanticTrainer
from src.core.core_tokenizer import TextTokenizer


def train_semantic_embeddings(
    text_corpus: str,
    output_model_path: str = "SOMA_semantic_model.pkl",
    embedding_dim: int = 768,
    window_size: int = 5,
    epochs: int = 10
):
    """
    Train semantic embeddings from text corpus.
    
    Args:
        text_corpus: Your text data (can be a single large string or multiple documents)
        output_model_path: Where to save the trained model
        embedding_dim: Embedding dimension (default: 768)
        window_size: Context window size
        epochs: Training epochs
    """
    print("=" * 60)
    print("SOMA Semantic Embedding Training")
    print("=" * 60)
    print(f"Corpus length: {len(text_corpus)} characters")
    print(f"Embedding dimension: {embedding_dim}")
    print(f"Window size: {window_size}")
    print(f"Epochs: {epochs}")
    print()
    
    # Step 1: Tokenize with SOMA
    print("Step 1: Tokenizing with soma...")
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    streams = tokenizer.build(text_corpus)
    
    # Collect all tokens
    all_tokens = []
    for stream_name, token_stream in streams.items():
        tokens = token_stream.tokens
        all_tokens.extend(tokens)
        print(f"  - {stream_name}: {len(tokens)} tokens")
    
    print(f"Total tokens: {len(all_tokens)}")
    print()
    
    # Step 2: Initialize trainer
    print("Step 2: Initializing semantic trainer...")
    trainer = SOMASemanticTrainer(
        embedding_dim=embedding_dim,
        window_size=window_size,
        epochs=epochs
    )
    print("[OK] Trainer initialized")
    print()
    
    # Step 3: Build vocabulary
    print("Step 3: Building vocabulary...")
    trainer.build_vocab(all_tokens)
    print()
    
    # Step 4: Build co-occurrence matrix
    print("Step 4: Building co-occurrence matrix from soma structure...")
    trainer.build_cooccurrence(all_tokens)
    print()
    
    # Step 5: Train embeddings
    print("Step 5: Training semantic embeddings...")
    trainer.train(all_tokens)
    print()
    
    # Step 6: Save model
    print(f"Step 6: Saving model to {output_model_path}...")
    trainer.save(output_model_path)
    print()
    
    print("=" * 60)
    print("[OK] Training Complete!")
    print(f"Model saved to: {output_model_path}")
    print("=" * 60)
    
    return trainer


def main():
    """Example usage."""
    
    # Example 1: Train on sample text
    sample_text = """
    Natural language processing is a field of artificial intelligence.
    Machine learning models learn patterns from data.
    Deep learning uses neural networks with multiple layers.
    Tokenization is the process of breaking text into tokens.
    Embeddings represent tokens as dense vectors.
    Semantic embeddings capture meaning and relationships.
    """
    
    print("Training on sample text...")
    trainer = train_semantic_embeddings(
        text_corpus=sample_text,
        output_model_path="SOMA_semantic_model.pkl",
        embedding_dim=768,
        epochs=5  # Use more epochs (10-20) for better results
    )
    
    # Example 2: Test the trained embeddings
    print("\n" + "=" * 60)
    print("Testing Trained Embeddings")
    print("=" * 60)
    
    # Tokenize new text
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    test_text = "Natural language processing"
    streams = tokenizer.build(test_text)
    
    # Get embeddings for tokens
    for stream_name, token_stream in streams.items():
        print(f"\n{stream_name} stream:")
        for token in token_stream.tokens[:5]:  # Show first 5 tokens
            uid = getattr(token, 'uid', 0)
            text = getattr(token, 'text', '')
            embedding = trainer.get_embedding(uid)
            
            if embedding is not None:
                print(f"  Token: '{text}' (UID: {uid})")
                print(f"    Embedding shape: {embedding.shape}")
                print(f"    Embedding sample: {embedding[:5]}...")
            else:
                print(f"  Token: '{text}' (UID: {uid}) - Not in vocabulary")


if __name__ == "__main__":
    main()
