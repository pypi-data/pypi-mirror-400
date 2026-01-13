"""
SOMA Core Pattern Builder
======================

Builds patterns from symbol combinations.

This is where "c + a + t" becomes a pattern!
- We don't assign meaning ("cat" = animal)
- We just recognize: "this sequence appears often"
- Patterns emerge from usage, not hardcoding
"""

from typing import List, Dict, Tuple, Set
from collections import defaultdict
from symbol_structures import get_registry, SymbolRegistry


class Pattern:
    """
    A pattern (sequence of symbols that appears together).
    
    Example: "cat" is a pattern if "c", "a", "t" appear together often.
    
    Remember: Pattern ≠ Meaning
    - Pattern: "cat" appears frequently
    - Meaning: "cat" = animal (comes from usage/context)
    """
    
    def __init__(self, symbols: List[str], frequency: int = 1):
        """
        Create a pattern.
        
        Args:
            symbols: List of symbols in the pattern (e.g., ['c', 'a', 't'])
            frequency: How many times we've seen this pattern
        """
        self.symbols = symbols
        self.frequency = frequency
        self.sequence = ''.join(symbols)  # "cat"
    
    def length(self) -> int:
        """Get pattern length."""
        return len(self.symbols)
    
    def __repr__(self) -> str:
        return f"Pattern('{self.sequence}', freq={self.frequency})"
    
    def __eq__(self, other):
        """Two patterns are equal if they have the same symbols."""
        if isinstance(other, Pattern):
            return self.symbols == other.symbols
        return False
    
    def __hash__(self):
        """Hash based on symbol sequence."""
        return hash(tuple(self.symbols))


class PatternBuilder:
    """
    Builds patterns from text by observing symbol combinations.
    
    How it works:
    1. Look at sequences of symbols
    2. Count how often they appear
    3. Frequent sequences become patterns
    4. Patterns are candidates (not fixed meanings)
    """
    
    def __init__(self, registry: SymbolRegistry = None):
        """
        Create a pattern builder.
        
        Args:
            registry: Symbol registry (uses global if None)
        """
        self.registry = registry or get_registry()
        self.patterns: Dict[str, Pattern] = {}  # sequence -> Pattern
        self.ngram_counts: Dict[Tuple, int] = defaultdict(int)  # Track n-grams
    
    def learn_from_text(self, text: str, min_pattern_length: int = 2, max_pattern_length: int = 10):
        """
        Learn patterns from text.
        
        Args:
            text: Text to learn from
            min_pattern_length: Minimum pattern length (default: 2)
            max_pattern_length: Maximum pattern length (default: 10)
        
        Example:
            >>> builder = PatternBuilder()
            >>> builder.learn_from_text("cat cat dog")
            >>> # Now "cat" is a pattern (appears twice)
        """
        # Convert text to symbols
        symbols = list(text.lower())
        
        # Learn combinations
        for i in range(len(symbols) - 1):
            sym1 = symbols[i]
            sym2 = symbols[i + 1]
            
            # Register symbols if needed
            if not self.registry.has_symbol(sym1):
                cls = self.registry.get_class(sym1)
                if cls == "UNKNOWN":
                    self.registry.register(sym1, "UNKNOWN")
            
            if not self.registry.has_symbol(sym2):
                cls = self.registry.get_class(sym2)
                if cls == "UNKNOWN":
                    self.registry.register(sym2, "UNKNOWN")
            
            # Learn combination
            self.registry.learn_combination(sym1, sym2)
        
        # Extract patterns of different lengths
        for length in range(min_pattern_length, min(max_pattern_length + 1, len(symbols) + 1)):
            for i in range(len(symbols) - length + 1):
                pattern_symbols = symbols[i:i + length]
                pattern_seq = ''.join(pattern_symbols)
                
                # Skip if contains whitespace (for now)
                if ' ' in pattern_seq or '\n' in pattern_seq or '\t' in pattern_seq:
                    continue
                
                # Create or update pattern
                if pattern_seq in self.patterns:
                    self.patterns[pattern_seq].frequency += 1
                else:
                    self.patterns[pattern_seq] = Pattern(pattern_symbols, frequency=1)
    
    def get_patterns(self, min_frequency: int = 1) -> List[Pattern]:
        """
        Get all patterns, optionally filtered by frequency.
        
        Args:
            min_frequency: Minimum frequency to include
        
        Returns:
            List of patterns, sorted by frequency (highest first)
        """
        patterns = [
            pattern for pattern in self.patterns.values()
            if pattern.frequency >= min_frequency
        ]
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns
    
    def get_pattern(self, sequence: str) -> Pattern:
        """
        Get a specific pattern by its sequence.
        
        Args:
            sequence: The symbol sequence (e.g., "cat")
        
        Returns:
            Pattern object or None if not found
        """
        return self.patterns.get(sequence)
    
    def find_patterns_containing(self, symbol: str) -> List[Pattern]:
        """
        Find all patterns containing a specific symbol.
        
        Args:
            symbol: Symbol to search for
        
        Returns:
            List of patterns containing that symbol
        """
        return [
            pattern for pattern in self.patterns.values()
            if symbol in pattern.symbols
        ]
    
    def get_top_patterns(self, top_k: int = 10) -> List[Pattern]:
        """
        Get top K most frequent patterns.
        
        Args:
            top_k: How many patterns to return
        
        Returns:
            List of top patterns
        """
        all_patterns = self.get_patterns(min_frequency=1)
        return all_patterns[:top_k]
    
    def pattern_exists(self, sequence: str) -> bool:
        """Check if a pattern exists."""
        return sequence in self.patterns
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about learned patterns.
        
        Returns:
            Dictionary with stats
        """
        all_patterns = self.get_patterns(min_frequency=1)
        
        if not all_patterns:
            return {
                "total_patterns": 0,
                "avg_frequency": 0,
                "max_frequency": 0,
                "avg_length": 0
            }
        
        total_freq = sum(p.frequency for p in all_patterns)
        total_length = sum(p.length() for p in all_patterns)
        
        return {
            "total_patterns": len(all_patterns),
            "avg_frequency": total_freq / len(all_patterns),
            "max_frequency": max(p.frequency for p in all_patterns),
            "avg_length": total_length / len(all_patterns)
        }


# Test it works
if __name__ == "__main__":
    print("Testing Pattern Builder...")
    print("=" * 50)
    
    builder = PatternBuilder()
    
    # Learn from simple text
    print("\n1. Learning from text:")
    text = "cat cat dog cat mouse"
    print(f"   Text: '{text}'")
    builder.learn_from_text(text)
    
    # Get patterns
    print("\n2. Discovered Patterns:")
    patterns = builder.get_patterns(min_frequency=1)
    for pattern in patterns[:10]:  # Show top 10
        print(f"   {pattern}")
    
    # Statistics
    print("\n3. Statistics:")
    stats = builder.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value:.2f}" if isinstance(value, float) else f"   {key}: {value}")
    
    print("\n✅ Pattern Builder works!")
