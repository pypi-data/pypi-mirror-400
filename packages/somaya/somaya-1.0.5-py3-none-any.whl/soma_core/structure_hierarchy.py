"""
SOMA Core Structure Hierarchy
==========================

Hierarchical structure system: symbols → patterns → units → meaning

This is where your idea comes together:
- Layer 1: Symbols (A, B, 0, 1, +, etc.)
- Layer 2: Patterns (cat, dog, 123, etc.)
- Layer 3: Units (words, phrases - emerges from usage)
- Layer 4: Meaning (comes from context, not hardcoded)

Remember: Structure enables meaning, doesn't define it!
"""

from typing import List, Dict, Optional, Set
from symbol_structures import SymbolRegistry, get_registry
from pattern_builder import PatternBuilder, Pattern


class StructureLevel:
    """Represents a level in the hierarchy."""
    SYMBOL = "symbol"      # Individual symbols (A, 0, +)
    PATTERN = "pattern"    # Symbol sequences (cat, 123)
    UNIT = "unit"          # Stable units (words, phrases)
    MEANING = "meaning"    # Semantic meaning (from usage)


class StructureNode:
    """
    A node in the structure hierarchy.
    
    Can represent:
    - A symbol (Layer 1)
    - A pattern (Layer 2)
    - A unit (Layer 3)
    - Meaning (Layer 4 - emerges, not hardcoded)
    """
    
    def __init__(self, content: str, level: str, parent: Optional['StructureNode'] = None):
        """
        Create a structure node.
        
        Args:
            content: What this node represents (e.g., "cat", "A")
            level: Structure level (SYMBOL, PATTERN, UNIT, MEANING)
            parent: Parent node (if this is built from another)
        """
        self.content = content
        self.level = level
        self.parent = parent
        self.children: List['StructureNode'] = []
        
        # Usage statistics (how often we see this)
        self.frequency = 0
        self.contexts: Set[str] = set()  # Where we've seen it
    
    def add_child(self, child: 'StructureNode'):
        """Add a child node (this is built from children)."""
        self.children.append(child)
        child.parent = self
    
    def add_context(self, context: str):
        """Record a context where we've seen this."""
        self.contexts.add(context)
        self.frequency += 1
    
    def __repr__(self) -> str:
        return f"StructureNode('{self.content}', level={self.level}, freq={self.frequency})"


