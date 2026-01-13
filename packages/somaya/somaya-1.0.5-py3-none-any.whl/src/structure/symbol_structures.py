"""
SOMA Symbol Structures - Core Foundation
==========================================

Defines the basic building blocks for ALL of SOMA:
- Symbols and their classes (A-Z, 0-9, math symbols, special chars)
- Symbol structures (constraints, not meanings)
- Combination rules

This is the foundation layer: symbols → patterns → meaning

Remember: Structure enables meaning, doesn't define it!
"""

from typing import Dict, List, Set, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class SymbolClass:
    """
    Symbol classification system for soma.
    
    All symbols are classified into these categories.
    This is syntax, not semantics!
    """
    
    # Basic symbol classes
    LETTER_UPPER = "LETTER_UPPER"
    LETTER_LOWER = "LETTER_LOWER"
    DIGIT = "DIGIT"
    MATH_SYMBOL = "MATH_SYMBOL"
    SPECIAL = "SPECIAL"
    PUNCTUATION = "PUNCTUATION"
    WHITESPACE = "WHITESPACE"
    UNKNOWN = "UNKNOWN"
    
    # Extended classes (for multilingual support)
    CJK = "CJK"  # Chinese, Japanese, Korean
    ARABIC = "ARABIC"
    CYRILLIC = "CYRILLIC"
    HEBREW = "HEBREW"
    THAI = "THAI"
    DEVANAGARI = "DEVANAGARI"


