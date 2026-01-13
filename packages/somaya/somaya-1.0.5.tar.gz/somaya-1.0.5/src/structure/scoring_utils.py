"""
SOMA Core Scoring Utilities - Clean, Bounded, Honest
================================================

Provides bounded scoring (0.0-1.0) with coarse buckets.
No fake precision. No unbounded scores.

Core principle: "If a number does not change a decision, it does not deserve to exist."
"""

from typing import Dict, Any, Tuple
from enum import Enum


class ConfidenceLevel(Enum):
    """Coarse confidence buckets."""
    VERY_LOW = 0.0
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    VERY_HIGH = 1.0


def bound_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Bound a score to [min_val, max_val].
    
    This prevents unbounded scores like 1.249.
    """
    return max(min_val, min(max_val, score))


def to_confidence_bucket(score: float) -> ConfidenceLevel:
    """
    Convert continuous score to coarse bucket.
    
    This makes comparisons meaningful and prevents fake precision.
    """
    score = bound_score(score)
    
    if score < 0.2:
        return ConfidenceLevel.VERY_LOW
    elif score < 0.4:
        return ConfidenceLevel.LOW
    elif score < 0.6:
        return ConfidenceLevel.MEDIUM
    elif score < 0.8:
        return ConfidenceLevel.HIGH
    else:
        return ConfidenceLevel.VERY_HIGH


def aggregate_scores(scores: list[float], weights: list[float] = None) -> float:
    """
    Aggregate multiple scores into one bounded score.
    
    All inputs are bounded to [0.0, 1.0] before aggregation.
    """
    if not scores:
        return 0.0
    
    # Bound all scores
    bounded_scores = [bound_score(s) for s in scores]
    
    # Apply weights if provided
    if weights and len(weights) == len(bounded_scores):
        total_weight = sum(weights)
        if total_weight > 0:
            weighted_sum = sum(s * w for s, w in zip(bounded_scores, weights))
            return bound_score(weighted_sum / total_weight)
    
    # Simple average
    return bound_score(sum(bounded_scores) / len(bounded_scores))


def normalize_to_bucket(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize value from [min_val, max_val] to [0.0, 1.0] bucket.
    
    Returns bounded score in [0.0, 1.0].
    """
    if max_val == min_val:
        return 0.5  # Neutral if no range
    
    normalized = (value - min_val) / (max_val - min_val)
    return bound_score(normalized)


def confidence_to_string(confidence: ConfidenceLevel) -> str:
    """Convert confidence level to human-readable string."""
    mapping = {
        ConfidenceLevel.VERY_LOW: "Very Low",
        ConfidenceLevel.LOW: "Low",
        ConfidenceLevel.MEDIUM: "Medium",
        ConfidenceLevel.HIGH: "High",
        ConfidenceLevel.VERY_HIGH: "Very High"
    }
    return mapping.get(confidence, "Unknown")
