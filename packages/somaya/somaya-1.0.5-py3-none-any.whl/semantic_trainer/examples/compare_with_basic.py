"""
Compare Enhanced Trainer vs Basic Trainer
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from enhanced_trainer import EnhancedSOMASemanticTrainer
from src.embeddings.semantic_trainer import somaSemanticTrainer
from src.core.core_tokenizer import TextTokenizer


def main():
    text = """
    Natural language processing is a field of artificial intelligence.
    Machine learning models learn patterns from data.
    Semantic embeddings capture meaning and relationships.
    """
    
    print("=" * 60)
    print("Comparison: Enhanced vs Basic Trainer")
    print("=" * 60)
    print()
    
    # Tokenize
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    streams = tokenizer.build(text)
    
    # Collect all tokens for basic trainer
    all_tokens = []
    for stream in streams.values():
        all_tokens.extend(stream.tokens)
    
    print("BASIC TRAINER:")
    print("-" * 60)
    basic_trainer = SOMASemanticTrainer(
        embedding_dim=768,
        window_size=5,
        epochs=3
    )
    basic_trainer.build_vocab(all_tokens)
    basic_trainer.build_cooccurrence(all_tokens)
    basic_trainer.train(all_tokens)
    
    print()
    print("ENHANCED TRAINER:")
    print("-" * 60)
    enhanced_trainer = EnhancedSOMASemanticTrainer(
        embedding_dim=768,
        window_size=5,
        epochs=3,
        use_multi_stream=True,
        use_temporal=True,
        use_content_id_clustering=True,
        use_math_properties=True
    )
    enhanced_trainer.train(streams)
    
    print()
    print("COMPARISON:")
    print("-" * 60)
    print("Basic trainer:")
    print(f"  - Uses single stream")
    print(f"  - Basic co-occurrence")
    print(f"  - No temporal awareness")
    print(f"  - No content-ID clustering")
    print(f"  - No math properties")
    print()
    print("Enhanced trainer:")
    print(f"  - Uses ALL streams simultaneously")
    print(f"  - Enhanced co-occurrence (neighbors + content-ID + sequential)")
    print(f"  - Temporal/position-dependent embeddings")
    print(f"  - Content-ID clustering")
    print(f"  - Math properties integration")
    print(f"  - Cross-stream alignment")
    print(f"  - Deterministic UID graph")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
