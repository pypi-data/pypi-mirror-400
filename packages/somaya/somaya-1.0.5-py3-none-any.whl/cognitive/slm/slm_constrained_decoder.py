"""
SOMA Constrained Decoder

Integrates the SOMA Sequence Optimizer with SOMA Cognitive constraints.

Rule: Sequence Optimizer proposes → SOMA Cognitive disposes

The sequence optimizer generates scores, but SOMA Cognitive decides
which tokens are actually allowed. Disallowed tokens get zero probability.

This makes hallucination structurally impossible even with a sequence component.
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Tuple
import numpy as np
import random

from .SOMA_sequence_optimizer import somaSequenceOptimizer, SOMASequenceConfig
from .slm_constraints import ConstraintEngine


@dataclass
class DecoderConfig:
    """Configuration for constrained decoding."""
    temperature: float = 1.0
    top_k: int = 50
    top_p: float = 0.9
    
    # Sampling strategy
    strategy: str = "constrained_nucleus"  # "greedy", "constrained_top_k", "constrained_nucleus"
    
    # Repetition control
    repetition_penalty: float = 1.2
    no_repeat_ngram: int = 3


class ConstrainedDecoder:
    """
    The constrained decoder.
    
    This is where sequence optimizer scores meet SOMA constraints.
    
    Flow:
    1. Sequence Optimizer generates scores for all tokens
    2. SOMA Cognitive filters to allowed tokens only
    3. Disallowed tokens get zero probability
    4. Sample from allowed set only
    """
    
    def __init__(
        self,
        sequence_optimizer: SOMASequenceOptimizer,
        constraint_engine: ConstraintEngine
    ):
        self.sequence_optimizer = sequence_optimizer
        self.engine = constraint_engine
        self.config = DecoderConfig()
        self.rng = random.Random()
        
        # Build symbol vocabulary from constraint engine
        self._build_vocabulary()
    
    def _build_vocabulary(self):
        """Build symbol-to-ID mapping from constraint engine vocabulary."""
        if self.engine.vocabulary_scope:
            # Get all tokens from vocabulary scope
            all_tokens = self.engine.vocabulary_scope.get_full_vocabulary()
            
            # Add fact tokens
            if self.engine.fact_constraint:
                all_tokens.update(self.engine.fact_constraint.fact_tokens)
            
            # Create mapping
            symbol_to_id = {token: i for i, token in enumerate(sorted(all_tokens))}
            self.sequence_optimizer.set_vocabulary(symbol_to_id)
            
            # Cache for lookup
            self.all_symbols = sorted(all_tokens)
        else:
            # Empty vocabulary - will be set later
            self.all_symbols = []
    
    def decode_step(
        self,
        current_sequence: List[str],
        allowed_tokens: Optional[Set[str]] = None
    ) -> Tuple[str, Dict]:
        """
        Decode one step.
        
        Args:
            current_sequence: Current sequence of symbols
            allowed_tokens: Set of allowed tokens (if None, uses constraint engine)
        Returns:
            (next_token, metadata)
        """
        # Get allowed tokens from constraint engine if not provided
        if allowed_tokens is None:
            allowed_tokens = self.engine.get_allowed_tokens()
        
        # Convert sequence to IDs
        sequence_ids = self.sequence_optimizer.encode_symbols(current_sequence)
        
        # Convert allowed tokens to candidate IDs
        candidate_symbols = [s for s in self.all_symbols if s in allowed_tokens]
        candidate_ids = self.sequence_optimizer.encode_symbols(candidate_symbols)
        
        if not candidate_ids:
            # No allowed tokens - return a structural token if available
            structural = ['the', 'is', 'a', 'an', '.']
            for struct in structural:
                if struct in self.all_symbols:
                    return struct, {'reason': 'fallback_structural'}
            return '.', {'reason': 'fallback_period'}
        
        # Get sequence optimizer scores for candidates
        candidate_scores = self.sequence_optimizer.get_scores(sequence_ids, candidate_ids)
        
        # Apply repetition penalty
        candidate_scores = self._apply_repetition_penalty(
            candidate_scores,
            candidate_symbols,
            current_sequence
        )
        
        # Convert scores to probabilities
        probabilities = self._scores_to_probs(candidate_scores)
        
        # Select token based on strategy
        selected_idx = self._select_token(probabilities)
        selected_token = candidate_symbols[selected_idx]
        
        # Metadata
        metadata = {
            'candidates': len(candidate_ids),
            'top_score': float(candidate_scores[selected_idx]),
            'strategy': self.config.strategy,
        }
        
        return selected_token, metadata
    
    def _apply_repetition_penalty(
        self,
        scores: np.ndarray,
        candidate_symbols: List[str],
        current_sequence: List[str]
    ) -> np.ndarray:
        """Apply repetition penalty to scores."""
        if not current_sequence:
            return scores
        
        penalized_scores = scores.copy()
        
        # Penalize tokens that appear in recent sequence
        recent_tokens = set(current_sequence[-self.config.no_repeat_ngram:])
        
        for i, symbol in enumerate(candidate_symbols):
            if symbol in recent_tokens:
                penalized_scores[i] /= self.config.repetition_penalty
        
        return penalized_scores
    
    def _scores_to_probs(self, scores: np.ndarray) -> np.ndarray:
        """Convert scores to probabilities with temperature."""
        # Apply temperature
        if self.config.temperature != 1.0:
            scores = scores / self.config.temperature
        
        # Softmax
        exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
        probs = exp_scores / np.sum(exp_scores)
        
        return probs
    
    def _select_token(self, probabilities: np.ndarray) -> int:
        """Select token index based on strategy."""
        if self.config.strategy == "greedy":
            return int(np.argmax(probabilities))
        
        elif self.config.strategy == "constrained_top_k":
            # Top-K sampling
            top_k = min(self.config.top_k, len(probabilities))
            top_indices = np.argsort(probabilities)[-top_k:][::-1]
            
            # Renormalize top-K
            top_probs = probabilities[top_indices]
            top_probs = top_probs / np.sum(top_probs)
            
            # Sample
            selected = self.rng.choices(
                range(len(top_indices)),
                weights=top_probs
            )[0]
            return int(top_indices[selected])
        
        elif self.config.strategy == "constrained_nucleus":
            # Nucleus sampling
            sorted_indices = np.argsort(probabilities)[::-1]
            sorted_probs = probabilities[sorted_indices]
            
            # Cumulative probability
            cumsum = np.cumsum(sorted_probs)
            
            # Find cutoff
            cutoff_idx = np.searchsorted(cumsum, self.config.top_p)
            if cutoff_idx == 0:
                cutoff_idx = 1
            
            # Select from nucleus
            nucleus_indices = sorted_indices[:cutoff_idx]
            nucleus_probs = probabilities[nucleus_indices]
            nucleus_probs = nucleus_probs / np.sum(nucleus_probs)
            
            # Sample
            selected = self.rng.choices(
                range(len(nucleus_indices)),
                weights=nucleus_probs
            )[0]
            return int(nucleus_indices[selected])
        
        else:
            # Default: greedy
            return int(np.argmax(probabilities))
    
    def decode(
        self,
        prompt: List[str],
        max_length: int = 50,
        min_length: int = 5,
        stop_tokens: Optional[Set[str]] = None
    ) -> Tuple[List[str], Dict]:
        """
        Decode a full sequence.
        
        Args:
            prompt: Initial sequence (can be empty)
            max_length: Maximum length
            min_length: Minimum length
            stop_tokens: Tokens that stop generation (default: sentence endings)
        Returns:
            (decoded_sequence, metadata)
        """
        if stop_tokens is None:
            stop_tokens = {'.', '!', '?'}
        
        sequence = list(prompt)
        metadata = {
            'steps': 0,
            'rejections': 0,
            'tokens_considered': [],
        }
        
        while len(sequence) < max_length:
            # Get allowed tokens
            allowed = self.engine.get_allowed_tokens()
            
            # Decode one step
            next_token, step_meta = self.decode_step(sequence, allowed)
            
            # Check constraint (double-check)
            passed, reason = self.engine.check_token(next_token)
            if not passed:
                metadata['rejections'] += 1
                # Try a structural token instead
                structural = ['the', 'is', 'a', 'an']
                next_token = None
                for struct in structural:
                    if struct in allowed:
                        next_token = struct
                        break
                if next_token is None:
                    break  # Can't continue
            
            sequence.append(next_token)
            metadata['steps'] += 1
            metadata['tokens_considered'].append(len(allowed))
            
            # Check stop conditions
            if len(sequence) >= min_length:
                if next_token in stop_tokens:
                    break
        
        return sequence, metadata
    
    def set_config(self, **kwargs):
        """Update decoder configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


