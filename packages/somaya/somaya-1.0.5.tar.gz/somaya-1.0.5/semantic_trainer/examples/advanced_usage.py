"""
Advanced usage example - Training on large corpus
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from enhanced_trainer import EnhancedSOMASemanticTrainer
from src.core.core_tokenizer import TextTokenizer


def main():
    # Larger corpus
    corpus = """
    Natural language processing is a field of artificial intelligence that focuses
    on the interaction between computers and human language. Machine learning models
    learn patterns from data to make predictions and decisions. Deep learning uses
    neural networks with multiple layers to learn complex representations.
    
    Tokenization is the process of breaking text into smaller units called tokens.
    Embeddings represent tokens as dense vectors in a high-dimensional space.
    Semantic embeddings capture meaning and relationships between tokens.
    
    Word embeddings like Word2Vec and GloVe learn representations based on
    co-occurrence patterns. Contextual embeddings like BERT capture meaning
    based on surrounding context. Transformer models use attention mechanisms
    to learn relationships between all tokens in a sequence.
    
    SOMA provides a unique tokenization system with deterministic UIDs,
    multi-stream tokenization, and mathematical properties on every token.
    The enhanced semantic trainer leverages all these features to create
    embeddings that understand meaning at multiple granularities.
    """
    
    print("=" * 60)
    print("Advanced Usage - Large Corpus Training")
    print("=" * 60)
    print()
    
    # Tokenize
    print("Tokenizing corpus...")
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    streams = tokenizer.build(corpus)
    
    total_tokens = sum(len(stream.tokens) for stream in streams.values())
    print(f"Total tokens across all streams: {total_tokens:,}")
    print()
    
    # Initialize trainer with all features
    trainer = EnhancedSOMASemanticTrainer(
        embedding_dim=768,
        window_size=5,
        epochs=10,
        min_count=1,  # Lower threshold for small corpus
        use_multi_stream=True,
        use_temporal=True,
        use_content_id_clustering=True,
        use_math_properties=True,
        use_cross_stream_alignment=True,
        use_deterministic_graph=True
    )
    
    # Train
    trainer.train(streams)
    
    # Save
    trainer.save("enhanced_model_advanced.pkl")
    
    # Test multiple tokens
    print()
    print("Testing embeddings for multiple tokens:")
    print("-" * 60)
    
    test_tokens = [
        ("word", 0, "Natural"),
        ("word", 1, "language"),
        ("char", 0, "N"),
        ("subword", 0, "Nat")
    ]
    
    for stream_name, idx, expected_text in test_tokens:
        if stream_name in streams and idx < len(streams[stream_name].tokens):
            token = streams[stream_name].tokens[idx]
            embedding = trainer.get_embedding(
                token_uid=token.uid,
                position=idx,
                stream=stream_name
            )
            
            if embedding is not None:
                print(f"Token: '{token.text}' (stream: {stream_name}, pos: {idx})")
                print(f"  UID: {token.uid}")
                print(f"  Embedding shape: {embedding.shape}")
                print(f"  Embedding norm: {np.linalg.norm(embedding):.4f}")
                print()
    
    print("=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    import numpy as np
    main()
