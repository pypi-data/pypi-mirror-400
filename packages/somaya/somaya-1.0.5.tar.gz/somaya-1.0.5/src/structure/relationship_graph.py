"""
SOMA Relationship Graph System
=================================

Comprehensive relationship understanding from ALL angles:
- Symbol relationships
- Pattern relationships
- Unit relationships
- Contextual relationships
- Temporal relationships
- Semantic relationships

This creates a complete relationship graph for deep understanding!
"""

import sys
import os
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.symbol_structures import get_registry, SymbolRegistry
from src.structure.pattern_builder import PatternBuilder, Pattern
from src.structure.structure_hierarchy import StructureHierarchy


@dataclass
class GraphNode:
    """Node in relationship graph."""
    id: str
    node_type: str  # 'symbol', 'pattern', 'unit', 'context'
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)


@dataclass
class GraphEdge:
    """Edge in relationship graph."""
    source: str
    target: str
    relationship_type: str
    strength: float
    perspectives: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


class RelationshipGraph:
    """
    Complete relationship graph system.
    
    Understands relationships from ALL angles:
    - Structural (how things are built)
    - Semantic (what things mean together)
    - Frequency (co-occurrence)
    - Contextual (where things appear)
    - Temporal (when things appear)
    """
    
    def __init__(self, registry: SymbolRegistry, builder: PatternBuilder, hierarchy: StructureHierarchy):
        """Create relationship graph."""
        self.registry = registry
        self.builder = builder
        self.hierarchy = hierarchy
        
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.edge_index: Dict[str, List[GraphEdge]] = defaultdict(list)
    
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any] = None):
        """Add node to graph."""
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(
                id=node_id,
                node_type=node_type,
                properties=properties or {}
            )
        else:
            self.nodes[node_id].properties.update(properties or {})
    
    def add_edge(self, source: str, target: str, relationship_type: str, 
                 strength: float, perspectives: List[str] = None, properties: Dict[str, Any] = None):
        """Add edge to graph."""
        edge = GraphEdge(
            source=source,
            target=target,
            relationship_type=relationship_type,
            strength=strength,
            perspectives=perspectives or [],
            properties=properties or {}
        )
        
        self.edges.append(edge)
        self.edge_index[source].append(edge)
        self.edge_index[target].append(edge)
        
        # Update node relationships
        if source in self.nodes:
            if target not in self.nodes[source].relationships:
                self.nodes[source].relationships.append(target)
        if target in self.nodes:
            if source not in self.nodes[target].relationships:
                self.nodes[target].relationships.append(source)
    
    def build_from_text(self, text: str):
        """Build complete relationship graph from text."""
        # Learn patterns
        self.builder.learn_from_text(text)
        self.hierarchy.build_from_text(text)
        
        words = text.lower().split()
        unique_words = set(words)
        
        # Add all words as nodes
        for word in unique_words:
            # Determine node type
            if word in self.hierarchy.unit_nodes:
                node_type = "unit"
            elif word in self.hierarchy.pattern_nodes:
                node_type = "pattern"
            else:
                node_type = "pattern"  # Default
            
            # Get properties
            properties = {
                "frequency": words.count(word),
                "length": len(word)
            }
            
            if self.builder.pattern_exists(word):
                pattern = self.builder.get_pattern(word)
                properties["stability"] = pattern.stability_score()
                properties["pattern_frequency"] = pattern.frequency
            
            self.add_node(word, node_type, properties)
        
        # Build relationships from ALL angles
        
        # 1. Symbol relationships (structural)
        self._build_symbol_relationships(unique_words)
        
        # 2. Pattern relationships (structural + semantic)
        self._build_pattern_relationships(unique_words)
        
        # 3. Co-occurrence relationships (semantic + contextual)
        self._build_cooccurrence_relationships(words)
        
        # 4. Frequency relationships (frequency perspective)
        self._build_frequency_relationships(unique_words, words)
        
        # 5. Contextual relationships (contextual perspective)
        self._build_contextual_relationships(words)
        
        # 6. Hierarchical relationships (structural)
        self._build_hierarchical_relationships(unique_words)
    
    def _build_symbol_relationships(self, words: Set[str]):
        """Build relationships based on shared symbols."""
        word_list = list(words)
        
        for i, word1 in enumerate(word_list):
            symbols1 = set(word1)
            
            for word2 in word_list[i+1:]:
                symbols2 = set(word2)
                overlap = symbols1 & symbols2
                
                if overlap:
                    strength = len(overlap) / max(len(symbols1), len(symbols2))
                    if strength > 0.2:  # Threshold
                        self.add_edge(
                            word1, word2,
                            "symbol_overlap",
                            strength,
                            perspectives=["structural", "relational"],
                            properties={"shared_symbols": list(overlap), "overlap_count": len(overlap)}
                        )
    
    def _build_pattern_relationships(self, words: Set[str]):
        """Build relationships based on pattern containment."""
        word_list = list(words)
        
        for i, word1 in enumerate(word_list):
            for word2 in word_list[i+1:]:
                # Check containment
                if word1 in word2:
                    self.add_edge(
                        word1, word2,
                        "pattern_containment",
                        0.8,
                        perspectives=["structural", "relational"],
                        properties={"containment_type": "word1_in_word2"}
                    )
                elif word2 in word1:
                    self.add_edge(
                        word1, word2,
                        "pattern_containment",
                        0.8,
                        perspectives=["structural", "relational"],
                        properties={"containment_type": "word2_in_word1"}
                    )
    
    def _build_cooccurrence_relationships(self, words: List[str]):
        """Build relationships based on co-occurrence."""
        cooccurrence: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Calculate co-occurrence within window
        window_size = 3
        for i, word1 in enumerate(words):
            for j in range(max(0, i-window_size), min(len(words), i+window_size+1)):
                if i != j:
                    word2 = words[j]
                    cooccurrence[word1][word2] += 1
        
        # Create edges
        for word1, cooccur in cooccurrence.items():
            for word2, count in cooccur.items():
                if count > 0:
                    strength = min(1.0, count / 5.0)  # Normalize
                    self.add_edge(
                        word1, word2,
                        "cooccurrence",
                        strength,
                        perspectives=["semantic", "contextual"],
                        properties={"cooccurrence_count": count}
                    )
    
    def _build_frequency_relationships(self, unique_words: Set[str], all_words: List[str]):
        """Build relationships based on frequency similarity."""
        word_freqs = {word: all_words.count(word) for word in unique_words}
        max_freq = max(word_freqs.values()) if word_freqs else 1
        
        word_list = list(unique_words)
        for i, word1 in enumerate(word_list):
            freq1 = word_freqs[word1] / max_freq
            
            for word2 in word_list[i+1:]:
                freq2 = word_freqs[word2] / max_freq
                
                # Similar frequency = relationship
                freq_similarity = 1.0 - abs(freq1 - freq2)
                if freq_similarity > 0.5:
                    self.add_edge(
                        word1, word2,
                        "frequency_similarity",
                        freq_similarity,
                        perspectives=["frequency", "relational"],
                        properties={"freq1": word_freqs[word1], "freq2": word_freqs[word2]}
                    )
    
    def _build_contextual_relationships(self, words: List[str]):
        """Build relationships based on contextual similarity."""
        # Words that appear in similar positions
        word_positions: Dict[str, List[int]] = defaultdict(list)
        
        for i, word in enumerate(words):
            word_positions[word].append(i)
        
        word_list = list(set(words))
        for i, word1 in enumerate(word_list):
            pos1 = word_positions[word1]
            
            for word2 in word_list[i+1:]:
                pos2 = word_positions[word2]
                
                # Check if positions are similar
                if pos1 and pos2:
                    avg_pos1 = sum(pos1) / len(pos1)
                    avg_pos2 = sum(pos2) / len(pos2)
                    pos_similarity = 1.0 / (1.0 + abs(avg_pos1 - avg_pos2) / len(words))
                    
                    if pos_similarity > 0.3:
                        self.add_edge(
                            word1, word2,
                            "contextual_similarity",
                            pos_similarity,
                            perspectives=["contextual", "relational"],
                            properties={"avg_pos1": avg_pos1, "avg_pos2": avg_pos2}
                        )
    
    def _build_hierarchical_relationships(self, words: Set[str]):
        """Build relationships based on hierarchy."""
        for word in words:
            trace = self.hierarchy.trace_structure(word)
            
            if trace and len(trace) > 1:
                # Connect to parent/child in hierarchy
                for i in range(len(trace) - 1):
                    parent = trace[i].content
                    child = trace[i+1].content
                    
                    if parent != child:
                        self.add_edge(
                            parent, child,
                            "hierarchical",
                            0.9,
                            perspectives=["structural", "relational"],
                            properties={"level": i, "direction": "parent_to_child"}
                        )
    
    def get_relationships(self, element: str, relationship_types: List[str] = None) -> List[GraphEdge]:
        """Get all relationships for element."""
        edges = []
        
        for edge in self.edges:
            if edge.source == element or edge.target == element:
                if relationship_types is None or edge.relationship_type in relationship_types:
                    edges.append(edge)
        
        return edges
    
    def get_strongest_relationships(self, element: str, top_k: int = 5) -> List[GraphEdge]:
        """Get strongest relationships for element."""
        relationships = self.get_relationships(element)
        relationships.sort(key=lambda e: e.strength, reverse=True)
        return relationships[:top_k]
    
    def find_path(self, source: str, target: str, max_depth: int = 3) -> Optional[List[str]]:
        """Find path between two nodes."""
        if source not in self.nodes or target not in self.nodes:
            return None
        
        # BFS
        queue = [(source, [source])]
        visited = {source}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == target:
                return path
            
            if len(path) >= max_depth:
                continue
            
            # Get neighbors
            edges = self.edge_index.get(current, [])
            for edge in edges:
                neighbor = edge.target if edge.source == current else edge.source
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_understanding(self, element: str) -> Dict[str, Any]:
        """Get comprehensive understanding of element from relationship graph."""
        if element not in self.nodes:
            return {}
        
        node = self.nodes[element]
        relationships = self.get_relationships(element)
        
        # Group by relationship type
        by_type: Dict[str, List[GraphEdge]] = defaultdict(list)
        for rel in relationships:
            by_type[rel.relationship_type].append(rel)
        
        # Group by perspective
        by_perspective: Dict[str, List[GraphEdge]] = defaultdict(list)
        for rel in relationships:
            for perspective in rel.perspectives:
                by_perspective[perspective].append(rel)
        
        return {
            "element": element,
            "node_type": node.node_type,
            "properties": node.properties,
            "total_relationships": len(relationships),
            "relationships_by_type": {
                rel_type: len(rels) for rel_type, rels in by_type.items()
            },
            "relationships_by_perspective": {
                perspective: len(rels) for perspective, rels in by_perspective.items()
            },
            "strongest_relationships": [
                {
                    "target": rel.target if rel.source == element else rel.source,
                    "type": rel.relationship_type,
                    "strength": rel.strength,
                    "perspectives": rel.perspectives
                }
                for rel in self.get_strongest_relationships(element, top_k=5)
            ],
            "relationship_diversity": len(by_type),
            "perspective_coverage": len(by_perspective)
        }


