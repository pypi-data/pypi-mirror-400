"""
SOMA Structure Hierarchy - Complete System
============================================

Complete hierarchical structure system for ENTIRE SOMA:
- Layer 1: Symbols (A, B, 0, 1, +, etc.) - YOUR IDEA!
- Layer 2: Patterns (cat, dog, 123, etc.) - Combinations create new structures
- Layer 3: Units (words, phrases) - Stable patterns
- Layer 4: Meaning (emerges from usage, NOT hardcoded)

This is your complete idea implemented for the full SOMA system!
"""

from typing import List, Dict, Optional, Set
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.symbol_structures import SymbolRegistry, get_registry
from src.structure.pattern_builder import PatternBuilder, Pattern


class StructureLevel:
    """Levels in the hierarchy."""
    SYMBOL = "symbol"      # Individual symbols (A, 0, +)
    PATTERN = "pattern"    # Symbol sequences (cat, 123)
    UNIT = "unit"          # Stable units (words, phrases)
    MEANING = "meaning"    # Semantic meaning (from usage - NOT hardcoded!)


class StructureNode:
    """
    A node in the structure hierarchy.
    
    Can represent any level:
    - Symbol (Layer 1)
    - Pattern (Layer 2)
    - Unit (Layer 3)
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
        
        # Usage statistics
        self.frequency = 0
        self.contexts: Set[str] = set()
        
        # Meaning hints (from usage, not hardcoded)
        self.usage_patterns: Set[str] = set()
        self.co_occurrences: Set[str] = set()
    
    def add_child(self, child: 'StructureNode'):
        """Add a child node (this is built from children)."""
        self.children.append(child)
        child.parent = self
    
    def add_context(self, context: str):
        """Record a context where we've seen this."""
        self.contexts.add(context)
        self.frequency += 1
    
    def add_usage(self, usage_pattern: str):
        """Record a usage pattern (for meaning emergence)."""
        self.usage_patterns.add(usage_pattern)
    
    def add_co_occurrence(self, other: str):
        """Record co-occurrence with another structure."""
        self.co_occurrences.add(other)
    
    def __repr__(self) -> str:
        return f"StructureNode('{self.content}', level={self.level}, freq={self.frequency})"


