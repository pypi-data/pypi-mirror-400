"""
SOMA Core Beginner Tokenizer
=========================

Simple tokenizer that splits text into words.
Think of it like cutting a sentence into individual words.

Example:
    text = "cats chase mice"
    tokens = tokenize(text)
    # Result: ["cats", "chase", "mice"]
"""


def tokenize(text: str) -> list:
    """
    Split text into tokens (words).
    
    What it does:
    - Takes a sentence like "cats chase mice"
    - Returns a list of words: ["cats", "chase", "mice"]
    
    Args:
        text: The text to split (e.g., "cats chase mice")
    
    Returns:
        List of words (tokens)
    
    Example:
        >>> tokenize("cats chase mice")
        ['cats', 'chase', 'mice']
    """
    # Simple: split by spaces and remove empty strings
    tokens = text.lower().split()
    return [token.strip() for token in tokens if token.strip()]


def tokenize_list(texts: list) -> list:
    """
    Tokenize multiple texts.
    
    Args:
        texts: List of text strings
    
    Returns:
        List of tokenized texts (each is a list of words)
    
    Example:
        >>> tokenize_list(["cats chase mice", "dogs chase balls"])
        [['cats', 'chase', 'mice'], ['dogs', 'chase', 'balls']]
    """
    return [tokenize(text) for text in texts]


# Test it works
if __name__ == "__main__":
    # Simple test
    test_text = "cats chase mice"
    result = tokenize(test_text)
    print(f"Text: '{test_text}'")
    print(f"Tokens: {result}")
    print("✅ Tokenizer works!")