# Test it works
if __name__ == "__main__":
    print("Testing Relationship Graph System...")
    print("=" * 70)
    
    from src.structure.symbol_structures import get_registry
    from src.structure.pattern_builder import PatternBuilder
    from src.structure.structure_hierarchy import StructureHierarchy
    
    registry = get_registry()
    builder = PatternBuilder(registry)
    hierarchy = StructureHierarchy(registry)
    
    graph = RelationshipGraph(registry, builder, hierarchy)
    
    text = "cat cat dog cat mouse python java python machine learning"
    print(f"\nBuilding graph from: '{text}'")
    graph.build_from_text(text)
    
    print(f"\nNodes: {len(graph.nodes)}")
    print(f"Edges: {len(graph.edges)}")
    
    print("\nUnderstanding 'cat':")
    understanding = graph.get_understanding("cat")
    print(f"  Total relationships: {understanding['total_relationships']}")
    print(f"  Relationship types: {understanding['relationships_by_type']}")
    print(f"  Perspectives: {understanding['relationships_by_perspective']}")
    
    print("\nStrongest relationships for 'cat':")
    for rel in understanding['strongest_relationships'][:3]:
        print(f"  {rel['target']}: {rel['type']} (strength: {rel['strength']:.2f})")
    
    print("\n✅ Relationship graph works!")
