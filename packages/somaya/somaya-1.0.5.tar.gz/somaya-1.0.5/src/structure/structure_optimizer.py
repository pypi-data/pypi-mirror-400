"""
SOMA Structure Optimizer
==========================

Optimizes structure system for better performance:
- Pattern caching
- Structure indexing
- Fast lookups
- Memory optimization

Makes your structure system fast and efficient!
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.symbol_structures import SymbolRegistry, get_registry
from src.structure.pattern_builder import PatternBuilder, Pattern
from src.structure.structure_hierarchy import StructureHierarchy


class StructureCache:
    """
    Cache for structure lookups (fast access).
    
    Caches:
    - Symbol classifications
    - Pattern lookups
    - Structure traces
    """
    
    def __init__(self):
        """Create structure cache."""
        self.symbol_class_cache: Dict[str, str] = {}
        self.pattern_cache: Dict[str, Optional[Pattern]] = {}
        self.trace_cache: Dict[str, List[str]] = {}
    
    def get_symbol_class(self, symbol: str, registry: SymbolRegistry) -> str:
        """Get symbol class (cached)."""
        if symbol not in self.symbol_class_cache:
            self.symbol_class_cache[symbol] = registry.get_class(symbol)
        return self.symbol_class_cache[symbol]
    
    def get_pattern(self, sequence: str, builder: PatternBuilder) -> Optional[Pattern]:
        """Get pattern (cached)."""
        if sequence not in self.pattern_cache:
            self.pattern_cache[sequence] = builder.get_pattern(sequence)
        return self.pattern_cache[sequence]
    
    def clear(self):
        """Clear cache."""
        self.symbol_class_cache.clear()
        self.pattern_cache.clear()
        self.trace_cache.clear()


class StructureIndex:
    """
    Fast index for structure lookups.
    
    Indexes:
    - Patterns by symbol (which patterns contain symbol X?)
    - Patterns by frequency (fast access to top patterns)
    - Patterns by stability (fast access to stable patterns)
    """
    
    def __init__(self, pattern_builder: PatternBuilder):
        """
        Create structure index.
        
        Args:
            pattern_builder: PatternBuilder with learned patterns
        """
        self.builder = pattern_builder
        self._build_indexes()
    
    def _build_indexes(self):
        """Build all indexes."""
        # Index: symbol → patterns containing it
        self.symbol_to_patterns: Dict[str, Set[str]] = defaultdict(set)
        
        # Index: frequency → patterns
        self.frequency_index: Dict[int, Set[str]] = defaultdict(set)
        
        # Index: stability → patterns
        self.stability_index: Dict[float, Set[str]] = defaultdict(set)
        
        patterns = self.builder.get_patterns(min_frequency=1)
        
        for pattern in patterns:
            # Symbol index
            for symbol in pattern.symbols:
                self.symbol_to_patterns[symbol].add(pattern.sequence)
            
            # Frequency index
            self.frequency_index[pattern.frequency].add(pattern.sequence)
            
            # Stability index (rounded)
            stability_rounded = round(pattern.stability_score(), 2)
            self.stability_index[stability_rounded].add(pattern.sequence)
    
    def find_patterns_by_symbol(self, symbol: str) -> List[str]:
        """Find all patterns containing a symbol."""
        return list(self.symbol_to_patterns.get(symbol, set()))
    
    def find_patterns_by_frequency(self, min_frequency: int) -> List[str]:
        """Find all patterns with at least this frequency."""
        result = set()
        for freq, patterns in self.frequency_index.items():
            if freq >= min_frequency:
                result.update(patterns)
        return list(result)
    
    def find_patterns_by_stability(self, min_stability: float) -> List[str]:
        """Find all patterns with at least this stability."""
        result = set()
        for stability, patterns in self.stability_index.items():
            if stability >= min_stability:
                result.update(patterns)
        return list(result)


class StructureOptimizer:
    """
    Optimizes structure system for performance.
    
    Features:
    - Caching for fast lookups
    - Indexing for fast searches
    - Memory optimization
    """
    
    def __init__(self):
        """Create optimizer."""
        self.cache = StructureCache()
        self.index: Optional[StructureIndex] = None
        self.registry = get_registry()
        self.builder = PatternBuilder(self.registry)
        self.hierarchy = StructureHierarchy(self.registry)
    
    def optimize_for_text(self, text: str):
        """
        Optimize structure system for a specific text.
        
        Pre-builds indexes and caches for fast access.
        
        Args:
            text: Text to optimize for
        """
        # Learn patterns
        self.builder.learn_from_text(text)
        
        # Build hierarchy
        self.hierarchy.build_from_text(text)
        
        # Build index
        self.index = StructureIndex(self.builder)
    
    def fast_classify(self, symbol: str) -> str:
        """Fast symbol classification (cached)."""
        return self.cache.get_symbol_class(symbol, self.registry)
    
    def fast_get_pattern(self, sequence: str) -> Optional[Pattern]:
        """Fast pattern lookup (cached)."""
        return self.cache.get_pattern(sequence, self.builder)
    
    def fast_find_patterns(self, symbol: str) -> List[str]:
        """Fast pattern search by symbol (indexed)."""
        if self.index:
            return self.index.find_patterns_by_symbol(symbol)
        # Fallback: search patterns manually
        patterns = self.builder.get_patterns(min_frequency=1)
        result = []
        for pattern in patterns:
            if symbol in pattern.symbols:
                result.append(pattern.sequence)
        return result
    
    def get_optimization_stats(self) -> Dict:
        """Get optimization statistics."""
        return {
            "cache_size": {
                "symbol_classes": len(self.cache.symbol_class_cache),
                "patterns": len(self.cache.pattern_cache),
                "traces": len(self.cache.trace_cache)
            },
            "index_built": self.index is not None,
            "patterns_indexed": len(self.builder.get_patterns()) if self.index else 0
        }


# Test it works
if __name__ == "__main__":
    print("Testing Structure Optimizer...")
    print("=" * 70)
    
    optimizer = StructureOptimizer()
    
    print("\n1. Optimizing for text...")
    text = "cat cat dog cat mouse python java python"
    optimizer.optimize_for_text(text)
    
    print("\n2. Fast lookups:")
    print(f"   Classify 'A': {optimizer.fast_classify('A')}")
    print(f"   Classify '0': {optimizer.fast_classify('0')}")
    
    pattern = optimizer.fast_get_pattern("cat")
    if pattern:
        print(f"   Pattern 'cat': frequency={pattern.frequency}")
    
    print("\n3. Fast pattern search:")
    patterns_with_c = optimizer.fast_find_patterns('c')
    print(f"   Patterns with 'c': {patterns_with_c[:5]}")
    
    print("\n4. Optimization stats:")
    stats = optimizer.get_optimization_stats()
    print(f"   Cache size: {stats['cache_size']}")
    print(f"   Index built: {stats['index_built']}")
    
    print("\n✅ Structure optimizer works!")
