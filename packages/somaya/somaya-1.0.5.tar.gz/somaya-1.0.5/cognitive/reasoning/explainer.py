"""
Explainer - Generate human-readable explanations.

Converts reasoning paths and query results into
clear, understandable explanations.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..graph import GraphNode, GraphEdge, RelationType
from ..trees import TreeNode
from ..memory import MemoryObject


@dataclass
class Explanation:
    """
    A structured explanation.
    
    Attributes:
        summary: One-line summary
        details: Full explanation
        evidence: Supporting facts
        confidence: How confident (0-1)
    """
    summary: str
    details: str = ""
    evidence: List[str] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "details": self.details,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown format."""
        lines = [f"## {self.summary}", ""]
        
        if self.details:
            lines.append(self.details)
            lines.append("")
        
        if self.evidence:
            lines.append("**Evidence:**")
            for item in self.evidence:
                lines.append(f"- {item}")
            lines.append("")
        
        lines.append(f"*Confidence: {self.confidence:.0%}*")
        
        return "\n".join(lines)


class Explainer:
    """
    Generate explanations for reasoning results.
    
    Example:
        explainer = Explainer()
        
        # Explain a path
        explanation = explainer.explain_path(path)
        
        # Explain a relationship
        explanation = explainer.explain_relation(obj1, obj2, relation)
        
        # Explain hierarchy
        explanation = explainer.explain_hierarchy(tree_path)
    """
    
    # Human-readable relation descriptions
    RELATION_TEMPLATES = {
        RelationType.IS_A: "{subject} is a type of {object}",
        RelationType.PART_OF: "{subject} is part of {object}",
        RelationType.HAS_PART: "{subject} contains {object}",
        RelationType.CAUSES: "{subject} causes {object}",
        RelationType.CAUSED_BY: "{subject} is caused by {object}",
        RelationType.RELATED_TO: "{subject} is related to {object}",
        RelationType.SIMILAR_TO: "{subject} is similar to {object}",
        RelationType.OPPOSITE_OF: "{subject} is opposite of {object}",
        RelationType.PRECEDES: "{subject} comes before {object}",
        RelationType.FOLLOWS: "{subject} comes after {object}",
        RelationType.DERIVED_FROM: "{subject} is derived from {object}",
        RelationType.INSTANCE_OF: "{subject} is an instance of {object}",
        RelationType.CONTAINS: "{subject} contains {object}",
        RelationType.BELONGS_TO: "{subject} belongs to {object}",
        RelationType.USES: "{subject} uses {object}",
        RelationType.USED_BY: "{subject} is used by {object}",
        RelationType.DEPENDS_ON: "{subject} depends on {object}",
    }
    
    def explain_path(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge]
    ) -> Explanation:
        """
        Explain a reasoning path through the graph.
        
        Args:
            nodes: Nodes in the path
            edges: Edges connecting nodes
            
        Returns:
            Explanation of the path
        """
        if not nodes:
            return Explanation(
                summary="No path found",
                confidence=0.0
            )
        
        if len(nodes) == 1:
            return Explanation(
                summary=f"Direct match: {nodes[0].text}",
                confidence=1.0
            )
        
        # Build step-by-step explanation
        steps = []
        evidence = []
        
        for i, edge in enumerate(edges):
            if i + 1 < len(nodes):
                subject = nodes[i].text
                obj = nodes[i + 1].text
                relation = edge.relation_type
                
                template = self.RELATION_TEMPLATES.get(
                    relation,
                    "{subject} --{relation}--> {object}"
                )
                
                step = template.format(
                    subject=subject,
                    object=obj,
                    relation=relation.value
                )
                steps.append(step)
                evidence.append(f"{subject} → {obj}")
        
        # Create summary
        start = nodes[0].text
        end = nodes[-1].text
        summary = f"Path from '{start}' to '{end}' ({len(edges)} steps)"
        
        # Confidence decreases with path length
        confidence = max(0.5, 1.0 - (len(edges) * 0.1))
        
        return Explanation(
            summary=summary,
            details="\n".join(f"{i+1}. {step}" for i, step in enumerate(steps)),
            evidence=evidence,
            confidence=confidence
        )
    
    def explain_relation(
        self,
        subject: MemoryObject,
        obj: MemoryObject,
        relation: RelationType
    ) -> Explanation:
        """
        Explain a single relationship.
        
        Args:
            subject: Source object
            obj: Target object
            relation: Relationship type
            
        Returns:
            Explanation of the relationship
        """
        template = self.RELATION_TEMPLATES.get(
            relation,
            "{subject} is connected to {object}"
        )
        
        description = template.format(
            subject=subject.content,
            object=obj.content
        )
        
        return Explanation(
            summary=description,
            details=f"Relationship: {relation.value}",
            evidence=[
                f"Subject: {subject.content}",
                f"Object: {obj.content}",
            ],
            confidence=1.0
        )
    
    def explain_hierarchy(
        self,
        tree_nodes: List[TreeNode]
    ) -> Explanation:
        """
        Explain a hierarchical path.
        
        Args:
            tree_nodes: Nodes from root to target
            
        Returns:
            Explanation of the hierarchy
        """
        if not tree_nodes:
            return Explanation(
                summary="No hierarchy found",
                confidence=0.0
            )
        
        # Build path string
        path_str = " > ".join(n.content for n in tree_nodes)
        
        # Build level descriptions
        levels = []
        for i, node in enumerate(tree_nodes):
            indent = "  " * i
            levels.append(f"{indent}└─ {node.content}")
        
        target = tree_nodes[-1]
        depth = target.depth
        
        return Explanation(
            summary=f"'{target.content}' at depth {depth}",
            details="Hierarchy:\n" + "\n".join(levels),
            evidence=[path_str],
            confidence=1.0
        )
    
    def explain_search_results(
        self,
        results: List[MemoryObject],
        query: str
    ) -> Explanation:
        """
        Explain search results.
        
        Args:
            results: List of matching objects
            query: Original search query
            
        Returns:
            Explanation of results
        """
        if not results:
            return Explanation(
                summary=f"No results found for '{query}'",
                confidence=0.0
            )
        
        evidence = [
            f"• {obj.content[:50]}{'...' if len(obj.content) > 50 else ''}"
            for obj in results[:5]
        ]
        
        more = len(results) - 5
        if more > 0:
            evidence.append(f"...and {more} more")
        
        return Explanation(
            summary=f"Found {len(results)} results for '{query}'",
            details=f"Top matches contain text related to '{query}'",
            evidence=evidence,
            confidence=min(1.0, len(results) / 10)
        )
    
    def explain_comparison(
        self,
        obj1: MemoryObject,
        obj2: MemoryObject,
        similarities: List[str],
        differences: List[str]
    ) -> Explanation:
        """
        Explain comparison between two objects.
        
        Args:
            obj1: First object
            obj2: Second object
            similarities: List of similarities
            differences: List of differences
            
        Returns:
            Explanation of comparison
        """
        summary = f"Comparing '{obj1.content[:30]}' and '{obj2.content[:30]}'"
        
        parts = []
        if similarities:
            parts.append("**Similarities:**")
            for s in similarities:
                parts.append(f"- {s}")
        
        if differences:
            parts.append("\n**Differences:**")
            for d in differences:
                parts.append(f"- {d}")
        
        return Explanation(
            summary=summary,
            details="\n".join(parts),
            evidence=similarities + differences,
            confidence=1.0
        )
    
    def __repr__(self) -> str:
        return "Explainer()"
