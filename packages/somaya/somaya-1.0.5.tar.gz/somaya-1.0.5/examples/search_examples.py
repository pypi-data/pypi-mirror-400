"""
What You Can Do With Your 30 Batches (3M Tokens)
==================================================

This script demonstrates practical uses of your loaded vector store:

1. SEMANTIC SEARCH - Find words/concepts similar to any token
2. CONCEPT EXPLORATION - Discover related terms and ideas
3. CONTEXT ANALYSIS - Understand word relationships
4. SIMILARITY ANALYSIS - Measure how similar tokens are
5. CLUSTERING - Group related concepts together
"""

import sys
import os
import json
import numpy as np
import pickle

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings.vector_store import FAISSVectorStore
from src.embeddings.embedding_generator import somaEmbeddingGenerator


def quick_load_vector_store(output_dir="workflow_output", max_batches=30):
    """Quickly load vector store (optimized version)."""
    print("[INFO] Loading vector store...")
    
    # Load tokens with proper import handling for pickle
    tokens_file = os.path.join(output_dir, "tokens.pkl")
    try:
        # Setup import paths for pickle compatibility
        import sys
        import types
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent
        src_path = project_root / 'src'
        
        # Add paths to sys.path if not already there
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Create mock modules for pickle compatibility
        if 'core' not in sys.modules:
            core_module = types.ModuleType('core')
            sys.modules['core'] = core_module
        if 'core.core_tokenizer' not in sys.modules:
            core_tokenizer_module = types.ModuleType('core.core_tokenizer')
            sys.modules['core.core_tokenizer'] = core_tokenizer_module
            try:
                from src.core.core_tokenizer import TokenRecord, TokenStream
                core_tokenizer_module.TokenRecord = TokenRecord
                core_tokenizer_module.TokenStream = TokenStream
            except ImportError:
                pass
        
        # Create custom unpickler
        class CustomUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                if module == 'core.core_tokenizer' or module == 'core':
                    try:
                        from src.core.core_tokenizer import TokenRecord, TokenStream
                        if name == 'TokenRecord':
                            return TokenRecord
                        elif name == 'TokenStream':
                            return TokenStream
                    except ImportError:
                        pass
                return super().find_class(module, name)
        
        with open(tokens_file, 'rb') as f:
            try:
                unpickler = CustomUnpickler(f)
                all_tokens = unpickler.load()
            except Exception:
                f.seek(0)
                all_tokens = pickle.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load tokens: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None
    
    # Load metadata
    metadata_file = os.path.join(output_dir, "embedding_batches_metadata.json")
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    batch_files = metadata.get("batch_files", [])[:max_batches]
    embedding_dim = metadata.get("embedding_dim", 768)
    batch_size = metadata.get("batch_size", 50000)
    
    # Create vector store
    vector_store = FAISSVectorStore(embedding_dim=embedding_dim)
    
    # Load batches
    max_tokens = max_batches * batch_size
    sample_tokens = all_tokens[:min(max_tokens, len(all_tokens))]
    
    total_added = 0
    for batch_idx, batch_file in enumerate(batch_files):
        if not os.path.exists(batch_file):
            continue
        
        batch_emb = np.load(batch_file)
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + len(batch_emb), len(sample_tokens))
        batch_tokens = sample_tokens[batch_start:batch_end]
        
        # Add in chunks
        for chunk_start in range(0, len(batch_tokens), 10000):
            chunk_end = min(chunk_start + 10000, len(batch_tokens))
            vector_store.add_tokens(
                batch_tokens[chunk_start:chunk_end],
                batch_emb[chunk_start:chunk_end]
            )
        
        total_added += len(batch_tokens)
        if (batch_idx + 1) % 10 == 0:
            print(f"  Loaded {batch_idx + 1}/{len(batch_files)} batches ({total_added:,} tokens)")
    
    print(f"[OK] Loaded {total_added:,} tokens into vector store\n")
    return vector_store, sample_tokens, batch_size, batch_files


