"""
TreeNode - A node in a knowledge tree.

Each node can have:
- One parent (except root)
- Multiple children
- Metadata and links to graph/vector stores
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class TreeNode:
    """
    A node in a hierarchical knowledge tree.
    
    Attributes:
        node_id: Unique identifier
        content: The text/label of this node
        parent_id: ID of parent node (None for root)
        children_ids: List of child node IDs
        depth: How deep in the tree (root = 0)
        metadata: Additional properties
        embedding_ref: Link to vector store
        graph_node_ref: Link to graph store
    """
    node_id: str
    content: str
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    depth: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding_ref: Optional[str] = None
    graph_node_ref: Optional[int] = None
    
    def is_root(self) -> bool:
        """Check if this is a root node."""
        return self.parent_id is None
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children_ids) == 0
    
    def add_child(self, child_id: str) -> None:
        """Add a child node ID."""
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)
    
    def remove_child(self, child_id: str) -> bool:
        """Remove a child node ID. Returns True if removed."""
        if child_id in self.children_ids:
            self.children_ids.remove(child_id)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "content": self.content,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids.copy(),
            "depth": self.depth,
            "metadata": self.metadata.copy(),
            "embedding_ref": self.embedding_ref,
            "graph_node_ref": self.graph_node_ref,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TreeNode":
        """Create from dictionary."""
        return cls(
            node_id=data["node_id"],
            content=data["content"],
            parent_id=data.get("parent_id"),
            children_ids=data.get("children_ids", []),
            depth=data.get("depth", 0),
            metadata=data.get("metadata", {}),
            embedding_ref=data.get("embedding_ref"),
            graph_node_ref=data.get("graph_node_ref"),
        )
    
    def __repr__(self) -> str:
        return f"TreeNode('{self.node_id}': '{self.content}', depth={self.depth})"

