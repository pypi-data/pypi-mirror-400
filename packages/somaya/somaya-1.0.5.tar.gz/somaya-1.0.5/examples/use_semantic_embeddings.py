"""
Use Trained Semantic Embeddings

Generate NLP-understandable embeddings using a trained semantic model.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings import somaEmbeddingGenerator
from src.core.core_tokenizer import TextTokenizer


def use_semantic_embeddings(
    text: str,
    model_path: str = "SOMA_semantic_model.pkl",
    embedding_dim: int = 768
):
    """
    Generate semantic embeddings for text using trained model.
    
    Args:
        text: Input text
        model_path: Path to trained semantic model
        embedding_dim: Embedding dimension
    """
    print("=" * 60)
    print("Generating Semantic Embeddings")
    print("=" * 60)
    print(f"Text: {text}")
    print(f"Model: {model_path}")
    print()
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"[ERROR] Error: Model file not found: {model_path}")
        print("   Train a model first using: python examples/train_semantic_embeddings.py")
        return None
    
    # Initialize embedding generator with semantic strategy
    print("Loading semantic model...")
    generator = SOMAEmbeddingGenerator(
        strategy="semantic",
        embedding_dim=embedding_dim,
        semantic_model_path=model_path
    )
    print("[OK] Model loaded")
    print()
    
    # Tokenize text
    print("Tokenizing text...")
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    streams = tokenizer.build(text)
    print("[OK] Tokenization complete")
    print()
    
    # Generate embeddings
    print("Generating embeddings...")
    results = []
    
    for stream_name, token_stream in streams.items():
        print(f"\n{stream_name} stream:")
        for token in token_stream.tokens:
            text = getattr(token, 'text', '')
            uid = getattr(token, 'uid', 0)
            
            try:
                embedding = generator.generate(token)
                results.append({
                    'text': text,
                    'uid': uid,
                    'embedding': embedding,
                    'stream': stream_name
                })
                print(f"  [OK] '{text}' -> embedding shape: {embedding.shape}")
            except Exception as e:
                print(f"  [WARNING]  '{text}' -> Error: {e}")
    
    print()
    print("=" * 60)
    print(f"[OK] Generated {len(results)} embeddings")
    print("=" * 60)
    
    return results


def compare_embeddings(text1: str, text2: str, model_path: str = "SOMA_semantic_model.pkl"):
    """
    Compare semantic similarity between two texts.
    """
    import numpy as np
    
    print("=" * 60)
    print("Semantic Similarity Comparison")
    print("=" * 60)
    
    # Get embeddings for both texts
    results1 = use_semantic_embeddings(text1, model_path)
    results2 = use_semantic_embeddings(text2, model_path)
    
    if not results1 or not results2:
        return
    
    # Average embeddings for each text
    emb1 = np.mean([r['embedding'] for r in results1], axis=0)
    emb2 = np.mean([r['embedding'] for r in results2], axis=0)
    
    # Compute cosine similarity
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    print()
    print("=" * 60)
    print("Similarity Results")
    print("=" * 60)
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Cosine Similarity: {similarity:.4f}")
    print("=" * 60)


def main():
    """Example usage."""
    
    # Example 1: Generate embeddings
    text = "Natural language processing and machine learning"
    results = use_semantic_embeddings(
        text=text,
        model_path="SOMA_semantic_model.pkl"
    )
    
    # Example 2: Compare similarity
    print("\n\n")
    compare_embeddings(
        text1="machine learning",
        text2="artificial intelligence",
        model_path="SOMA_semantic_model.pkl"
    )


if __name__ == "__main__":
    main()