def find_token_embedding(token_text, sample_tokens, batch_files, batch_size):
    """Find embedding for a token."""
    # Find token
    for idx, token in enumerate(sample_tokens):
        if getattr(token, 'text', '') == token_text:
            batch_idx = idx // batch_size
            if batch_idx < len(batch_files) and os.path.exists(batch_files[batch_idx]):
                batch_emb = np.load(batch_files[batch_idx])
                local_idx = idx % batch_size
                if local_idx < len(batch_emb):
                    return batch_emb[local_idx]
    
    # Try case-insensitive
    for idx, token in enumerate(sample_tokens):
        if getattr(token, 'text', '').lower() == token_text.lower():
            batch_idx = idx // batch_size
            if batch_idx < len(batch_files) and os.path.exists(batch_files[batch_idx]):
                batch_emb = np.load(batch_files[batch_idx])
                local_idx = idx % batch_size
                if local_idx < len(batch_emb):
                    return batch_emb[local_idx]
    
    return None


def filter_stop_words(results, stop_words=None):
    """Filter out common stop words from results."""
    if stop_words is None:
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'it', 'its',
            'they', 'them', 'their', 'there', 'here', 'where', 'when', 'what', 'who',
            'which', 'how', 'why', 'if', 'then', 'else', 'so', 'than', 'more', 'most',
            'very', 'just', 'only', 'also', 'too', 'up', 'down', 'out', 'off', 'over',
            'under', 'again', 'further', 'then', 'once'
        }
    
    filtered = []
    seen = set()
    for result in results:
        text = result.get('text', '').strip()
        text_lower = text.lower()
        
        # Skip if empty, stop word, or duplicate
        if not text or text_lower in stop_words or text_lower in seen:
            continue
        
        # Skip single character tokens (except if they're meaningful)
        if len(text) == 1 and text.lower() not in ['i', 'a']:
            continue
        
        # Skip punctuation-only tokens
        if text.strip('.,!?;:()[]{}"\'').strip() == '':
            continue
        
        seen.add(text_lower)
        filtered.append(result)
    
    return filtered


def semantic_search(vector_store, query_token, sample_tokens, batch_files, batch_size, 
                   top_k=20, min_similarity=0.5, filter_stop=True):
    """Search for semantically similar tokens with filtering."""
    print(f"\n[INFO] Searching for tokens similar to: '{query_token}'")
    print("-" * 60)
    
    # Get query embedding
    query_emb = find_token_embedding(query_token, sample_tokens, batch_files, batch_size)
    if query_emb is None:
        print(f"[ERROR] Token '{query_token}' not found in dataset")
        return []
    
    # Search with larger top_k to have more candidates after filtering
    results = vector_store.search(query_emb, top_k=top_k * 3)
    
    # Filter results
    if filter_stop:
        results = filter_stop_words(results)
    
    # Filter by minimum similarity
    filtered_results = []
    for result in results:
        dist = result.get('distance', 0.0)
        similarity = 1.0 / (1.0 + dist)
        if similarity >= min_similarity:
            filtered_results.append(result)
        if len(filtered_results) >= top_k:
            break
    
    # Display results
    if not filtered_results:
        print(f"[ERROR] No similar tokens found (min similarity: {min_similarity})")
        return []
    
    print(f"Top {len(filtered_results)} most similar tokens (min similarity: {min_similarity}):")
    for i, result in enumerate(filtered_results, 1):
        text = result.get('text', 'N/A')
        dist = result.get('distance', 0.0)
        similarity = 1.0 / (1.0 + dist)
        metadata = result.get('metadata', {})
        
        # Skip the query token itself if it appears
        if text.lower() == query_token.lower() and i > 1:
            continue
        
        print(f"  {i:2d}. {text:30s} (similarity: {similarity:.3f}, distance: {dist:.4f})")
        if metadata.get('stream'):
            print(f"      └─ Stream: {metadata['stream']}, UID: {metadata.get('uid', 'N/A')}")
    
    return filtered_results


