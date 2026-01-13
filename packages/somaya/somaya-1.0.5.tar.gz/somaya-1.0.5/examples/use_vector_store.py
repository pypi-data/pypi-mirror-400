"""
Vector Store Usage Examples
============================

This script demonstrates what you can do with your loaded vector store:
- Semantic similarity search
- Concept exploration
- Related term finding
- Clustering analysis
- Interactive queries
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


def load_vector_store(output_dir="workflow_output", max_batches=30):
    """Load the vector store from existing batches."""
    print("=" * 80)
    print("LOADING VECTOR STORE")
    print("=" * 80)
    
    # Load tokens
    tokens_file = os.path.join(output_dir, "tokens.pkl")
    if not os.path.exists(tokens_file):
        print(f"[ERROR] Tokens file not found: {tokens_file}")
        return None, None
    
    print(f"📂 Loading tokens from {tokens_file}...")
    with open(tokens_file, 'rb') as f:
        all_tokens = pickle.load(f)
    print(f"[OK] Loaded {len(all_tokens):,} tokens")
    
    # Load embedding batches
    metadata_file = os.path.join(output_dir, "embedding_batches_metadata.json")
    if not os.path.exists(metadata_file):
        print(f"[ERROR] Metadata file not found: {metadata_file}")
        return None, None
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    batch_files = metadata.get("batch_files", [])
    embedding_dim = metadata.get("embedding_dim", 768)
    batch_size = metadata.get("batch_size", 50000)
    
    # Limit batches
    batches_to_load = batch_files[:min(max_batches, len(batch_files))]
    print(f"📦 Loading {len(batches_to_load)} batches into vector store...")
    
    # Initialize vector store
    vector_store = FAISSVectorStore(embedding_dim=embedding_dim)
    
    # Initialize embedding generator to create query embeddings
    embedding_gen = SOMAEmbeddingGenerator(
        strategy="feature_based",
        embedding_dim=embedding_dim
    )
    
    # Load batches
    total_tokens_added = 0
    for batch_idx, batch_file in enumerate(batches_to_load):
        if not os.path.exists(batch_file):
            continue
        
        batch_embeddings = np.load(batch_file)
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + len(batch_embeddings), len(all_tokens))
        batch_tokens = all_tokens[batch_start:batch_end]
        
        # Add in chunks
        chunk_size = 10000
        for chunk_start in range(0, len(batch_tokens), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(batch_tokens))
            chunk_tokens = batch_tokens[chunk_start:chunk_end]
            chunk_embeddings = batch_embeddings[chunk_start:chunk_end]
            vector_store.add_tokens(chunk_tokens, chunk_embeddings)
        
        total_tokens_added += len(batch_tokens)
        print(f"  [OK] Loaded batch {batch_idx + 1}/{len(batches_to_load)} ({total_tokens_added:,} tokens)")
    
    print(f"[OK] Vector store ready with {total_tokens_added:,} tokens!")
    return vector_store, embedding_gen


def search_similar_tokens(vector_store, embedding_gen, query_text, top_k=10):
    """Search for similar tokens to a query text."""
    # Create a dummy token to generate embedding
    # We'll use the embedding generator's feature-based method
    print(f"\n[INFO] Searching for tokens similar to: '{query_text}'")
    
    # Generate embedding for query text
    # For simplicity, we'll find a token with this text and use its embedding
    # In practice, you'd generate embedding directly from text
    
    # For now, we'll search using tokens that contain the query text
    # This is a simplified approach - in production, you'd use a proper text encoder
    
    return None


def find_token_by_text(all_tokens, text):
    """Find a token by its text."""
    for token in all_tokens:
        if getattr(token, 'text', '') == text:
            return token
    return None


def search_examples(vector_store, all_tokens, embedding_gen, max_batches=30):
    """Run example searches."""
    print("\n" + "=" * 80)
    print("SEMANTIC SEARCH EXAMPLES")
    print("=" * 80)
    
    # Load a sample of tokens from the loaded batches
    batch_size = 50000
    max_tokens = max_batches * batch_size
    sample_tokens = all_tokens[:min(max_tokens, len(all_tokens))]
    
    # Example queries - find tokens and search for similar ones
    example_queries = [
        "Artificial",
        "intelligence",
        "machine",
        "learning",
        "data",
        "science",
        "algorithm",
        "neural",
        "network",
        "processing"
    ]
    
    results = {}
    
    for query_text in example_queries:
        # Find token with this text
        token = find_token_by_text(sample_tokens, query_text)
        if token is None:
            # Try case-insensitive
            for t in sample_tokens:
                if getattr(t, 'text', '').lower() == query_text.lower():
                    token = t
                    break
        
        if token:
            # Get its position in the vector store
            # We need to find the index of this token
            token_idx = sample_tokens.index(token)
            if token_idx < len(sample_tokens):
                # Get embedding from batch
                batch_idx = token_idx // batch_size
                batch_file = os.path.join("workflow_output", "embedding_batches", 
                                         f"emb_batch_{batch_idx:04d}.npy")
                if os.path.exists(batch_file):
                    batch_embeddings = np.load(batch_file)
                    local_idx = token_idx % batch_size
                    if local_idx < len(batch_embeddings):
                        query_embedding = batch_embeddings[local_idx]
                        
                        # Search
                        search_results = vector_store.search(query_embedding, top_k=top_k)
                        results[query_text] = search_results
                        
                        print(f"\n[INFO] Top {top_k} similar tokens to '{query_text}':")
                        for i, result in enumerate(search_results[:top_k], 1):
                            result_text = result.get('text', 'N/A')
                            distance = result.get('distance', 0.0)
                            print(f"  {i:2d}. {result_text:20s} (distance: {distance:.4f})")
    
    return results


def interactive_search(vector_store, all_tokens, embedding_gen, max_batches=30):
    """Interactive search interface."""
    print("\n" + "=" * 80)
    print("INTERACTIVE SEARCH")
    print("=" * 80)
    print("Enter a token to search for similar tokens (or 'quit' to exit)")
    
    batch_size = 50000
    max_tokens = max_batches * batch_size
    sample_tokens = all_tokens[:min(max_tokens, len(all_tokens))]
    
    while True:
        query = input("\n[INFO] Search for: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        # Find token
        token = find_token_by_text(sample_tokens, query)
        if token is None:
            # Try case-insensitive
            for t in sample_tokens:
                if getattr(t, 'text', '').lower() == query.lower():
                    token = t
                    break
        
        if not token:
            print(f"[ERROR] Token '{query}' not found in the loaded dataset")
            print("   Tip: Make sure the token exists in the first 30 batches")
            continue
        
        # Get embedding
        token_idx = sample_tokens.index(token)
        batch_idx = token_idx // batch_size
        batch_file = os.path.join("workflow_output", "embedding_batches", 
                                 f"emb_batch_{batch_idx:04d}.npy")
        
        if not os.path.exists(batch_file):
            print(f"[ERROR] Batch file not found for token")
            continue
        
        batch_embeddings = np.load(batch_file)
        local_idx = token_idx % batch_size
        
        if local_idx >= len(batch_embeddings):
            print(f"[ERROR] Token index out of range")
            continue
        
        query_embedding = batch_embeddings[local_idx]
        
        # Search
        try:
            top_k = int(input("   How many results? [default: 10]: ").strip() or "10")
        except ValueError:
            top_k = 10
        
        results = vector_store.search(query_embedding, top_k=top_k)
        
        print(f"\n[INFO] Top {len(results)} similar tokens to '{query}':")
        for i, result in enumerate(results, 1):
            result_text = result.get('text', 'N/A')
            distance = result.get('distance', 0.0)
            metadata = result.get('metadata', {})
            print(f"  {i:2d}. {result_text:30s} (distance: {distance:.4f})")
            if metadata.get('stream'):
                print(f"      Stream: {metadata['stream']}, UID: {metadata.get('uid', 'N/A')}")


def analyze_clusters(vector_store, all_tokens, max_batches=30, sample_size=1000):
    """Analyze token clusters (simplified)."""
    print("\n" + "=" * 80)
    print("CLUSTER ANALYSIS")
    print("=" * 80)
    print("Finding groups of similar tokens...")
    
    batch_size = 50000
    max_tokens = max_batches * batch_size
    sample_tokens = all_tokens[:min(max_tokens, len(all_tokens))]
    
    # Sample tokens for analysis
    import random
    sample_indices = random.sample(range(len(sample_tokens)), 
                                  min(sample_size, len(sample_tokens)))
    sample = [sample_tokens[i] for i in sample_indices]
    
    print(f"Analyzing {len(sample)} sample tokens...")
    
    # For each token, find its neighbors
    clusters = {}
    processed = set()
    
    for token in sample[:100]:  # Limit to first 100 for speed
        token_text = getattr(token, 'text', '')
        if token_text in processed:
            continue
        
        # Get embedding and find neighbors
        token_idx = sample_tokens.index(token)
        batch_idx = token_idx // batch_size
        batch_file = os.path.join("workflow_output", "embedding_batches", 
                                 f"emb_batch_{batch_idx:04d}.npy")
        
        if os.path.exists(batch_file):
            batch_embeddings = np.load(batch_file)
            local_idx = token_idx % batch_size
            if local_idx < len(batch_embeddings):
                query_embedding = batch_embeddings[local_idx]
                neighbors = vector_store.search(query_embedding, top_k=5)
                
                if neighbors:
                    cluster = [r.get('text', '') for r in neighbors]
                    clusters[token_text] = cluster
                    processed.update(cluster)
    
    print(f"\n[INFO] Found {len(clusters)} clusters:")
    for i, (center, members) in enumerate(list(clusters.items())[:10], 1):
        print(f"\n  Cluster {i}: '{center}'")
        print(f"    Members: {', '.join(members[:5])}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Use the vector store for semantic search")
    parser.add_argument("--output-dir", default="workflow_output", 
                       help="Output directory with embeddings")
    parser.add_argument("--max-batches", type=int, default=30,
                       help="Maximum batches to load (default: 30)")
    parser.add_argument("--mode", choices=["examples", "interactive", "clusters", "all"],
                       default="all", help="Operation mode")
    
    args = parser.parse_args()
    
    # Load vector store
    vector_store, embedding_gen = load_vector_store(args.output_dir, args.max_batches)
    
    if vector_store is None:
        print("[ERROR] Failed to load vector store")
        return
    
    # Load tokens
    tokens_file = os.path.join(args.output_dir, "tokens.pkl")
    with open(tokens_file, 'rb') as f:
        all_tokens = pickle.load(f)
    
    # Run operations
    if args.mode in ["examples", "all"]:
        search_examples(vector_store, all_tokens, embedding_gen, args.max_batches)
    
    if args.mode in ["clusters", "all"]:
        analyze_clusters(vector_store, all_tokens, args.max_batches)
    
    if args.mode in ["interactive", "all"]:
        interactive_search(vector_store, all_tokens, embedding_gen, args.max_batches)


if __name__ == "__main__":
    main()
