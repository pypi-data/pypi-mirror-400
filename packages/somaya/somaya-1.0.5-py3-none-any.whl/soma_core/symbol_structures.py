"""
SOMA Core Symbol Structures
========================

Defines the basic building blocks: symbols and their classes.

Remember: These are CONSTRAINTS, not meanings!
- A is a LETTER_UPPER (that's all we know)
- We don't say "A means animal" - that comes later from usage
"""

from typing import Dict, List, Set, Optional


class SymbolClass:
    """
    A class of symbols (like LETTER, DIGIT, etc.).
    
    This is just classification - NO meaning attached!
    """
    
    # Symbol classes (constraints only, no meaning)
    LETTER_UPPER = "LETTER_UPPER"
    LETTER_LOWER = "LETTER_LOWER"
    DIGIT = "DIGIT"
    MATH_SYMBOL = "MATH_SYMBOL"
    SPECIAL = "SPECIAL"
    PUNCTUATION = "PUNCTUATION"
    WHITESPACE = "WHITESPACE"
    UNKNOWN = "UNKNOWN"


class SymbolStructure:
    """
    Represents a single symbol and its structure.
    
    What we know:
    - What class it belongs to (LETTER, DIGIT, etc.)
    - What it can combine with (constraints)
    - Its visual/structural properties
    
    What we DON'T know:
    - What it "means" (that comes from usage)
    """
    
    def __init__(self, symbol: str, symbol_class: str):
        """
        Create a symbol structure.
        
        Args:
            symbol: The actual symbol (e.g., 'A', '0', '+')
            symbol_class: Its class (LETTER_UPPER, DIGIT, etc.)
        """
        self.symbol = symbol
        self.symbol_class = symbol_class
        
        # What can this combine with? (learned from usage)
        self.can_combine_with: Set[str] = set()
        
        # Frequency (how often we see it)
        self.frequency = 0
    
    def add_combination(self, other_symbol: str):
        """Record that this symbol can combine with another."""
        self.can_combine_with.add(other_symbol)
    
    def can_combine(self, other_symbol: str) -> bool:
        """Check if this can combine with another symbol."""
        return other_symbol in self.can_combine_with
    
    def __repr__(self) -> str:
        return f"SymbolStructure('{self.symbol}', class={self.symbol_class})"


class SymbolRegistry:
    """
    Registry of all symbols and their structures.
    
    This is the foundation: all symbols we know about.
    """
    
    def __init__(self):
        """Create an empty symbol registry."""
        self.symbols: Dict[str, SymbolStructure] = {}
        self._initialize_basic_symbols()
    
    def _initialize_basic_symbols(self):
        """Initialize basic symbol sets."""
        # Letters (upper)
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.register(char, SymbolClass.LETTER_UPPER)
        
        # Letters (lower)
        for char in "abcdefghijklmnopqrstuvwxyz":
            self.register(char, SymbolClass.LETTER_LOWER)
        
        # Digits
        for char in "0123456789":
            self.register(char, SymbolClass.DIGIT)
        
        # Math symbols
        math_chars = "+-*/=<>≤≥≠≈±×÷∑∏∫√∞"
        for char in math_chars:
            self.register(char, SymbolClass.MATH_SYMBOL)
        
        # Punctuation
        punct_chars = ".,;:!?'\"()[]{}"
        for char in punct_chars:
            self.register(char, SymbolClass.PUNCTUATION)
        
        # Special characters
        special_chars = "@#$%^&*_|\\~`"
        for char in special_chars:
            self.register(char, SymbolClass.SPECIAL)
        
        # Whitespace
        self.register(" ", SymbolClass.WHITESPACE)
        self.register("\t", SymbolClass.WHITESPACE)
        self.register("\n", SymbolClass.WHITESPACE)
    
    def register(self, symbol: str, symbol_class: str):
        """
        Register a symbol with its class.
        
        Args:
            symbol: The symbol to register
            symbol_class: Its class (LETTER_UPPER, DIGIT, etc.)
        """
        if symbol not in self.symbols:
            self.symbols[symbol] = SymbolStructure(symbol, symbol_class)
        self.symbols[symbol].frequency += 1
    
    def get(self, symbol: str) -> Optional[SymbolStructure]:
        """
        Get structure for a symbol.
        
        Args:
            symbol: Symbol to look up
        
        Returns:
            SymbolStructure or None if not found
        """
        return self.symbols.get(symbol)
    
    def get_class(self, symbol: str) -> str:
        """
        Get the class of a symbol.
        
        Args:
            symbol: Symbol to check
        
        Returns:
            Symbol class (LETTER_UPPER, DIGIT, etc.) or UNKNOWN
        """
        structure = self.get(symbol)
        if structure:
            return structure.symbol_class
        return SymbolClass.UNKNOWN
    
    def has_symbol(self, symbol: str) -> bool:
        """Check if we know about this symbol."""
        return symbol in self.symbols
    
    def get_all_symbols(self) -> List[str]:
        """Get all registered symbols."""
        return list(self.symbols.keys())
    
    def get_symbols_by_class(self, symbol_class: str) -> List[str]:
        """
        Get all symbols of a specific class.
        
        Args:
            symbol_class: Class to filter by
        
        Returns:
            List of symbols in that class
        """
        return [
            symbol for symbol, structure in self.symbols.items()
            if structure.symbol_class == symbol_class
        ]
    
    def learn_combination(self, symbol1: str, symbol2: str):
        """
        Learn that two symbols can combine.
        
        This is how we learn patterns from usage!
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
        """
        struct1 = self.get(symbol1)
        struct2 = self.get(symbol2)
        
        if struct1 and struct2:
            struct1.add_combination(symbol2)
            struct2.add_combination(symbol1)
    
    def can_combine(self, symbol1: str, symbol2: str) -> bool:
        """
        Check if two symbols can combine (based on learned patterns).
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
        
        Returns:
            True if they can combine
        """
        struct1 = self.get(symbol1)
        if struct1:
            return struct1.can_combine(symbol2)
        return False