def find_related_concepts(vector_store, concept_tokens, sample_tokens, batch_files, batch_size, 
                         top_k=15, min_similarity=0.4):
    """Find concepts related to multiple tokens."""
    print(f"\n[INFO] Finding concepts related to: {', '.join(concept_tokens)}")
    print("-" * 60)
    
    # Get embeddings for all concept tokens
    embeddings = []
    found_tokens = []
    for token in concept_tokens:
        emb = find_token_embedding(token, sample_tokens, batch_files, batch_size)
        if emb is not None:
            embeddings.append(emb)
            found_tokens.append(token)
    
    if not embeddings:
        print("[ERROR] None of the concept tokens found")
        return []
    
    if len(found_tokens) < len(concept_tokens):
        print(f"[WARNING]  Only found {len(found_tokens)}/{len(concept_tokens)} tokens: {found_tokens}")
    
    # Average the embeddings to get a combined concept
    avg_embedding = np.mean(embeddings, axis=0)
    
    # Search with filtering
    results = vector_store.search(avg_embedding, top_k=top_k * 3)
    results = filter_stop_words(results)
    
    # Filter by similarity and exclude input tokens
    filtered_results = []
    input_lower = {t.lower() for t in concept_tokens}
    for result in results:
        text = result.get('text', 'N/A')
        if text.lower() in input_lower:
            continue
        
        dist = result.get('distance', 0.0)
        similarity = 1.0 / (1.0 + dist)
        if similarity >= min_similarity:
            filtered_results.append(result)
        if len(filtered_results) >= top_k:
            break
    
    print(f"Related concepts (min similarity: {min_similarity}):")
    for i, result in enumerate(filtered_results, 1):
        text = result.get('text', 'N/A')
        dist = result.get('distance', 0.0)
        similarity = 1.0 / (1.0 + dist)
        print(f"  {i:2d}. {text:30s} (similarity: {similarity:.3f}, distance: {dist:.4f})")
    
    return filtered_results


def compare_tokens(vector_store, token1, token2, sample_tokens, batch_files, batch_size):
    """Compare similarity between two tokens."""
    print(f"\n[INFO]  Comparing: '{token1}' vs '{token2}'")
    print("-" * 60)
    
    emb1 = find_token_embedding(token1, sample_tokens, batch_files, batch_size)
    emb2 = find_token_embedding(token2, sample_tokens, batch_files, batch_size)
    
    if emb1 is None or emb2 is None:
        print("[ERROR] One or both tokens not found")
        return None
    
    # Calculate distance
    distance = np.linalg.norm(emb1 - emb2)
    similarity = 1.0 / (1.0 + distance)
    
    print(f"Distance: {distance:.4f}")
    print(f"Similarity: {similarity:.3f} ({similarity*100:.1f}%)")
    
    if similarity > 0.8:
        print("  → Very similar (likely related concepts)")
    elif similarity > 0.6:
        print("  → Moderately similar (somewhat related)")
    elif similarity > 0.4:
        print("  → Somewhat similar (loosely related)")
    else:
        print("  → Not very similar (different concepts)")
    
    return similarity


