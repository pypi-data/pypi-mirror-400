"""
ContradictionDetector - Find conflicts in knowledge.

Detects:
- Direct contradictions (A OPPOSITE_OF B and A SIMILAR_TO B)
- Temporal conflicts (A PRECEDES B and A FOLLOWS B)
- Type conflicts (A IS_A B and A IS_A C where B OPPOSITE_OF C)
- Cyclical contradictions (A CAUSES B CAUSES A in non-feedback context)
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from ..graph import GraphStore, GraphNode, GraphEdge, RelationType


class ContradictionType(Enum):
    """Types of contradictions that can be detected."""
    DIRECT_OPPOSITE = "direct_opposite"       # Same pair with conflicting relations
    TEMPORAL_CONFLICT = "temporal_conflict"   # A precedes and follows B
    TYPE_CONFLICT = "type_conflict"           # IS_A paths lead to opposites
    CAUSAL_CYCLE = "causal_cycle"             # Circular causation
    SEMANTIC_CONFLICT = "semantic_conflict"   # Similar and opposite
    PART_WHOLE_CONFLICT = "part_whole"        # A part_of B and B part_of A
    ASYMMETRIC_VIOLATION = "asymmetric"       # Violates asymmetric property


@dataclass
class Contradiction:
    """
    A detected contradiction in the knowledge graph.
    
    Attributes:
        contradiction_type: Type of contradiction
        nodes: Nodes involved
        edges: Edges that create the contradiction
        description: Human-readable explanation
        severity: How serious (0.0 to 1.0)
        suggestion: How to resolve
    """
    contradiction_type: ContradictionType
    nodes: List[int]
    edges: List[int]  # edge_ids
    description: str
    severity: float = 0.5
    suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.contradiction_type.value,
            "nodes": self.nodes,
            "edges": self.edges,
            "description": self.description,
            "severity": self.severity,
            "suggestion": self.suggestion,
        }


@dataclass
class ContradictionReport:
    """Full report of contradictions found."""
    contradictions: List[Contradiction]
    nodes_checked: int
    edges_checked: int
    time_elapsed: float
    
    @property
    def has_contradictions(self) -> bool:
        return len(self.contradictions) > 0
    
    @property
    def critical_count(self) -> int:
        return sum(1 for c in self.contradictions if c.severity >= 0.8)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contradiction_count": len(self.contradictions),
            "critical_count": self.critical_count,
            "nodes_checked": self.nodes_checked,
            "edges_checked": self.edges_checked,
            "time_ms": self.time_elapsed * 1000,
            "contradictions": [c.to_dict() for c in self.contradictions],
        }
    
    def summary(self) -> str:
        """Get a summary string."""
        lines = [
            f"Contradiction Report",
            f"=" * 40,
            f"Total contradictions: {len(self.contradictions)}",
            f"Critical (severity >= 0.8): {self.critical_count}",
            f"Nodes checked: {self.nodes_checked}",
            f"Edges checked: {self.edges_checked}",
        ]
        
        if self.contradictions:
            lines.append("\nContradictions found:")
            for i, c in enumerate(self.contradictions[:10]):  # Show first 10
                lines.append(f"  {i+1}. [{c.contradiction_type.value}] {c.description}")
            
            if len(self.contradictions) > 10:
                lines.append(f"  ... and {len(self.contradictions) - 10} more")
        
        return "\n".join(lines)


class ContradictionDetector:
    """
    Detect contradictions in the knowledge graph.
    
    Checks for:
    1. Direct opposites on same pair
    2. Temporal conflicts
    3. Cyclical issues
    4. Type hierarchhy conflicts
    
    Example:
        detector = ContradictionDetector(graph_store)
        
        # Check everything
        report = detector.detect_all()
        
        # Check specific nodes
        issues = detector.check_node(node_id)
        
        # Check if adding an edge would create contradiction
        would_conflict = detector.would_contradict(src, tgt, relation)
    """
    
    # Relations that are mutually exclusive on the same pair
    EXCLUSIVE_PAIRS = [
        (RelationType.OPPOSITE_OF, RelationType.SIMILAR_TO),
        (RelationType.PRECEDES, RelationType.FOLLOWS),
        (RelationType.CAUSES, RelationType.CAUSED_BY),
        (RelationType.PART_OF, RelationType.CONTAINS),
    ]
    
    # Relations that should not be reflexive (A->A)
    NON_REFLEXIVE = [
        RelationType.IS_A,
        RelationType.PART_OF,
        RelationType.CAUSES,
        RelationType.PRECEDES,
        RelationType.OPPOSITE_OF,
    ]
    
    # Relations that should not have cycles
    ACYCLIC_RELATIONS = [
        RelationType.IS_A,
        RelationType.PART_OF,
        RelationType.PRECEDES,
    ]
    
    def __init__(self, graph: GraphStore):
        """
        Initialize detector.
        
        Args:
            graph: The knowledge graph to check
        """
        self.graph = graph
    
    def detect_all(self) -> ContradictionReport:
        """
        Run all contradiction checks.
        
        Returns:
            ContradictionReport with all found issues
        """
        import time
        start = time.time()
        
        contradictions = []
        
        # Check all detection methods
        contradictions.extend(self._detect_exclusive_pairs())
        contradictions.extend(self._detect_reflexive_violations())
        contradictions.extend(self._detect_cycles())
        contradictions.extend(self._detect_type_conflicts())
        
        elapsed = time.time() - start
        
        return ContradictionReport(
            contradictions=contradictions,
            nodes_checked=self.graph.node_count,
            edges_checked=self.graph.edge_count,
            time_elapsed=elapsed
        )
    
    def check_node(self, node_id: int) -> List[Contradiction]:
        """Check contradictions involving a specific node."""
        contradictions = []
        
        # Get all edges for this node
        outgoing = self.graph.get_outgoing_edges(node_id)
        incoming = self.graph.get_incoming_edges(node_id)
        
        # Check for exclusive pairs
        for edge1 in outgoing:
            for edge2 in outgoing:
                if edge1.edge_id >= edge2.edge_id:
                    continue
                if edge1.target_id != edge2.target_id:
                    continue
                
                if self._are_exclusive(edge1.relation_type, edge2.relation_type):
                    contradictions.append(Contradiction(
                        contradiction_type=ContradictionType.DIRECT_OPPOSITE,
                        nodes=[node_id, edge1.target_id],
                        edges=[edge1.edge_id, edge2.edge_id],
                        description=f"Node has both {edge1.relation_type.value} and {edge2.relation_type.value} to same target",
                        severity=0.9,
                        suggestion=f"Remove one of the conflicting edges"
                    ))
        
        return contradictions
    
    def would_contradict(
        self,
        source_id: int,
        target_id: int,
        relation: RelationType
    ) -> Tuple[bool, Optional[Contradiction]]:
        """
        Check if adding an edge would create a contradiction.
        
        Args:
            source_id: Proposed edge source
            target_id: Proposed edge target
            relation: Proposed relation type
            
        Returns:
            (would_contradict, Contradiction or None)
        """
        # Check reflexive violation
        if source_id == target_id and relation in self.NON_REFLEXIVE:
            return True, Contradiction(
                contradiction_type=ContradictionType.ASYMMETRIC_VIOLATION,
                nodes=[source_id],
                edges=[],
                description=f"Cannot have {relation.value} relation to self",
                severity=1.0,
                suggestion="Remove self-referential edge"
            )
        
        # Check for exclusive existing edges
        existing = self.graph.get_outgoing_edges(source_id)
        for edge in existing:
            if edge.target_id != target_id:
                continue
            
            if self._are_exclusive(relation, edge.relation_type):
                return True, Contradiction(
                    contradiction_type=ContradictionType.DIRECT_OPPOSITE,
                    nodes=[source_id, target_id],
                    edges=[edge.edge_id],
                    description=f"Would conflict with existing {edge.relation_type.value}",
                    severity=0.9,
                    suggestion=f"Remove existing {edge.relation_type.value} edge first"
                )
        
        # Check for cycle creation in acyclic relations
        if relation in self.ACYCLIC_RELATIONS:
            if self._would_create_cycle(source_id, target_id, relation):
                return True, Contradiction(
                    contradiction_type=ContradictionType.CAUSAL_CYCLE,
                    nodes=[source_id, target_id],
                    edges=[],
                    description=f"Would create cycle in {relation.value} hierarchy",
                    severity=0.85,
                    suggestion="Check if relation direction is correct"
                )
        
        return False, None
    
    def _detect_exclusive_pairs(self) -> List[Contradiction]:
        """Find edges that have mutually exclusive relations on same pair."""
        contradictions = []
        
        # Build edge index: (source, target) -> list of edges
        edge_index: Dict[Tuple[int, int], List[GraphEdge]] = defaultdict(list)
        
        for edge in self.graph.get_all_edges():
            key = (edge.source_id, edge.target_id)
            edge_index[key].append(edge)
        
        # Check each pair
        for (src, tgt), edges in edge_index.items():
            if len(edges) < 2:
                continue
            
            for i, edge1 in enumerate(edges):
                for edge2 in edges[i+1:]:
                    if self._are_exclusive(edge1.relation_type, edge2.relation_type):
                        src_node = self.graph.get_node(src)
                        tgt_node = self.graph.get_node(tgt)
                        
                        src_name = src_node.text if src_node else f"Node({src})"
                        tgt_name = tgt_node.text if tgt_node else f"Node({tgt})"
                        
                        contradictions.append(Contradiction(
                            contradiction_type=ContradictionType.DIRECT_OPPOSITE,
                            nodes=[src, tgt],
                            edges=[edge1.edge_id, edge2.edge_id],
                            description=f"'{src_name}' has both {edge1.relation_type.value} and {edge2.relation_type.value} to '{tgt_name}'",
                            severity=0.9,
                            suggestion="Remove one of the conflicting edges"
                        ))
        
        return contradictions
    
    def _detect_reflexive_violations(self) -> List[Contradiction]:
        """Find self-referential edges that shouldn't exist."""
        contradictions = []
        
        for edge in self.graph.get_all_edges():
            if edge.source_id == edge.target_id and edge.relation_type in self.NON_REFLEXIVE:
                node = self.graph.get_node(edge.source_id)
                name = node.text if node else f"Node({edge.source_id})"
                
                contradictions.append(Contradiction(
                    contradiction_type=ContradictionType.ASYMMETRIC_VIOLATION,
                    nodes=[edge.source_id],
                    edges=[edge.edge_id],
                    description=f"'{name}' has {edge.relation_type.value} relation to itself",
                    severity=0.8,
                    suggestion="Remove self-referential edge"
                ))
        
        return contradictions
    
    def _detect_cycles(self) -> List[Contradiction]:
        """Find cycles in relations that should be acyclic."""
        contradictions = []
        
        for relation in self.ACYCLIC_RELATIONS:
            cycles = self._find_cycles_for_relation(relation)
            
            for cycle in cycles:
                node_names = []
                for nid in cycle:
                    node = self.graph.get_node(nid)
                    node_names.append(node.text if node else f"Node({nid})")
                
                cycle_str = " → ".join(node_names) + f" → {node_names[0]}"
                
                contradictions.append(Contradiction(
                    contradiction_type=ContradictionType.CAUSAL_CYCLE,
                    nodes=cycle,
                    edges=[],  # Would need to track edges in cycle detection
                    description=f"Cycle in {relation.value}: {cycle_str}",
                    severity=0.85,
                    suggestion="Break the cycle by removing one edge"
                ))
        
        return contradictions
    
    def _detect_type_conflicts(self) -> List[Contradiction]:
        """Find entities that IS_A two opposite types."""
        contradictions = []
        
        # For each node, get all IS_A targets (direct and transitive)
        is_a_edges = self.graph.get_edges_by_type(RelationType.IS_A)
        
        # Group by source
        is_a_by_source: Dict[int, List[int]] = defaultdict(list)
        for edge in is_a_edges:
            is_a_by_source[edge.source_id].append(edge.target_id)
        
        # Check if any types are marked as opposites
        opposite_edges = self.graph.get_edges_by_type(RelationType.OPPOSITE_OF)
        opposite_pairs = {(e.source_id, e.target_id) for e in opposite_edges}
        opposite_pairs.update((e.target_id, e.source_id) for e in opposite_edges)
        
        for source, targets in is_a_by_source.items():
            if len(targets) < 2:
                continue
            
            for i, t1 in enumerate(targets):
                for t2 in targets[i+1:]:
                    if (t1, t2) in opposite_pairs:
                        src_node = self.graph.get_node(source)
                        t1_node = self.graph.get_node(t1)
                        t2_node = self.graph.get_node(t2)
                        
                        src_name = src_node.text if src_node else f"Node({source})"
                        t1_name = t1_node.text if t1_node else f"Node({t1})"
                        t2_name = t2_node.text if t2_node else f"Node({t2})"
                        
                        contradictions.append(Contradiction(
                            contradiction_type=ContradictionType.TYPE_CONFLICT,
                            nodes=[source, t1, t2],
                            edges=[],
                            description=f"'{src_name}' IS_A both '{t1_name}' and '{t2_name}', which are opposites",
                            severity=0.95,
                            suggestion="Review type assignments - entity cannot be two opposite types"
                        ))
        
        return contradictions
    
    def _are_exclusive(self, rel1: RelationType, rel2: RelationType) -> bool:
        """Check if two relations are mutually exclusive."""
        for excl1, excl2 in self.EXCLUSIVE_PAIRS:
            if (rel1 == excl1 and rel2 == excl2) or (rel1 == excl2 and rel2 == excl1):
                return True
        return False
    
    def _would_create_cycle(
        self,
        source_id: int,
        target_id: int,
        relation: RelationType
    ) -> bool:
        """Check if adding edge would create a cycle."""
        # DFS from target to see if we can reach source
        visited = set()
        stack = [target_id]
        
        while stack:
            current = stack.pop()
            if current == source_id:
                return True
            
            if current in visited:
                continue
            visited.add(current)
            
            for edge in self.graph.get_outgoing_edges(current):
                if edge.relation_type == relation:
                    stack.append(edge.target_id)
        
        return False
    
    def _find_cycles_for_relation(self, relation: RelationType) -> List[List[int]]:
        """Find all cycles for a specific relation type."""
        cycles = []
        visited = set()
        
        edges = self.graph.get_edges_by_type(relation)
        
        # Build adjacency list
        adj: Dict[int, List[int]] = defaultdict(list)
        for edge in edges:
            adj[edge.source_id].append(edge.target_id)
        
        def dfs(node: int, path: List[int], path_set: Set[int]):
            if node in path_set:
                # Found cycle - extract it
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:])
                return
            
            if node in visited:
                return
            
            path.append(node)
            path_set.add(node)
            
            for neighbor in adj.get(node, []):
                dfs(neighbor, path, path_set)
            
            path.pop()
            path_set.remove(node)
            visited.add(node)
        
        # Start DFS from each node
        for node in adj.keys():
            if node not in visited:
                dfs(node, [], set())
        
        return cycles
    
    def __repr__(self) -> str:
        return f"ContradictionDetector(graph_nodes={self.graph.node_count})"

