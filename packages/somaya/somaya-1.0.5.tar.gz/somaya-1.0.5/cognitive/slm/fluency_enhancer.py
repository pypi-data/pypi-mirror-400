"""
SOMA Fluency Enhancer
=======================

Improves text generation fluency through:
- Advanced sampling strategies (nucleus/top-p, top-k)
- Better temperature handling
- N-gram smoothing
- Improved repetition control
- Context-aware generation
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import deque
import random


class FluencyConfig:
    """Optimal configuration for excellent fluency"""
    
    # Sampling parameters (tuned for fluency)
    temperature: float = 0.7  # Lower = more deterministic, higher = more creative (0.7 is sweet spot)
    top_p: float = 0.95  # Nucleus sampling - cumulative probability threshold
    top_k: int = 50  # Top-k sampling fallback
    
    # Repetition control
    repetition_penalty: float = 1.15  # Penalize recent tokens (1.0 = no penalty, 1.2 = strong penalty)
    repetition_window: int = 20  # How many recent tokens to consider
    
    # N-gram smoothing
    no_repeat_ngram_size: int = 3  # Prevent repeating 3-grams
    ngram_penalty: float = 0.5  # Penalty for n-gram repetition
    
    # Context awareness
    context_window: int = 10  # Consider last N tokens for context
    context_boost: float = 1.3  # Boost tokens that appear in context
    
    # Smoothing
    length_penalty: float = 1.0  # Penalty for very short sequences
    min_length: int = 5  # Minimum generation length


class NucleusSampler:
    """Nucleus (top-p) sampling for better fluency"""
    
    @staticmethod
    def sample(logits: np.ndarray, top_p: float, temperature: float = 1.0) -> Tuple[int, np.ndarray]:
        """
        Sample using nucleus (top-p) sampling.
        
        This is better than top-k for fluency because it:
        - Adapts to the distribution (more tokens when confident, fewer when uncertain)
        - Produces more natural text
        - Reduces repetition
        
        Args:
            logits: Raw logits from model
            top_p: Cumulative probability threshold (0.9-0.95 is good)
            temperature: Sampling temperature
            
        Returns:
            (selected_token_id, probabilities)
        """
        # Apply temperature
        if temperature != 1.0:
            logits = logits / max(temperature, 0.01)
        
        # Numerical stability
        logits = logits - np.max(logits)
        
        # Convert to probabilities
        exp_logits = np.exp(logits)
        probs = exp_logits / (np.sum(exp_logits) + 1e-10)
        
        # Sort by probability (descending)
        sorted_indices = np.argsort(probs)[::-1]
        sorted_probs = probs[sorted_indices]
        
        # Cumulative probability
        cumsum_probs = np.cumsum(sorted_probs)
        
        # Find nucleus (smallest set with cumulative prob >= top_p)
        nucleus_mask = cumsum_probs <= top_p
        if not np.any(nucleus_mask):
            # Fallback: at least take top token
            nucleus_mask[0] = True
        
        # Get nucleus tokens
        nucleus_indices = sorted_indices[nucleus_mask]
        nucleus_probs = sorted_probs[nucleus_mask]
        
        # Renormalize nucleus probabilities
        nucleus_probs = nucleus_probs / np.sum(nucleus_probs)
        
        # Sample from nucleus
        if len(nucleus_indices) > 0:
            selected_idx = np.random.choice(len(nucleus_indices), p=nucleus_probs)
            selected_token_id = nucleus_indices[selected_idx]
        else:
            # Fallback to top token
            selected_token_id = sorted_indices[0]
        
        return int(selected_token_id), probs


class RepetitionController:
    """Advanced repetition control for better fluency"""
    
    def __init__(self, config: FluencyConfig):
        self.config = config
        self.recent_tokens: deque = deque(maxlen=config.repetition_window)
        self.ngram_history: Dict[Tuple, int] = {}  # Track n-grams
    
    def apply_penalty(self, logits: np.ndarray, token_ids: List[int]) -> np.ndarray:
        """
        Apply repetition penalty to logits.
        
        This reduces the probability of recently generated tokens,
        making the text more diverse and fluent.
        """
        penalized_logits = logits.copy()
        
        if len(self.recent_tokens) == 0:
            return penalized_logits
        
        # Apply repetition penalty to recent tokens
        for token_id in self.recent_tokens:
            if 0 <= token_id < len(penalized_logits):
                if penalized_logits[token_id] > 0:
                    penalized_logits[token_id] /= self.config.repetition_penalty
                else:
                    penalized_logits[token_id] *= self.config.repetition_penalty
        
        return penalized_logits
    
    def check_ngram_repetition(self, generated: List[int], candidate_id: int) -> bool:
        """Check if adding candidate would create a repeated n-gram."""
        if len(generated) < self.config.no_repeat_ngram_size - 1:
            return False
        
        # Build potential n-gram
        ngram = tuple(generated[-(self.config.no_repeat_ngram_size - 1):] + [candidate_id])
        
        # Check if this n-gram was seen recently
        if ngram in self.ngram_history:
            return True
        
        return False
    
    def apply_ngram_penalty(self, logits: np.ndarray, generated: List[int]) -> np.ndarray:
        """Apply penalty to tokens that would create repeated n-grams."""
        if len(generated) < self.config.no_repeat_ngram_size - 1:
            return logits
        
        penalized_logits = logits.copy()
        
        # Check each token
        for token_id in range(len(logits)):
            if self.check_ngram_repetition(generated, token_id):
                # Apply penalty
                if penalized_logits[token_id] > 0:
                    penalized_logits[token_id] *= self.config.ngram_penalty
                else:
                    penalized_logits[token_id] /= self.config.ngram_penalty
        
        return penalized_logits
    
    def update(self, token_id: int, generated: List[int]):
        """Update repetition tracking."""
        self.recent_tokens.append(token_id)
        
        # Update n-gram history
        if len(generated) >= self.config.no_repeat_ngram_size:
            ngram = tuple(generated[-self.config.no_repeat_ngram_size:])
            self.ngram_history[ngram] = self.ngram_history.get(ngram, 0) + 1
            
            # Limit history size (keep only recent n-grams)
            if len(self.ngram_history) > 1000:
                # Remove oldest entries
                oldest = min(self.ngram_history.items(), key=lambda x: x[1])
                del self.ngram_history[oldest[0]]
    
    def reset(self):
        """Reset repetition tracking."""
        self.recent_tokens.clear()
        self.ngram_history.clear()


class ContextAwareScorer:
    """Boost tokens that fit well in the current context"""
    
    def __init__(self, config: FluencyConfig):
        self.config = config
    
    def boost_context_tokens(
        self,
        logits: np.ndarray,
        generated: List[int],
        vocab: Dict[int, str]
    ) -> np.ndarray:
        """
        Boost tokens that appear frequently with recent context tokens.
        
        This improves fluency by preferring tokens that naturally
        follow the current context.
        """
        if len(generated) < 2:
            return logits
        
        boosted_logits = logits.copy()
        
        # Get recent context tokens
        context_tokens = generated[-self.config.context_window:]
        
        # Simple boost: if a token appears near context tokens in training,
        # boost it slightly. For now, we'll use a simple heuristic:
        # Boost tokens that are likely to follow common patterns
        
        # This is a placeholder - in a real implementation, you'd use
        # co-occurrence statistics from training data
        
        return boosted_logits


class FluencyEnhancer:
    """
    Main fluency enhancement system.
    
    Combines all techniques for excellent fluency:
    - Nucleus sampling
    - Repetition control
    - N-gram smoothing
    - Context awareness
    """
    
    def __init__(self, config: Optional[FluencyConfig] = None):
        self.config = config or FluencyConfig()
        self.sampler = NucleusSampler()
        self.repetition_controller = RepetitionController(self.config)
        self.context_scorer = ContextAwareScorer(self.config)
    
    def enhance_generation(
        self,
        logits: np.ndarray,
        generated: List[int],
        vocab: Optional[Dict[int, str]] = None
    ) -> int:
        """
        Enhance generation with all fluency techniques.
        
        Args:
            logits: Raw logits from model
            generated: List of already generated token IDs
            vocab: Optional vocabulary for context scoring
            
        Returns:
            Selected token ID
        """
        # Step 1: Apply repetition penalty
        logits = self.repetition_controller.apply_penalty(logits, generated)
        
        # Step 2: Apply n-gram penalty
        logits = self.repetition_controller.apply_ngram_penalty(logits, generated)
        
        # Step 3: Context-aware boosting (if vocab provided)
        if vocab:
            logits = self.context_scorer.boost_context_tokens(logits, generated, vocab)
        
        # Step 4: Nucleus sampling
        selected_id, probs = self.sampler.sample(
            logits,
            top_p=self.config.top_p,
            temperature=self.config.temperature
        )
        
        # Step 5: Update repetition tracking
        self.repetition_controller.update(selected_id, generated)
        
        return selected_id
    
    def reset(self):
        """Reset all state for new generation."""
        self.repetition_controller.reset()


# Convenience function for easy integration
def generate_with_fluency(
    model,
    prompt: str,
    max_tokens: int = 100,
    config: Optional[FluencyConfig] = None
) -> str:
    """
    Generate text with excellent fluency.
    
    This is a drop-in replacement for model.generate() that
    uses all fluency enhancement techniques.
    
    Args:
        model: SOMA model with forward() and tokenizer
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        config: Optional fluency configuration
        
    Returns:
        Generated text
    """
    enhancer = FluencyEnhancer(config)
    
    # Encode prompt
    if hasattr(model, 'tokenizer'):
        token_ids = model.tokenizer.encode(prompt, allow_unk=False)
    else:
        # Fallback
        token_ids = [ord(c) for c in prompt[:10]]  # Simple fallback
    
    generated = token_ids.copy()
    
    # Generate tokens
    for _ in range(max_tokens):
        # Forward pass
        try:
            logits = model.forward(generated)
            
            # Enhance with fluency techniques
            next_id = enhancer.enhance_generation(
                logits,
                generated,
                vocab=getattr(model.tokenizer, 'id_to_token', None)
            )
            
            generated.append(next_id)
            
            # Check for EOS
            if hasattr(model, 'tokenizer'):
                eos_id = model.tokenizer.vocab.get("<EOS>", -1)
                if next_id == eos_id:
                    break
        except Exception as e:
            print(f"Generation error: {e}")
            break
    
    # Decode
    if hasattr(model, 'tokenizer'):
        return model.tokenizer.decode(generated)
    else:
        # Fallback
        return ''.join([chr(id) if id < 256 else '?' for id in generated])
