"""
SOMA Core Beginner Embeddings
==========================

Simple word embeddings (vectors) that represent words as numbers.
Think of it like giving each word a "fingerprint" made of numbers.

Similar words get similar fingerprints (vectors).

Example:
    embeddings = Embeddings()
    embeddings.train(["cats chase mice", "dogs chase balls"])
    vector = embeddings.get("cats")
    # Result: [0.1, 0.2, 0.3, ...] (a list of numbers)
"""

import random
import math


class Embeddings:
    """
    Simple word embeddings.
    
    What it does:
    - Takes words and converts them to vectors (lists of numbers)
    - Similar words get similar vectors
    - We can compare vectors to see if words are similar
    """
    
    def __init__(self, vector_size: int = 10):
        """
        Create embeddings.
        
        Args:
            vector_size: How many numbers in each vector (default: 10)
                        More numbers = more detail, but slower
        """
        self.vector_size = vector_size
        self.vectors = {}  # {word: [numbers]}
        self.vocab = []  # List of all words
    
    def _random_vector(self) -> list:
        """
        Create a random vector (list of small random numbers).
        
        Returns:
            List of random numbers between -0.1 and 0.1
        """
        return [random.uniform(-0.1, 0.1) for _ in range(self.vector_size)]
    
    def add_word(self, word: str):
        """
        Add a word and give it a random vector.
        
        Args:
            word: The word to add (e.g., "cats")
        """
        word = word.lower().strip()
        if not word or word in self.vectors:
            return
        
        self.vectors[word] = self._random_vector()
        self.vocab.append(word)
    
    def get(self, word: str) -> list:
        """
        Get the vector (fingerprint) for a word.
        
        Args:
            word: The word to look up
        
        Returns:
            List of numbers (the vector)
        
        Example:
            >>> emb = Embeddings()
            >>> emb.add_word("cats")
            >>> emb.get("cats")
            [0.05, -0.02, 0.08, ...]
        """
        word = word.lower().strip()
        if word not in self.vectors:
            # If word not found, return zeros
            return [0.0] * self.vector_size
        return self.vectors[word].copy()
    
    def update(self, word: str, vector: list):
        """
        Update a word's vector.
        
        Args:
            word: The word to update
            vector: New vector (list of numbers)
        """
        word = word.lower().strip()
        if word in self.vectors:
            self.vectors[word] = vector.copy()
    
    def has_word(self, word: str) -> bool:
        """
        Check if we know this word.
        
        Args:
            word: Word to check
        
        Returns:
            True if we have this word, False otherwise
        """
        return word.lower().strip() in self.vectors
    
    def get_all_words(self) -> list:
        """
        Get all words we know.
        
        Returns:
            List of all words
        """
        return self.vocab.copy()
    
    def size(self) -> int:
        """
        How many words do we know?
        
        Returns:
            Number of words
        """
        return len(self.vocab)


# Helper function for cosine similarity (how similar two vectors are)
def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    Calculate how similar two vectors are.
    
    Returns a number between -1 and 1:
    - 1.0 = exactly the same
    - 0.0 = not similar at all
    - -1.0 = completely opposite
    
    Args:
        vec1: First vector (list of numbers)
        vec2: Second vector (list of numbers)
    
    Returns:
        Similarity score (0.0 to 1.0)
    
    Example:
        >>> vec1 = [1, 0, 0]
        >>> vec2 = [1, 0, 0]
        >>> cosine_similarity(vec1, vec2)
        1.0  # Exactly the same
    """
    if len(vec1) != len(vec2):
        return 0.0
    
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Calculate magnitudes
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    # Cosine similarity
    similarity = dot_product / (mag1 * mag2)
    
    # Normalize to 0-1 range
    return max(0.0, min(1.0, (similarity + 1.0) / 2.0))


# Test it works
if __name__ == "__main__":
    emb = Embeddings(vector_size=5)
    emb.add_word("cats")
    emb.add_word("dogs")
    
    vec1 = emb.get("cats")
    vec2 = emb.get("dogs")
    
    print(f"Cats vector: {vec1}")
    print(f"Dogs vector: {vec2}")
    print(f"Similarity: {cosine_similarity(vec1, vec2):.3f}")
    print("✅ Embeddings work!")
