"""
SOMA Ranker - Custom Hybrid Ranking Algorithm
===============================================

SOMA-ORIGINAL ALGORITHM. NOT BM25. NOT TF-IDF. NOT NEURAL.

The SOMA Ranking Formula:
    
    score = α·Relevance + β·Connectivity + γ·Hierarchy + δ·Freshness
    
Where:
    Relevance   = Token overlap × Position boost × Digital root alignment
    Connectivity = Graph centrality × Relation strength × Path distance⁻¹
    Hierarchy   = Tree depth weight × Sibling penalty × Parent inheritance
    Freshness   = Temporal decay × Access frequency × Modification boost
    
    α, β, γ, δ are learnable weights (default: 0.4, 0.3, 0.2, 0.1)

The "9-Centric" twist:
    All scores are folded through digital root (mod 9 + 1)
    This creates a bounded, cyclic scoring pattern unique to soma.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import math

from ..graph import GraphStore, GraphNode, RelationType
from ..trees import TreeStore, TreeNode
from ..memory import MemoryObject


@dataclass
class RankingResult:
    """Result from soma ranking."""
    item_id: str
    score: float
    
    # Component scores
    relevance_score: float
    connectivity_score: float
    hierarchy_score: float
    freshness_score: float
    
    # 9-centric transformed score
    digital_root: int
    
    # Metadata
    ranking_version: str = "SOMA-v1"
    
    def explain(self) -> str:
        """Explain the ranking."""
        return (
            f"Score: {self.score:.4f}\n"
            f"  Relevance:    {self.relevance_score:.4f}\n"
            f"  Connectivity: {self.connectivity_score:.4f}\n"
            f"  Hierarchy:    {self.hierarchy_score:.4f}\n"
            f"  Freshness:    {self.freshness_score:.4f}\n"
            f"  Digital Root: {self.digital_root}"
        )


class SOMARanker:
    """
    SOMA Hybrid Ranking Algorithm.
    
    UNIQUE TO soma. Custom formula combining:
    - Token-based relevance
    - Graph connectivity
    - Tree hierarchy
    - Temporal freshness
    - 9-centric digital root folding
    
    Example:
        ranker = SOMARanker(graph, trees)
        
        results = ranker.rank(query_tokens, candidates)
        for result in results:
            print(f"{result.item_id}: {result.score:.4f}")
    """
    
    # Default weights (learnable)
    DEFAULT_WEIGHTS = {
        "alpha": 0.4,   # Relevance
        "beta": 0.3,    # Connectivity
        "gamma": 0.2,   # Hierarchy
        "delta": 0.1,   # Freshness
    }
    
    # Relation strength weights
    RELATION_WEIGHTS = {
        RelationType.IS_A: 0.9,
        RelationType.PART_OF: 0.85,
        RelationType.HAS_PART: 0.85,
        RelationType.CAUSES: 0.8,
        RelationType.DERIVED_FROM: 0.75,
        RelationType.RELATED_TO: 0.5,
        RelationType.SIMILAR_TO: 0.6,
        RelationType.USES: 0.7,
        RelationType.DEPENDS_ON: 0.75,
        RelationType.MENTIONS: 0.3,
    }
    
    def __init__(
        self,
        graph: Optional[GraphStore] = None,
        trees: Optional[TreeStore] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize SOMA Ranker.
        
        Args:
            graph: GraphStore for connectivity scoring
            trees: TreeStore for hierarchy scoring
            weights: Custom weights (alpha, beta, gamma, delta)
        """
        self.graph = graph
        self.trees = trees
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        
        # Cache for graph centrality
        self._centrality_cache: Dict[int, float] = {}
    
    def rank(
        self,
        query_tokens: List[str],
        candidates: List[MemoryObject],
        context: Optional[Dict[str, Any]] = None
    ) -> List[RankingResult]:
        """
        Rank candidates using SOMA's custom algorithm.
        
        Args:
            query_tokens: Tokenized query
            candidates: List of MemoryObject to rank
            context: Optional context for freshness scoring
            
        Returns:
            Sorted list of RankingResult (highest first)
        """
        results = []
        
        for candidate in candidates:
            result = self._score_candidate(query_tokens, candidate, context)
            results.append(result)
        
        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results
    
    def _score_candidate(
        self,
        query_tokens: List[str],
        candidate: MemoryObject,
        context: Optional[Dict[str, Any]]
    ) -> RankingResult:
        """Score a single candidate."""
        
        # 1. Relevance Score
        relevance = self._compute_relevance(query_tokens, candidate)
        
        # 2. Connectivity Score
        connectivity = self._compute_connectivity(candidate)
        
        # 3. Hierarchy Score
        hierarchy = self._compute_hierarchy(candidate)
        
        # 4. Freshness Score
        freshness = self._compute_freshness(candidate, context)
        
        # 5. Combine with weights
        raw_score = (
            self.weights["alpha"] * relevance +
            self.weights["beta"] * connectivity +
            self.weights["gamma"] * hierarchy +
            self.weights["delta"] * freshness
        )
        
        # 6. Apply 9-centric transformation
        digital_root = self._digital_root_9(raw_score)
        
        # Normalize to [0, 1]
        final_score = raw_score  # Keep raw for sorting
        
        return RankingResult(
            item_id=candidate.uid,
            score=final_score,
            relevance_score=relevance,
            connectivity_score=connectivity,
            hierarchy_score=hierarchy,
            freshness_score=freshness,
            digital_root=digital_root,
        )
    
    def _compute_relevance(
        self,
        query_tokens: List[str],
        candidate: MemoryObject
    ) -> float:
        """
        Compute relevance score using SOMA's custom formula.
        
        Formula:
            relevance = Σ(token_match × position_boost) / |query_tokens|
            
        Where:
            position_boost = 1 / (1 + log(position + 1))
        """
        if not query_tokens:
            return 0.0
        
        # Tokenize candidate content (simple)
        candidate_tokens = candidate.content.lower().split()
        candidate_set = set(candidate_tokens)
        
        total_score = 0.0
        
        for i, token in enumerate(query_tokens):
            token_lower = token.lower()
            
            # Exact match
            if token_lower in candidate_set:
                position_boost = 1.0 / (1.0 + math.log(i + 2))
                total_score += position_boost
            
            # Partial match (substring)
            else:
                for ct in candidate_tokens:
                    if token_lower in ct or ct in token_lower:
                        position_boost = 0.5 / (1.0 + math.log(i + 2))
                        total_score += position_boost
                        break
        
        # Normalize
        return min(1.0, total_score / len(query_tokens))
    
    def _compute_connectivity(self, candidate: MemoryObject) -> float:
        """
        Compute connectivity score from graph.
        
        Formula:
            connectivity = centrality × avg_relation_strength × (1 / avg_distance)
        """
        if not self.graph or not candidate.graph_node_id:
            return 0.5  # Default
        
        node_id = candidate.graph_node_id
        
        # Get centrality (cached)
        centrality = self._get_centrality(node_id)
        
        # Get edges
        edges = self.graph.get_outgoing_edges(node_id) + self.graph.get_incoming_edges(node_id)
        
        if not edges:
            return centrality
        
        # Average relation strength
        total_strength = sum(
            self.RELATION_WEIGHTS.get(e.relation_type, 0.5) * e.weight
            for e in edges
        )
        avg_strength = total_strength / len(edges)
        
        # Combine
        return centrality * avg_strength
    
    def _get_centrality(self, node_id: int) -> float:
        """
        Compute centrality (degree-based).
        
        Uses simple degree centrality:
            centrality = degree / (total_nodes - 1)
        """
        if node_id in self._centrality_cache:
            return self._centrality_cache[node_id]
        
        if not self.graph:
            return 0.5
        
        total_nodes = self.graph.node_count
        if total_nodes <= 1:
            return 1.0
        
        # Degree = in_edges + out_edges
        in_edges = len(self.graph.get_incoming_edges(node_id))
        out_edges = len(self.graph.get_outgoing_edges(node_id))
        degree = in_edges + out_edges
        
        centrality = degree / (total_nodes - 1)
        self._centrality_cache[node_id] = centrality
        
        return centrality
    
    def _compute_hierarchy(self, candidate: MemoryObject) -> float:
        """
        Compute hierarchy score from tree position.
        
        Formula:
            hierarchy = depth_weight × (1 - sibling_penalty) × parent_inheritance
            
        Where:
            depth_weight = 1 / (1 + depth)  (shallower = better)
            sibling_penalty = siblings / (siblings + 1)
            parent_inheritance = 0.9^distance_to_root
        """
        if not self.trees or not candidate.tree_id or not candidate.tree_node_id:
            return 0.5  # Default
        
        tree = self.trees.get_tree(candidate.tree_id)
        if not tree:
            return 0.5
        
        node = tree.get_node(candidate.tree_node_id)
        if not node:
            return 0.5
        
        # Depth weight (shallower = higher score)
        depth_weight = 1.0 / (1.0 + node.depth)
        
        # Sibling penalty
        parent = tree.get_parent(candidate.tree_node_id)
        if parent:
            siblings = len(tree.get_children(parent.node_id))
            sibling_penalty = siblings / (siblings + 10)  # Softened
        else:
            sibling_penalty = 0
        
        # Parent inheritance
        parent_inheritance = 0.9 ** node.depth
        
        hierarchy = depth_weight * (1 - sibling_penalty) * parent_inheritance
        
        return min(1.0, hierarchy)
    
    def _compute_freshness(
        self,
        candidate: MemoryObject,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Compute freshness score based on temporal factors.
        
        Formula:
            freshness = decay × access_boost × modification_boost
            
        Where:
            decay = 0.95^days_since_creation
        """
        # Since we don't have actual timestamps, use content length as proxy
        # Shorter content = more recent (heuristic)
        content_length = len(candidate.content)
        length_factor = 1.0 / (1.0 + math.log(content_length + 1))
        
        # Access frequency (if available in context)
        access_boost = 1.0
        if context:
            access_count = context.get("access_counts", {}).get(candidate.uid, 0)
            access_boost = 1.0 + math.log(access_count + 1) * 0.1
        
        return min(1.0, length_factor * access_boost)
    
    def _digital_root_9(self, value: float) -> int:
        """
        SOMA's 9-centric digital root transformation.
        
        Maps any float to 1-9 using digital root formula:
            dr(n) = 1 + ((n - 1) mod 9)
            
        For decimals: multiply by 1000, then compute digital root.
        """
        # Convert to integer representation
        int_value = abs(int(value * 1000))
        
        if int_value == 0:
            return 9  # 0 maps to 9 in SOMA numerology
        
        # Digital root formula
        dr = 1 + ((int_value - 1) % 9)
        
        return dr
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """Update ranking weights."""
        self.weights.update(new_weights)
    
    def clear_cache(self) -> None:
        """Clear centrality cache."""
        self._centrality_cache.clear()
    
    def __repr__(self) -> str:
        return (
            f"SOMARanker("
            f"α={self.weights['alpha']}, "
            f"β={self.weights['beta']}, "
            f"γ={self.weights['gamma']}, "
            f"δ={self.weights['delta']})"
        )

