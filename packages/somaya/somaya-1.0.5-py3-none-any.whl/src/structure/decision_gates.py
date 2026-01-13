"""
SOMA Core Decision Gates - What Actually Matters
==============================================

Every signal must feed into a decision gate.
If a score does not affect a gate → it doesn't deserve to exist.

Three core gates:
1. Promote/Demote - Should this pattern be a unit?
2. Trust/Distrust - Should we trust this pattern?
3. Generate/Block - Should we generate this token?
"""

from typing import Dict, Any, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

from src.structure.scoring_utils import bound_score, ConfidenceLevel, to_confidence_bucket


class PromotionDecision(Enum):
    """Decision on whether to promote pattern to unit."""
    DEMOTE = "demote"  # Not a unit
    KEEP = "keep"      # Current status OK
    PROMOTE = "promote"  # Should be a unit


class TrustLevel(Enum):
    """Trust level for a pattern."""
    DISTRUST = "distrust"  # Low trust
    MEDIUM = "medium"      # Medium trust
    TRUST = "trust"        # High trust


class GenerationDecision(Enum):
    """Decision on whether to generate a token."""
    BLOCK = "block"    # Don't generate
    ALLOW = "allow"    # Generate


@dataclass
class GateInputs:
    """Inputs to decision gates."""
    # For Promote/Demote
    frequency: float = 0.0
    stability: float = 0.0
    structural_consistency: float = 0.0
    
    # For Trust/Distrust
    context_diversity: float = 0.0
    relational_consistency: float = 0.0
    
    # For Generate/Block
    fluency_score: float = 0.0
    repetition_risk: float = 0.0
    instability: float = 0.0


class DecisionGates:
    """
    Decision gates that use signals to make actual decisions.
    
    This is where signals become actions.
    """
    
    def __init__(self):
        """Create decision gates."""
        # Thresholds (tunable)
        self.promote_frequency_threshold = 0.6  # High frequency needed
        self.promote_stability_threshold = 0.7   # High stability needed
        self.trust_diversity_threshold = 0.5     # Medium diversity needed
        self.generate_fluency_threshold = 0.6    # Medium fluency needed
        self.generate_repetition_threshold = 0.8  # High repetition = block
    
    def should_be_unit(self, inputs: GateInputs) -> Tuple[PromotionDecision, ConfidenceLevel]:
        """
        Gate A: Promote/Demote
        
        Decides if a pattern should be promoted to a unit.
        
        Uses:
        - frequency (how often it appears)
        - stability (how consistent it is)
        - structural_consistency (how well-formed it is)
        """
        # Bound all inputs
        freq = bound_score(inputs.frequency)
        stability = bound_score(inputs.stability)
        structural = bound_score(inputs.structural_consistency)
        
        # Weighted decision
        promote_score = (freq * 0.4 + stability * 0.4 + structural * 0.2)
        promote_score = bound_score(promote_score)
        
        # Decision
        if promote_score >= self.promote_stability_threshold:
            decision = PromotionDecision.PROMOTE
        elif promote_score < 0.3:
            decision = PromotionDecision.DEMOTE
        else:
            decision = PromotionDecision.KEEP
        
        confidence = to_confidence_bucket(promote_score)
        
        return decision, confidence
    
    def should_trust_pattern(self, inputs: GateInputs) -> Tuple[TrustLevel, ConfidenceLevel]:
        """
        Gate B: Trust/Distrust
        
        Decides how much to trust a pattern.
        
        Uses:
        - context_diversity (appears in diverse contexts)
        - relational_consistency (consistent relationships)
        """
        # Bound all inputs
        diversity = bound_score(inputs.context_diversity)
        consistency = bound_score(inputs.relational_consistency)
        
        # Weighted decision
        trust_score = (diversity * 0.6 + consistency * 0.4)
        trust_score = bound_score(trust_score)
        
        # Decision
        if trust_score >= self.trust_diversity_threshold:
            decision = TrustLevel.TRUST
        elif trust_score < 0.3:
            decision = TrustLevel.DISTRUST
        else:
            decision = TrustLevel.MEDIUM
        
        confidence = to_confidence_bucket(trust_score)
        
        return decision, confidence
    
    def should_generate(self, inputs: GateInputs) -> Tuple[GenerationDecision, ConfidenceLevel]:
        """
        Gate C: Generate/Block
        
        Decides if a token should be generated.
        
        Uses:
        - fluency_score (how fluent it is)
        - repetition_risk (risk of repetition)
        - instability (how unstable the pattern is)
        """
        # Bound all inputs
        fluency = bound_score(inputs.fluency_score)
        repetition = bound_score(inputs.repetition_risk)
        instability = bound_score(inputs.instability)
        
        # Decision logic
        # High repetition = block
        if repetition >= self.generate_repetition_threshold:
            return GenerationDecision.BLOCK, ConfidenceLevel.VERY_HIGH
        
        # Low fluency = block
        if fluency < 0.3:
            return GenerationDecision.BLOCK, ConfidenceLevel.HIGH
        
        # High instability = block
        if instability > 0.7:
            return GenerationDecision.BLOCK, ConfidenceLevel.MEDIUM
        
        # Otherwise allow if fluency is good enough
        if fluency >= self.generate_fluency_threshold:
            return GenerationDecision.ALLOW, to_confidence_bucket(fluency)
        else:
            # Medium fluency = allow but with lower confidence
            return GenerationDecision.ALLOW, ConfidenceLevel.MEDIUM
