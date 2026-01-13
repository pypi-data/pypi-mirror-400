"""
MemoryObject - A unified knowledge unit.

Links together:
- Raw content
- Vector embedding reference
- Graph node reference
- Tree node reference

This is the "glue" between all storage systems.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class MemoryObject:
    """
    A unified knowledge object that can be linked to
    vectors, graphs, and trees.
    
    Attributes:
        uid: Unique identifier (hash-based)
        content: The raw text/data
        content_type: Type of content (fact, concept, entity, etc.)
        created_at: Creation timestamp
        metadata: Additional properties
        
        # Cross-store references
        embedding_id: Reference to vector store
        graph_node_id: Reference to graph store
        tree_node_id: Reference to tree store
        tree_id: Which tree the node belongs to
        
        # SOMA-specific
        token_uids: List of SOMA token UIDs
    """
    uid: str
    content: str
    content_type: str = "generic"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Vector store link
    embedding_id: Optional[str] = None
    embedding_vector: Optional[List[float]] = None
    
    # Graph store link
    graph_node_id: Optional[int] = None
    
    # Tree store link
    tree_node_id: Optional[str] = None
    tree_id: Optional[str] = None
    
    # SOMA token references
    token_uids: List[int] = field(default_factory=list)
    
    @staticmethod
    def generate_uid(content: str) -> str:
        """Generate a deterministic UID from content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    
    @classmethod
    def create(
        cls,
        content: str,
        content_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None
    ) -> "MemoryObject":
        """
        Create a new MemoryObject.
        
        Args:
            content: The text content
            content_type: Type (fact, concept, entity, event, etc.)
            metadata: Additional properties
        """
        uid = cls.generate_uid(content)
        return cls(
            uid=uid,
            content=content,
            content_type=content_type,
            metadata=metadata or {}
        )
    
    def is_linked_to_vector(self) -> bool:
        """Check if linked to vector store."""
        return self.embedding_id is not None
    
    def is_linked_to_graph(self) -> bool:
        """Check if linked to graph store."""
        return self.graph_node_id is not None
    
    def is_linked_to_tree(self) -> bool:
        """Check if linked to tree store."""
        return self.tree_node_id is not None and self.tree_id is not None
    
    def link_count(self) -> int:
        """Count how many stores this object is linked to."""
        count = 0
        if self.is_linked_to_vector():
            count += 1
        if self.is_linked_to_graph():
            count += 1
        if self.is_linked_to_tree():
            count += 1
        return count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "uid": self.uid,
            "content": self.content,
            "content_type": self.content_type,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "embedding_id": self.embedding_id,
            "graph_node_id": self.graph_node_id,
            "tree_node_id": self.tree_node_id,
            "tree_id": self.tree_id,
            "token_uids": self.token_uids,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryObject":
        """Create from dictionary."""
        return cls(
            uid=data["uid"],
            content=data["content"],
            content_type=data.get("content_type", "generic"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            metadata=data.get("metadata", {}),
            embedding_id=data.get("embedding_id"),
            graph_node_id=data.get("graph_node_id"),
            tree_node_id=data.get("tree_node_id"),
            tree_id=data.get("tree_id"),
            token_uids=data.get("token_uids", []),
        )
    
    def __repr__(self) -> str:
        links = []
        if self.is_linked_to_vector():
            links.append("vec")
        if self.is_linked_to_graph():
            links.append("graph")
        if self.is_linked_to_tree():
            links.append("tree")
        
        link_str = "+".join(links) if links else "unlinked"
        content_preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        
        return f"MemoryObject('{self.uid[:8]}', '{content_preview}', [{link_str}])"

