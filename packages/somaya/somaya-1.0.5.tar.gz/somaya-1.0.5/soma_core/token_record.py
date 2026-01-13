"""
SOMA Core Token Record
===================

Keeps track of all tokens (words) we've seen.
Like a dictionary that remembers every word.

Example:
    record = TokenRecord()
    record.add("cats")
    record.add("dogs")
    print(record.get_all())  # ["cats", "dogs"]
"""


class TokenRecord:
    """
    Records all tokens we've seen.
    
    Think of it like a notebook where you write down
    every new word you see, and count how many times you see it.
    """
    
    def __init__(self):
        """Create a new empty token record."""
        self.tokens = {}  # {word: count}
        self.token_list = []  # List of all unique tokens
    
    def add(self, token: str):
        """
        Add a token (word) to the record.
        
        If we've seen it before, just count it again.
        If it's new, add it to our list.
        
        Args:
            token: The word to add (e.g., "cats")
        
        Example:
            >>> record = TokenRecord()
            >>> record.add("cats")
            >>> record.add("cats")  # Count goes up
            >>> record.count("cats")
            2
        """
        token = token.lower().strip()
        if not token:
            return
        
        if token in self.tokens:
            self.tokens[token] += 1
        else:
            self.tokens[token] = 1
            self.token_list.append(token)
    
    def add_many(self, tokens: list):
        """
        Add multiple tokens at once.
        
        Args:
            tokens: List of words to add
        
        Example:
            >>> record = TokenRecord()
            >>> record.add_many(["cats", "chase", "mice"])
        """
        for token in tokens:
            self.add(token)
    
    def count(self, token: str) -> int:
        """
        How many times have we seen this token?
        
        Args:
            token: The word to check
        
        Returns:
            Number of times we've seen it (0 if never seen)
        
        Example:
            >>> record = TokenRecord()
            >>> record.add("cats")
            >>> record.add("cats")
            >>> record.count("cats")
            2
        """
        return self.tokens.get(token.lower(), 0)
    
    def get_all(self) -> list:
        """
        Get all unique tokens we've seen.
        
        Returns:
            List of all unique words
        
        Example:
            >>> record = TokenRecord()
            >>> record.add("cats")
            >>> record.add("dogs")
            >>> record.get_all()
            ['cats', 'dogs']
        """
        return self.token_list.copy()
    
    def size(self) -> int:
        """
        How many unique tokens do we have?
        
        Returns:
            Number of unique words
        
        Example:
            >>> record = TokenRecord()
            >>> record.add("cats")
            >>> record.add("dogs")
            >>> record.size()
            2
        """
        return len(self.token_list)
    
    def get_vocab(self) -> dict:
        """
        Get the full vocabulary (all tokens with counts).
        
        Returns:
            Dictionary: {word: count}
        
        Example:
            >>> record = TokenRecord()
            >>> record.add("cats")
            >>> record.add("cats")
            >>> record.get_vocab()
            {'cats': 2}
        """
        return self.tokens.copy()


# Test it works
if __name__ == "__main__":
    record = TokenRecord()
    record.add("cats")
    record.add("dogs")
    record.add("cats")  # Count should be 2
    
    print(f"All tokens: {record.get_all()}")
    print(f"Count of 'cats': {record.count('cats')}")
    print(f"Total unique tokens: {record.size()}")
    print("✅ TokenRecord works!")
