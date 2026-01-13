"""
SOMA Core Train Embeddings
=======================

Train embeddings so similar words end up closer together.

How it works:
1. Start with random vectors for each word
2. Look at which words appear together in sentences
3. Move their vectors closer together
4. Repeat many times

Example:
    texts = ["cats chase mice", "dogs chase balls"]
    train_embeddings(texts)
    # Now "cats" and "dogs" are closer because they both appear with "chase"
"""

from tokenizer import tokenize_list
from token_record import TokenRecord
from embeddings import Embeddings, cosine_similarity
import random


def train_embeddings(texts: list, vector_size: int = 10, epochs: int = 10, learning_rate: float = 0.01):
    """
    Train embeddings from text.
    
    What it does:
    - Takes sentences like ["cats chase mice", "dogs chase balls"]
    - Learns that words appearing together should be similar
    - Updates vectors so similar words are closer
    
    Args:
        texts: List of text strings to train on
        vector_size: Size of each vector (default: 10)
        epochs: How many times to go through the data (default: 10)
        learning_rate: How fast to learn (default: 0.01)
    
    Returns:
        Trained Embeddings object
    
    Example:
        >>> texts = ["cats chase mice", "dogs chase balls", "cats like milk"]
        >>> emb = train_embeddings(texts, epochs=20)
        >>> # Now embeddings are trained!
    """
    # Step 1: Tokenize all texts
    print("Step 1: Tokenizing texts...")
    tokenized = tokenize_list(texts)
    
    # Step 2: Build vocabulary (all unique words)
    print("Step 2: Building vocabulary...")
    vocab = TokenRecord()
    for tokens in tokenized:
        vocab.add_many(tokens)
    
    print(f"Found {vocab.size()} unique words")
    
    # Step 3: Create embeddings for all words
    print("Step 3: Creating embeddings...")
    embeddings = Embeddings(vector_size=vector_size)
    for word in vocab.get_all():
        embeddings.add_word(word)
    
    print(f"Created embeddings for {embeddings.size()} words")
    
    # Step 4: Train (move similar words closer)
    print(f"Step 4: Training for {epochs} epochs...")
    
    for epoch in range(epochs):
        total_updates = 0
        
        # Go through each sentence
        for tokens in tokenized:
            if len(tokens) < 2:
                continue
            
            # For each word, look at nearby words
            for i, word in enumerate(tokens):
                if not embeddings.has_word(word):
                    continue
                
                # Get nearby words (context window)
                context_start = max(0, i - 1)
                context_end = min(len(tokens), i + 2)
                context_words = tokens[context_start:context_end]
                context_words = [w for w in context_words if w != word]
                
                if not context_words:
                    continue
                
                # Get current vector
                word_vec = embeddings.get(word)
                
                # Average of context word vectors
                context_vecs = [embeddings.get(cw) for cw in context_words]
                avg_context = [
                    sum(v[i] for v in context_vecs) / len(context_vecs)
                    for i in range(vector_size)
                ]
                
                # Move word vector closer to context
                new_vec = [
                    word_vec[i] + learning_rate * (avg_context[i] - word_vec[i])
                    for i in range(vector_size)
                ]
                
                # Normalize (keep vector length reasonable)
                mag = sum(x * x for x in new_vec) ** 0.5
                if mag > 0:
                    new_vec = [x / mag * 0.5 for x in new_vec]
                
                embeddings.update(word, new_vec)
                total_updates += 1
        
        if (epoch + 1) % max(1, epochs // 5) == 0:
            print(f"  Epoch {epoch + 1}/{epochs} complete ({total_updates} updates)")
    
    print("✅ Training complete!")
    return embeddings


# Test it works
if __name__ == "__main__":
    # Simple test
    texts = [
        "cats chase mice",
        "dogs chase balls",
        "cats like milk"
    ]
    
    print("Training embeddings...")
    print("=" * 50)
    embeddings = train_embeddings(texts, epochs=20)
    
    print("\nTesting similarity:")
    print("=" * 50)
    
    # Test similarity
    from similarity import similarity
    
    print(f"similarity('cats', 'dogs'): {similarity('cats', 'dogs', embeddings):.3f}")
    print(f"similarity('cats', 'milk'): {similarity('cats', 'milk', embeddings):.3f}")
    print(f"similarity('chase', 'balls'): {similarity('chase', 'balls', embeddings):.3f}")
    
    print("\n✅ Training works!")