class StructureHierarchy:
    """
    The complete hierarchical structure system.
    
    This is your idea implemented correctly:
    - Start with symbols
    - Build patterns
    - Let units emerge
    - Meaning comes from usage
    """
    
    def __init__(self, registry: SymbolRegistry = None):
        """
        Create a structure hierarchy.
        
        Args:
            registry: Symbol registry (uses global if None)
        """
        self.registry = registry or get_registry()
        self.pattern_builder = PatternBuilder(self.registry)
        
        # Nodes at each level
        self.symbol_nodes: Dict[str, StructureNode] = {}
        self.pattern_nodes: Dict[str, StructureNode] = {}
        self.unit_nodes: Dict[str, StructureNode] = {}
    
    def build_from_text(self, text: str):
        """
        Build hierarchy from text.
        
        This is the main function: feed it text, it builds the hierarchy!
        
        Args:
            text: Text to learn from
        
        Example:
            >>> hierarchy = StructureHierarchy()
            >>> hierarchy.build_from_text("cat cat dog")
            >>> # Now we have:
            >>> # - Symbol nodes: 'c', 'a', 't', 'd', 'o', 'g'
            >>> # - Pattern nodes: 'cat', 'dog'
            >>> # - Unit nodes: (if patterns are stable enough)
        """
        # Step 1: Learn patterns
        self.pattern_builder.learn_from_text(text)
        
        # Step 2: Build symbol nodes
        for symbol in self.registry.get_all_symbols():
            if symbol in text.lower():
                if symbol not in self.symbol_nodes:
                    self.symbol_nodes[symbol] = StructureNode(
                        symbol,
                        StructureLevel.SYMBOL
                    )
                self.symbol_nodes[symbol].add_context(text)
        
        # Step 3: Build pattern nodes from discovered patterns
        patterns = self.pattern_builder.get_patterns(min_frequency=1)
        for pattern in patterns:
            if pattern.sequence not in self.pattern_nodes:
                pattern_node = StructureNode(
                    pattern.sequence,
                    StructureLevel.PATTERN
                )
                self.pattern_nodes[pattern.sequence] = pattern_node
                
                # Link to symbol nodes (patterns are built from symbols)
                for symbol in pattern.symbols:
                    if symbol in self.symbol_nodes:
                        symbol_node = self.symbol_nodes[symbol]
                        pattern_node.add_child(symbol_node)
                
                pattern_node.frequency = pattern.frequency
        
        # Step 4: Build unit nodes (patterns that are stable enough)
        # A pattern becomes a "unit" if it appears frequently and consistently
        stable_patterns = [
            p for p in patterns
            if p.frequency >= 2  # Appears at least twice
        ]
        
        for pattern in stable_patterns:
            if pattern.sequence not in self.unit_nodes:
                unit_node = StructureNode(
                    pattern.sequence,
                    StructureLevel.UNIT
                )
                self.unit_nodes[pattern.sequence] = unit_node
                
                # Link to pattern node
                if pattern.sequence in self.pattern_nodes:
                    pattern_node = self.pattern_nodes[pattern.sequence]
                    unit_node.add_child(pattern_node)
    
    def get_symbol_structure(self, symbol: str) -> Optional[StructureNode]:
        """Get structure node for a symbol."""
        return self.symbol_nodes.get(symbol)
    
    def get_pattern_structure(self, pattern: str) -> Optional[StructureNode]:
        """Get structure node for a pattern."""
        return self.pattern_nodes.get(pattern)
    
    def get_unit_structure(self, unit: str) -> Optional[StructureNode]:
        """Get structure node for a unit."""
        return self.unit_nodes.get(unit)
    
    def trace_structure(self, content: str) -> List[StructureNode]:
        """
        Trace the structure hierarchy for a given content.
        
        Shows how it's built from symbols → patterns → units.
        
        Args:
            content: Content to trace (e.g., "cat")
        
        Returns:
            List of nodes from bottom to top
        """
        trace = []
        
        # Check if it's a unit
        if content in self.unit_nodes:
            trace.append(self.unit_nodes[content])
        
        # Check if it's a pattern
        if content in self.pattern_nodes:
            trace.append(self.pattern_nodes[content])
        
        # Add symbol nodes
        for symbol in content:
            if symbol in self.symbol_nodes:
                trace.append(self.symbol_nodes[symbol])
        
        return trace
    
    def get_statistics(self) -> Dict:
        """Get statistics about the hierarchy."""
        return {
            "symbols": len(self.symbol_nodes),
            "patterns": len(self.pattern_nodes),
            "units": len(self.unit_nodes),
            "total_nodes": len(self.symbol_nodes) + len(self.pattern_nodes) + len(self.unit_nodes)
        }
    
    def explain_structure(self, content: str) -> str:
        """
        Explain how a structure is built (for debugging/learning).
        
        Args:
            content: Content to explain (e.g., "cat")
        
        Returns:
            Human-readable explanation
        """
        lines = [f"Structure explanation for '{content}':", ""]
        
        # Check each level
        if content in self.unit_nodes:
            unit = self.unit_nodes[content]
            lines.append(f"✓ Unit level: '{content}' (frequency: {unit.frequency})")
            lines.append(f"  Built from pattern: {[c.content for c in unit.children]}")
        
        if content in self.pattern_nodes:
            pattern = self.pattern_nodes[content]
            lines.append(f"✓ Pattern level: '{content}' (frequency: {pattern.frequency})")
            lines.append(f"  Built from symbols: {[c.content for c in pattern.children]}")
        
        # Symbol level
        symbol_list = [s for s in content if s in self.symbol_nodes]
        if symbol_list:
            lines.append(f"✓ Symbol level: {symbol_list}")
        
        if len(lines) == 2:  # Only header
            lines.append("  (Not yet in hierarchy - needs more usage)")
        
        return "\n".join(lines)


# Test it works
if __name__ == "__main__":
    print("Testing Structure Hierarchy...")
    print("=" * 50)
    
    hierarchy = StructureHierarchy()
    
    # Build from text
    print("\n1. Building hierarchy from text:")
    text = "cat cat dog cat mouse"
    print(f"   Text: '{text}'")
    hierarchy.build_from_text(text)
    
    # Statistics
    print("\n2. Hierarchy Statistics:")
    stats = hierarchy.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Explain structure
    print("\n3. Structure Explanation:")
    print(hierarchy.explain_structure("cat"))
    
    print("\n✅ Structure Hierarchy works!")
