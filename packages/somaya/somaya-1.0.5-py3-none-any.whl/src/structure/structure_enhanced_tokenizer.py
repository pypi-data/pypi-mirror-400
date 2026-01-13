"""
SOMA Structure-Enhanced Tokenizer
====================================

Enhances SOMA tokenization with structure information.

Uses your structure idea to improve tokenization:
- Symbols inform tokenization
- Patterns guide token boundaries
- Structure hierarchy provides context

This makes SOMA tokenization smarter using your structure foundation!
"""

import sys
import os
from typing import List, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure import (
    get_registry,
    PatternBuilder,
    StructureHierarchy
)


class StructureEnhancedTokenizer:
    """
    Tokenizer enhanced with structure information.
    
    Uses structure system to improve tokenization:
    - Symbol classes inform tokenization rules
    - Patterns help identify token boundaries
    - Structure hierarchy provides context
    """
    
    def __init__(self):
        """Create structure-enhanced tokenizer."""
        self.registry = get_registry()
        self.pattern_builder = PatternBuilder(self.registry)
        self.hierarchy = StructureHierarchy(self.registry)
    
    def tokenize_with_structure(self, text: str) -> List[Dict]:
        """
        Tokenize text with structure information.
        
        Returns tokens enhanced with structure metadata.
        
        Args:
            text: Text to tokenize
        
        Returns:
            List of token dictionaries with structure info
        """
        # Build structure hierarchy first
        self.hierarchy.build_from_text(text)
        self.pattern_builder.learn_from_text(text)
        
        # Simple word tokenization (can be enhanced)
        words = text.split()
        
        tokens = []
        for i, word in enumerate(words):
            token = {
                "token": word,
                "position": i,
                "structure": self._get_structure_info(word)
            }
            tokens.append(token)
        
        return tokens
    
    def _get_structure_info(self, word: str) -> Dict:
        """Get structure information for a word."""
        word_lower = word.lower()
        
        info = {
            "symbol_classes": [],
            "pattern_exists": False,
            "is_stable_unit": False,
            "structure_level": "unknown"
        }
        
        # Get symbol classes
        classes = set()
        for char in word_lower:
            cls = self.registry.get_class(char)
            classes.add(cls)
        info["symbol_classes"] = list(classes)
        
        # Check if pattern exists
        if self.pattern_builder.pattern_exists(word_lower):
            info["pattern_exists"] = True
            pattern = self.pattern_builder.get_pattern(word_lower)
            info["pattern_frequency"] = pattern.frequency
            info["pattern_stability"] = pattern.stability_score()
        
        # Check if stable unit
        if word_lower in self.hierarchy.unit_nodes:
            info["is_stable_unit"] = True
            info["structure_level"] = "unit"
        elif word_lower in self.hierarchy.pattern_nodes:
            info["structure_level"] = "pattern"
        else:
            info["structure_level"] = "symbol"
        
        return info
    
    def smart_tokenize(self, text: str, use_patterns: bool = True) -> List[str]:
        """
        Smart tokenization using structure patterns.
        
        Uses learned patterns to improve token boundaries.
        
        Args:
            text: Text to tokenize
            use_patterns: Use pattern information for tokenization
        
        Returns:
            List of tokens
        """
        # Learn patterns first
        self.pattern_builder.learn_from_text(text)
        
        if not use_patterns:
            # Simple word tokenization
            return text.split()
        
        # Pattern-aware tokenization
        # Find all known patterns in text
        patterns = self.pattern_builder.get_top_patterns(min_frequency=1)
        pattern_sequences = [p.sequence for p in patterns]
        pattern_sequences.sort(key=len, reverse=True)  # Longest first
        
        # Tokenize using patterns
        tokens = []
        text_lower = text.lower()
        i = 0
        
        while i < len(text_lower):
            # Try to match longest pattern first
            matched = False
            for pattern in pattern_sequences:
                if text_lower[i:i+len(pattern)] == pattern:
                    tokens.append(pattern)
                    i += len(pattern)
                    matched = True
                    break
            
            if not matched:
                # Single character
                tokens.append(text_lower[i])
                i += 1
        
        return tokens


# Convenience function
def tokenize_with_structure(text: str) -> List[Dict]:
    """
    Quick function to tokenize with structure information.
    
    Args:
        text: Text to tokenize
    
    Returns:
        List of tokens with structure info
    """
    tokenizer = StructureEnhancedTokenizer()
    return tokenizer.tokenize_with_structure(text)


# Test it works
if __name__ == "__main__":
    print("Testing Structure-Enhanced Tokenizer...")
    print("=" * 70)
    
    tokenizer = StructureEnhancedTokenizer()
    
    text = "cat cat dog"
    tokens = tokenizer.tokenize_with_structure(text)
    
    print(f"\nText: '{text}'")
    print("\nTokens with structure:")
    for token in tokens:
        print(f"  '{token['token']}':")
        struct = token.get('structure', {})
        print(f"    Classes: {struct.get('symbol_classes', [])}")
        print(f"    Pattern exists: {struct.get('pattern_exists', False)}")
        print(f"    Structure level: {struct.get('structure_level', 'unknown')}")
    
    print("\n✅ Structure-enhanced tokenizer works!")