def explore_concept(vector_store, concept, sample_tokens, batch_files, batch_size, depth=2, 
                   top_k_per_level=10, min_similarity=0.4, verbose=True):
    """Explore a concept by finding related terms at multiple levels."""
    print(f"\n🌐 Exploring concept: '{concept}' (depth: {depth}, min similarity: {min_similarity})")
    print("-" * 60)
    
    # Track explored concepts (but allow starting concept to be processed)
    explored = set()
    to_explore = [concept]
    all_related = []
    
    for level in range(depth):
        if not to_explore:
            break
        
        print(f"\n📍 Level {level + 1} - Exploring {len(to_explore)} concept(s):")
        level_terms = []
        level_results = []
        
        for term in to_explore:
            # Mark as explored (but still process it)
            term_key = term.lower()
            if term_key in explored:
                continue
            explored.add(term_key)
            
            # Get embedding for this term
            query_emb = find_token_embedding(term, sample_tokens, batch_files, batch_size)
            if query_emb is None:
                print(f"  [WARNING]  Could not find embedding for '{term}'")
                continue
            
            # Search for similar tokens
            results = vector_store.search(query_emb, top_k=top_k_per_level * 5)
            if not results:
                print(f"  [WARNING]  No results found for '{term}'")
                continue
            
            # Filter stop words
            results = filter_stop_words(results)
            
            # Filter by similarity and collect unique terms
            filtered = []
            seen_texts = set()
            
            for result in results:
                text = result.get('text', '').strip()
                if not text or text.lower() in seen_texts:
                    continue
                
                dist = result.get('distance', 0.0)
                similarity = 1.0 / (1.0 + dist)
                
                # Skip the query term itself
                if text.lower() == term_key:
                    continue
                
                # Apply similarity threshold
                if similarity >= min_similarity:
                    filtered.append((text, dist, similarity))
                    seen_texts.add(text.lower())
                    if len(filtered) >= top_k_per_level:
                        break
            
            # If no results found, try with a lower threshold
            if not filtered and min_similarity > 0.3:
                fallback_threshold = max(0.3, min_similarity - 0.15)
                for result in results:
                    text = result.get('text', '').strip()
                    if not text or text.lower() in seen_texts or text.lower() == term_key:
                        continue
                    
                    dist = result.get('distance', 0.0)
                    similarity = 1.0 / (1.0 + dist)
                    
                    if similarity >= fallback_threshold:
                        filtered.append((text, dist, similarity))
                        seen_texts.add(text.lower())
                        if len(filtered) >= top_k_per_level:
                            break
                
                if filtered:
                    print(f"     (Lowered threshold to {fallback_threshold:.2f} to find results)")
            
            # Add to results
            for text, dist, similarity in filtered:
                text_lower = text.lower()
                # Only add if not already explored and not the starting concept
                if text_lower not in explored and text_lower != concept.lower():
                    level_terms.append(text)
                    level_results.append((text, level + 1, dist, similarity))
                    all_related.append((text, level + 1))
        
        # Show level results
        if level_results:
            print(f"  [OK] Found {len(level_results)} unique related concepts:")
            for text, lev, dist, similarity in level_results[:15]:
                print(f"     • {text:25s} (similarity: {similarity:.3f}, level {lev})")
        else:
            print(f"  [WARNING]  No new concepts found at level {level + 1}")
            # Try with lower threshold
            if level == 0 and min_similarity >= 0.4:
                print(f"     (Try lowering min_similarity or check if '{concept}' exists in the dataset)")
        
        # Prepare next level
        to_explore = level_terms[:10]  # Limit expansion for next level
    
    # Final summary
    print(f"\n[INFO] Summary: Discovered {len(all_related)} unique related terms across {depth} levels")
    if all_related:
        # Show unique concepts by level
        by_level = {}
        for text, lev in all_related:
            if lev not in by_level:
                by_level[lev] = []
            if text not in by_level[lev]:
                by_level[lev].append(text)
        
        for lev in sorted(by_level.keys()):
            print(f"\n  Level {lev} concepts ({len(by_level[lev])}): {', '.join(by_level[lev][:10])}")
            if len(by_level[lev]) > 10:
                print(f"    ... and {len(by_level[lev]) - 10} more")
    else:
        print(f"  💡 Tip: Try lowering min_similarity or using 'search {concept}' to see what's available")
    
    return all_related


def find_concept_cluster(vector_store, seed_concept, sample_tokens, batch_files, batch_size, 
                        cluster_size=10, min_similarity=0.6):
    """Find a cluster of related concepts around a seed."""
    print(f"\n[INFO] Finding concept cluster around: '{seed_concept}'")
    print("-" * 60)
    print(f"Cluster size: {cluster_size}, Min similarity: {min_similarity}")
    
    # Get seed embedding
    seed_emb = find_token_embedding(seed_concept, sample_tokens, batch_files, batch_size)
    if seed_emb is None:
        print(f"[ERROR] Seed concept '{seed_concept}' not found")
        return []
    
    # Search for cluster
    results = vector_store.search(seed_emb, top_k=cluster_size * 2)
    results = filter_stop_words(results)
    
    # Filter and build cluster
    cluster = []
    seed_lower = seed_concept.lower()
    for result in results:
        text = result.get('text', 'N/A')
        if text.lower() == seed_lower:
            continue
        
        dist = result.get('distance', 0.0)
        similarity = 1.0 / (1.0 + dist)
        if similarity >= min_similarity:
            cluster.append({
                'concept': text,
                'similarity': similarity,
                'distance': dist
            })
        if len(cluster) >= cluster_size:
            break
    
    if cluster:
        print(f"\n📦 Concept Cluster (found {len(cluster)} concepts):")
        for i, item in enumerate(cluster, 1):
            print(f"  {i:2d}. {item['concept']:30s} (similarity: {item['similarity']:.3f})")
    else:
        print(f"[ERROR] No cluster found (try lowering min_similarity)")
    
    return cluster


