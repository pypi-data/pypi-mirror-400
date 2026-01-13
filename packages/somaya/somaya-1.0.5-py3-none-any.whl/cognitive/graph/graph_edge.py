"""
GraphEdge: A directed edge in SOMA's knowledge graph.

Represents a typed relationship between two nodes.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RelationType(Enum):
    """
    Standard relation types for the knowledge graph.
    
    Categories:
    - Hierarchical: IS_A, PART_OF, HAS_PART
    - Causal: CAUSES, ENABLES, PREVENTS
    - Temporal: PRECEDES, FOLLOWS
    - Semantic: RELATED_TO, SIMILAR_TO, OPPOSITE_OF
    - Reference: MENTIONS, DEFINES
    """
    
    # === HIERARCHICAL ===
    IS_A = "is_a"              # Dog IS_A Animal (type/class)
    PART_OF = "part_of"        # Wheel PART_OF Car (composition)
    HAS_PART = "has_part"      # Car HAS_PART Wheel (inverse of part_of)
    INSTANCE_OF = "instance_of" # Fido INSTANCE_OF Dog (instance/type)
    
    # === CAUSAL ===
    CAUSES = "causes"          # Rain CAUSES Wet
    CAUSED_BY = "caused_by"    # Wet CAUSED_BY Rain
    ENABLES = "enables"        # Key ENABLES Unlock
    PREVENTS = "prevents"      # Lock PREVENTS Entry
    
    # === TEMPORAL ===
    PRECEDES = "precedes"      # Login PRECEDES Dashboard (comes before)
    FOLLOWS = "follows"        # Dashboard FOLLOWS Login (comes after)
    
    # === SEMANTIC ===
    RELATED_TO = "related_to"  # General association
    SIMILAR_TO = "similar_to"  # Semantic similarity
    OPPOSITE_OF = "opposite_of" # Antonym relationship
    DERIVED_FROM = "derived_from" # Summary DERIVED_FROM Document
    
    # === REFERENCE ===
    MENTIONS = "mentions"      # Article MENTIONS Person
    DEFINES = "defines"        # Definition DEFINES Term
    CONTAINS = "contains"      # Document CONTAINS Section
    BELONGS_TO = "belongs_to"  # Item BELONGS_TO Category
    
    # === FUNCTIONAL ===
    USES = "uses"              # System USES Component
    USED_BY = "used_by"        # Component USED_BY System
    DEPENDS_ON = "depends_on"  # Module DEPENDS_ON Library
    
    # === CUSTOM ===
    CUSTOM = "custom"          # User-defined relationship


# Mapping for creating reverse edges
REVERSE_RELATION_MAP = {
    RelationType.IS_A: RelationType.HAS_PART,
    RelationType.PART_OF: RelationType.HAS_PART,
    RelationType.HAS_PART: RelationType.PART_OF,
    RelationType.CAUSES: RelationType.CAUSED_BY,
    RelationType.CAUSED_BY: RelationType.CAUSES,
    RelationType.PRECEDES: RelationType.FOLLOWS,
    RelationType.FOLLOWS: RelationType.PRECEDES,
    RelationType.CONTAINS: RelationType.PART_OF,
}


@dataclass
class GraphEdge:
    """
    A directed edge from source node to target node.
    
    Design Principles:
    - edge_id: Unique identifier for this edge
    - source_id: The node this edge starts from
    - target_id: The node this edge points to
    - relation_type: What kind of relationship
    - weight: Strength/confidence (0.0 to 1.0)
    - evidence: Why this edge exists
    
    Memory footprint: ~150 bytes per edge
    
    Example:
        >>> edge = GraphEdge(
        ...     edge_id=1,
        ...     source_id=100,
        ...     target_id=200,
        ...     relation_type=RelationType.IS_A
        ... )
        >>> edge.weight = 0.9
        >>> edge.evidence = "pattern: 'X is a Y'"
    """
    
    # === IDENTITY ===
    edge_id: int                          # Unique edge identifier
    source_id: int                        # Source node's node_id
    target_id: int                        # Target node's node_id
    relation_type: RelationType           # Type of relationship
    
    # === PROPERTIES ===
    weight: float = 1.0                   # Strength (0.0 to 1.0)
    evidence: str = ""                    # Why this edge exists
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # === METADATA ===
    created_at: datetime = field(default_factory=datetime.now)
    
    # ═══════════════════════════════════════════════════════════════
    # MAGIC METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def __hash__(self) -> int:
        """Hash by edge_id for use in sets/dicts."""
        return self.edge_id
    
    def __eq__(self, other) -> bool:
        """Two edges are equal if they have the same edge_id."""
        if isinstance(other, GraphEdge):
            return self.edge_id == other.edge_id
        return False
    
    def __str__(self) -> str:
        return f"Edge({self.source_id} --[{self.relation_type.value}]--> {self.target_id})"
    
    def __repr__(self) -> str:
        return f"GraphEdge(edge_id={self.edge_id}, {self.source_id}--{self.relation_type.value}-->{self.target_id})"
    
    # ═══════════════════════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════════════════════
    
    @property
    def is_strong(self) -> bool:
        """Is this a strong relationship (weight >= 0.7)?"""
        return self.weight >= 0.7
    
    @property
    def is_weak(self) -> bool:
        """Is this a weak relationship (weight < 0.3)?"""
        return self.weight < 0.3
    
    @property
    def relation_name(self) -> str:
        """Get the relation type as a string."""
        return self.relation_type.value
    
    # ═══════════════════════════════════════════════════════════════
    # METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def reverse(self) -> "GraphEdge":
        """
        Create a reverse edge (target → source) with appropriate relation type.
        
        Returns:
            New GraphEdge with swapped source/target and reversed relation type.
        """
        # Get reverse relation type, or use RELATED_TO as fallback
        new_type = REVERSE_RELATION_MAP.get(self.relation_type, RelationType.RELATED_TO)
        
        # Generate new edge_id
        new_edge_id = hash((self.target_id, self.source_id, new_type.value)) & 0x7FFFFFFF
        
        return GraphEdge(
            edge_id=new_edge_id,
            source_id=self.target_id,
            target_id=self.source_id,
            relation_type=new_type,
            weight=self.weight,
            evidence=f"reverse of edge {self.edge_id}",
            properties=self.properties.copy()
        )
    
    def with_weight(self, new_weight: float) -> "GraphEdge":
        """
        Create a copy with a different weight.
        
        Args:
            new_weight: New weight value (0.0 to 1.0)
        
        Returns:
            New GraphEdge with updated weight
        """
        return GraphEdge(
            edge_id=self.edge_id,
            source_id=self.source_id,
            target_id=self.target_id,
            relation_type=self.relation_type,
            weight=max(0.0, min(1.0, new_weight)),
            evidence=self.evidence,
            properties=self.properties.copy(),
            created_at=self.created_at
        )
    
    # ═══════════════════════════════════════════════════════════════
    # SERIALIZATION
    # ═══════════════════════════════════════════════════════════════
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize edge to dictionary."""
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "weight": self.weight,
            "evidence": self.evidence,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEdge":
        """Create edge from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
        
        return cls(
            edge_id=int(data["edge_id"]),
            source_id=int(data["source_id"]),
            target_id=int(data["target_id"]),
            relation_type=RelationType(data["relation_type"]),
            weight=float(data.get("weight", 1.0)),
            evidence=str(data.get("evidence", "")),
            properties=data.get("properties", {}),
            created_at=created_at
        )
    
    # ═══════════════════════════════════════════════════════════════
    # DISPLAY
    # ═══════════════════════════════════════════════════════════════
    
    def to_readable(self, source_text: str = "", target_text: str = "") -> str:
        """
        Create a human-readable representation.
        
        Args:
            source_text: Text of source node (optional)
            target_text: Text of target node (optional)
        
        Returns:
            Human-readable string like "dog --[is_a]--> animal"
        """
        src = source_text if source_text else f"#{self.source_id}"
        tgt = target_text if target_text else f"#{self.target_id}"
        return f'"{src}" --[{self.relation_type.value}]--> "{tgt}"'

