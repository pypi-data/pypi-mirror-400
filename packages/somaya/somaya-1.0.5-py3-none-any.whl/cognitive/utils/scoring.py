"""
Scoring utilities for ranking explanations and context quality.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import math

from ..reasoning import ReasoningPath, InferredFact, StructuredContext


@dataclass
class Score:
    """A scored item with breakdown."""
    total: float
    breakdown: Dict[str, float]
    
    def __repr__(self):
        return f"Score({self.total:.2f})"


class ExplanationScorer:
    """
    Score explanations based on quality metrics.
    
    Metrics:
    - Path length (shorter = better)
    - Confidence (higher = better)
    - Evidence count (more = better)
    - Contradiction penalty
    
    Example:
        scorer = ExplanationScorer()
        
        score = scorer.score_path(reasoning_path)
        print(f"Path score: {score.total:.2f}")
        
        ranked = scorer.rank_paths(paths)
    """
    
    # Default weights for scoring components
    DEFAULT_WEIGHTS = {
        "path_length": -0.1,      # Penalty per hop
        "confidence": 0.4,         # Bonus for confidence
        "evidence": 0.1,           # Bonus per evidence item
        "rule_quality": 0.2,       # Bonus for strong rules
        "contradiction": -0.5,     # Penalty for contradictions
    }
    
    # Rule quality scores
    RULE_QUALITY = {
        "transitive_is_a": 0.9,
        "transitive_part_of": 0.85,
        "inverse": 0.95,
        "symmetric": 0.9,
        "inherit": 0.8,
        "compose": 0.75,
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize scorer.
        
        Args:
            weights: Custom weights (uses defaults if None)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
    
    def score_path(self, path: ReasoningPath) -> Score:
        """
        Score a reasoning path.
        
        Args:
            path: ReasoningPath to score
            
        Returns:
            Score with breakdown
        """
        breakdown = {}
        
        # Path length penalty
        length_score = len(path.edges) * self.weights["path_length"]
        breakdown["path_length"] = length_score
        
        # Confidence bonus
        if hasattr(path, 'score') and path.score > 0:
            conf_score = (1.0 / path.score) * self.weights["confidence"]
        else:
            conf_score = self.weights["confidence"]
        breakdown["confidence"] = conf_score
        
        # Base score
        total = 1.0 + length_score + conf_score
        
        return Score(total=max(0.0, min(1.0, total)), breakdown=breakdown)
    
    def score_inference(self, fact: InferredFact) -> Score:
        """
        Score an inferred fact.
        
        Args:
            fact: InferredFact to score
            
        Returns:
            Score with breakdown
        """
        breakdown = {}
        
        # Confidence
        conf_score = fact.confidence * self.weights["confidence"]
        breakdown["confidence"] = conf_score
        
        # Depth penalty
        depth_score = fact.depth * self.weights["path_length"]
        breakdown["depth"] = depth_score
        
        # Rule quality
        rule_quality = 0.5  # Default
        for rule_prefix, quality in self.RULE_QUALITY.items():
            if fact.rule_id.startswith(rule_prefix):
                rule_quality = quality
                break
        
        rule_score = rule_quality * self.weights["rule_quality"]
        breakdown["rule_quality"] = rule_score
        
        total = conf_score + depth_score + rule_score
        
        return Score(total=max(0.0, min(1.0, total)), breakdown=breakdown)
    
    def rank_paths(self, paths: List[ReasoningPath]) -> List[tuple]:
        """
        Rank paths by score.
        
        Returns:
            List of (path, score) tuples, highest first
        """
        scored = [(path, self.score_path(path)) for path in paths]
        scored.sort(key=lambda x: -x[1].total)
        return scored
    
    def rank_inferences(self, facts: List[InferredFact]) -> List[tuple]:
        """
        Rank inferences by score.
        
        Returns:
            List of (fact, score) tuples, highest first
        """
        scored = [(fact, self.score_inference(fact)) for fact in facts]
        scored.sort(key=lambda x: -x[1].total)
        return scored


class ContextScorer:
    """
    Score structured context for quality.
    
    Used to assess how good the context is before sending to LLM.
    
    Example:
        scorer = ContextScorer()
        
        score = scorer.score(context)
        
        if score.total < 0.3:
            print("Warning: Low quality context")
    """
    
    def __init__(self):
        self.weights = {
            "facts": 0.3,
            "inferences": 0.25,
            "paths": 0.2,
            "hierarchy": 0.15,
            "contradiction_penalty": 0.3,
        }
    
    def score(self, context: StructuredContext) -> Score:
        """
        Score a structured context.
        
        Args:
            context: StructuredContext to score
            
        Returns:
            Score with breakdown
        """
        breakdown = {}
        
        # Facts score (more facts = better, up to a point)
        fact_count = len(context.relevant_facts)
        fact_score = min(1.0, fact_count / 5) * self.weights["facts"]
        breakdown["facts"] = fact_score
        
        # Inference score
        inf_count = len(context.inferences)
        inf_score = min(1.0, inf_count / 3) * self.weights["inferences"]
        breakdown["inferences"] = inf_score
        
        # Path score
        path_count = len(context.reasoning_paths)
        path_score = min(1.0, path_count / 2) * self.weights["paths"]
        breakdown["paths"] = path_score
        
        # Hierarchy score
        hier_score = (0.5 if context.hierarchy else 0.0) * self.weights["hierarchy"]
        breakdown["hierarchy"] = hier_score
        
        # Contradiction penalty
        cont_count = len(context.contradictions)
        cont_penalty = min(1.0, cont_count * 0.3) * self.weights["contradiction_penalty"]
        breakdown["contradictions"] = -cont_penalty
        
        total = fact_score + inf_score + path_score + hier_score - cont_penalty
        
        return Score(total=max(0.0, min(1.0, total)), breakdown=breakdown)
    
    def assess_quality(self, context: StructuredContext) -> str:
        """
        Get a quality assessment string.
        
        Returns:
            "excellent", "good", "fair", "poor", or "insufficient"
        """
        score = self.score(context)
        
        if score.total >= 0.8:
            return "excellent"
        elif score.total >= 0.6:
            return "good"
        elif score.total >= 0.4:
            return "fair"
        elif score.total >= 0.2:
            return "poor"
        else:
            return "insufficient"

