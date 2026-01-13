"""
GraphStore: Custom knowledge graph storage.

Pure Python implementation - NO external graph libraries.
Provides O(1) node/edge lookup and efficient traversal.
"""

from typing import Dict, List, Set, Optional, Tuple, Iterator, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json
import pickle

from .graph_node import GraphNode
from .graph_edge import GraphEdge, RelationType


@dataclass
class GraphStats:
    """Statistics about the graph."""
    node_count: int = 0
    edge_count: int = 0
    relation_type_counts: Dict[str, int] = field(default_factory=dict)
    avg_degree: float = 0.0
    isolated_nodes: int = 0


class GraphStore:
    """
    Custom knowledge graph implementation.
    
    Design Goals:
    - Pure Python (no networkx, no neo4j)
    - O(1) node/edge lookup
    - Efficient neighbor traversal
    - Serializable to JSON/pickle
    
    Data Structures:
    - _nodes: Dict[node_id, GraphNode]
    - _edges: Dict[edge_id, GraphEdge]
    - _outgoing: Dict[node_id, Set[edge_id]]  # Adjacency list
    - _incoming: Dict[node_id, Set[edge_id]]  # Reverse adjacency
    - _by_type: Dict[relation_type, Set[edge_id]]  # Index by relation type
    
    Example:
        >>> store = GraphStore()
        >>> store.add_node(GraphNode(1, "dog"))
        >>> store.add_node(GraphNode(2, "animal"))
        >>> store.add_edge(1, 2, RelationType.IS_A)
        >>> neighbors = store.get_neighbors(1)
    """
    
    def __init__(self):
        # === PRIMARY STORAGE ===
        self._nodes: Dict[int, GraphNode] = {}
        self._edges: Dict[int, GraphEdge] = {}
        
        # === ADJACENCY LISTS ===
        self._outgoing: Dict[int, Set[int]] = defaultdict(set)
        self._incoming: Dict[int, Set[int]] = defaultdict(set)
        
        # === INDICES ===
        self._by_relation_type: Dict[str, Set[int]] = defaultdict(set)
        self._by_node_type: Dict[str, Set[int]] = defaultdict(set)
        self._by_text: Dict[str, Set[int]] = defaultdict(set)  # text → node_ids
        
        # === EDGE ID GENERATOR ===
        self._next_edge_id = 1
    
    # ═══════════════════════════════════════════════════════════════════
    # NODE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════
    
    def add_node(self, node: GraphNode) -> int:
        """
        Add a node to the graph.
        
        Args:
            node: GraphNode to add
        
        Returns:
            node_id of the added node
        """
        self._nodes[node.node_id] = node
        self._by_node_type[node.node_type].add(node.node_id)
        self._by_text[node.text.lower()].add(node.node_id)
        return node.node_id
    
    def add_node_simple(self, node_id: int, text: str, node_type: str = "token") -> int:
        """
        Add a node with minimal parameters.
        
        Args:
            node_id: Unique ID
            text: Node text/label
            node_type: Type of node
        
        Returns:
            node_id
        """
        node = GraphNode(node_id=node_id, text=text, node_type=node_type)
        return self.add_node(node)
    
    def get_node(self, node_id: int) -> Optional[GraphNode]:
        """Get node by ID. O(1)."""
        return self._nodes.get(node_id)
    
    def has_node(self, node_id: int) -> bool:
        """Check if node exists. O(1)."""
        return node_id in self._nodes
    
    def remove_node(self, node_id: int) -> bool:
        """
        Remove node and all its edges.
        
        Args:
            node_id: ID of node to remove
        
        Returns:
            True if node existed and was removed
        """
        if node_id not in self._nodes:
            return False
        
        # Remove all edges connected to this node
        edges_to_remove = set()
        edges_to_remove.update(self._outgoing.get(node_id, set()))
        edges_to_remove.update(self._incoming.get(node_id, set()))
        
        for edge_id in edges_to_remove:
            self.remove_edge(edge_id)
        
        # Remove from indices
        node = self._nodes[node_id]
        self._by_node_type[node.node_type].discard(node_id)
        self._by_text[node.text.lower()].discard(node_id)
        
        # Remove node
        del self._nodes[node_id]
        
        # Clean up adjacency lists
        self._outgoing.pop(node_id, None)
        self._incoming.pop(node_id, None)
        
        return True
    
    def get_nodes_by_type(self, node_type: str) -> List[GraphNode]:
        """Get all nodes of a specific type."""
        node_ids = self._by_node_type.get(node_type, set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def get_nodes_by_text(self, text: str) -> List[GraphNode]:
        """Get all nodes with matching text (case-insensitive)."""
        node_ids = self._by_text.get(text.lower(), set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def get_all_nodes(self) -> List[GraphNode]:
        """Get all nodes in the graph."""
        return list(self._nodes.values())
    
    # ═══════════════════════════════════════════════════════════════════
    # EDGE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════
    
    def add_edge(
        self,
        source_id: int,
        target_id: int,
        relation_type: RelationType,
        weight: float = 1.0,
        evidence: str = "",
        edge_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Add an edge between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Type of relationship
            weight: Edge weight (0.0 to 1.0)
            evidence: Why this edge exists
            edge_id: Optional specific edge ID (auto-generated if None)
        
        Returns:
            edge_id if successful, None if nodes don't exist
        """
        # Check nodes exist
        if source_id not in self._nodes or target_id not in self._nodes:
            return None
        
        # Generate edge_id
        if edge_id is None:
            edge_id = self._next_edge_id
            self._next_edge_id += 1
        else:
            self._next_edge_id = max(self._next_edge_id, edge_id + 1)
        
        # Create edge
        edge = GraphEdge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            evidence=evidence
        )
        
        # Store edge
        self._edges[edge_id] = edge
        
        # Update adjacency lists
        self._outgoing[source_id].add(edge_id)
        self._incoming[target_id].add(edge_id)
        
        # Update node edge sets
        self._nodes[source_id]._outgoing_edge_ids.add(edge_id)
        self._nodes[target_id]._incoming_edge_ids.add(edge_id)
        
        # Update indices
        self._by_relation_type[relation_type.value].add(edge_id)
        
        return edge_id
    
    def get_edge(self, edge_id: int) -> Optional[GraphEdge]:
        """Get edge by ID. O(1)."""
        return self._edges.get(edge_id)
    
    def has_edge(self, edge_id: int) -> bool:
        """Check if edge exists. O(1)."""
        return edge_id in self._edges
    
    def has_edge_between(self, source_id: int, target_id: int, 
                         relation_type: Optional[RelationType] = None) -> bool:
        """Check if an edge exists between two nodes."""
        for edge_id in self._outgoing.get(source_id, set()):
            edge = self._edges.get(edge_id)
            if edge and edge.target_id == target_id:
                if relation_type is None or edge.relation_type == relation_type:
                    return True
        return False
    
    def remove_edge(self, edge_id: int) -> bool:
        """
        Remove an edge.
        
        Args:
            edge_id: ID of edge to remove
        
        Returns:
            True if edge existed and was removed
        """
        if edge_id not in self._edges:
            return False
        
        edge = self._edges[edge_id]
        
        # Update adjacency lists
        self._outgoing[edge.source_id].discard(edge_id)
        self._incoming[edge.target_id].discard(edge_id)
        
        # Update node edge sets
        if edge.source_id in self._nodes:
            self._nodes[edge.source_id]._outgoing_edge_ids.discard(edge_id)
        if edge.target_id in self._nodes:
            self._nodes[edge.target_id]._incoming_edge_ids.discard(edge_id)
        
        # Update indices
        self._by_relation_type[edge.relation_type.value].discard(edge_id)
        
        # Remove edge
        del self._edges[edge_id]
        return True
    
    def get_edges_by_type(self, relation_type: RelationType) -> List[GraphEdge]:
        """Get all edges of a specific relation type."""
        edge_ids = self._by_relation_type.get(relation_type.value, set())
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]
    
    def get_all_edges(self) -> List[GraphEdge]:
        """Get all edges in the graph."""
        return list(self._edges.values())
    
    # ═══════════════════════════════════════════════════════════════════
    # TRAVERSAL OPERATIONS
    # ═══════════════════════════════════════════════════════════════════
    
    def get_neighbors(
        self,
        node_id: int,
        direction: str = "outgoing",
        relation_type: Optional[RelationType] = None
    ) -> List[Tuple[GraphNode, GraphEdge]]:
        """
        Get neighboring nodes with connecting edges.
        
        Args:
            node_id: Starting node
            direction: "outgoing", "incoming", or "both"
            relation_type: Filter by relation type (optional)
        
        Returns:
            List of (neighbor_node, connecting_edge) tuples
        """
        results = []
        
        # Outgoing neighbors
        if direction in ("outgoing", "both"):
            for edge_id in self._outgoing.get(node_id, set()):
                edge = self._edges.get(edge_id)
                if edge:
                    if relation_type is None or edge.relation_type == relation_type:
                        neighbor = self._nodes.get(edge.target_id)
                        if neighbor:
                            results.append((neighbor, edge))
        
        # Incoming neighbors
        if direction in ("incoming", "both"):
            for edge_id in self._incoming.get(node_id, set()):
                edge = self._edges.get(edge_id)
                if edge:
                    if relation_type is None or edge.relation_type == relation_type:
                        neighbor = self._nodes.get(edge.source_id)
                        if neighbor:
                            results.append((neighbor, edge))
        
        return results
    
    def get_outgoing_edges(self, node_id: int) -> List[GraphEdge]:
        """Get all outgoing edges from a node."""
        edge_ids = self._outgoing.get(node_id, set())
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]
    
    def get_incoming_edges(self, node_id: int) -> List[GraphEdge]:
        """Get all incoming edges to a node."""
        edge_ids = self._incoming.get(node_id, set())
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]
    
    # ═══════════════════════════════════════════════════════════════════
    # PATH FINDING
    # ═══════════════════════════════════════════════════════════════════
    
    def find_path(
        self,
        source_id: int,
        target_id: int,
        max_depth: int = 5
    ) -> Optional[List[Tuple[GraphNode, Optional[GraphEdge]]]]:
        """
        Find shortest path between two nodes using BFS.
        
        Args:
            source_id: Starting node ID
            target_id: Target node ID
            max_depth: Maximum path length
        
        Returns:
            List of (node, edge_to_next) tuples representing the path,
            or None if no path exists.
            The last tuple has edge=None.
        """
        if source_id not in self._nodes or target_id not in self._nodes:
            return None
        
        if source_id == target_id:
            return [(self._nodes[source_id], None)]
        
        # BFS with path tracking
        visited = {source_id}
        # Queue: (current_node_id, path_so_far)
        # path_so_far is list of (node_id, edge_id_to_get_here)
        queue = [(source_id, [(source_id, None)])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            # Explore neighbors
            for edge_id in self._outgoing.get(current_id, set()):
                edge = self._edges.get(edge_id)
                if not edge:
                    continue
                
                next_id = edge.target_id
                
                if next_id == target_id:
                    # Found! Build result path
                    result_path = []
                    for nid, eid in path:
                        node = self._nodes[nid]
                        edge_obj = self._edges.get(eid) if eid else None
                        result_path.append((node, edge_obj))
                    # Add the edge to target
                    result_path[-1] = (result_path[-1][0], edge)
                    # Add target node
                    result_path.append((self._nodes[target_id], None))
                    return result_path
                
                if next_id not in visited:
                    visited.add(next_id)
                    new_path = path + [(next_id, edge_id)]
                    queue.append((next_id, new_path))
        
        return None  # No path found
    
    def find_all_paths(
        self,
        source_id: int,
        target_id: int,
        max_depth: int = 4,
        max_paths: int = 10
    ) -> List[List[Tuple[GraphNode, Optional[GraphEdge]]]]:
        """
        Find all paths between two nodes using DFS.
        
        Args:
            source_id: Starting node ID
            target_id: Target node ID
            max_depth: Maximum path length
            max_paths: Maximum number of paths to return
        
        Returns:
            List of paths, where each path is a list of (node, edge) tuples
        """
        if source_id not in self._nodes or target_id not in self._nodes:
            return []
        
        all_paths = []
        
        def dfs(current_id: int, path: List[Tuple[int, Optional[int]]], visited: Set[int]):
            if len(all_paths) >= max_paths:
                return
            if len(path) > max_depth:
                return
            
            if current_id == target_id:
                # Convert path to result format
                result = []
                for i, (nid, eid) in enumerate(path):
                    node = self._nodes[nid]
                    edge = self._edges.get(eid) if eid else None
                    result.append((node, edge))
                all_paths.append(result)
                return
            
            # Explore neighbors
            for edge_id in self._outgoing.get(current_id, set()):
                edge = self._edges.get(edge_id)
                if not edge or edge.target_id in visited:
                    continue
                
                next_id = edge.target_id
                visited.add(next_id)
                path.append((next_id, edge_id if next_id != target_id else None))
                # Fix: set the edge on previous node
                if len(path) >= 2:
                    path[-2] = (path[-2][0], edge_id)
                dfs(next_id, path, visited)
                path.pop()
                visited.remove(next_id)
        
        dfs(source_id, [(source_id, None)], {source_id})
        return all_paths
    
    # ═══════════════════════════════════════════════════════════════════
    # STATISTICS
    # ═══════════════════════════════════════════════════════════════════
    
    def get_stats(self) -> GraphStats:
        """Get graph statistics."""
        relation_counts = {}
        for rel_type, edge_ids in self._by_relation_type.items():
            relation_counts[rel_type] = len(edge_ids)
        
        node_count = len(self._nodes)
        edge_count = len(self._edges)
        avg_degree = (2 * edge_count / node_count) if node_count > 0 else 0
        
        isolated = sum(1 for n in self._nodes.values() if n.is_isolated)
        
        return GraphStats(
            node_count=node_count,
            edge_count=edge_count,
            relation_type_counts=relation_counts,
            avg_degree=avg_degree,
            isolated_nodes=isolated
        )
    
    @property
    def node_count(self) -> int:
        return len(self._nodes)
    
    @property
    def edge_count(self) -> int:
        return len(self._edges)
    
    def __len__(self) -> int:
        """Return number of nodes."""
        return len(self._nodes)
    
    def __contains__(self, node_id: int) -> bool:
        """Check if node exists."""
        return node_id in self._nodes
    
    def __iter__(self) -> Iterator[GraphNode]:
        """Iterate over nodes."""
        return iter(self._nodes.values())
    
    # ═══════════════════════════════════════════════════════════════════
    # SERIALIZATION
    # ═══════════════════════════════════════════════════════════════════
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary."""
        return {
            "nodes": {str(nid): node.to_dict() for nid, node in self._nodes.items()},
            "edges": {str(eid): edge.to_dict() for eid, edge in self._edges.items()},
            "next_edge_id": self._next_edge_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphStore":
        """Create graph from dictionary."""
        store = cls()
        store._next_edge_id = data.get("next_edge_id", 1)
        
        # Load nodes first
        for nid_str, node_data in data.get("nodes", {}).items():
            node = GraphNode.from_dict(node_data)
            store.add_node(node)
        
        # Load edges
        for eid_str, edge_data in data.get("edges", {}).items():
            edge = GraphEdge.from_dict(edge_data)
            store.add_edge(
                source_id=edge.source_id,
                target_id=edge.target_id,
                relation_type=edge.relation_type,
                weight=edge.weight,
                evidence=edge.evidence,
                edge_id=edge.edge_id
            )
        
        return store
    
    def save_json(self, filepath: str):
        """Save graph to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
    
    @classmethod
    def load_json(cls, filepath: str) -> "GraphStore":
        """Load graph from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def save_pickle(self, filepath: str):
        """Save graph to pickle file (faster, smaller)."""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @classmethod
    def load_pickle(cls, filepath: str) -> "GraphStore":
        """Load graph from pickle file."""
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    # ═══════════════════════════════════════════════════════════════════
    # DISPLAY
    # ═══════════════════════════════════════════════════════════════════
    
    def __str__(self) -> str:
        return f"GraphStore(nodes={len(self._nodes)}, edges={len(self._edges)})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def print_summary(self):
        """Print a summary of the graph."""
        stats = self.get_stats()
        print(f"=== Graph Summary ===")
        print(f"Nodes: {stats.node_count}")
        print(f"Edges: {stats.edge_count}")
        print(f"Average Degree: {stats.avg_degree:.2f}")
        print(f"Isolated Nodes: {stats.isolated_nodes}")
        if stats.relation_type_counts:
            print(f"Relations:")
            for rel_type, count in sorted(stats.relation_type_counts.items()):
                print(f"  - {rel_type}: {count}")

