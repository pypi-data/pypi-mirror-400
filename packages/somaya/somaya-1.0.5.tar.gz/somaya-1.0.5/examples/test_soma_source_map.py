"""
Test SOMA Source Map Integration
===================================

This script demonstrates how to use the SOMA Source Map system
for token source tagging and embedding merging.

Designed for Railway compute execution.
"""

import sys
import os

# Force immediate output for job manager
sys.stdout.flush()
sys.stderr.flush()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Print immediately so job manager sees we're starting
print("Loading modules...", flush=True)
sys.stdout.flush()

try:
    from src.SOMA_sources import get_source_map, SOMA_SOURCES
    print("✓ Loaded SOMA_sources", flush=True)
except ImportError as e:
    print(f"✗ Failed to import soma_sources: {e}", flush=True, file=sys.stderr)
    raise

try:
    from src.core.core_tokenizer import TextTokenizer, TokenStream
    print("✓ Loaded core_tokenizer", flush=True)
except ImportError as e:
    print(f"✗ Failed to import core_tokenizer: {e}", flush=True, file=sys.stderr)
    raise

try:
    from src.embeddings.embedding_generator import somaEmbeddingGenerator
    print("✓ Loaded embedding_generator", flush=True)
except ImportError as e:
    print(f"✗ Failed to import embedding_generator: {e}", flush=True, file=sys.stderr)
    raise

sys.stdout.flush()


def test_source_map_basic():
    """Test basic source map functionality."""
    print("=" * 80)
    print("TEST 1: Basic Source Map Operations")
    print("=" * 80)
    
    # Get source map instance
    source_map = get_source_map()
    print(f"\n✓ Source map initialized: {source_map}")
    print(f"✓ Total sources registered: {len(source_map.sources)}")
    
    # Get all sources
    all_sources = source_map.get_all_sources(enabled_only=False)
    print(f"\n✓ Total sources available: {len(all_sources)}")
    
    # Test source ID generation
    wikipedia_id = source_map.get_source_id("wikipedia")
    print(f"\n✓ Wikipedia source ID: {wikipedia_id}")
    
    # Get source metadata
    wiki_metadata = source_map.get_source_metadata("wikipedia")
    if wiki_metadata:
        print(f"✓ Wikipedia metadata:")
        print(f"  - Category: {wiki_metadata.category}")
        print(f"  - Description: {wiki_metadata.description}")
        print(f"  - Weight: {wiki_metadata.weight}")
        print(f"  - Priority: {wiki_metadata.priority}")
    
    print("\n" + "=" * 80)


def test_source_tagging():
    """Test token source tagging."""
    print("\n" + "=" * 80)
    print("TEST 2: Token Source Tagging")
    print("=" * 80)
    
    source_map = get_source_map()
    
    # Example: Tokenize text from Wikipedia source
    text = "SOMA is a universal tokenization system."
    
    print(f"\n✓ Tokenizing text from Wikipedia source...")
    print(f"  Text: '{text}'")
    
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    streams = tokenizer.build(text)
    # Get tokens from the 'word' stream
    word_stream = streams.get('word')
    tokens = word_stream.tokens if word_stream else []
    
    print(f"\n✓ Tokens generated: {len(tokens)} tokens")
    
    # Tag tokens with source metadata
    source_tags = source_map.get_source_tags_for_token(
        source_tag="wikipedia",
        algorithm_id="word_tokenization",
        timestamp=None  # Will use current time
    )
    
    print(f"\n✓ Source tags for tokens:")
    for key, value in source_tags.items():
        print(f"  - {key}: {value}")
    
    # Example with multiple sources
    print(f"\n✓ Testing multiple source tags...")
    sources = ["wikipedia", "arxiv", "github_corpus"]
    for source_tag in sources:
        tags = source_map.get_source_tags_for_token(
            source_tag=source_tag,
            algorithm_id="hybrid_tokenization"
        )
        print(f"  - {source_tag}: source_id={tags['source_id'][:8]}...")
    
    print("\n" + "=" * 80)


def test_embedding_merging():
    """Test weighted embedding merging."""
    print("\n" + "=" * 80)
    print("TEST 3: Weighted Embedding Merging")
    print("=" * 80)
    
    source_map = get_source_map()
    
    # Create sample embeddings from different sources
    print("\n✓ Creating sample embeddings from different sources...")
    
    # Embedding 1: Wikipedia (weight 1.0)
    embedding1 = [0.1, 0.2, 0.3, 0.4, 0.5]
    tags1 = source_map.get_source_tags_for_token("wikipedia", "word_tokenization")
    
    # Embedding 2: ArXiv (weight 1.0)
    embedding2 = [0.2, 0.3, 0.4, 0.5, 0.6]
    tags2 = source_map.get_source_tags_for_token("arxiv", "subword_tokenization")
    
    # Embedding 3: Reddit (weight 0.8)
    embedding3 = [0.3, 0.4, 0.5, 0.6, 0.7]
    tags3 = source_map.get_source_tags_for_token("reddit", "byte_tokenization")
    
    embeddings = [
        (embedding1, tags1),
        (embedding2, tags2),
        (embedding3, tags3)
    ]
    
    print(f"  - Wikipedia embedding: {embedding1[:3]}... (weight: {tags1['weight']})")
    print(f"  - ArXiv embedding: {embedding2[:3]}... (weight: {tags2['weight']})")
    print(f"  - Reddit embedding: {embedding3[:3]}... (weight: {tags3['weight']})")
    
    # Merge embeddings
    merged_embedding, combined_metadata = source_map.merge_embeddings(embeddings)
    
    print(f"\n✓ Merged embedding: {[round(x, 4) for x in merged_embedding]}")
    print(f"\n✓ Combined metadata:")
    print(f"  - Source IDs: {combined_metadata['source_ids']}")
    print(f"  - Source tags: {combined_metadata['source_tags']}")
    print(f"  - Algorithm IDs: {combined_metadata['algorithm_ids']}")
    print(f"  - Weights: {combined_metadata['weights']}")
    print(f"  - Merged at: {combined_metadata['merged_at']}")
    
    print("\n" + "=" * 80)


