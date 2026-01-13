"""
PathFinder - Find reasoning paths through knowledge.

Uses graph traversal + tree hierarchy to find
meaningful paths between concepts.
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from collections import deque
import heapq

from ..graph import GraphStore, GraphNode, GraphEdge, RelationType


@dataclass
class ReasoningPath:
    """
    A path through the knowledge graph with explanation.
    
    Attributes:
        nodes: List of nodes in the path
        edges: List of edges connecting nodes
        score: Path quality score (lower = better)
        explanation: Human-readable description
    """
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    score: float = 0.0
    explanation: str = ""
    
    def __len__(self) -> int:
        return len(self.nodes)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.node_id for n in self.nodes],
            "edges": [(e.source_id, e.relation_type.value, e.target_id) for e in self.edges],
            "score": self.score,
            "explanation": self.explanation,
        }


class PathFinder:
    """
    Find reasoning paths through the knowledge graph.
    
    Supports:
    - Shortest path (BFS)
    - Weighted path (Dijkstra)
    - All paths up to max depth
    - Constrained paths (by relation type)
    
    Example:
        finder = PathFinder(graph_store)
        
        # Find shortest path
        path = finder.find_shortest_path(node1, node2)
        
        # Find all paths
        paths = finder.find_all_paths(node1, node2, max_depth=4)
        
        # Find weighted best path
        path = finder.find_best_path(node1, node2)
    """
    
    # Relation weights for path scoring (lower = preferred)
    RELATION_WEIGHTS = {
        RelationType.IS_A: 0.5,
        RelationType.PART_OF: 0.6,
        RelationType.HAS_PART: 0.6,
        RelationType.CAUSES: 0.7,
        RelationType.CAUSED_BY: 0.7,
        RelationType.RELATED_TO: 1.0,
        RelationType.SIMILAR_TO: 0.8,
        RelationType.OPPOSITE_OF: 1.2,
        RelationType.PRECEDES: 0.9,
        RelationType.FOLLOWS: 0.9,
        RelationType.DERIVED_FROM: 0.7,
        RelationType.INSTANCE_OF: 0.5,
        RelationType.CONTAINS: 0.6,
        RelationType.BELONGS_TO: 0.6,
        RelationType.USES: 0.8,
        RelationType.USED_BY: 0.8,
        RelationType.DEPENDS_ON: 0.7,
    }
    
    def __init__(self, graph: GraphStore):
        """
        Initialize PathFinder.
        
        Args:
            graph: The GraphStore to search in
        """
        self.graph = graph
    
    def find_shortest_path(
        self,
        source_id: int,
        target_id: int,
        relation_types: Optional[List[RelationType]] = None
    ) -> Optional[ReasoningPath]:
        """
        Find shortest path using BFS.
        
        Args:
            source_id: Starting node ID
            target_id: Target node ID
            relation_types: Allowed relation types (None = all)
            
        Returns:
            ReasoningPath or None if no path exists
        """
        if source_id == target_id:
            node = self.graph.get_node(source_id)
            if node:
                return ReasoningPath(nodes=[node], edges=[], score=0)
            return None
        
        # BFS
        queue = deque([(source_id, [source_id], [])])
        visited = {source_id}
        
        while queue:
            current_id, path, edges = queue.popleft()
            
            # Get neighbors via outgoing edges
            for edge in self.graph.get_outgoing_edges(current_id):
                if relation_types and edge.relation_type not in relation_types:
                    continue
                
                neighbor_id = edge.target_id
                
                if neighbor_id == target_id:
                    # Found!
                    new_path = path + [neighbor_id]
                    new_edges = edges + [edge]
                    nodes = [self.graph.get_node(nid) for nid in new_path]
                    return ReasoningPath(
                        nodes=[n for n in nodes if n],
                        edges=new_edges,
                        score=len(new_edges),
                        explanation=self._generate_explanation(
                            [n for n in nodes if n], new_edges
                        )
                    )
                
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((
                        neighbor_id,
                        path + [neighbor_id],
                        edges + [edge]
                    ))
            
            # Also check incoming edges (bidirectional search)
            for edge in self.graph.get_incoming_edges(current_id):
                if relation_types and edge.relation_type not in relation_types:
                    continue
                
                neighbor_id = edge.source_id
                
                if neighbor_id == target_id:
                    new_path = path + [neighbor_id]
                    new_edges = edges + [edge]
                    nodes = [self.graph.get_node(nid) for nid in new_path]
                    return ReasoningPath(
                        nodes=[n for n in nodes if n],
                        edges=new_edges,
                        score=len(new_edges),
                        explanation=self._generate_explanation(
                            [n for n in nodes if n], new_edges
                        )
                    )
                
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((
                        neighbor_id,
                        path + [neighbor_id],
                        edges + [edge]
                    ))
        
        return None
    
    def find_best_path(
        self,
        source_id: int,
        target_id: int,
        relation_types: Optional[List[RelationType]] = None
    ) -> Optional[ReasoningPath]:
        """
        Find best weighted path using Dijkstra's algorithm.
        
        Args:
            source_id: Starting node ID
            target_id: Target node ID
            relation_types: Allowed relation types (None = all)
            
        Returns:
            ReasoningPath with lowest score
        """
        if source_id == target_id:
            node = self.graph.get_node(source_id)
            if node:
                return ReasoningPath(nodes=[node], edges=[], score=0)
            return None
        
        # Priority queue: (score, node_id, path, edges)
        heap = [(0.0, source_id, [source_id], [])]
        visited = set()
        
        while heap:
            score, current_id, path, edges = heapq.heappop(heap)
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            if current_id == target_id:
                nodes = [self.graph.get_node(nid) for nid in path]
                return ReasoningPath(
                    nodes=[n for n in nodes if n],
                    edges=edges,
                    score=score,
                    explanation=self._generate_explanation(
                        [n for n in nodes if n], edges
                    )
                )
            
            # Explore neighbors via outgoing
            for edge in self.graph.get_outgoing_edges(current_id):
                if relation_types and edge.relation_type not in relation_types:
                    continue
                
                neighbor_id = edge.target_id
                if neighbor_id not in visited:
                    edge_weight = self.RELATION_WEIGHTS.get(
                        edge.relation_type, 1.0
                    ) * edge.weight
                    
                    heapq.heappush(heap, (
                        score + edge_weight,
                        neighbor_id,
                        path + [neighbor_id],
                        edges + [edge]
                    ))
            
            # Also check incoming
            for edge in self.graph.get_incoming_edges(current_id):
                if relation_types and edge.relation_type not in relation_types:
                    continue
                
                neighbor_id = edge.source_id
                if neighbor_id not in visited:
                    edge_weight = self.RELATION_WEIGHTS.get(
                        edge.relation_type, 1.0
                    ) * edge.weight
                    
                    heapq.heappush(heap, (
                        score + edge_weight,
                        neighbor_id,
                        path + [neighbor_id],
                        edges + [edge]
                    ))
        
        return None
    
    def find_all_paths(
        self,
        source_id: int,
        target_id: int,
        max_depth: int = 5,
        relation_types: Optional[List[RelationType]] = None
    ) -> List[ReasoningPath]:
        """
        Find all paths up to max_depth.
        
        Args:
            source_id: Starting node ID
            target_id: Target node ID
            max_depth: Maximum path length
            relation_types: Allowed relation types (None = all)
            
        Returns:
            List of all valid ReasoningPaths
        """
        paths = []
        
        def dfs(
            current_id: int,
            target: int,
            path: List[int],
            edges: List[GraphEdge],
            visited: Set[int],
            depth: int
        ):
            if depth > max_depth:
                return
            
            if current_id == target:
                nodes = [self.graph.get_node(nid) for nid in path]
                valid_nodes = [n for n in nodes if n]
                score = sum(
                    self.RELATION_WEIGHTS.get(e.relation_type, 1.0) * e.weight
                    for e in edges
                )
                paths.append(ReasoningPath(
                    nodes=valid_nodes,
                    edges=edges.copy(),
                    score=score,
                    explanation=self._generate_explanation(valid_nodes, edges)
                ))
                return
            
            # Explore outgoing
            for edge in self.graph.get_outgoing_edges(current_id):
                if relation_types and edge.relation_type not in relation_types:
                    continue
                
                neighbor_id = edge.target_id
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    path.append(neighbor_id)
                    edges.append(edge)
                    
                    dfs(neighbor_id, target, path, edges, visited, depth + 1)
                    
                    path.pop()
                    edges.pop()
                    visited.remove(neighbor_id)
            
            # Explore incoming
            for edge in self.graph.get_incoming_edges(current_id):
                if relation_types and edge.relation_type not in relation_types:
                    continue
                
                neighbor_id = edge.source_id
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    path.append(neighbor_id)
                    edges.append(edge)
                    
                    dfs(neighbor_id, target, path, edges, visited, depth + 1)
                    
                    path.pop()
                    edges.pop()
                    visited.remove(neighbor_id)
        
        dfs(source_id, target_id, [source_id], [], {source_id}, 0)
        
        # Sort by score
        paths.sort(key=lambda p: p.score)
        return paths
    
    def find_common_ancestors(
        self,
        node_ids: List[int],
        max_depth: int = 5
    ) -> List[GraphNode]:
        """
        Find common ancestors of multiple nodes.
        
        Useful for finding shared concepts/categories.
        """
        if not node_ids:
            return []
        
        # Get ancestors for each node
        ancestors_sets = []
        
        for node_id in node_ids:
            ancestors = set()
            visited = set()
            queue = deque([(node_id, 0)])
            
            while queue:
                current_id, depth = queue.popleft()
                if depth > max_depth or current_id in visited:
                    continue
                visited.add(current_id)
                
                # Look for IS_A and PART_OF relations going up
                for edge in self.graph.get_outgoing_edges(current_id):
                    if edge.relation_type in [RelationType.IS_A, RelationType.PART_OF]:
                        ancestors.add(edge.target_id)
                        queue.append((edge.target_id, depth + 1))
            
            ancestors_sets.append(ancestors)
        
        # Find intersection
        if not ancestors_sets:
            return []
        
        common = ancestors_sets[0]
        for ancestor_set in ancestors_sets[1:]:
            common = common.intersection(ancestor_set)
        
        return [
            self.graph.get_node(nid)
            for nid in common
            if self.graph.get_node(nid)
        ]
    
    def _generate_explanation(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge]
    ) -> str:
        """Generate a human-readable explanation of the path."""
        if not nodes:
            return "Empty path"
        
        if len(nodes) == 1:
            return f"Direct: {nodes[0].text}"
        
        parts = [nodes[0].text]
        
        for i, edge in enumerate(edges):
            relation_name = edge.relation_type.value.replace("_", " ")
            if i + 1 < len(nodes):
                parts.append(f" --[{relation_name}]--> {nodes[i + 1].text}")
        
        return "".join(parts)
    
    def __repr__(self) -> str:
        return f"PathFinder(graph_nodes={len(self.graph)})"
