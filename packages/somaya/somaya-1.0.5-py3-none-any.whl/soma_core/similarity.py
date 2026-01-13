"""
SOMA Core Similarity
=================

Measure how similar two words are.
Uses the embeddings (vectors) we trained.

Example:
    similarity("cats", "dogs")  # Returns a number between 0 and 1
    # 0.0 = not similar at all
    # 1.0 = very similar
"""

from embeddings import Embeddings, cosine_similarity


def similarity(word1: str, word2: str, embeddings: Embeddings = None) -> float:
    """
    Calculate how similar two words are.
    
    How it works:
    1. Get the vector (fingerprint) for each word
    2. Compare the vectors
    3. Return a number: 0.0 (not similar) to 1.0 (very similar)
    
    Args:
        word1: First word (e.g., "cats")
        word2: Second word (e.g., "dogs")
        embeddings: Trained embeddings (if None, returns 0.0)
    
    Returns:
        Similarity score between 0.0 and 1.0
    
    Example:
        >>> emb = train_embeddings(["cats chase mice", "dogs chase balls"])
        >>> similarity("cats", "dogs", emb)
        0.65  # They're somewhat similar (both animals)
        >>> similarity("cats", "milk", emb)
        0.45  # Less similar
    """
    if embeddings is None:
        return 0.0
    
    # Get vectors for both words
    vec1 = embeddings.get(word1)
    vec2 = embeddings.get(word2)
    
    # If either word not found, return 0
    if not embeddings.has_word(word1) or not embeddings.has_word(word2):
        return 0.0
    
    # Calculate similarity
    return cosine_similarity(vec1, vec2)


def find_similar_words(word: str, embeddings: Embeddings, top_k: int = 5) -> list:
    """
    Find words most similar to the given word.
    
    Args:
        word: Word to find similar words for
        embeddings: Trained embeddings
        top_k: How many similar words to return
    
    Returns:
        List of (word, similarity_score) tuples, sorted by similarity
    
    Example:
        >>> emb = train_embeddings(["cats chase mice", "dogs chase balls"])
        >>> find_similar_words("cats", emb)
        [('dogs', 0.65), ('mice', 0.55), ...]
    """
    if not embeddings.has_word(word):
        return []
    
    # Calculate similarity to all words
    similarities = []
    for other_word in embeddings.get_all_words():
        if other_word != word:
            sim = similarity(word, other_word, embeddings)
            similarities.append((other_word, sim))
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k
    return similarities[:top_k]


# Test it works
if __name__ == "__main__":
    # This will only work if embeddings are trained
    print("Similarity module loaded!")
    print("Use train_embeddings() first, then call similarity()")
    print("✅ Similarity module ready!")
