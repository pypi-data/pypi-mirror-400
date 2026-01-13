"""
SOMA 9-Scorer - 9-Centric Confidence Propagation
==================================================

SOMA-ORIGINAL ALGORITHM. Based on SOMA's 9-centric numerology.

The 9-Centric Philosophy:
    In SOMA, 9 represents completeness and cyclic return.
    All scores, confidences, and weights are folded through digital root.
    
    Digital Root: dr(n) = 1 + ((n - 1) mod 9)
    
    This creates bounded, cyclic, interpretable scores.

Features:
- Confidence propagation through graphs
- Score combination using 9-centric math
- Decay functions based on digital root cycles
- Interpretable scoring (1-9 scale)
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class Score9:
    """
    A 9-centric score.
    
    Contains both raw value and digital root.
    """
    raw: float          # Original value
    digital_root: int   # 1-9 digital root
    cycle: int          # Which 9-cycle (0, 1, 2, ...)
    
    @property
    def combined(self) -> float:
        """Combine cycle and digital root for full value."""
        return self.cycle * 9 + self.digital_root
    
    def __repr__(self) -> str:
        return f"Score9(raw={self.raw:.4f}, dr={self.digital_root}, cycle={self.cycle})"


class SOMA9Scorer:
    """
    9-Centric Scoring System.
    
    UNIQUE TO soma. All operations use 9-centric math.
    
    Key Operations:
    - to_9: Convert any number to 9-scale
    - combine_9: Combine multiple scores using 9-math
    - propagate_9: Propagate confidence through chain
    - decay_9: Apply 9-centric decay
    
    Example:
        scorer = SOMA9Scorer()
        
        # Convert to 9-scale
        score = scorer.to_9(0.85)
        print(score.digital_root)  # 8
        
        # Combine scores
        combined = scorer.combine_9([0.8, 0.6, 0.9])
        print(combined.digital_root)  # Result in 1-9
    """
    
    # 9-centric constants
    CYCLE_BASE = 9
    MAX_CONFIDENCE = 1.0
    MIN_CONFIDENCE = 0.0
    
    # Digital root meanings (SOMA numerology)
    ROOT_MEANINGS = {
        1: "origin",       # Beginning, source
        2: "duality",      # Opposition, comparison
        3: "synthesis",    # Combination, creation
        4: "structure",    # Foundation, stability
        5: "change",       # Transformation, adaptation
        6: "balance",      # Harmony, equilibrium
        7: "analysis",     # Investigation, depth
        8: "power",        # Strength, confidence
        9: "completion",   # Fullness, cycle end
    }
    
    def __init__(self, precision: int = 4):
        """
        Initialize 9-Scorer.
        
        Args:
            precision: Decimal precision for raw scores
        """
        self.precision = precision
    
    def to_9(self, value: float) -> Score9:
        """
        Convert any value to 9-scale representation.
        
        Formula:
            digital_root = 1 + ((|value| × 1000 - 1) mod 9)
            cycle = |value| × 1000 // 9
        """
        # Handle special case
        if value == 0:
            return Score9(raw=0.0, digital_root=9, cycle=0)
        
        # Convert to integer representation
        int_val = abs(int(value * 1000))
        
        # Compute digital root
        if int_val == 0:
            dr = 9
        else:
            dr = 1 + ((int_val - 1) % 9)
        
        # Compute cycle
        cycle = int_val // 9
        
        return Score9(
            raw=round(value, self.precision),
            digital_root=dr,
            cycle=cycle
        )
    
    def combine_9(self, values: List[float], method: str = "mean") -> Score9:
        """
        Combine multiple values using 9-centric math.
        
        Methods:
        - "mean": Average then convert
        - "product": Multiply then convert
        - "root_sum": Sum digital roots mod 9
        - "max": Maximum value
        - "min": Minimum value
        
        Args:
            values: List of values to combine
            method: Combination method
            
        Returns:
            Combined Score9
        """
        if not values:
            return Score9(raw=0.0, digital_root=9, cycle=0)
        
        if method == "mean":
            combined = sum(values) / len(values)
        
        elif method == "product":
            combined = 1.0
            for v in values:
                combined *= v
        
        elif method == "root_sum":
            # Sum digital roots, then take digital root
            root_sum = sum(self.to_9(v).digital_root for v in values)
            return self.to_9(root_sum / 1000)  # Scale back
        
        elif method == "max":
            combined = max(values)
        
        elif method == "min":
            combined = min(values)
        
        else:
            combined = sum(values) / len(values)  # Default to mean
        
        return self.to_9(combined)
    
    def propagate_9(
        self,
        initial_confidence: float,
        chain_length: int,
        decay_factor: float = 0.9
    ) -> List[Score9]:
        """
        Propagate confidence through a chain using 9-centric decay.
        
        Formula:
            conf[i] = conf[0] × decay^i × (1 - dr_penalty[i])
            
        Where dr_penalty is based on digital root alignment.
        
        Args:
            initial_confidence: Starting confidence
            chain_length: Number of steps
            decay_factor: Base decay per step
            
        Returns:
            List of Score9 for each position
        """
        scores = []
        current = initial_confidence
        
        for i in range(chain_length):
            # Apply decay
            current = current * decay_factor
            
            # Apply 9-centric adjustment
            score = self.to_9(current)
            
            # Penalty based on digital root (higher roots = more stable)
            dr_factor = score.digital_root / 9
            current = current * (0.9 + 0.1 * dr_factor)
            
            scores.append(self.to_9(current))
        
        return scores
    
    def decay_9(self, value: float, steps: int) -> float:
        """
        Apply 9-centric decay.
        
        Formula:
            decayed = value × (dr / 9)^steps
            
        Where dr is the digital root of value.
        """
        score = self.to_9(value)
        
        # Decay factor based on digital root
        decay = score.digital_root / 9
        
        return value * (decay ** steps)
    
    def confidence_from_root(self, digital_root: int) -> float:
        """
        Convert digital root back to confidence estimate.
        
        Mapping (SOMA convention):
            9 -> 1.0 (complete)
            8 -> 0.9 (strong)
            7 -> 0.8
            6 -> 0.7
            5 -> 0.55
            4 -> 0.45
            3 -> 0.35
            2 -> 0.25
            1 -> 0.15
        """
        mapping = {
            9: 1.0,
            8: 0.9,
            7: 0.8,
            6: 0.7,
            5: 0.55,
            4: 0.45,
            3: 0.35,
            2: 0.25,
            1: 0.15,
        }
        return mapping.get(digital_root, 0.5)
    
    def interpret_root(self, digital_root: int) -> str:
        """Get the meaning of a digital root."""
        return self.ROOT_MEANINGS.get(digital_root, "unknown")
    
    def harmonize(self, scores: List[Score9]) -> Score9:
        """
        Find the harmonic combination of multiple scores.
        
        Uses 9-centric harmonic mean:
            harmonic = n / Σ(1/dr_i) × (9/n)
        """
        if not scores:
            return Score9(raw=0.0, digital_root=9, cycle=0)
        
        # Compute harmonic mean of digital roots
        inverse_sum = sum(1.0 / s.digital_root for s in scores)
        harmonic_dr = len(scores) / inverse_sum
        
        # Compute harmonic mean of raw values
        raw_inverse_sum = sum(1.0 / max(0.001, s.raw) for s in scores)
        harmonic_raw = len(scores) / raw_inverse_sum
        
        return self.to_9(harmonic_raw)
    
    def score_explanation(self, score: Score9) -> str:
        """Generate human-readable explanation of a score."""
        meaning = self.interpret_root(score.digital_root)
        conf = self.confidence_from_root(score.digital_root)
        
        return (
            f"Score: {score.raw:.4f}\n"
            f"Digital Root: {score.digital_root} ({meaning})\n"
            f"Cycle: {score.cycle}\n"
            f"Implied Confidence: {conf:.0%}"
        )
    
    def __repr__(self) -> str:
        return f"SOMA9Scorer(precision={self.precision})"