# Global registry (singleton pattern)
_registry: Optional[SymbolRegistry] = None


def get_registry() -> SymbolRegistry:
    """Get the global symbol registry."""
    global _registry
    if _registry is None:
        _registry = SymbolRegistry()
    return _registry


# Helper functions
def classify_symbol(symbol: str) -> str:
    """
    Classify a symbol into its class.
    
    Args:
        symbol: Symbol to classify
    
    Returns:
        Symbol class
    
    Example:
        >>> classify_symbol('A')
        'LETTER_UPPER'
        >>> classify_symbol('0')
        'DIGIT'
    """
    registry = get_registry()
    return registry.get_class(symbol)


def is_letter(symbol: str) -> bool:
    """Check if symbol is a letter (upper or lower)."""
    cls = classify_symbol(symbol)
    return cls in [SymbolClass.LETTER_UPPER, SymbolClass.LETTER_LOWER]


def is_digit(symbol: str) -> bool:
    """Check if symbol is a digit."""
    return classify_symbol(symbol) == SymbolClass.DIGIT


def is_math_symbol(symbol: str) -> bool:
    """Check if symbol is a math symbol."""
    return classify_symbol(symbol) == SymbolClass.MATH_SYMBOL


# Test it works
if __name__ == "__main__":
    print("Testing Symbol Structures...")
    print("=" * 50)
    
    registry = get_registry()
    
    # Test classification
    print("\n1. Symbol Classification:")
    test_symbols = ['A', 'a', '0', '+', '.', ' ']
    for sym in test_symbols:
        cls = registry.get_class(sym)
        print(f"   '{sym}' → {cls}")
    
    # Test getting symbols by class
    print("\n2. Symbols by Class:")
    letters = registry.get_symbols_by_class(SymbolClass.LETTER_UPPER)
    print(f"   Uppercase letters: {len(letters)} (first 5: {letters[:5]})")
    
    digits = registry.get_symbols_by_class(SymbolClass.DIGIT)
    print(f"   Digits: {digits}")
    
    # Test learning combinations
    print("\n3. Learning Combinations:")
    registry.learn_combination('c', 'a')
    registry.learn_combination('a', 't')
    print(f"   'c' can combine with: {registry.get('c').can_combine_with}")
    print(f"   'a' can combine with: {registry.get('a').can_combine_with}")
    
    print("\n✅ Symbol Structures work!")
