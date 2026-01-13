"""
TinySLM - Ultra-lightweight Small Language Model

A minimal SLM designed for CPU-only inference with very low memory footprint.
Uses simple n-gram statistics instead of transformers.

Key features:
- Minimal memory: ~1-5 MB for typical vocabularies
- CPU-friendly: No GPU required, fast on any CPU
- Simple n-gram model: Learns token co-occurrence patterns
- Constraint integration: Works with SOMA constraint system
- Fast inference: O(vocab_size) per token

Perfect for:
- Edge devices
- Low-resource environments
- Quick prototyping
- Educational purposes
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, Counter
import random
import math

from .slm_constraints import ConstraintEngine, VocabularyScope
from .slm_generator import GenerationConfig, GenerationResult, DecodingStrategy


@dataclass
class TinySLMConfig:
    """Configuration for TinySLM."""
    # N-gram settings
    max_ngram: int = 3  # Maximum n-gram size (1=unigram, 2=bigram, 3=trigram)
    
    # Scoring
    ngram_weight: float = 1.0  # Weight for n-gram scores
    frequency_weight: float = 0.5  # Weight for token frequency
    context_weight: float = 0.3  # Weight for context matching
    
    # Generation
    temperature: float = 1.0  # Sampling temperature
    top_k: int = 10  # Top-K sampling
    
    # Memory limits
    max_vocab_size: int = 10000  # Maximum vocabulary size
    max_ngram_entries: int = 50000  # Maximum n-gram entries to store


class TinySLM:
    """
    Ultra-lightweight Small Language Model.
    
    Uses simple n-gram statistics for token prediction.
    Perfect for low-resource environments.
    
    Memory usage:
    - Vocabulary: ~vocab_size * 8 bytes (for frequencies)
    - N-grams: ~ngram_count * 16 bytes (for counts)
    - Total: ~1-5 MB for typical use cases
    
    Example:
        slm = TinySLM()
        slm.train_from_facts(["Python is a language", "Python is popular"])
        result = slm.generate("What is Python?", constraint_engine)
    """
    
    def __init__(self, config: Optional[TinySLMConfig] = None):
        self.config = config or TinySLMConfig()
        
        # Vocabulary and frequencies
        self.vocab: Set[str] = set()
        self.token_freq: Counter = Counter()
        
        # N-gram statistics
        # Structure: {ngram_tuple: count}
        self.ngrams: Dict[Tuple[str, ...], int] = defaultdict(int)
        
        # Context patterns (which tokens follow which contexts)
        self.context_patterns: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        
        # Training statistics
        self.training_stats = {
            'facts_processed': 0,
            'tokens_processed': 0,
            'ngrams_learned': 0,
        }
    
    def train_from_facts(self, facts: List[str]) -> None:
        """
        Train the model from a list of facts.
        
        This is a simple training process that:
        1. Extracts tokens from facts
        2. Builds n-gram statistics
        3. Learns context patterns
        
        Args:
            facts: List of fact strings to learn from
        """
        import re
        
        for fact in facts:
            # Tokenize fact
            tokens = re.findall(r'\b\w+\b', fact.lower())
            if not tokens:
                continue
            
            # Update vocabulary and frequencies
            self.vocab.update(tokens)
            self.token_freq.update(tokens)
            
            # Build n-grams (1-gram, 2-gram, 3-gram, etc.)
            for n in range(1, min(self.config.max_ngram + 1, len(tokens) + 1)):
                for i in range(len(tokens) - n + 1):
                    ngram = tuple(tokens[i:i+n])
                    self.ngrams[ngram] += 1
                    
                    # Store context patterns (for n>1, store what follows)
                    if n < len(tokens) - i:
                        context = ngram[:-1] if n > 1 else tuple()
                        next_token = tokens[i+n]
                        self.context_patterns[context][next_token] += 1
            
            self.training_stats['facts_processed'] += 1
            self.training_stats['tokens_processed'] += len(tokens)
        
        # Limit n-gram storage to prevent memory bloat
        if len(self.ngrams) > self.config.max_ngram_entries:
            # Keep most frequent n-grams
            sorted_ngrams = sorted(
                self.ngrams.items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.ngrams = dict(sorted_ngrams[:self.config.max_ngram_entries])
            self.training_stats['ngrams_learned'] = len(self.ngrams)
        else:
            self.training_stats['ngrams_learned'] = len(self.ngrams)
    
    def score_token(
        self,
        token: str,
        context: List[str],
        allowed_tokens: Optional[Set[str]] = None
    ) -> float:
        """
        Score a token given the current context.
        
        Uses:
        1. N-gram probability
        2. Token frequency
        3. Context matching
        
        Args:
            token: Token to score
            context: Previous tokens in sequence
            allowed_tokens: Set of allowed tokens (for filtering)
        
        Returns:
            Score (higher = more likely)
        """
        if allowed_tokens and token not in allowed_tokens:
            return -float('inf')
        
        score = 0.0
        
        # 1. Token frequency score
        freq_score = math.log(self.token_freq.get(token, 1) + 1)
        score += self.config.frequency_weight * freq_score
        
        # 2. N-gram score (check if token follows context)
        if context:
            # Try different context lengths (longest first)
            for n in range(min(len(context), self.config.max_ngram), 0, -1):
                context_tuple = tuple(context[-n:])
                
                # Check if this context pattern exists
                if context_tuple in self.context_patterns:
                    pattern = self.context_patterns[context_tuple]
                    if token in pattern:
                        # Score based on how often token follows this context
                        count = pattern[token]
                        total = sum(pattern.values())
                        ngram_score = math.log(count + 1) / math.log(total + 1)
                        score += self.config.ngram_weight * ngram_score
                        break  # Use longest matching context
        
        # 3. Direct n-gram match (if context + token forms known n-gram)
        if context:
            for n in range(min(len(context) + 1, self.config.max_ngram + 1), 1, -1):
                if len(context) >= n - 1:
                    ngram = tuple(context[-(n-1):] + [token])
                    if ngram in self.ngrams:
                        count = self.ngrams[ngram]
                        # Normalize by context frequency
                        context_ngram = tuple(context[-(n-1):])
                        context_count = sum(
                            v for k, v in self.ngrams.items()
                            if k[:len(context_ngram)] == context_ngram
                        )
                        if context_count > 0:
                            ngram_prob = count / context_count
                            score += self.config.ngram_weight * math.log(ngram_prob + 1e-10)
                        break
        
        return score
    
    def generate(
        self,
        query: str,
        constraint_engine: ConstraintEngine,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """
        Generate text using the model with constraints.
        
        Args:
            query: Input query/prompt
            constraint_engine: Constraint engine to filter tokens
            config: Generation configuration
        
        Returns:
            GenerationResult with generated text
        """
        gen_config = config or GenerationConfig()
        rng = random.Random(gen_config.seed)
        
        # Get allowed tokens from constraint engine
        allowed_tokens = set(constraint_engine.get_allowed_tokens())
        if not allowed_tokens:
            return GenerationResult(
                text="[No allowed tokens]",
                tokens=[],
                source_facts=constraint_engine.context.facts,
            )
        
        # Tokenize query for context
        import re
        query_tokens = re.findall(r'\b\w+\b', query.lower())
        
        # Generation loop
        generated: List[str] = []
        context: List[str] = query_tokens.copy()  # Start with query context
        tokens_considered = 0
        tokens_rejected = 0
        
        for step in range(gen_config.max_tokens):
            # Score all allowed tokens
            scores: Dict[str, float] = {}
            for token in allowed_tokens:
                tokens_considered += 1
                score = self.score_token(token, context, allowed_tokens)
                
                # Check constraint
                passed, reason = constraint_engine.check_token(token)
                if passed:
                    scores[token] = score
                else:
                    tokens_rejected += 1
            
            if not scores:
                # No valid tokens
                break
            
            # Select token based on strategy
            token = self._select_token(scores, gen_config, rng)
            generated.append(token)
            context.append(token)
            
            # Limit context size (keep last N tokens)
            max_context = self.config.max_ngram * 2
            if len(context) > max_context:
                context = context[-max_context:]
            
            # Check stop conditions
            if self._should_stop(generated, token, gen_config):
                break
        
        # Build result
        text = self._tokens_to_text(generated)
        
        return GenerationResult(
            text=text,
            tokens=generated,
            tokens_considered=tokens_considered,
            tokens_rejected=tokens_rejected,
            constraints_applied=[c.name for c in constraint_engine.constraints],
            source_facts=constraint_engine.context.facts,
            config=gen_config,
        )
    
    def _select_token(
        self,
        scores: Dict[str, float],
        config: GenerationConfig,
        rng: random.Random
    ) -> str:
        """Select next token from scored candidates."""
        if not scores:
            return "."
        
        # Apply temperature
        if config.temperature > 0:
            temp_scores = {
                token: score / config.temperature
                for token, score in scores.items()
            }
        else:
            temp_scores = scores
        
        # Top-K filtering
        if config.strategy == DecodingStrategy.TOP_K:
            sorted_tokens = sorted(
                temp_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            candidates = dict(sorted_tokens[:config.top_k])
        elif config.strategy == DecodingStrategy.GREEDY:
            # Greedy: pick highest score
            return max(temp_scores.items(), key=lambda x: x[1])[0]
        else:
            candidates = temp_scores
        
        # Convert scores to probabilities
        max_score = max(candidates.values())
        exp_scores = {
            token: math.exp(score - max_score)
            for token, score in candidates.items()
        }
        total = sum(exp_scores.values())
        
        if total == 0:
            return rng.choice(list(candidates.keys()))
        
        probs = {token: score / total for token, score in exp_scores.items()}
        
        # Sample
        r = rng.random()
        cumsum = 0.0
        for token, prob in probs.items():
            cumsum += prob
            if r <= cumsum:
                return token
        
        return list(probs.keys())[-1]
    
    def _should_stop(
        self,
        generated: List[str],
        last_token: str,
        config: GenerationConfig
    ) -> bool:
        """Check if generation should stop."""
        if len(generated) < config.min_tokens:
            return False
        
        if config.stop_after_sentence:
            if last_token in config.stop_tokens:
                return True
        
        return False
    
    def _tokens_to_text(self, tokens: List[str]) -> str:
        """Convert tokens to readable text."""
        if not tokens:
            return ""
        
        text = tokens[0]
        for token in tokens[1:]:
            if token in '.,:;!?':
                text += token
            else:
                text += ' ' + token
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def get_stats(self) -> Dict:
        """Get model statistics."""
        return {
            'vocab_size': len(self.vocab),
            'ngram_count': len(self.ngrams),
            'context_patterns': len(self.context_patterns),
            'training_stats': self.training_stats.copy(),
            'memory_estimate_mb': self._estimate_memory_mb(),
        }
    
    def _estimate_memory_mb(self) -> float:
        """Estimate memory usage in MB."""
        # Rough estimates
        vocab_mem = len(self.vocab) * 8  # bytes
        ngram_mem = len(self.ngrams) * 24  # bytes (tuple + int)
        pattern_mem = sum(
            len(counter) * 16
            for counter in self.context_patterns.values()
        )
        
        total_bytes = vocab_mem + ngram_mem + pattern_mem
        return total_bytes / (1024 * 1024)  # Convert to MB


class TinySLMWrapper:
    """
    Wrapper that integrates TinySLM with SOMA Cognitive.
    
    This provides the same interface as SOMASLM but uses
    the lightweight TinySLM backend.
    
    Usage:
        slm = TinySLMWrapper()
        slm.load_knowledge(facts, reasoning_path)
        result = slm.generate("What is Python?")
    """
    
    def __init__(self, config: Optional[TinySLMConfig] = None):
        self.slm = TinySLM(config)
        self.engine = ConstraintEngine()
        self.facts: List[str] = []
        self.reasoning_path: List[str] = []
    
    def load_knowledge(
        self,
        facts: List[str],
        reasoning_path: Optional[List[str]] = None,
        relations: Optional[List[str]] = None
    ):
        """
        Load knowledge from soma Cognitive and train the model.
        """
        self.facts = facts
        self.reasoning_path = reasoning_path or []
        
        # Train the SLM from facts
        self.slm.train_from_facts(facts)
        
        # Setup constraint engine
        self.engine.add_facts_from_cognitive(facts)
        if reasoning_path:
            self.engine.set_reasoning_path(reasoning_path)
        
        # Build vocabulary scope
        scope = VocabularyScope()
        import re
        for fact in facts:
            tokens = re.findall(r'\b\w+\b', fact.lower())
            scope.add_tokens(tokens)
        if relations:
            scope.add_domain(relations)
        self.engine.set_vocabulary_scope(scope)
    
    def generate(self, query: str) -> GenerationResult:
        """
        Generate grounded response to query.
        """
        return self.slm.generate(query, self.engine)
    
    def set_config(self, **kwargs):
        """Set generation configuration."""
        # This would need to be passed to generate() call
        pass
    
    def get_stats(self) -> Dict:
        """Get model and constraint statistics."""
        slm_stats = self.slm.get_stats()
        constraint_stats = self.engine.get_stats()
        return {
            'slm': slm_stats,
            'constraints': constraint_stats,
        }
    
    def explain(self) -> str:
        """Explain the model."""
        stats = self.get_stats()
        lines = [
            "=== TinySLM Model ===",
            "",
            "Model Statistics:",
            f"  Vocabulary size: {stats['slm']['vocab_size']}",
            f"  N-grams learned: {stats['slm']['ngram_count']}",
            f"  Memory usage: {stats['slm']['memory_estimate_mb']:.2f} MB",
            "",
            "Training:",
            f"  Facts processed: {stats['slm']['training_stats']['facts_processed']}",
            f"  Tokens processed: {stats['slm']['training_stats']['tokens_processed']}",
            "",
            "Constraints:",
            f"  Facts loaded: {stats['constraints']['fact_count']}",
            f"  Active constraints: {stats['constraints']['active_constraints']}",
            "",
            "This is a lightweight SLM that runs efficiently on CPU.",
        ]
        return "\n".join(lines)
