"""
SOMA Graph Walker - Custom Graph Traversal Algorithm
=====================================================

SOMA-ORIGINAL ALGORITHM. NOT PageRank. NOT BFS/DFS alone.

The SOMA Walk Algorithm:
    
    1. Start at source node with initial energy E
    2. At each step:
       - Compute edge weights using relation strength + confidence
       - Apply 9-centric decay to energy
       - Choose next node using weighted probability
       - Record path with accumulated score
    3. Continue until energy depletes or target reached

Features:
- Weighted random walks
- Deterministic shortest path
- Multi-hop reasoning paths
- Explanation generation
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import random
import math

from ..graph import GraphStore, GraphNode, RelationType
from ..graph.graph_edge import GraphEdge


class WalkMode(Enum):
    """Graph walk modes."""
    SHORTEST = "shortest"           # Deterministic shortest path
    WEIGHTED = "weighted"           # Weighted by relation strength
    RANDOM = "random"               # Random walk
    EXHAUSTIVE = "exhaustive"       # Find all paths


@dataclass
class WalkStep:
    """A single step in a graph walk."""
    node_id: int
    node_text: str
    relation: Optional[RelationType]
    energy: float
    accumulated_score: float


@dataclass  
class WalkResult:
    """Result of a graph walk."""
    path: List[WalkStep]
    
    total_score: float
    total_energy_used: float
    hops: int
    
    # Success info
    reached_target: bool
    terminated_reason: str  # "target", "energy", "dead_end", "max_hops"
    
    def explain(self) -> str:
        """Generate explanation of the walk."""
        lines = [f"Walk Result ({self.hops} hops, score={self.total_score:.4f})"]
        
        for i, step in enumerate(self.path):
            rel_str = f"--[{step.relation.value}]-->" if step.relation else "[START]"
            lines.append(f"  {i}: {rel_str} {step.node_text} (E={step.energy:.2f})")
        
        lines.append(f"Terminated: {self.terminated_reason}")
        
        return "\n".join(lines)


class SOMAGraphWalker:
    """
    SOMA Custom Graph Walking Algorithm.
    
    UNIQUE TO soma. Combines:
    - Energy-based traversal
    - Relation-weighted edges
    - 9-centric scoring
    - Explainable paths
    
    Example:
        walker = SOMAGraphWalker(graph)
        
        # Find path from node 1 to node 5
        result = walker.walk(source=1, target=5)
        print(result.explain())
        
        # Random walk with energy budget
        result = walker.random_walk(source=1, energy=10.0, steps=20)
    """
    
    # Default relation weights (how much energy each relation consumes)
    RELATION_COSTS = {
        RelationType.IS_A: 0.5,         # Cheap - strong relation
        RelationType.PART_OF: 0.5,
        RelationType.HAS_PART: 0.5,
        RelationType.CAUSES: 0.7,
        RelationType.CAUSED_BY: 0.7,
        RelationType.USES: 0.6,
        RelationType.USED_BY: 0.6,
        RelationType.DEPENDS_ON: 0.6,
        RelationType.SIMILAR_TO: 0.8,   # Expensive - weak relation
        RelationType.RELATED_TO: 0.9,
        RelationType.OPPOSITE_OF: 1.0,
        RelationType.MENTIONS: 1.0,
    }
    
    # Relation scores (contribution to total score)
    RELATION_SCORES = {
        RelationType.IS_A: 1.0,
        RelationType.PART_OF: 0.9,
        RelationType.HAS_PART: 0.9,
        RelationType.CAUSES: 0.85,
        RelationType.CAUSED_BY: 0.85,
        RelationType.USES: 0.8,
        RelationType.USED_BY: 0.8,
        RelationType.DEPENDS_ON: 0.8,
        RelationType.DERIVED_FROM: 0.75,
        RelationType.SIMILAR_TO: 0.6,
        RelationType.RELATED_TO: 0.5,
        RelationType.OPPOSITE_OF: 0.4,
        RelationType.MENTIONS: 0.3,
    }
    
    def __init__(
        self,
        graph: GraphStore,
        initial_energy: float = 10.0,
        decay_rate: float = 0.1
    ):
        """
        Initialize SOMA Graph Walker.
        
        Args:
            graph: GraphStore to walk
            initial_energy: Starting energy for walks
            decay_rate: Energy decay per step (added to relation cost)
        """
        self.graph = graph
        self.initial_energy = initial_energy
        self.decay_rate = decay_rate
    
    def walk(
        self,
        source: int,
        target: int,
        mode: WalkMode = WalkMode.WEIGHTED,
        max_hops: int = 10
    ) -> WalkResult:
        """
        Walk from source to target.
        
        Args:
            source: Starting node ID
            target: Target node ID
            mode: Walk mode
            max_hops: Maximum number of hops
            
        Returns:
            WalkResult
        """
        if mode == WalkMode.SHORTEST:
            return self._shortest_path(source, target, max_hops)
        elif mode == WalkMode.WEIGHTED:
            return self._weighted_walk(source, target, max_hops)
        elif mode == WalkMode.RANDOM:
            return self._random_walk_to_target(source, target, max_hops)
        else:
            return self._weighted_walk(source, target, max_hops)
    
    def random_walk(
        self,
        source: int,
        steps: int = 10,
        energy: Optional[float] = None
    ) -> WalkResult:
        """
        Perform a random walk from source.
        
        Args:
            source: Starting node ID
            steps: Maximum steps
            energy: Energy budget (default: initial_energy)
            
        Returns:
            WalkResult
        """
        energy = energy or self.initial_energy
        
        path: List[WalkStep] = []
        current = source
        visited: Set[int] = {source}
        total_score = 0.0
        
        # Initial step
        node = self.graph.get_node(current)
        if not node:
            return WalkResult(
                path=[], total_score=0, total_energy_used=0,
                hops=0, reached_target=False, terminated_reason="invalid_source"
            )
        
        path.append(WalkStep(
            node_id=current,
            node_text=node.text,
            relation=None,
            energy=energy,
            accumulated_score=0
        ))
        
        for _ in range(steps):
            # Get outgoing edges
            edges = self.graph.get_outgoing_edges(current)
            
            # Filter to unvisited (optional - allow revisits for random walk)
            if not edges:
                break
            
            # Choose random edge weighted by score
            weights = [self.RELATION_SCORES.get(e.relation_type, 0.5) for e in edges]
            total_weight = sum(weights)
            
            if total_weight == 0:
                break
            
            # Weighted random selection
            r = random.random() * total_weight
            cumulative = 0
            chosen_edge = edges[0]
            
            for edge, weight in zip(edges, weights):
                cumulative += weight
                if r <= cumulative:
                    chosen_edge = edge
                    break
            
            # Compute cost
            cost = self.RELATION_COSTS.get(chosen_edge.relation_type, 0.5) + self.decay_rate
            
            # Check energy
            if energy < cost:
                break
            
            energy -= cost
            
            # Move to next node
            current = chosen_edge.target_id
            visited.add(current)
            
            node = self.graph.get_node(current)
            score = self.RELATION_SCORES.get(chosen_edge.relation_type, 0.5) * chosen_edge.weight
            total_score += score
            
            path.append(WalkStep(
                node_id=current,
                node_text=node.text if node else f"Node({current})",
                relation=chosen_edge.relation_type,
                energy=energy,
                accumulated_score=total_score
            ))
        
        return WalkResult(
            path=path,
            total_score=total_score,
            total_energy_used=self.initial_energy - energy,
            hops=len(path) - 1,
            reached_target=False,
            terminated_reason="steps" if len(path) > steps else "energy"
        )
    
    def _shortest_path(self, source: int, target: int, max_hops: int) -> WalkResult:
        """Find shortest path using BFS."""
        from collections import deque
        
        # BFS
        queue = deque([(source, [source], [])])  # (node, path, edges)
        visited = {source}
        
        while queue:
            current, node_path, edge_path = queue.popleft()
            
            if current == target:
                return self._build_result(node_path, edge_path, True, "target")
            
            if len(node_path) >= max_hops:
                continue
            
            for edge in self.graph.get_outgoing_edges(current):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((
                        edge.target_id,
                        node_path + [edge.target_id],
                        edge_path + [edge]
                    ))
        
        return WalkResult(
            path=[], total_score=0, total_energy_used=0,
            hops=0, reached_target=False, terminated_reason="no_path"
        )
    
    def _weighted_walk(self, source: int, target: int, max_hops: int) -> WalkResult:
        """Weighted walk prioritizing high-score edges."""
        import heapq
        
        # Priority queue: (-score, node, path, edges)
        heap = [(0, source, [source], [])]
        visited = set()
        
        while heap:
            neg_score, current, node_path, edge_path = heapq.heappop(heap)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == target:
                return self._build_result(node_path, edge_path, True, "target")
            
            if len(node_path) >= max_hops:
                continue
            
            for edge in self.graph.get_outgoing_edges(current):
                if edge.target_id not in visited:
                    edge_score = self.RELATION_SCORES.get(edge.relation_type, 0.5) * edge.weight
                    new_score = -neg_score + edge_score
                    
                    heapq.heappush(heap, (
                        -new_score,
                        edge.target_id,
                        node_path + [edge.target_id],
                        edge_path + [edge]
                    ))
        
        return WalkResult(
            path=[], total_score=0, total_energy_used=0,
            hops=0, reached_target=False, terminated_reason="no_path"
        )
    
    def _random_walk_to_target(self, source: int, target: int, max_hops: int) -> WalkResult:
        """Random walk trying to reach target."""
        current = source
        node_path = [source]
        edge_path: List[GraphEdge] = []
        
        for _ in range(max_hops * 3):  # Allow more attempts
            if current == target:
                return self._build_result(node_path, edge_path, True, "target")
            
            edges = self.graph.get_edges_from(current)
            if not edges:
                break
            
            # Bias toward target if visible
            target_edges = [e for e in edges if e.target_id == target]
            if target_edges:
                chosen = target_edges[0]
            else:
                chosen = random.choice(edges)
            
            current = chosen.target_id
            node_path.append(current)
            edge_path.append(chosen)
            
            if len(node_path) > max_hops:
                break
        
        reached = current == target
        return self._build_result(
            node_path, edge_path, reached,
            "target" if reached else "max_hops"
        )
    
    def _build_result(
        self,
        node_path: List[int],
        edge_path: List[GraphEdge],
        reached: bool,
        reason: str
    ) -> WalkResult:
        """Build WalkResult from path."""
        steps: List[WalkStep] = []
        energy = self.initial_energy
        total_score = 0.0
        
        for i, node_id in enumerate(node_path):
            node = self.graph.get_node(node_id)
            
            relation = edge_path[i - 1].relation_type if i > 0 else None
            
            if i > 0:
                edge = edge_path[i - 1]
                cost = self.RELATION_COSTS.get(edge.relation_type, 0.5) + self.decay_rate
                energy -= cost
                score = self.RELATION_SCORES.get(edge.relation_type, 0.5) * edge.weight
                total_score += score
            
            steps.append(WalkStep(
                node_id=node_id,
                node_text=node.text if node else f"Node({node_id})",
                relation=relation,
                energy=max(0, energy),
                accumulated_score=total_score
            ))
        
        return WalkResult(
            path=steps,
            total_score=total_score,
            total_energy_used=self.initial_energy - energy,
            hops=len(steps) - 1,
            reached_target=reached,
            terminated_reason=reason
        )
    
    def find_all_paths(
        self,
        source: int,
        target: int,
        max_hops: int = 5,
        max_paths: int = 10
    ) -> List[WalkResult]:
        """Find all paths between source and target (up to limit)."""
        all_paths: List[WalkResult] = []
        
        def dfs(current: int, path: List[int], edges: List[GraphEdge], visited: Set[int]):
            if len(all_paths) >= max_paths:
                return
            
            if current == target:
                result = self._build_result(path, edges, True, "target")
                all_paths.append(result)
                return
            
            if len(path) >= max_hops:
                return
            
            for edge in self.graph.get_outgoing_edges(current):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    dfs(
                        edge.target_id,
                        path + [edge.target_id],
                        edges + [edge],
                        visited
                    )
                    visited.remove(edge.target_id)
        
        dfs(source, [source], [], {source})
        
        # Sort by score
        all_paths.sort(key=lambda r: r.total_score, reverse=True)
        
        return all_paths
    
    def __repr__(self) -> str:
        return (
            f"SOMAGraphWalker("
            f"energy={self.initial_energy}, "
            f"decay={self.decay_rate})"
        )

