"""
Example: Using SOMA Embeddings for Inference

This example demonstrates:
1. Generating embeddings from soma tokens
2. Storing embeddings in vector database
3. Performing similarity search
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.core_tokenizer import TextTokenizer
from src.embeddings import (
    SOMAEmbeddingGenerator,
    ChromaVectorStore,
    SOMAInferencePipeline
)
import numpy as np


def example_1_basic_embedding():
    """Example 1: Basic embedding generation"""
    print("\n" + "="*60)
    print("Example 1: Basic Embedding Generation")
    print("="*60)
    
    # Initialize tokenizer
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    
    # Initialize embedding generator
    embedding_gen = SOMAEmbeddingGenerator(
        strategy="feature_based",
        embedding_dim=768
    )
    
    # Tokenize text
    text = "Hello world, this is SOMA!"
    print(f"\nInput text: {text}")
    
    streams = tokenizer.build(text)
    
    # Generate embeddings for tokens
    print("\nGenerating embeddings...")
    for stream_name, token_stream in streams.items():
        print(f"\nStream: {stream_name} ({len(token_stream.tokens)} tokens)")
        for i, token in enumerate(token_stream.tokens[:5]):  # Show first 5
            embedding = embedding_gen.generate(token)
            print(f"  Token {i+1}: '{token.text}'")
            print(f"    Embedding shape: {embedding.shape}")
            print(f"    Embedding norm: {np.linalg.norm(embedding):.4f}")
            print(f"    UID: {token.uid}")
            print(f"    Frontend: {token.frontend}")


def example_2_vector_store():
    """Example 2: Vector database storage and search"""
    print("\n" + "="*60)
    print("Example 2: Vector Database Storage and Search")
    print("="*60)
    
    # Initialize components
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    embedding_gen = SOMAEmbeddingGenerator(
        strategy="feature_based",
        embedding_dim=768
    )
    
    # Initialize vector store (using ChromaDB)
    try:
        vector_store = ChromaVectorStore(
            collection_name="SOMA_example",
            persist_directory="./vector_db_example"
        )
    except ImportError:
        print("\n[WARNING]  ChromaDB not available. Install with: pip install chromadb")
        print("Skipping vector store example...")
        return
    
    # Process multiple documents
    documents = [
        "Machine learning is fascinating",
        "Natural language processing enables AI",
        "SOMA provides perfect tokenization",
        "Embeddings enable semantic search",
        "Vector databases store high-dimensional data"
    ]
    
    print("\nProcessing documents...")
    for i, doc in enumerate(documents):
        print(f"  {i+1}. {doc}")
        streams = tokenizer.build(doc)
        
        # Collect all tokens
        all_tokens = []
        for stream_name, token_stream in streams.items():
            all_tokens.extend(token_stream.tokens)
        
        # Generate embeddings
        embeddings = embedding_gen.generate_batch(all_tokens)
        
        # Store in vector database
        vector_store.add_tokens(all_tokens, embeddings)
    
    print(f"\n[OK] Stored {len(documents)} documents in vector database")
    
    # Search for similar content
    query = "artificial intelligence"
    print(f"\nSearching for: '{query}'")
    
    # Generate query embedding
    query_streams = tokenizer.build(query)
    query_tokens = []
    for stream_name, token_stream in query_streams.items():
        query_tokens.extend(token_stream.tokens)
    
    if query_tokens:
        query_embeddings = embedding_gen.generate_batch(query_tokens)
        query_embedding = np.mean(query_embeddings, axis=0)
        
        # Search
        results = vector_store.search(query_embedding, top_k=5)
        
        print(f"\nTop {len(results)} results:")
        for i, result in enumerate(results):
            print(f"  {i+1}. '{result['text']}'")
            if 'distance' in result and result['distance'] is not None:
                print(f"     Similarity: {result['distance']:.4f}")


def example_3_inference_pipeline():
    """Example 3: Complete inference pipeline"""
    print("\n" + "="*60)
    print("Example 3: Complete Inference Pipeline")
    print("="*60)
    
    # Initialize pipeline
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    embedding_gen = SOMAEmbeddingGenerator(
        strategy="feature_based",
        embedding_dim=768
    )
    
    try:
        vector_store = ChromaVectorStore(
            collection_name="SOMA_pipeline",
            persist_directory="./vector_db_pipeline"
        )
    except ImportError:
        print("\n[WARNING]  ChromaDB not available. Install with: pip install chromadb")
        print("Skipping pipeline example...")
        return
    
    pipeline = SOMAInferencePipeline(
        embedding_generator=embedding_gen,
        vector_store=vector_store,
        tokenizer=tokenizer
    )
    
    # Process documents
    documents = [
        "Python is a programming language",
        "Machine learning uses algorithms",
        "SOMA tokenizes text perfectly",
        "Embeddings represent meaning",
        "Vector search finds similar content"
    ]
    
    print("\nProcessing documents through pipeline...")
    for doc in documents:
        result = pipeline.process_text(doc, store=True)
        print(f"  Processed: '{doc}'")
        print(f"    Tokens: {result['num_tokens']}")
        print(f"    Embedding shape: {result['embeddings'].shape}")
    
    # Similarity search
    print("\n" + "-"*60)
    print("Similarity Search Examples:")
    print("-"*60)
    
    queries = [
        "programming",
        "algorithms and data",
        "text processing"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = pipeline.similarity_search(query, top_k=3)
        
        for i, result in enumerate(results):
            print(f"  {i+1}. '{result.get('text', 'N/A')}'")
            if 'distance' in result:
                print(f"     Distance: {result['distance']:.4f}")


def example_4_document_embeddings():
    """Example 4: Document-level embeddings"""
    print("\n" + "="*60)
    print("Example 4: Document-Level Embeddings")
    print("="*60)
    
    # Initialize pipeline
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    embedding_gen = SOMAEmbeddingGenerator(
        strategy="feature_based",
        embedding_dim=768
    )
    
    pipeline = SOMAInferencePipeline(
        embedding_generator=embedding_gen,
        vector_store=None,  # Not needed for this example
        tokenizer=tokenizer
    )
    
    documents = [
        "Machine learning is a subset of artificial intelligence",
        "Natural language processing helps computers understand text",
        "Deep learning uses neural networks with multiple layers"
    ]
    
    print("\nGenerating document embeddings...")
    doc_embeddings = []
    for doc in documents:
        doc_emb = pipeline.get_document_embedding(doc, method="mean")
        doc_embeddings.append(doc_emb)
        print(f"  '{doc[:50]}...'")
        print(f"    Embedding shape: {doc_emb.shape}")
        print(f"    Embedding norm: {np.linalg.norm(doc_emb):.4f}")
    
    # Compute similarities between documents
    print("\nDocument Similarities:")
    doc_embeddings = np.array(doc_embeddings)
    for i in range(len(documents)):
        for j in range(i+1, len(documents)):
            similarity = np.dot(doc_embeddings[i], doc_embeddings[j])
            print(f"  Doc {i+1} ↔ Doc {j+1}: {similarity:.4f}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SOMA Embedding Examples")
    print("="*60)
    
    # Run examples
    try:
        example_1_basic_embedding()
        example_2_vector_store()
        example_3_inference_pipeline()
        example_4_document_embeddings()
        
        print("\n" + "="*60)
        print("[OK] All examples completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
