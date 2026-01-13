"""
SOMA Advanced Pattern Analysis
================================

Advanced pattern analysis for the structure system:
- Pattern relationships
- Pattern evolution over time
- Pattern clusters
- Pattern significance scoring

This extends your structure idea with advanced capabilities!
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.pattern_builder import PatternBuilder, Pattern
from src.structure.symbol_structures import get_registry


class PatternRelationship:
    """
    Relationship between patterns.
    
    Patterns can relate in many ways:
    - Overlap (share symbols)
    - Co-occurrence (appear together)
    - Sub-patterns (one contains another)
    """
    
    def __init__(self, pattern1: str, pattern2: str, relationship_type: str, strength: float):
        """
        Create a pattern relationship.
        
        Args:
            pattern1: First pattern
            pattern2: Second pattern
            relationship_type: Type of relationship
            strength: Relationship strength (0.0 to 1.0)
        """
        self.pattern1 = pattern1
        self.pattern2 = pattern2
        self.relationship_type = relationship_type
        self.strength = strength
    
    def __repr__(self) -> str:
        return f"PatternRelationship('{self.pattern1}' → '{self.pattern2}', type={self.relationship_type}, strength={self.strength:.2f})"


class PatternAnalyzer:
    """
    Advanced pattern analysis.
    
    Analyzes patterns to find:
    - Relationships between patterns
    - Pattern clusters
    - Significant patterns
    - Pattern evolution
    """
    
    def __init__(self, pattern_builder: PatternBuilder):
        """
        Create pattern analyzer.
        
        Args:
            pattern_builder: PatternBuilder with learned patterns
        """
        self.builder = pattern_builder
        self.registry = get_registry()
    
    def find_pattern_relationships(self) -> List[PatternRelationship]:
        """
        Find relationships between patterns.
        
        Returns:
            List of pattern relationships
        """
        relationships = []
        patterns = self.builder.get_patterns(min_frequency=1)
        pattern_dict = {p.sequence: p for p in patterns}
        
        for pattern1 in patterns:
            for pattern2 in patterns:
                if pattern1.sequence == pattern2.sequence:
                    continue
                
                # Check for overlap (shared symbols)
                symbols1 = set(pattern1.symbols)
                symbols2 = set(pattern2.symbols)
                overlap = symbols1 & symbols2
                
                if overlap:
                    overlap_ratio = len(overlap) / max(len(symbols1), len(symbols2))
                    relationships.append(PatternRelationship(
                        pattern1.sequence,
                        pattern2.sequence,
                        "overlap",
                        overlap_ratio
                    ))
                
                # Check for sub-pattern (one contains another)
                if pattern1.sequence in pattern2.sequence or pattern2.sequence in pattern1.sequence:
                    relationships.append(PatternRelationship(
                        pattern1.sequence,
                        pattern2.sequence,
                        "subpattern",
                        0.8
                    ))
        
        return relationships
    
    def find_pattern_clusters(self, min_cluster_size: int = 2) -> List[List[str]]:
        """
        Find clusters of related patterns.
        
        Args:
            min_cluster_size: Minimum cluster size
        
        Returns:
            List of pattern clusters (each cluster is a list of pattern sequences)
        """
        relationships = self.find_pattern_relationships()
        
        # Build graph
        graph: Dict[str, Set[str]] = defaultdict(set)
        for rel in relationships:
            if rel.strength > 0.3:  # Only strong relationships
                graph[rel.pattern1].add(rel.pattern2)
                graph[rel.pattern2].add(rel.pattern1)
        
        # Find connected components (clusters)
        visited = set()
        clusters = []
        
        for pattern_seq in graph:
            if pattern_seq in visited:
                continue
            
            # BFS to find cluster
            cluster = []
            queue = [pattern_seq]
            visited.add(pattern_seq)
            
            while queue:
                current = queue.pop(0)
                cluster.append(current)
                
                for neighbor in graph.get(current, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)
        
        return clusters
    
    def calculate_pattern_significance(self, pattern: Pattern) -> float:
        """
        Calculate how significant a pattern is.
        
        Significance combines:
        - Frequency (how often it appears)
        - Stability (how consistent it is)
        - Uniqueness (how distinct it is)
        
        Args:
            pattern: Pattern to analyze
        
        Returns:
            Significance score (0.0 to 1.0)
        """
        # Base: frequency and stability
        base_score = pattern.stability_score()
        
        # Uniqueness: how distinct from other patterns
        all_patterns = self.builder.get_patterns(min_frequency=1)
        similar_count = 0
        
        for other in all_patterns:
            if other.sequence == pattern.sequence:
                continue
            
            # Check similarity (shared symbols)
            symbols1 = set(pattern.symbols)
            symbols2 = set(other.symbols)
            overlap = len(symbols1 & symbols2) / max(len(symbols1), len(symbols2))
            
            if overlap > 0.7:  # Very similar
                similar_count += 1
        
        uniqueness = 1.0 / (1.0 + similar_count * 0.1)
        
        # Combine
        significance = base_score * 0.7 + uniqueness * 0.3
        
        return min(1.0, significance)
    
    def get_most_significant_patterns(self, top_k: int = 10) -> List[Tuple[Pattern, float]]:
        """
        Get most significant patterns.
        
        Args:
            top_k: How many to return
        
        Returns:
            List of (pattern, significance_score) tuples
        """
        patterns = self.builder.get_patterns(min_frequency=2)
        
        scored = []
        for pattern in patterns:
            significance = self.calculate_pattern_significance(pattern)
            scored.append((pattern, significance))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
    
    def analyze_pattern_evolution(self, text_history: List[str]) -> Dict[str, List[float]]:
        """
        Analyze how patterns evolve over time.
        
        Args:
            text_history: List of texts in chronological order
        
        Returns:
            Dictionary mapping pattern sequences to frequency over time
        """
        evolution = defaultdict(list)
        
        # Build patterns incrementally
        temp_builder = PatternBuilder(self.registry)
        
        for text in text_history:
            temp_builder.learn_from_text(text)
            
            # Get current pattern frequencies
            current_patterns = temp_builder.get_patterns(min_frequency=1)
            for pattern in current_patterns:
                evolution[pattern.sequence].append(pattern.frequency)
        
        return dict(evolution)
    
    def find_emerging_patterns(self, text_history: List[str], threshold: float = 0.5) -> List[str]:
        """
        Find patterns that are emerging (increasing frequency).
        
        Args:
            text_history: List of texts in chronological order
            threshold: Minimum growth rate to consider "emerging"
        
        Returns:
            List of emerging pattern sequences
        """
        evolution = self.analyze_pattern_evolution(text_history)
        emerging = []
        
        for pattern_seq, frequencies in evolution.items():
            if len(frequencies) < 2:
                continue
            
            # Check if frequency is increasing
            growth_rate = (frequencies[-1] - frequencies[0]) / max(frequencies[0], 1)
            
            if growth_rate >= threshold:
                emerging.append(pattern_seq)
        
        return emerging


# Test it works
if __name__ == "__main__":
    print("Testing Advanced Pattern Analysis...")
    print("=" * 70)
    
    builder = PatternBuilder()
    builder.learn_from_text("cat cat dog cat mouse python java python")
    
    analyzer = PatternAnalyzer(builder)
    
    print("\n1. Pattern Relationships:")
    relationships = analyzer.find_pattern_relationships()
    for rel in relationships[:5]:
        print(f"   {rel}")
    
    print("\n2. Pattern Clusters:")
    clusters = analyzer.find_pattern_clusters()
    for i, cluster in enumerate(clusters[:3], 1):
        print(f"   Cluster {i}: {cluster}")
    
    print("\n3. Most Significant Patterns:")
    significant = analyzer.get_most_significant_patterns(top_k=5)
    for pattern, score in significant:
        print(f"   '{pattern.sequence}': significance {score:.3f}")
    
    print("\n✅ Advanced pattern analysis works!")