def main():
    """Run example searches."""
    print("=" * 80)
    print("VECTOR STORE USAGE EXAMPLES")
    print("=" * 80)
    print("\nWhat you can do with your 30 batches (3M tokens):")
    print("  1. Semantic Search - Find similar words/concepts")
    print("  2. Concept Exploration - Discover related terms")
    print("  3. Similarity Comparison - Compare two tokens")
    print("  4. Concept Clustering - Find groups of related concepts")
    print("  5. Context Analysis - Understand word relationships\n")
    
    # Load vector store
    vector_store, sample_tokens, batch_size, batch_files = quick_load_vector_store(max_batches=30)
    
    # Example 1: Semantic Search (Improved with filtering)
    print("\n" + "=" * 80)
    print("EXAMPLE 1: SEMANTIC SEARCH (Filtered)")
    print("=" * 80)
    print("💡 Now with stop word filtering and deduplication for better results!")
    semantic_search(vector_store, "Artificial", sample_tokens, batch_files, batch_size, 
                   top_k=10, min_similarity=0.6)
    semantic_search(vector_store, "machine", sample_tokens, batch_files, batch_size, 
                   top_k=10, min_similarity=0.6)
    semantic_search(vector_store, "learning", sample_tokens, batch_files, batch_size, 
                   top_k=10, min_similarity=0.6)
    
    # Example 2: Compare Tokens
    print("\n" + "=" * 80)
    print("EXAMPLE 2: TOKEN COMPARISON")
    print("=" * 80)
    compare_tokens(vector_store, "Artificial", "intelligence", sample_tokens, batch_files, batch_size)
    compare_tokens(vector_store, "machine", "learning", sample_tokens, batch_files, batch_size)
    compare_tokens(vector_store, "data", "science", sample_tokens, batch_files, batch_size)
    
    # Example 3: Find Related Concepts (Improved)
    print("\n" + "=" * 80)
    print("EXAMPLE 3: RELATED CONCEPTS")
    print("=" * 80)
    find_related_concepts(vector_store, ["machine", "learning"], sample_tokens, batch_files, batch_size,
                         top_k=15, min_similarity=0.5)
    find_related_concepts(vector_store, ["artificial", "intelligence"], sample_tokens, batch_files, batch_size,
                         top_k=15, min_similarity=0.5)
    
    # Example 4: Concept Clusters
    print("\n" + "=" * 80)
    print("EXAMPLE 4: CONCEPT CLUSTERS")
    print("=" * 80)
    find_concept_cluster(vector_store, "neural", sample_tokens, batch_files, batch_size,
                        cluster_size=10, min_similarity=0.6)
    find_concept_cluster(vector_store, "algorithm", sample_tokens, batch_files, batch_size,
                        cluster_size=10, min_similarity=0.6)
    
    # Example 5: Concept Exploration (Improved)
    print("\n" + "=" * 80)
    print("EXAMPLE 5: CONCEPT EXPLORATION")
    print("=" * 80)
    explore_concept(vector_store, "neural", sample_tokens, batch_files, batch_size, 
                   depth=2, min_similarity=0.4, verbose=True)
    
    print("\n" + "=" * 80)
    print("[OK] EXAMPLES COMPLETE!")
    print("=" * 80)
    print("\n💡 Practical Applications with Your 30 Batches (3M Tokens):")
    print("\n  1. SEMANTIC SEARCH ENGINE")
    print("     - Find tokens by meaning, not just keywords")
    print("     - Build search for your documents/content")
    print("     - Create autocomplete/suggestion systems")
    print("\n  2. RECOMMENDATION SYSTEM")
    print("     - Recommend similar content/concepts")
    print("     - Find related items/products")
    print("     - Content discovery")
    print("\n  3. TEXT ANALYSIS")
    print("     - Document similarity analysis")
    print("     - Duplicate detection")
    print("     - Content clustering")
    print("     - Topic modeling")
    print("\n  4. KNOWLEDGE DISCOVERY")
    print("     - Explore concept relationships")
    print("     - Build knowledge graphs")
    print("     - Discover hidden patterns")
    print("     - Research assistance")
    print("\n  5. NLP TASKS")
    print("     - Word sense disambiguation")
    print("     - Semantic role labeling")
    print("     - Entity linking")
    print("     - Concept extraction")
    print("\n[INFO] Your Data:")
    print(f"  - 3,000,000 tokens searchable in real-time")
    print(f"  - 768-dimensional embeddings")
    print(f"  - Fast FAISS-based similarity search")
    print(f"  - All 117 batches (11.6M tokens) available on disk")
    print("\n[INFO] Next Steps:")
    print("  - Integrate into your applications")
    print("  - Build custom search interfaces")
    print("  - Create recommendation systems")
    print("  - Analyze your text data")
    print("  - Explore concept relationships")
    
    # Offer interactive mode
    try:
        response = input("\n[INFO] Start interactive search? (y/n) [default: n]: ").strip().lower()
        if response == 'y':
            interactive_search_mode(vector_store, sample_tokens, batch_files, batch_size)
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Goodbye!")


