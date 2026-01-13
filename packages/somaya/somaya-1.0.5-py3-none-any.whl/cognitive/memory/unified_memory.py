"""
UnifiedMemory - Central hub connecting all knowledge stores.

This is the main interface for the cognitive system.
It coordinates:
- Vector storage (similarity search)
- Graph storage (relationship queries)
- Tree storage (hierarchical queries)
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json

from .memory_object import MemoryObject
from ..graph import GraphStore, GraphNode, GraphEdge, RelationType
from ..trees import TreeStore, Tree, TreeNode


class UnifiedMemory:
    """
    Central hub for SOMA cognitive system.
    
    Provides unified interface to:
    - Add/retrieve knowledge
    - Link across stores
    - Search with multiple strategies
    
    Example:
        memory = UnifiedMemory()
        
        # Add knowledge
        obj = memory.add("Transformers use attention mechanisms", "fact")
        
        # Link to graph
        memory.link_to_graph(obj.uid)
        
        # Add relationship
        obj2 = memory.add("Attention computes weighted sums", "fact")
        memory.link_to_graph(obj2.uid)
        memory.add_relation(obj.uid, obj2.uid, RelationType.RELATED_TO)
        
        # Search
        results = memory.search_by_content("how attention works")
    """
    
    def __init__(self):
        """Initialize unified memory with all stores."""
        # Core storage
        self.objects: Dict[str, MemoryObject] = {}
        
        # Sub-stores
        self.graph = GraphStore()
        self.trees = TreeStore()
        
        # Index for fast lookup
        self._content_index: Dict[str, str] = {}  # content_hash -> uid
        
        # Auto-increment for graph node IDs
        self._next_graph_id = 1
    
    def add(
        self,
        content: str,
        content_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
        auto_link_graph: bool = False
    ) -> MemoryObject:
        """
        Add a new memory object.
        
        Args:
            content: The text content
            content_type: Type (fact, concept, entity, event)
            metadata: Additional properties
            auto_link_graph: If True, automatically create graph node
            
        Returns:
            The created MemoryObject
        """
        # Check for duplicates
        content_hash = MemoryObject.generate_uid(content)
        if content_hash in self._content_index:
            existing_uid = self._content_index[content_hash]
            return self.objects[existing_uid]
        
        # Create object
        obj = MemoryObject.create(content, content_type, metadata)
        self.objects[obj.uid] = obj
        self._content_index[content_hash] = obj.uid
        
        # Auto-link to graph if requested
        if auto_link_graph:
            self.link_to_graph(obj.uid)
        
        return obj
    
    def get(self, uid: str) -> Optional[MemoryObject]:
        """Get a memory object by UID."""
        return self.objects.get(uid)
    
    def delete(self, uid: str) -> bool:
        """
        Delete a memory object and all its links.
        
        Returns True if deleted.
        """
        obj = self.objects.get(uid)
        if not obj:
            return False
        
        # Remove from graph
        if obj.graph_node_id is not None:
            self.graph.remove_node(obj.graph_node_id)
        
        # Remove from trees
        if obj.tree_node_id and obj.tree_id:
            tree = self.trees.get_tree(obj.tree_id)
            if tree:
                tree.remove_node(obj.tree_node_id)
        
        # Remove from index
        content_hash = MemoryObject.generate_uid(obj.content)
        if content_hash in self._content_index:
            del self._content_index[content_hash]
        
        # Remove object
        del self.objects[uid]
        return True
    
    def link_to_graph(
        self,
        uid: str,
        node_type: Optional[str] = None
    ) -> Optional[int]:
        """
        Link a memory object to the graph store.
        
        Args:
            uid: Memory object UID
            node_type: Graph node type (defaults to content_type)
            
        Returns:
            Graph node ID, or None if failed
        """
        obj = self.objects.get(uid)
        if not obj:
            return None
        
        # Already linked?
        if obj.graph_node_id is not None:
            return obj.graph_node_id
        
        # Create graph node
        node_type = node_type or obj.content_type
        graph_id = self._next_graph_id
        self._next_graph_id += 1
        
        node = GraphNode(
            node_id=graph_id,
            text=obj.content,
            node_type=node_type,
            properties={
                "memory_uid": uid,
                "content_type": obj.content_type,
            }
        )
        
        self.graph.add_node(node)
        obj.graph_node_id = graph_id
        
        return graph_id
    
    def link_to_tree(
        self,
        uid: str,
        tree_id: str,
        parent_node_id: Optional[str] = None,
        node_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Link a memory object to a tree.
        
        Args:
            uid: Memory object UID
            tree_id: Tree to add to
            parent_node_id: Parent node (defaults to root)
            node_id: Custom node ID (defaults to uid)
            
        Returns:
            Tree node ID, or None if failed
        """
        obj = self.objects.get(uid)
        if not obj:
            return None
        
        tree = self.trees.get_tree(tree_id)
        if not tree:
            return None
        
        # Use uid as node_id if not provided
        node_id = node_id or uid
        
        # Add to tree
        tree_node = tree.add_node(
            node_id=node_id,
            content=obj.content,
            parent_id=parent_node_id,
            metadata={"memory_uid": uid}
        )
        
        # Update object
        obj.tree_node_id = tree_node.node_id
        obj.tree_id = tree_id
        
        return tree_node.node_id
    
    def add_relation(
        self,
        from_uid: str,
        to_uid: str,
        relation_type: RelationType,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Add a relationship between two memory objects.
        
        Both objects must be linked to the graph first.
        
        Args:
            from_uid: Source memory object UID
            to_uid: Target memory object UID
            relation_type: Type of relationship
            confidence: Confidence score (0-1)
            metadata: Additional edge properties
            
        Returns:
            The edge_id, or None if failed
        """
        from_obj = self.objects.get(from_uid)
        to_obj = self.objects.get(to_uid)
        
        if not from_obj or not to_obj:
            return None
        
        # Ensure both are linked to graph
        if from_obj.graph_node_id is None:
            self.link_to_graph(from_uid)
        if to_obj.graph_node_id is None:
            self.link_to_graph(to_uid)
        
        # Create edge
        edge_id = self.graph.add_edge(
            source_id=from_obj.graph_node_id,
            target_id=to_obj.graph_node_id,
            relation_type=relation_type,
            weight=confidence,
            evidence=str(metadata) if metadata else ""
        )
        
        return edge_id
    
    def get_relations(self, uid: str) -> List[Tuple[str, RelationType, str]]:
        """
        Get all relations for a memory object.
        
        Returns:
            List of (from_uid, relation_type, to_uid) tuples
        """
        obj = self.objects.get(uid)
        if not obj or obj.graph_node_id is None:
            return []
        
        relations = []
        
        # Get outgoing edges
        outgoing = self.graph.get_outgoing_edges(obj.graph_node_id)
        for edge in outgoing:
            target_node = self.graph.get_node(edge.target_id)
            if target_node:
                target_uid = target_node.properties.get("memory_uid")
                if target_uid:
                    relations.append((uid, edge.relation_type, target_uid))
        
        # Get incoming edges
        incoming = self.graph.get_incoming_edges(obj.graph_node_id)
        for edge in incoming:
            source_node = self.graph.get_node(edge.source_id)
            if source_node:
                source_uid = source_node.properties.get("memory_uid")
                if source_uid:
                    relations.append((source_uid, edge.relation_type, uid))
        
        return relations
    
    def find_related(
        self,
        uid: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 1
    ) -> List[MemoryObject]:
        """
        Find related memory objects through the graph.
        
        Args:
            uid: Starting memory object UID
            relation_types: Filter by relation types (None = all)
            max_depth: How many hops to traverse
            
        Returns:
            List of related MemoryObjects
        """
        obj = self.objects.get(uid)
        if not obj or obj.graph_node_id is None:
            return []
        
        # Traverse graph using neighbors
        visited = {obj.graph_node_id}
        current_level = {obj.graph_node_id}
        
        for _ in range(max_depth):
            next_level = set()
            for node_id in current_level:
                neighbors = self.graph.get_neighbors(node_id, direction="both")
                for neighbor, edge in neighbors:
                    if relation_types and edge.relation_type not in relation_types:
                        continue
                    if neighbor.node_id not in visited:
                        visited.add(neighbor.node_id)
                        next_level.add(neighbor.node_id)
            current_level = next_level
        
        # Convert to memory objects
        results = []
        for node_id in visited:
            if node_id == obj.graph_node_id:
                continue
            node = self.graph.get_node(node_id)
            if node:
                memory_uid = node.properties.get("memory_uid")
                if memory_uid:
                    memory_obj = self.objects.get(memory_uid)
                    if memory_obj:
                        results.append(memory_obj)
        
        return results
    
    def get_tree_path(self, uid: str) -> List[MemoryObject]:
        """
        Get the path from root to this object in its tree.
        
        Returns:
            List of MemoryObjects from root to this object
        """
        obj = self.objects.get(uid)
        if not obj or not obj.tree_node_id or not obj.tree_id:
            return []
        
        tree = self.trees.get_tree(obj.tree_id)
        if not tree:
            return []
        
        path_nodes = tree.get_path_from_root(obj.tree_node_id)
        
        # Convert to memory objects
        results = []
        for tree_node in path_nodes:
            memory_uid = tree_node.metadata.get("memory_uid")
            if memory_uid:
                memory_obj = self.objects.get(memory_uid)
                if memory_obj:
                    results.append(memory_obj)
        
        return results
    
    def search_by_content(
        self,
        query: str,
        limit: int = 10
    ) -> List[MemoryObject]:
        """
        Simple substring search across all objects.
        
        For semantic search, integrate with src's vector store.
        """
        query_lower = query.lower()
        results = []
        
        for obj in self.objects.values():
            if query_lower in obj.content.lower():
                results.append(obj)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for the unified memory."""
        linked_to_graph = sum(
            1 for obj in self.objects.values()
            if obj.is_linked_to_graph()
        )
        linked_to_tree = sum(
            1 for obj in self.objects.values()
            if obj.is_linked_to_tree()
        )
        
        return {
            "total_objects": len(self.objects),
            "linked_to_graph": linked_to_graph,
            "linked_to_tree": linked_to_tree,
            "graph_nodes": self.graph.node_count,
            "graph_edges": self.graph.edge_count,
            "trees": len(self.trees),
        }
    
    def save(self, directory: str) -> None:
        """
        Save all data to a directory.
        
        Creates:
        - objects.json (memory objects)
        - graph.json (graph store)
        - trees.json (tree store)
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save objects
        objects_data = {
            "version": "1.0",
            "next_graph_id": self._next_graph_id,
            "objects": {
                uid: obj.to_dict()
                for uid, obj in self.objects.items()
            }
        }
        with open(path / "objects.json", "w", encoding="utf-8") as f:
            json.dump(objects_data, f, indent=2)
        
        # Save graph
        self.graph.save_json(str(path / "graph.json"))
        
        # Save trees
        self.trees.save(str(path / "trees.json"))
    
    def load(self, directory: str) -> None:
        """Load all data from a directory."""
        path = Path(directory)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Load objects
        objects_path = path / "objects.json"
        if objects_path.exists():
            with open(objects_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self._next_graph_id = data.get("next_graph_id", 1)
            self.objects = {}
            self._content_index = {}
            
            for uid, obj_data in data.get("objects", {}).items():
                obj = MemoryObject.from_dict(obj_data)
                self.objects[uid] = obj
                content_hash = MemoryObject.generate_uid(obj.content)
                self._content_index[content_hash] = uid
        
        # Load graph
        graph_path = path / "graph.json"
        if graph_path.exists():
            self.graph = GraphStore.load_json(str(graph_path))
        
        # Load trees
        trees_path = path / "trees.json"
        if trees_path.exists():
            self.trees.load(str(trees_path))
    
    def clear(self) -> None:
        """Clear all data."""
        self.objects.clear()
        self._content_index.clear()
        self._next_graph_id = 1
        self.graph = GraphStore()
        self.trees = TreeStore()
    
    def __len__(self) -> int:
        return len(self.objects)
    
    def __repr__(self) -> str:
        return f"UnifiedMemory(objects={len(self.objects)}, graph={self.graph.node_count}, trees={len(self.trees)})"
