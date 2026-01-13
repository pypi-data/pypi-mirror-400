"""
QueryEngine - Execute complex queries across knowledge stores.

Combines:
- Content search
- Graph traversal
- Tree hierarchy
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from ..graph import GraphStore, GraphNode, RelationType
from ..trees import TreeStore, Tree, TreeNode
from ..memory import MemoryObject, UnifiedMemory


class QueryType(Enum):
    """Types of queries supported."""
    CONTENT = "content"           # Text search
    RELATION = "relation"         # Find by relationship
    PATH = "path"                 # Find path between
    HIERARCHY = "hierarchy"       # Tree-based
    HYBRID = "hybrid"             # Combined


@dataclass
class QueryResult:
    """
    Result from a query execution.
    
    Attributes:
        objects: List of matching MemoryObjects
        paths: Any reasoning paths found
        explanation: How the result was obtained
        score: Relevance score
    """
    objects: List[MemoryObject] = field(default_factory=list)
    paths: List[Any] = field(default_factory=list)
    explanation: str = ""
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "objects": [obj.to_dict() for obj in self.objects],
            "explanation": self.explanation,
            "score": self.score,
            "metadata": self.metadata,
        }


class QueryEngine:
    """
    Execute complex queries across the knowledge system.
    
    Example:
        engine = QueryEngine(unified_memory)
        
        # Simple content search
        result = engine.search("attention mechanism")
        
        # Find related concepts
        result = engine.find_related(uid, RelationType.IS_A)
        
        # Get hierarchy
        result = engine.get_hierarchy(uid, "concepts")
        
        # Combined query
        result = engine.query({
            "content": "attention",
            "relation": RelationType.RELATED_TO,
            "tree": "concepts"
        })
    """
    
    def __init__(self, memory: UnifiedMemory):
        """
        Initialize QueryEngine.
        
        Args:
            memory: The UnifiedMemory instance to query
        """
        self.memory = memory
    
    def search(
        self,
        query: str,
        limit: int = 10,
        content_types: Optional[List[str]] = None
    ) -> QueryResult:
        """
        Search for objects by content.
        
        Args:
            query: Text to search for
            limit: Maximum results
            content_types: Filter by content type
            
        Returns:
            QueryResult with matching objects
        """
        results = self.memory.search_by_content(query, limit=limit * 2)
        
        # Filter by content type if specified
        if content_types:
            results = [
                obj for obj in results
                if obj.content_type in content_types
            ]
        
        results = results[:limit]
        
        return QueryResult(
            objects=results,
            explanation=f"Found {len(results)} objects matching '{query}'",
            score=1.0 if results else 0.0,
            metadata={"query": query, "type": "content"}
        )
    
    def find_related(
        self,
        uid: str,
        relation_type: Optional[RelationType] = None,
        direction: str = "both",
        limit: int = 10
    ) -> QueryResult:
        """
        Find objects related to a given object.
        
        Args:
            uid: Source object UID
            relation_type: Filter by relation type
            direction: "outgoing", "incoming", or "both"
            limit: Maximum results
            
        Returns:
            QueryResult with related objects
        """
        obj = self.memory.get(uid)
        if not obj:
            return QueryResult(
                explanation=f"Object '{uid}' not found",
                score=0.0
            )
        
        if obj.graph_node_id is None:
            return QueryResult(
                explanation=f"Object '{uid}' not linked to graph",
                score=0.0
            )
        
        results = []
        seen_uids = set()
        
        # Get outgoing relations
        if direction in ["outgoing", "both"]:
            for edge in self.memory.graph.get_edges_from(obj.graph_node_id):
                if relation_type and edge.relation_type != relation_type:
                    continue
                
                target_node = self.memory.graph.get_node(edge.to_id)
                if target_node:
                    target_uid = target_node.properties.get("memory_uid")
                    if target_uid and target_uid not in seen_uids:
                        target_obj = self.memory.get(target_uid)
                        if target_obj:
                            results.append(target_obj)
                            seen_uids.add(target_uid)
        
        # Get incoming relations
        if direction in ["incoming", "both"]:
            for edge in self.memory.graph.get_edges_to(obj.graph_node_id):
                if relation_type and edge.relation_type != relation_type:
                    continue
                
                source_node = self.memory.graph.get_node(edge.from_id)
                if source_node:
                    source_uid = source_node.properties.get("memory_uid")
                    if source_uid and source_uid not in seen_uids:
                        source_obj = self.memory.get(source_uid)
                        if source_obj:
                            results.append(source_obj)
                            seen_uids.add(source_uid)
        
        results = results[:limit]
        
        relation_str = relation_type.value if relation_type else "any relation"
        return QueryResult(
            objects=results,
            explanation=f"Found {len(results)} objects related by '{relation_str}'",
            score=1.0 if results else 0.0,
            metadata={
                "source_uid": uid,
                "relation_type": relation_type.value if relation_type else None,
                "type": "relation"
            }
        )
    
    def get_hierarchy(
        self,
        uid: str,
        tree_id: Optional[str] = None
    ) -> QueryResult:
        """
        Get the hierarchical context for an object.
        
        Args:
            uid: Object UID
            tree_id: Specific tree to check (defaults to object's tree)
            
        Returns:
            QueryResult with path objects and tree structure
        """
        obj = self.memory.get(uid)
        if not obj:
            return QueryResult(
                explanation=f"Object '{uid}' not found",
                score=0.0
            )
        
        # Determine which tree
        tree_id = tree_id or obj.tree_id
        if not tree_id:
            return QueryResult(
                explanation=f"Object '{uid}' not linked to any tree",
                score=0.0
            )
        
        tree = self.memory.trees.get_tree(tree_id)
        if not tree:
            return QueryResult(
                explanation=f"Tree '{tree_id}' not found",
                score=0.0
            )
        
        # Get tree node
        tree_node_id = obj.tree_node_id
        if not tree_node_id:
            return QueryResult(
                explanation=f"Object '{uid}' not linked to tree '{tree_id}'",
                score=0.0
            )
        
        # Get path and related nodes
        path_nodes = tree.get_path_from_root(tree_node_id)
        siblings = tree.get_siblings(tree_node_id)
        
        # Convert to memory objects where possible
        path_objects = []
        for tree_node in path_nodes:
            mem_uid = tree_node.metadata.get("memory_uid")
            if mem_uid:
                mem_obj = self.memory.get(mem_uid)
                if mem_obj:
                    path_objects.append(mem_obj)
        
        sibling_objects = []
        for tree_node in siblings:
            mem_uid = tree_node.metadata.get("memory_uid")
            if mem_uid:
                mem_obj = self.memory.get(mem_uid)
                if mem_obj:
                    sibling_objects.append(mem_obj)
        
        # Build path string
        path_str = " > ".join(n.content for n in path_nodes)
        
        return QueryResult(
            objects=path_objects,
            explanation=f"Hierarchy: {path_str}",
            score=1.0,
            metadata={
                "tree_id": tree_id,
                "path_nodes": [n.node_id for n in path_nodes],
                "siblings": [s.content for s in sibling_objects],
                "depth": path_nodes[-1].depth if path_nodes else 0,
                "type": "hierarchy"
            }
        )
    
    def query(
        self,
        params: Dict[str, Any]
    ) -> QueryResult:
        """
        Execute a combined query.
        
        Args:
            params: Query parameters:
                - content: Text to search for
                - relation: RelationType to filter by
                - tree_id: Tree to search in
                - limit: Max results
                
        Returns:
            Combined QueryResult
        """
        content = params.get("content")
        relation = params.get("relation")
        tree_id = params.get("tree_id")
        limit = params.get("limit", 10)
        
        all_objects = []
        explanations = []
        
        # Content search
        if content:
            content_result = self.search(content, limit=limit)
            all_objects.extend(content_result.objects)
            if content_result.objects:
                explanations.append(content_result.explanation)
        
        # Relation filter (if we have objects and a relation type)
        if relation and all_objects:
            filtered = []
            for obj in all_objects:
                related = self.find_related(obj.uid, relation, limit=5)
                filtered.extend(related.objects)
            
            if filtered:
                all_objects = filtered
                explanations.append(
                    f"Filtered by relation: {relation.value}"
                )
        
        # Tree filter
        if tree_id and all_objects:
            tree_filtered = [
                obj for obj in all_objects
                if obj.tree_id == tree_id
            ]
            if tree_filtered:
                all_objects = tree_filtered
                explanations.append(f"Filtered by tree: {tree_id}")
        
        # Deduplicate
        seen = set()
        unique = []
        for obj in all_objects:
            if obj.uid not in seen:
                seen.add(obj.uid)
                unique.append(obj)
        
        return QueryResult(
            objects=unique[:limit],
            explanation=" | ".join(explanations) if explanations else "No results",
            score=1.0 if unique else 0.0,
            metadata={
                "params": params,
                "type": "hybrid"
            }
        )
    
    def __repr__(self) -> str:
        return f"QueryEngine(memory_objects={len(self.memory)})"

