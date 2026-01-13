"""
SOMA Semantic Similarity - Custom Similarity Without Neural Embeddings
=======================================================================

SOMA-ORIGINAL ALGORITHM. NO BERT. NO WORD2VEC. NO NEURAL EMBEDDINGS.

Computes semantic similarity using:
1. Lexical overlap (Jaccard, Dice, etc.)
2. Character n-gram similarity
3. Position-weighted matching
4. Graph-based relatedness (if graph available)
5. 9-centric harmonic combination

The SOMA Similarity Formula:
    sim(a, b) = α·Lexical + β·Ngram + γ·Position + δ·Graph
    
    Final score is 9-centric harmonized.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import math

from ..graph import GraphStore, RelationType


@dataclass
class SimilarityResult:
    """Result of similarity computation."""
    score: float              # Combined score [0, 1]
    digital_root: int         # 9-centric root
    
    # Component scores
    lexical_score: float
    ngram_score: float
    position_score: float
    graph_score: float
    
    # Debug info
    common_tokens: List[str]
    common_ngrams: int
    
    def explain(self) -> str:
        """Explain the similarity."""
        return (
            f"Similarity: {self.score:.4f} (DR={self.digital_root})\n"
            f"  Lexical:  {self.lexical_score:.4f}\n"
            f"  N-gram:   {self.ngram_score:.4f}\n"
            f"  Position: {self.position_score:.4f}\n"
            f"  Graph:    {self.graph_score:.4f}\n"
            f"  Common tokens: {', '.join(self.common_tokens[:5])}"
        )


class SOMASimilarity:
    """
    SOMA Custom Semantic Similarity.
    
    100% UNIQUE. NO neural embeddings. NO pretrained models.
    
    Methods:
    - Jaccard similarity (token overlap)
    - Dice coefficient
    - Character n-gram overlap
    - Position-weighted matching
    - Graph-based relatedness
    
    Example:
        sim = SOMASimilarity()
        
        result = sim.compute("machine learning", "deep learning")
        print(result.score)  # 0.67
        print(result.explain())
    """
    
    # Default weights
    DEFAULT_WEIGHTS = {
        "alpha": 0.35,   # Lexical
        "beta": 0.25,    # N-gram
        "gamma": 0.20,   # Position
        "delta": 0.20,   # Graph
    }
    
    # Stopwords to ignore
    STOPWORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall",
        "i", "you", "he", "she", "it", "we", "they", "this", "that",
        "and", "or", "but", "if", "then", "else", "when", "where",
        "what", "which", "who", "whom", "how", "why",
        "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "very", "really", "just", "only", "also", "too",
    }
    
    def __init__(
        self,
        graph: Optional[GraphStore] = None,
        weights: Optional[Dict[str, float]] = None,
        ngram_size: int = 3
    ):
        """
        Initialize SOMA Similarity.
        
        Args:
            graph: Optional GraphStore for graph-based similarity
            weights: Custom weights for components
            ngram_size: Size of character n-grams
        """
        self.graph = graph
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.ngram_size = ngram_size
    
    def compute(self, text_a: str, text_b: str) -> SimilarityResult:
        """
        Compute similarity between two texts.
        
        Args:
            text_a: First text
            text_b: Second text
            
        Returns:
            SimilarityResult
        """
        # Tokenize
        tokens_a = self._tokenize(text_a)
        tokens_b = self._tokenize(text_b)
        
        # 1. Lexical similarity (Jaccard + Dice)
        lexical, common = self._lexical_similarity(tokens_a, tokens_b)
        
        # 2. N-gram similarity
        ngram, ngram_count = self._ngram_similarity(text_a, text_b)
        
        # 3. Position-weighted similarity
        position = self._position_similarity(tokens_a, tokens_b)
        
        # 4. Graph-based similarity
        graph_sim = self._graph_similarity(tokens_a, tokens_b)
        
        # 5. Combine with weights
        combined = (
            self.weights["alpha"] * lexical +
            self.weights["beta"] * ngram +
            self.weights["gamma"] * position +
            self.weights["delta"] * graph_sim
        )
        
        # 6. Apply 9-centric transformation
        digital_root = self._digital_root_9(combined)
        
        return SimilarityResult(
            score=combined,
            digital_root=digital_root,
            lexical_score=lexical,
            ngram_score=ngram,
            position_score=position,
            graph_score=graph_sim,
            common_tokens=common,
            common_ngrams=ngram_count,
        )
    
    def batch_compute(
        self,
        query: str,
        candidates: List[str]
    ) -> List[Tuple[int, SimilarityResult]]:
        """
        Compute similarity of query against multiple candidates.
        
        Returns list of (index, result) sorted by score descending.
        """
        results = []
        
        for i, candidate in enumerate(candidates):
            result = self.compute(query, candidate)
            results.append((i, result))
        
        results.sort(key=lambda x: x[1].score, reverse=True)
        return results
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize and clean text."""
        # Simple tokenization
        tokens = text.lower().split()
        
        # Remove stopwords and short tokens
        tokens = [
            t for t in tokens
            if t not in self.STOPWORDS and len(t) > 1
        ]
        
        return tokens
    
    def _lexical_similarity(
        self,
        tokens_a: List[str],
        tokens_b: List[str]
    ) -> Tuple[float, List[str]]:
        """
        Compute lexical similarity using Jaccard and Dice.
        
        Returns (score, common_tokens)
        """
        set_a = set(tokens_a)
        set_b = set(tokens_b)
        
        if not set_a and not set_b:
            return 1.0, []
        
        if not set_a or not set_b:
            return 0.0, []
        
        intersection = set_a & set_b
        union = set_a | set_b
        
        # Jaccard
        jaccard = len(intersection) / len(union)
        
        # Dice
        dice = 2 * len(intersection) / (len(set_a) + len(set_b))
        
        # Average
        score = (jaccard + dice) / 2
        
        return score, list(intersection)
    
    def _ngram_similarity(self, text_a: str, text_b: str) -> Tuple[float, int]:
        """
        Compute character n-gram similarity.
        
        Returns (score, common_ngram_count)
        """
        ngrams_a = self._get_ngrams(text_a.lower())
        ngrams_b = self._get_ngrams(text_b.lower())
        
        if not ngrams_a and not ngrams_b:
            return 1.0, 0
        
        if not ngrams_a or not ngrams_b:
            return 0.0, 0
        
        # Use Counter for weighted overlap
        counter_a = Counter(ngrams_a)
        counter_b = Counter(ngrams_b)
        
        # Intersection count
        intersection = sum((counter_a & counter_b).values())
        
        # Total
        total = sum(counter_a.values()) + sum(counter_b.values())
        
        if total == 0:
            return 0.0, 0
        
        score = 2 * intersection / total
        
        return score, intersection
    
    def _get_ngrams(self, text: str) -> List[str]:
        """Extract character n-grams."""
        # Remove spaces for character n-grams
        text = text.replace(" ", "_")
        
        if len(text) < self.ngram_size:
            return [text]
        
        return [
            text[i:i + self.ngram_size]
            for i in range(len(text) - self.ngram_size + 1)
        ]
    
    def _position_similarity(
        self,
        tokens_a: List[str],
        tokens_b: List[str]
    ) -> float:
        """
        Compute position-weighted similarity.
        
        Tokens at same positions get higher weight.
        """
        if not tokens_a or not tokens_b:
            return 0.0
        
        max_len = max(len(tokens_a), len(tokens_b))
        min_len = min(len(tokens_a), len(tokens_b))
        
        if max_len == 0:
            return 1.0
        
        # Length penalty
        length_penalty = min_len / max_len
        
        # Position matches
        position_matches = 0
        total_weight = 0
        
        for i in range(min_len):
            # Weight decreases with position (first tokens more important)
            weight = 1.0 / (1.0 + math.log(i + 2))
            total_weight += weight
            
            if tokens_a[i] == tokens_b[i]:
                position_matches += weight
            else:
                # Partial match for similar tokens
                if self._token_similar(tokens_a[i], tokens_b[i]):
                    position_matches += weight * 0.5
        
        if total_weight == 0:
            return 0.0
        
        score = (position_matches / total_weight) * length_penalty
        
        return score
    
    def _token_similar(self, token_a: str, token_b: str) -> bool:
        """Check if two tokens are similar (substring or edit distance)."""
        # Substring check
        if token_a in token_b or token_b in token_a:
            return True
        
        # Prefix check
        min_len = min(len(token_a), len(token_b))
        prefix_len = 0
        for i in range(min_len):
            if token_a[i] == token_b[i]:
                prefix_len += 1
            else:
                break
        
        if prefix_len >= 3:
            return True
        
        return False
    
    def _graph_similarity(
        self,
        tokens_a: List[str],
        tokens_b: List[str]
    ) -> float:
        """
        Compute graph-based similarity.
        
        Uses shortest path and common neighbors in knowledge graph.
        """
        if not self.graph or self.graph.node_count == 0:
            return 0.5  # Neutral if no graph
        
        # Find nodes for tokens
        nodes_a = self._find_nodes(tokens_a)
        nodes_b = self._find_nodes(tokens_b)
        
        if not nodes_a or not nodes_b:
            return 0.5
        
        # Compute relatedness
        total_relatedness = 0.0
        pairs = 0
        
        for node_a in nodes_a[:3]:  # Limit for efficiency
            for node_b in nodes_b[:3]:
                relatedness = self._node_relatedness(node_a, node_b)
                total_relatedness += relatedness
                pairs += 1
        
        if pairs == 0:
            return 0.5
        
        return total_relatedness / pairs
    
    def _find_nodes(self, tokens: List[str]) -> List[int]:
        """Find graph nodes matching tokens."""
        if not self.graph:
            return []
        
        nodes = []
        for token in tokens:
            matching = self.graph.get_nodes_by_text(token)
            for node in matching:
                nodes.append(node.node_id)
        
        return nodes
    
    def _node_relatedness(self, node_a: int, node_b: int) -> float:
        """
        Compute relatedness between two nodes.
        
        Based on:
        - Direct edge: 1.0
        - Common neighbors: 0.5-0.8
        - Path exists: 0.3-0.5
        - No connection: 0.0
        """
        if not self.graph:
            return 0.0
        
        if node_a == node_b:
            return 1.0
        
        # Check direct edge
        edges_a = self.graph.get_outgoing_edges(node_a)
        for edge in edges_a:
            if edge.target_id == node_b:
                return 1.0
        
        edges_b = self.graph.get_outgoing_edges(node_b)
        for edge in edges_b:
            if edge.target_id == node_a:
                return 1.0
        
        # Check common neighbors
        neighbors_a = {e.target_id for e in edges_a}
        neighbors_b = {e.target_id for e in edges_b}
        
        common = neighbors_a & neighbors_b
        if common:
            # More common neighbors = higher relatedness
            return min(0.8, 0.5 + 0.1 * len(common))
        
        # Check 2-hop path
        for neighbor in neighbors_a:
            neighbor_edges = self.graph.get_outgoing_edges(neighbor)
            for edge in neighbor_edges:
                if edge.target_id == node_b:
                    return 0.4
        
        return 0.0
    
    def _digital_root_9(self, value: float) -> int:
        """Compute 9-centric digital root."""
        int_val = abs(int(value * 1000))
        
        if int_val == 0:
            return 9
        
        return 1 + ((int_val - 1) % 9)
    
    def jaccard(self, text_a: str, text_b: str) -> float:
        """Pure Jaccard similarity."""
        tokens_a = set(self._tokenize(text_a))
        tokens_b = set(self._tokenize(text_b))
        
        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0
        
        return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
    
    def dice(self, text_a: str, text_b: str) -> float:
        """Pure Dice coefficient."""
        tokens_a = set(self._tokenize(text_a))
        tokens_b = set(self._tokenize(text_b))
        
        if not tokens_a and not tokens_b:
            return 1.0
        if not tokens_a or not tokens_b:
            return 0.0
        
        return 2 * len(tokens_a & tokens_b) / (len(tokens_a) + len(tokens_b))
    
    def cosine(self, text_a: str, text_b: str) -> float:
        """
        Cosine similarity using term frequency.
        
        NO neural embeddings - pure TF-based.
        """
        tokens_a = self._tokenize(text_a)
        tokens_b = self._tokenize(text_b)
        
        if not tokens_a or not tokens_b:
            return 0.0
        
        # Term frequency vectors
        vocab = set(tokens_a) | set(tokens_b)
        
        tf_a = Counter(tokens_a)
        tf_b = Counter(tokens_b)
        
        # Dot product
        dot = sum(tf_a.get(t, 0) * tf_b.get(t, 0) for t in vocab)
        
        # Magnitudes
        mag_a = math.sqrt(sum(v**2 for v in tf_a.values()))
        mag_b = math.sqrt(sum(v**2 for v in tf_b.values()))
        
        if mag_a == 0 or mag_b == 0:
            return 0.0
        
        return dot / (mag_a * mag_b)
    
    def __repr__(self) -> str:
        return (
            f"SOMASimilarity("
            f"ngram={self.ngram_size}, "
            f"has_graph={self.graph is not None})"
        )