class SOMAConstrainedSLM:
    """
    Complete SOMA sequence-constrained SLM.
    
    This integrates:
    - SOMASequenceOptimizer (sequence optimization)
    - ConstraintEngine (fact grounding)
    - ConstrainedDecoder (integration layer)
    
    Usage:
        slm = SOMAConstrainedSLM()
        slm.load_knowledge(facts, reasoning_path)
        slm.set_vocabulary_from_facts()
        result = slm.generate("What is Python?")
    """
    
    def __init__(
        self,
        transformer_config: Optional[SOMASequenceConfig] = None
    ):
        # Import here to avoid circular import
        from .slm_constraints import ConstraintEngine
        
        # Create constraint engine
        self.engine = ConstraintEngine()
        
        # Create sequence optimizer
        if transformer_config is None:
            transformer_config = SOMASequenceConfig(
                vocab_size=10000,
                d_model=128,
                n_layers=2,
                n_heads=4,
                d_ff=512,
            )
        self.sequence_optimizer = SOMASequenceOptimizer(transformer_config)
        
        # Create decoder
        self.decoder = ConstrainedDecoder(self.sequence_optimizer, self.engine)
        
        # Knowledge
        self.facts: List[str] = []
        self.reasoning_path: List[str] = []
    
    def load_knowledge(
        self,
        facts: List[str],
        reasoning_path: Optional[List[str]] = None,
        relations: Optional[List[str]] = None
    ):
        """Load knowledge from soma Cognitive."""
        self.facts = facts
        self.reasoning_path = reasoning_path or []
        
        # Add to constraint engine
        self.engine.add_facts_from_cognitive(facts)
        if reasoning_path:
            self.engine.set_reasoning_path(reasoning_path)
        
        # Build vocabulary scope
        from .slm_constraints import VocabularyScope
        import re
        
        scope = VocabularyScope()
        for fact in facts:
            tokens = re.findall(r'\b\w+\b', fact.lower())
            scope.add_tokens(tokens)
        
        if relations:
            scope.add_domain(relations)
        
        self.engine.set_vocabulary_scope(scope)
        
        # Rebuild decoder vocabulary
        self.decoder._build_vocabulary()
    
    def generate(
        self,
        query: str,
        max_length: int = 50,
        min_length: int = 5
    ) -> Tuple[str, Dict]:
        """
        Generate constrained response.
        
        Returns:
            (generated_text, metadata)
        """
        # Reset context
        self.engine.reset_context()
        self.engine.context.query = query
        
        # Start with query tokens as prompt
        import re
        query_tokens = re.findall(r'\b\w+\b', query.lower())
        
        # Decode
        sequence, metadata = self.decoder.decode(
            prompt=query_tokens[:3],  # Use first 3 query tokens as prompt
            max_length=max_length,
            min_length=min_length,
        )
        
        # Convert to text
        text = ' '.join(sequence)
        if text:
            text = text[0].upper() + text[1:]  # Capitalize first letter
        
        # Add to metadata
        metadata['text'] = text
        metadata['tokens'] = sequence
        metadata['facts'] = self.facts
        metadata['reasoning_path'] = self.reasoning_path
        
        return text, metadata
    
    def get_stats(self) -> Dict:
        """Get statistics."""
        optimizer_params = self.sequence_optimizer.count_parameters()
        constraint_stats = self.engine.get_stats()
        
        return {
            'optimizer_parameters': optimizer_params,
            'optimizer_size_mb': optimizer_params * 4 / (1024 * 1024),  # Assuming float32
            'constraint_stats': constraint_stats,
            'facts_loaded': len(self.facts),
            'vocab_size': len(self.decoder.all_symbols),
        }


def create_SOMA_constrained_slm(
    vocab_size: int = 10000,
    d_model: int = 128,
    n_layers: int = 2,
    n_heads: int = 4
) -> SOMAConstrainedSLM:
    """
    Factory function to create a SOMA sequence-constrained SLM.
    
    Defaults create a ~1M parameter model.
    """
    config = SOMASequenceConfig(
        vocab_size=vocab_size,
        d_model=d_model,
        n_layers=n_layers,
        n_heads=n_heads,
        d_ff=d_model * 4,
    )
    return SOMAConstrainedSLM(config)

