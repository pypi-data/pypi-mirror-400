"""
Complete Source Map Integration Example
========================================

Demonstrates how to use the SOMA Source Map system in a complete workflow
from tokenization to embedding generation with source tagging.

Designed for Railway compute execution.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.integration.source_map_integration import (
    SourceMapTokenizer,
    SourceMapEmbeddingGenerator,
    create_source_aware_workflow
)
from src.SOMA_sources import get_source_map


def example_basic_workflow():
    """Basic workflow with source tagging."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Source-Aware Workflow")
    print("=" * 80)
    
    text = """
    SOMA is a universal tokenization system that supports multiple algorithms.
    It can tokenize text using space, word, character, grammar, and subword methods.
    The system generates embeddings that can be merged from multiple knowledge sources.
    """
    
    # Process with Wikipedia source
    result = create_source_aware_workflow(
        text=text,
        source_tag="wikipedia",
        tokenization_method="word",
        embedding_strategy="feature_based"
    )
    
    print(f"\n✓ Text processed from Wikipedia source")
    print(f"  - Tokens: {result['tokenization']['token_count']}")
    print(f"  - Source ID: {result['tokenization']['source_id']}")
    print(f"  - Algorithm: {result['tokenization']['algorithm_id']}")
    print(f"  - Embeddings: {result['embedding']['embedding_count']}")
    
    print("\n" + "=" * 80)


def example_multi_source_merging():
    """Merge embeddings from multiple sources."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Multi-Source Embedding Merging")
    print("=" * 80)
    
    text = "Machine learning and natural language processing are advancing rapidly."
    
    # Process from multiple sources
    sources = ["wikipedia", "arxiv", "github_corpus"]
    embeddings_list = []
    
    embedding_gen = SourceMapEmbeddingGenerator()
    
    for source_tag in sources:
        print(f"\n✓ Processing from {source_tag}...")
        
        # Tokenize
        tokenizer = SourceMapTokenizer(source_tag=source_tag)
        token_result = tokenizer.tokenize_with_source(text, method="word")
        
        # Generate embeddings
        embedding_result = embedding_gen.generate_with_source(
            tokens=token_result["tokens"],
            source_tag=source_tag,
            strategy="feature_based"
        )
        
        embeddings_list.append(embedding_result)
        print(f"  - Source ID: {embedding_result['source_id']}")
        print(f"  - Weight: {embedding_result['weight']}")
    
    # Merge embeddings
    print(f"\n✓ Merging embeddings from {len(sources)} sources...")
    merged = embedding_gen.merge_embeddings_from_sources(embeddings_list)
    
    print(f"  - Merged embedding dimension: {len(merged['merged_embedding'])}")
    print(f"  - Combined sources: {merged['combined_metadata']['source_tags']}")
    print(f"  - Weights: {merged['combined_metadata']['weights']}")
    
    print("\n" + "=" * 80)


def example_source_profiling():
    """Show source performance profiling."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Source Performance Profiling")
    print("=" * 80)
    
    source_map = get_source_map()
    
    # Get overall profile
    profile = source_map.get_performance_profile()
    
    print(f"\n✓ Overall Source Map Profile:")
    print(f"  - Total sources: {profile['total_sources']}")
    print(f"  - Enabled sources: {profile['enabled_sources']}")
    print(f"  - Total weight: {profile['total_weight']:.2f}")
    print(f"  - Average priority: {profile['average_priority']:.2f}")
    
    print(f"\n✓ Category Breakdown:")
    for category, cat_data in profile['categories'].items():
        print(f"\n  [{category.upper()}]")
        print(f"    - Sources: {cat_data['count']} (enabled: {cat_data['enabled_count']})")
        print(f"    - Total weight: {cat_data['total_weight']:.2f}")
        print(f"    - Average priority: {cat_data['average_priority']:.2f}")
        print(f"    - Top sources: {', '.join([s['tag'] for s in cat_data['sources'][:3]])}")
    
    print("\n" + "=" * 80)


def example_custom_source():
    """Register and use a custom source."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Custom Source Registration")
    print("=" * 80)
    
    source_map = get_source_map()
    
    # Register a custom source
    print("\n✓ Registering custom source...")
    custom_source_id = source_map.register_source(
        tag="my_custom_corpus",
        category="domain",
        description="My custom text corpus",
        url="https://example.com/my-corpus",
        weight=1.0,
        priority=7,
        enabled=True
    )
    
    print(f"  - Source ID: {custom_source_id}")
    print(f"  - Tag: my_custom_corpus")
    
    # Use the custom source
    text = "This text comes from my custom corpus."
    tokenizer = SourceMapTokenizer(source_tag="my_custom_corpus")
    result = tokenizer.tokenize_with_source(text, method="word")
    
    print(f"\n✓ Tokenized with custom source:")
    print(f"  - Source ID: {result['source_id']}")
    print(f"  - Tokens: {result['token_count']}")
    
    print("\n" + "=" * 80)


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("SOMA SOURCE MAP INTEGRATION EXAMPLES")
    print("=" * 80)
    print("\nDemonstrating complete source map integration workflow...")
    
    try:
        example_basic_workflow()
        example_multi_source_merging()
        example_source_profiling()
        example_custom_source()
        
        print("\n" + "=" * 80)
        print("✓ ALL EXAMPLES COMPLETED")
        print("=" * 80)
        print("\n✓ Source map system fully integrated!")
        print("✓ Ready for Railway compute deployment!")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