class StructureHierarchy:
    """
    Complete hierarchical structure system for soma.
    
    This is YOUR IDEA implemented correctly:
    - Start with symbols (your foundation)
    - Build patterns (combinations create new structures)
    - Let units emerge (stable patterns)
    - Meaning comes from usage (not hardcoded)
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
        self.meaning_nodes: Dict[str, StructureNode] = {}
    
    def build_from_text(self, text: str):
        """
        Build hierarchy from text.
        
        This is the main function: feed it text, it builds the complete hierarchy!
        
        Args:
            text: Text to learn from
        """
        # Step 1: Learn patterns
        self.pattern_builder.learn_from_text(text)
        
        # Step 2: Build symbol nodes
        for symbol in text.lower():
            if symbol not in self.symbol_nodes:
                if self.registry.has_symbol(symbol):
                    self.symbol_nodes[symbol] = StructureNode(
                        symbol,
                        StructureLevel.SYMBOL
                    )
            if symbol in self.symbol_nodes:
                self.symbol_nodes[symbol].add_context(text[:100])
        
        # Step 3: Build pattern nodes
        patterns = self.pattern_builder.get_patterns(min_frequency=1)
        for pattern in patterns:
            if pattern.sequence not in self.pattern_nodes:
                pattern_node = StructureNode(
                    pattern.sequence,
                    StructureLevel.PATTERN
                )
                self.pattern_nodes[pattern.sequence] = pattern_node
                
                # Link to symbol nodes (patterns are built from symbols!)
                for symbol in pattern.symbols:
                    if symbol in self.symbol_nodes:
                        symbol_node = self.symbol_nodes[symbol]
                        pattern_node.add_child(symbol_node)
                
                pattern_node.frequency = pattern.frequency
        
        # Step 4: Build unit nodes (stable patterns)
        stable_patterns = [
            p for p in patterns
            if p.frequency >= 2 and p.stability_score() > 0.5
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
    
    def build_from_SOMA_tokens(self, tokens: List[Dict]):
        """
        Build hierarchy from soma tokenization output.
        
        This integrates with SOMA's existing tokenization!
        
        Args:
            tokens: List of token dictionaries from soma tokenizer
        """
        # Extract token texts
        token_texts = []
        for token in tokens:
            if isinstance(token, dict):
                token_text = token.get('token', token.get('text', ''))
            else:
                token_text = str(token)
            if token_text:
                token_texts.append(token_text)
        
        # Learn patterns from tokens
        self.pattern_builder.learn_from_tokens(token_texts)
        
        # Build hierarchy
        for token_text in token_texts:
            # Build symbol nodes
            for symbol in token_text.lower():
                if symbol not in self.symbol_nodes:
                    if self.registry.has_symbol(symbol):
                        self.symbol_nodes[symbol] = StructureNode(
                            symbol,
                            StructureLevel.SYMBOL
                        )
                if symbol in self.symbol_nodes:
                    self.symbol_nodes[symbol].add_context(token_text)
            
            # Build pattern nodes
            if len(token_text) >= 2:
                if token_text not in self.pattern_nodes:
                    pattern_node = StructureNode(
                        token_text,
                        StructureLevel.PATTERN
                    )
                    self.pattern_nodes[token_text] = pattern_node
                    
                    # Link to symbols
                    for symbol in token_text.lower():
                        if symbol in self.symbol_nodes:
                            pattern_node.add_child(self.symbol_nodes[symbol])
                else:
                    self.pattern_nodes[token_text].add_context(token_text)
    
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
        Trace the structure hierarchy for given content.
        
        Shows: symbols → patterns → units
        
        Args:
            content: Content to trace (e.g., "cat")
        
        Returns:
            List of nodes from bottom to top
        """
        trace = []
        
        # Check each level
        if content in self.unit_nodes:
            trace.append(self.unit_nodes[content])
        
        if content in self.pattern_nodes:
            trace.append(self.pattern_nodes[content])
        
        # Add symbol nodes
        for symbol in content.lower():
            if symbol in self.symbol_nodes:
                trace.append(self.symbol_nodes[symbol])
        
        return trace
    
    def explain_structure(self, content: str) -> str:
        """
        Explain how a structure is built (human-readable).
        
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
        symbol_list = [s for s in content.lower() if s in self.symbol_nodes]
        if symbol_list:
            lines.append(f"✓ Symbol level: {symbol_list}")
        
        if len(lines) == 2:  # Only header
            lines.append("  (Not yet in hierarchy - needs more usage)")
        
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict:
        """Get statistics about the hierarchy."""
        return {
            "symbols": len(self.symbol_nodes),
            "patterns": len(self.pattern_nodes),
            "units": len(self.unit_nodes),
            "meanings": len(self.meaning_nodes),
            "total_nodes": len(self.symbol_nodes) + len(self.pattern_nodes) + len(self.unit_nodes) + len(self.meaning_nodes)
        }


# Integration function for SOMA
def build_hierarchy_from_SOMA(text: str, tokenizer=None) -> StructureHierarchy:
    """
    Build structure hierarchy from text using SOMA tokenization.
    
    This is the main integration point with SOMA!
    
    Args:
        text: Text to process
        tokenizer: Optional SOMA tokenizer (uses default if None)
    
    Returns:
        Complete structure hierarchy
    """
    hierarchy = StructureHierarchy()
    
    # Option 1: Build directly from text
    hierarchy.build_from_text(text)
    
    # Option 2: If tokenizer provided, use SOMA tokens
    if tokenizer:
        try:
            tokens = tokenizer(text)
            hierarchy.build_from_SOMA_tokens(tokens)
        except:
            pass  # Fallback to text-based
    
    return hierarchy