def interactive_search_mode(vector_store, sample_tokens, batch_files, batch_size):
    """Interactive search mode for exploring the vector store."""
    print("\n" + "=" * 80)
    print("INTERACTIVE SEARCH MODE")
    print("=" * 80)
    print("\nCommands:")
    print("  search <token>      - Search for similar tokens")
    print("  compare <t1> <t2>   - Compare two tokens")
    print("  related <t1> [t2]   - Find concepts related to token(s) (1 or more)")
    print("  cluster <token>     - Find concept cluster")
    print("  explore <token>     - Explore concept relationships")
    print("  help                - Show this help")
    print("  quit/exit           - Exit interactive mode")
    print("\n" + "-" * 80)
    
    while True:
        try:
            cmd = input("\n[INFO] > ").strip().split()
            if not cmd:
                continue
            
            command = cmd[0].lower()
            
            if command in ['quit', 'exit', 'q']:
                print("👋 Exiting interactive mode...")
                break
            
            elif command == 'help':
                print("\nCommands:")
                print("  search <token>      - Search for similar tokens")
                print("  compare <t1> <t2>   - Compare two tokens")
                print("  related <t1> [t2]   - Find concepts related to token(s) (1 or more)")
                print("  cluster <token>     - Find concept cluster")
                print("  explore <token>     - Explore concept relationships")
                print("  quit/exit           - Exit")
            
            elif command == 'search' and len(cmd) > 1:
                token = cmd[1]
                semantic_search(vector_store, token, sample_tokens, batch_files, batch_size,
                               top_k=15, min_similarity=0.5)
            
            elif command == 'compare' and len(cmd) > 2:
                compare_tokens(vector_store, cmd[1], cmd[2], sample_tokens, batch_files, batch_size)
            
            elif command == 'related' and len(cmd) > 1:
                tokens = cmd[1:]
                find_related_concepts(vector_store, tokens, sample_tokens, batch_files, batch_size,
                                     top_k=15, min_similarity=0.4)
            
            elif command == 'cluster' and len(cmd) > 1:
                find_concept_cluster(vector_store, cmd[1], sample_tokens, batch_files, batch_size,
                                    cluster_size=10, min_similarity=0.6)
            
            elif command == 'explore' and len(cmd) > 1:
                explore_concept(vector_store, cmd[1], sample_tokens, batch_files, batch_size,
                               depth=2, min_similarity=0.4, verbose=True)
            
            else:
                print("[ERROR] Invalid command. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n👋 Exiting interactive mode...")
            break
        except Exception as e:
            print(f"[ERROR] Error: {e}")


if __name__ == "__main__":
    main()
