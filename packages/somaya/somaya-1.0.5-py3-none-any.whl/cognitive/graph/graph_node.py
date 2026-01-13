"""
GraphNode: A node in SOMA's knowledge graph.

Each node represents a piece of knowledge (token, concept, entity, etc.)
and can be connected to other nodes via edges.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Set
from datetime import datetime


@dataclass
class GraphNode:
    """
    A node in the knowledge graph.
    
    Design Principles:
    - node_id: Uses TokenRecord.uid for deterministic identity
    - text: The content/label of this node
    - node_type: Category (token, entity, concept, document, etc.)
    - properties: Flexible key-value storage for metadata
    
    Memory footprint: ~200 bytes per node (excluding properties)
    
    Example:
        >>> node = GraphNode(node_id=12345, text="machine learning")
        >>> node.node_type = "concept"
        >>> node.properties["domain"] = "AI"
    """
    
    # === IDENTITY ===
    node_id: int                          # Unique ID (from TokenRecord.uid)
    text: str                             # Content/label
    
    # === CLASSIFICATION ===
    node_type: str = "token"              # token, entity, concept, document, event
    
    # === PROPERTIES ===
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # === METADATA ===
    stream: str = "word"                  # Which tokenizer stream (word, subword, etc.)
    confidence: float = 1.0               # Confidence score (0.0 to 1.0)
    created_at: datetime = field(default_factory=datetime.now)
    
    # === GRAPH CONNECTIVITY ===
    # These are managed by GraphStore, not set directly
    _outgoing_edge_ids: Set[int] = field(default_factory=set, repr=False)
    _incoming_edge_ids: Set[int] = field(default_factory=set, repr=False)
    
    # ═══════════════════════════════════════════════════════════════
    # MAGIC METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def __hash__(self) -> int:
        """Hash by node_id for use in sets/dicts."""
        return self.node_id
    
    def __eq__(self, other) -> bool:
        """Two nodes are equal if they have the same node_id."""
        if isinstance(other, GraphNode):
            return self.node_id == other.node_id
        return False
    
    def __str__(self) -> str:
        return f"GraphNode({self.node_id}: '{self.text}')"
    
    def __repr__(self) -> str:
        return f"GraphNode(node_id={self.node_id}, text='{self.text}', type='{self.node_type}')"
    
    # ═══════════════════════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════════════════════
    
    @property
    def degree(self) -> int:
        """Total number of connections (in + out)."""
        return len(self._outgoing_edge_ids) + len(self._incoming_edge_ids)
    
    @property
    def out_degree(self) -> int:
        """Number of outgoing edges."""
        return len(self._outgoing_edge_ids)
    
    @property
    def in_degree(self) -> int:
        """Number of incoming edges."""
        return len(self._incoming_edge_ids)
    
    @property
    def is_isolated(self) -> bool:
        """True if node has no connections."""
        return self.degree == 0
    
    # ═══════════════════════════════════════════════════════════════
    # SERIALIZATION
    # ═══════════════════════════════════════════════════════════════
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize node to dictionary.
        
        Does NOT include edge IDs (those are managed by GraphStore).
        """
        return {
            "node_id": self.node_id,
            "text": self.text,
            "node_type": self.node_type,
            "properties": self.properties,
            "stream": self.stream,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphNode":
        """Create node from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        return cls(
            node_id=int(data["node_id"]),
            text=str(data["text"]),
            node_type=data.get("node_type", "token"),
            properties=data.get("properties", {}),
            stream=data.get("stream", "word"),
            confidence=float(data.get("confidence", 1.0)),
            created_at=created_at
        )
    
    # ═══════════════════════════════════════════════════════════════
    # FACTORY METHODS
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def from_token(cls, token) -> "GraphNode":
        """
        Create GraphNode from a SOMA TokenRecord.
        
        This bridges src's TokenRecord to SOMA_cognitive's GraphNode.
        
        Args:
            token: A TokenRecord from src.core.core_tokenizer
        
        Returns:
            GraphNode with data from the token
        """
        return cls(
            node_id=getattr(token, 'uid', hash(str(token))),
            text=getattr(token, 'text', str(token)),
            node_type="token",
            stream=getattr(token, 'stream', 'word'),
            properties={
                "content_id": getattr(token, 'content_id', None),
                "frontend": getattr(token, 'frontend', None),
                "backend_huge": getattr(token, 'backend_huge', None),
                "index": getattr(token, 'index', None),
                "global_id": getattr(token, 'global_id', None),
            }
        )
    
    @classmethod
    def create_concept(cls, concept_id: int, name: str, **properties) -> "GraphNode":
        """
        Factory method for creating concept nodes.
        
        Args:
            concept_id: Unique ID for the concept
            name: Name of the concept
            **properties: Additional properties
        
        Returns:
            GraphNode with node_type="concept"
        """
        return cls(
            node_id=concept_id,
            text=name,
            node_type="concept",
            properties=properties
        )
    
    @classmethod
    def create_entity(cls, entity_id: int, name: str, entity_type: str = "unknown", **properties) -> "GraphNode":
        """
        Factory method for creating entity nodes.
        
        Args:
            entity_id: Unique ID for the entity
            name: Name of the entity
            entity_type: Type of entity (person, place, organization, etc.)
            **properties: Additional properties
        
        Returns:
            GraphNode with node_type="entity"
        """
        props = {"entity_type": entity_type}
        props.update(properties)
        
        return cls(
            node_id=entity_id,
            text=name,
            node_type="entity",
            properties=props
        )