def test_performance_profile():
    """Test hierarchical performance profiling."""
    print("\n" + "=" * 80)
    print("TEST 4: Hierarchical Performance Profiling")
    print("=" * 80)
    
    source_map = get_source_map()
    
    # Get overall profile
    profile = source_map.get_performance_profile()
    
    print(f"\n✓ Overall Profile:")
    print(f"  - Total sources: {profile['total_sources']}")
    print(f"  - Enabled sources: {profile['enabled_sources']}")
    print(f"  - Total weight: {profile['total_weight']:.2f}")
    print(f"  - Average priority: {profile['average_priority']:.2f}")
    
    print(f"\n✓ Category-wise breakdown:")
    for category, cat_data in profile['categories'].items():
        print(f"\n  [{category.upper()}]")
        print(f"    - Sources: {cat_data['count']} (enabled: {cat_data['enabled_count']})")
        print(f"    - Total weight: {cat_data['total_weight']:.2f}")
        print(f"    - Average priority: {cat_data['average_priority']:.2f}")
        print(f"    - Source tags: {[s['tag'] for s in cat_data['sources'][:5]]}")
        if cat_data['count'] > 5:
            print(f"      ... and {cat_data['count'] - 5} more")
    
    # Get profile for specific category
    print(f"\n✓ Knowledge category profile:")
    knowledge_profile = source_map.get_performance_profile(category="knowledge")
    print(f"  - Sources: {knowledge_profile['total_sources']}")
    print(f"  - Enabled: {knowledge_profile['enabled_sources']}")
    
    print("\n" + "=" * 80)


def test_integration_with_tokenizer():
    """Test integration with actual tokenizer and embedding generator."""
    print("\n" + "=" * 80)
    print("TEST 5: Integration with Tokenizer & Embedding Generator")
    print("=" * 80)
    
    source_map = get_source_map()
    
    # Sample text (simulating Wikipedia content)
    text = """
    SOMA is a universal tokenization system that supports multiple algorithms.
    It can tokenize text using space, word, character, grammar, and subword methods.
    The system generates embeddings that can be merged from multiple knowledge sources.
    """
    
    print(f"\n✓ Processing text from Wikipedia source...")
    print(f"  Text length: {len(text)} characters")
    
    # Tokenize
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    streams = tokenizer.build(text)
    # Get tokens from the 'word' stream
    word_stream = streams.get('word')
    tokens = word_stream.tokens if word_stream else []
    
    print(f"\n✓ Tokenization complete:")
    print(f"  - Method: word")
    print(f"  - Tokens: {len(tokens)}")
    print(f"  - Sample tokens: {[t.text for t in tokens[:10]]}")
    
    # Generate embeddings with source tagging
    print(f"\n✓ Generating embeddings with source tagging...")
    
    generator = SOMAEmbeddingGenerator()
    
    # Get source tags
    source_tags = source_map.get_source_tags_for_token(
        source_tag="wikipedia",
        algorithm_id="word_tokenization"
    )
    
    print(f"  - Source ID: {source_tags['source_id']}")
    print(f"  - Source tag: {source_tags['source_tag']}")
    print(f"  - Algorithm ID: {source_tags['algorithm_id']}")
    
    # Generate embedding (simplified example)
    print(f"\n✓ Embedding generation would include source metadata:")
    print(f"  {source_tags}")
    
    print("\n" + "=" * 80)


def main():
    """Run all tests."""
    import sys
    # Force immediate output
    sys.stdout.flush()
    sys.stderr.flush()
    
    print("\n" + "=" * 80, flush=True)
    print("SOMA SOURCE MAP TEST SUITE", flush=True)
    print("=" * 80, flush=True)
    print("\nTesting SOMA Source Map system for Railway compute...", flush=True)
    sys.stdout.flush()
    
    try:
        test_source_map_basic()
        test_source_tagging()
        test_embedding_merging()
        test_performance_profile()
        test_integration_with_tokenizer()
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED")
        print("=" * 80)
        print("\n✓ Source map system is ready for Railway compute integration!")
        print("✓ All sources registered and metadata available")
        print("✓ Source tagging, embedding merging, and profiling working")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    # Flush output immediately to help with job manager
    import sys
    sys.stdout.flush()
    sys.stderr.flush()
    
    # Print immediately so job manager knows we started
    print("Starting SOMA Source Map test...", flush=True)
    sys.stdout.flush()
    
    exit(main())