class SymbolStructure:
    """
    Represents a single symbol and its structural properties.
    
    What we know:
    - Class (LETTER, DIGIT, etc.)
    - What it can combine with (learned from usage)
    - Frequency patterns
    
    What we DON'T know:
    - Meaning (comes from usage/context)
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
        
        # Combination rules (learned from usage)
        self.can_combine_with: Set[str] = set()
        self.combination_frequency: Dict[str, int] = {}
        
        # Usage statistics
        self.frequency = 0
        self.contexts: Set[str] = set()
    
    def add_combination(self, other_symbol: str):
        """Record that this symbol can combine with another."""
        self.can_combine_with.add(other_symbol)
        self.combination_frequency[other_symbol] = self.combination_frequency.get(other_symbol, 0) + 1
    
    def can_combine(self, other_symbol: str) -> bool:
        """Check if this can combine with another symbol."""
        return other_symbol in self.can_combine_with
    
    def get_combination_strength(self, other_symbol: str) -> float:
        """
        Get how strongly this symbol combines with another.
        
        Returns:
            Strength score (0.0 to 1.0) based on frequency
        """
        if other_symbol not in self.combination_frequency:
            return 0.0
        
        freq = self.combination_frequency[other_symbol]
        max_freq = max(self.combination_frequency.values()) if self.combination_frequency else 1
        return min(1.0, freq / max_freq)
    
    def __repr__(self) -> str:
        return f"SymbolStructure('{self.symbol}', class={self.symbol_class}, freq={self.frequency})"


class SymbolRegistry:
    """
    Global registry of all symbols and their structures.
    
    This is the foundation of SOMA's structure system.
    All symbols (A-Z, 0-9, math symbols, special chars) are registered here.
    """
    
    def __init__(self):
        """Create and initialize symbol registry."""
        self.symbols: Dict[str, SymbolStructure] = {}
        self._initialize_all_symbols()
    
    def _initialize_all_symbols(self):
        """Initialize all symbol sets (your idea!)."""
        # Letters (upper) - 26
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.register(char, SymbolClass.LETTER_UPPER)
        
        # Letters (lower) - 26
        for char in "abcdefghijklmnopqrstuvwxyz":
            self.register(char, SymbolClass.LETTER_LOWER)
        
        # Digits - 0-9
        for char in "0123456789":
            self.register(char, SymbolClass.DIGIT)
        
        # Math symbols (~500 possible)
        math_chars = "+-*/=<>≤≥≠≈±×÷∑∏∫√∞∂∇∆∈∉⊂⊃∪∩∧∨¬→←↑↓↔⇒⇐⇔∀∃∄∅"
        math_chars += "αβγδεζηθικλμνξοπρστυφχψω"  # Greek letters (often used in math)
        math_chars += "ℕℤℚℝℂ"  # Number sets
        for char in math_chars:
            self.register(char, SymbolClass.MATH_SYMBOL)
        
        # Punctuation
        punct_chars = ".,;:!?'\"()[]{}"
        for char in punct_chars:
            self.register(char, SymbolClass.PUNCTUATION)
        
        # Special characters (~200 possible)
        special_chars = "@#$%^&*_|\\~`"
        special_chars += "©®™€£¥§¶†‡•…"  # Extended special chars
        for char in special_chars:
            self.register(char, SymbolClass.SPECIAL)
        
        # Whitespace
        self.register(" ", SymbolClass.WHITESPACE)
        self.register("\t", SymbolClass.WHITESPACE)
        self.register("\n", SymbolClass.WHITESPACE)
        self.register("\r", SymbolClass.WHITESPACE)
    
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
        """Get structure for a symbol."""
        return self.symbols.get(symbol)
    
    def get_class(self, symbol: str) -> str:
        """Get the class of a symbol."""
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
        """Get all symbols of a specific class."""
        return [
            symbol for symbol, structure in self.symbols.items()
            if structure.symbol_class == symbol_class
        ]
    
    def learn_combination(self, symbol1: str, symbol2: str):
        """
        Learn that two symbols can combine (from usage).
        
        This is how patterns emerge!
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
        """
        # Auto-register if not known
        if not self.has_symbol(symbol1):
            cls1 = self._detect_class(symbol1)
            self.register(symbol1, cls1)
        
        if not self.has_symbol(symbol2):
            cls2 = self._detect_class(symbol2)
            self.register(symbol2, cls2)
        
        struct1 = self.get(symbol1)
        struct2 = self.get(symbol2)
        
        if struct1 and struct2:
            struct1.add_combination(symbol2)
            struct2.add_combination(symbol1)
    
    def _detect_class(self, symbol: str) -> str:
        """Auto-detect symbol class if not registered."""
        if len(symbol) != 1:
            return SymbolClass.UNKNOWN
        
        char = symbol
        code = ord(char)
        
        if 65 <= code <= 90:
            return SymbolClass.LETTER_UPPER
        elif 97 <= code <= 122:
            return SymbolClass.LETTER_LOWER
        elif 48 <= code <= 57:
            return SymbolClass.DIGIT
        elif char in " \t\n\r":
            return SymbolClass.WHITESPACE
        elif char in ".,;:!?'\"()[]{}":
            return SymbolClass.PUNCTUATION
        else:
            return SymbolClass.UNKNOWN
    
    def can_combine(self, symbol1: str, symbol2: str) -> bool:
        """Check if two symbols can combine."""
        struct1 = self.get(symbol1)
        if struct1:
            return struct1.can_combine(symbol2)
        return False
    
    def get_statistics(self) -> Dict:
        """Get statistics about registered symbols."""
        return {
            "total_symbols": len(self.symbols),
            "by_class": {
                cls: len(self.get_symbols_by_class(cls))
                for cls in [
                    SymbolClass.LETTER_UPPER,
                    SymbolClass.LETTER_LOWER,
                    SymbolClass.DIGIT,
                    SymbolClass.MATH_SYMBOL,
                    SymbolClass.SPECIAL,
                    SymbolClass.PUNCTUATION
                ]
            }
        }


# Global registry (singleton)
_registry: Optional[SymbolRegistry] = None


def get_registry() -> SymbolRegistry:
    """Get the global symbol registry."""
    global _registry
    if _registry is None:
        _registry = SymbolRegistry()
    return _registry


# Helper functions for SOMA integration
def classify_symbol(symbol: str) -> str:
    """Classify a symbol into its class."""
    return get_registry().get_class(symbol)


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
