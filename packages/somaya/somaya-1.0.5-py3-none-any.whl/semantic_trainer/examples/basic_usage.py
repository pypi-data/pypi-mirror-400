"""
Basic usage example for Enhanced SOMA Semantic Trainer
"""

import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from enhanced_trainer import EnhancedSOMASemanticTrainer
from src.core.core_tokenizer import TextTokenizer


def main():
    # Sample text corpus
    text = """
    Natural language processing is a field of artificial intelligence.
    Machine learning models learn patterns from data.
    Deep learning uses neural networks with multiple layers.
    Tokenization is the process of breaking text into tokens.
    Embeddings represent tokens as dense vectors.
    Semantic embeddings capture meaning and relationships.
    """
    
    print("=" * 60)
    print("Enhanced SOMA Semantic Trainer - Basic Example")
    print("=" * 60)
    print()
    
    # Step 1: Tokenize with all streams
    print("Step 1: Tokenizing with SOMA (all streams)...")
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    streams = tokenizer.build(text)
    
    print(f"Streams: {list(streams.keys())}")
    for stream_name, stream in streams.items():
        print(f"  - {stream_name}: {len(stream.tokens)} tokens")
    print()
    
    # Step 2: Initialize enhanced trainer
    print("Step 2: Initializing enhanced trainer...")
    trainer = EnhancedSOMASemanticTrainer(
        embedding_dim=768,
        window_size=5,
        epochs=5,
        use_multi_stream=True,
        use_temporal=True,
        use_content_id_clustering=True,
        use_math_properties=True,
        use_cross_stream_alignment=True,
        use_deterministic_graph=True
    )
    print("[OK] Trainer initialized")
    print()
    
    # Step 3: Train
    print("Step 3: Training...")
    trainer.train(streams)
    print()
    
    # Step 4: Save
    print("Step 4: Saving model...")
    trainer.save("enhanced_model.pkl")
    print()
    
    # Step 5: Test embeddings
    print("Step 5: Testing embeddings...")
    test_token = streams["word"].tokens[0]
    print(f"Test token: '{test_token.text}' (UID: {test_token.uid})")
    
    embedding = trainer.get_embedding(
        token_uid=test_token.uid,
        position=0,
        stream="word"
    )
    
    if embedding is not None:
        print(f"Embedding shape: {embedding.shape}")
        print(f"Embedding sample: {embedding[:5]}")
    else:
        print("Token not in vocabulary")
    
    print()
    print("=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
