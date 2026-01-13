"""
SOMA Pattern Builder - Core System
=====================================

Builds patterns from symbol combinations for the ENTIRE SOMA system.

This is where your idea comes to life:
- Symbols (c, a, t) → Pattern ("cat")
- Patterns emerge from usage
- No hardcoded meanings!

Integrates with SOMA's tokenization system.
"""

from typing import List, Dict, Tuple, Set
from collections import defaultdict
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.symbol_structures import get_registry, SymbolRegistry


class Pattern:
    """
    A pattern: sequence of symbols that appears together.
    
    Example: "cat" is a pattern if "c", "a", "t" appear together often.
    
    Key insight: Pattern ≠ Meaning
    - Pattern: "cat" appears frequently (structure)
    - Meaning: "cat" = animal (comes from usage/context)
    """
    
    def __init__(self, symbols: List[str], frequency: int = 1, context: str = ""):
        """
        Create a pattern.
        
        Args:
            symbols: List of symbols in the pattern (e.g., ['c', 'a', 't'])
            frequency: How many times we've seen this pattern
            context: Where we saw it (for tracking)
        """
        self.symbols = symbols
        self.frequency = frequency
        self.sequence = ''.join(symbols)  # "cat"
        self.contexts: Set[str] = set()
        if context:
            self.contexts.add(context)
    
    def length(self) -> int:
        """Get pattern length."""
        return len(self.symbols)
    
    def add_occurrence(self, context: str = ""):
        """Record another occurrence of this pattern."""
        self.frequency += 1
        if context:
            self.contexts.add(context)
    
    def stability_score(self) -> float:
        """
        Calculate how stable this pattern is.
        
        Stability = frequency / (number of unique contexts + 1)
        Higher = more stable (appears in many contexts)
        """
        if len(self.contexts) == 0:
            return float(self.frequency)
        return self.frequency / (len(self.contexts) + 1)
    
    def __repr__(self) -> str:
        return f"Pattern('{self.sequence}', freq={self.frequency}, stability={self.stability_score():.2f})"
    
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
    
    This integrates with SOMA's tokenization system.
    Works with any text input and learns patterns automatically.
    """
    
    def __init__(self, registry: SymbolRegistry = None):
        """
        Create a pattern builder.
        
        Args:
            registry: Symbol registry (uses global if None)
        """
        self.registry = registry or get_registry()
        self.patterns: Dict[str, Pattern] = {}
        self.ngram_counts: Dict[Tuple, int] = defaultdict(int)
    
    def learn_from_text(self, text: str, min_pattern_length: int = 2, max_pattern_length: int = 20):
        """
        Learn patterns from text.
        
        This is the main learning function - feed it text, it finds patterns!
        
        Args:
            text: Text to learn from
            min_pattern_length: Minimum pattern length (default: 2)
            max_pattern_length: Maximum pattern length (default: 20)
        """
        # Convert text to symbols (character level)
        symbols = list(text.lower())
        
        # Learn symbol combinations
        for i in range(len(symbols) - 1):
            sym1 = symbols[i]
            sym2 = symbols[i + 1]
            
            # Learn combination (registers symbols if needed)
            self.registry.learn_combination(sym1, sym2)
        
        # Extract patterns of different lengths
        for length in range(min_pattern_length, min(max_pattern_length + 1, len(symbols) + 1)):
            for i in range(len(symbols) - length + 1):
                pattern_symbols = symbols[i:i + length]
                pattern_seq = ''.join(pattern_symbols)
                
                # Skip whitespace-only patterns
                if all(c in ' \t\n\r' for c in pattern_seq):
                    continue
                
                # Create or update pattern
                if pattern_seq in self.patterns:
                    self.patterns[pattern_seq].add_occurrence(context=text[:50])
                else:
                    self.patterns[pattern_seq] = Pattern(
                        pattern_symbols,
                        frequency=1,
                        context=text[:50]
                    )
    
    def learn_from_tokens(self, tokens: List[str]):
        """
        Learn patterns from soma tokens.
        
        This integrates with SOMA's tokenization output.
        
        Args:
            tokens: List of tokens from soma tokenizer
        """
        # Treat each token as a potential pattern
        for token in tokens:
            if len(token) >= 2:  # Only meaningful tokens
                pattern_symbols = list(token.lower())
                pattern_seq = ''.join(pattern_symbols)
                
                if pattern_seq in self.patterns:
                    self.patterns[pattern_seq].add_occurrence()
                else:
                    self.patterns[pattern_seq] = Pattern(pattern_symbols, frequency=1)
    
    def get_patterns(self, min_frequency: int = 1, min_stability: float = 0.0) -> List[Pattern]:
        """
        Get all patterns, optionally filtered.
        
        Args:
            min_frequency: Minimum frequency to include
            min_stability: Minimum stability score to include
        
        Returns:
            List of patterns, sorted by stability (highest first)
        """
        patterns = [
            pattern for pattern in self.patterns.values()
            if pattern.frequency >= min_frequency and pattern.stability_score() >= min_stability
        ]
        patterns.sort(key=lambda p: p.stability_score(), reverse=True)
        return patterns
    
    def get_pattern(self, sequence: str) -> Pattern:
        """Get a specific pattern by its sequence."""
        return self.patterns.get(sequence)
    
    def find_patterns_containing(self, symbol: str) -> List[Pattern]:
        """Find all patterns containing a specific symbol."""
        return [
            pattern for pattern in self.patterns.values()
            if symbol in pattern.symbols
        ]
    
    def get_top_patterns(self, top_k: int = 10, min_frequency: int = 2) -> List[Pattern]:
        """Get top K most stable patterns."""
        all_patterns = self.get_patterns(min_frequency=min_frequency)
        return all_patterns[:top_k]
    
    def pattern_exists(self, sequence: str) -> bool:
        """Check if a pattern exists."""
        return sequence in self.patterns
    
    def get_statistics(self) -> Dict:
        """Get statistics about learned patterns."""
        all_patterns = self.get_patterns(min_frequency=1)
        
        if not all_patterns:
            return {
                "total_patterns": 0,
                "avg_frequency": 0,
                "max_frequency": 0,
                "avg_length": 0,
                "avg_stability": 0
            }
        
        total_freq = sum(p.frequency for p in all_patterns)
        total_length = sum(p.length() for p in all_patterns)
        total_stability = sum(p.stability_score() for p in all_patterns)
        
        return {
            "total_patterns": len(all_patterns),
            "avg_frequency": total_freq / len(all_patterns),
            "max_frequency": max(p.frequency for p in all_patterns),
            "avg_length": total_length / len(all_patterns),
            "avg_stability": total_stability / len(all_patterns)
        }


# Integration function for SOMA
def build_patterns_from_SOMA_tokens(tokens: List[Dict]) -> PatternBuilder:
    """
    Build patterns from soma tokenization output.
    
    This integrates with SOMA's existing tokenization system.
    
    Args:
        tokens: List of token dictionaries from soma tokenizer
    
    Returns:
        PatternBuilder with learned patterns
    """
    builder = PatternBuilder()
    
    # Extract token text from soma format
    token_texts = []
    for token in tokens:
        if isinstance(token, dict):
            token_text = token.get('token', token.get('text', ''))
        else:
            token_text = str(token)
        
        if token_text:
            token_texts.append(token_text)
    
    # Learn patterns
    builder.learn_from_tokens(token_texts)
    
    return builder
