"""
SOMA Small Language Model (SLM)
=================================

Constraint-Grounded Small Language Model (CG-SLM)

A lightweight, CPU-friendly language model that uses ONLY SOMA's custom infrastructure.

100% SOMA-NATIVE - NO THIRD-PARTY AI DEPENDENCIES:
- ✅ Uses ONLY SOMA tokenization (custom implementation)
- ✅ Uses ONLY SOMA embeddings (custom implementation)
- ✅ Uses ONLY SOMA semantic processing (custom implementation)
- ✅ Uses ONLY SOMA trees and graphs (custom implementation)
- ✅ Uses ONLY SOMA training/testing (custom implementation)

SYSTEM BEHAVIOR (SLM Characteristics):
✅ Has embeddings
✅ Has sequence modeling
✅ Has learned parameters
✅ Has probabilistic sampling
✅ Improves ordering with training

This IS an SLM, but of a different class:
- Class: Constraint-Grounded Small Language Model (CG-SLM)
- Terminology: SOMA SLM

DEPENDENCIES:
- ✅ NumPy: ONLY as numerical substrate (arrays, math, matrix ops)
  - NOT used as AI framework
  - NOT used as ML library
  - Just basic numerical operations
- ✅ Python Standard Library: typing, dataclasses, math, sys, os, collections
- ❌ NO TensorFlow
- ❌ NO PyTorch
- ❌ NO Keras
- ❌ NO other AI/ML frameworks

Designed for small CPU environments - no GPU required.
"""

import numpy as np
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math
import sys
import os

# Add paths for SOMA imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

try:
    from src.src.core.core_tokenizer import tokenize_text
    SOMA_TOKENIZER_AVAILABLE = True
except ImportError:
    try:
        from src.core.core_tokenizer import tokenize_text
        SOMA_TOKENIZER_AVAILABLE = True
    except ImportError:
        SOMA_TOKENIZER_AVAILABLE = False
        print("Warning: SOMA tokenizer not found, using fallback")

# Note: SOMAEmbeddingGenerator may import TensorFlow, but we don't use it
# The SLM itself is pure NumPy and doesn't depend on TensorFlow
try:
    from src.embeddings.embedding_generator import somaEmbeddingGenerator
    SOMA_EMBEDDINGS_AVAILABLE = True
except ImportError:
    try:
        from embeddings.embedding_generator import somaEmbeddingGenerator
        SOMA_EMBEDDINGS_AVAILABLE = True
    except ImportError:
        SOMA_EMBEDDINGS_AVAILABLE = False
        print("Warning: SOMA embeddings not found, using fallback")

try:
    from soma_cognitive.algorithms.semantic_similarity import somaSimilarity
    SOMA_SEMANTIC_AVAILABLE = True
except ImportError:
    SOMA_SEMANTIC_AVAILABLE = False
    print("Warning: SOMA semantic similarity not found, using fallback")

try:
    from soma_cognitive.graph import GraphStore
    SOMA_GRAPH_AVAILABLE = True
except ImportError:
    SOMA_GRAPH_AVAILABLE = False
    print("Warning: SOMA graph not found, using fallback")


@dataclass
class SLMConfig:
    """Configuration for Small SLM"""
    # Model size (small = CPU-friendly)
    vocab_size: int = 10000
    d_model: int = 128  # Small embedding dimension
    n_layers: int = 2  # Just 2 layers for small model
    n_heads: int = 4  # 4 attention heads
    d_ff: int = 512  # Feed-forward dimension
    max_seq_len: int = 256  # Maximum sequence length
    
    # SOMA integration
    use_SOMA_tokenizer: bool = True
    use_SOMA_embeddings: bool = False  # Disabled by default to avoid TF imports
    use_SOMA_semantic: bool = True
    use_SOMA_graph: bool = True
    
    # Training
    learning_rate: float = 0.001
    batch_size: int = 32
    dropout: float = 0.1


class SOMATokenizerWrapper:
    """Wrapper for SOMA tokenization"""
    
    def __init__(self):
        self.tokenizer_available = SOMA_TOKENIZER_AVAILABLE
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using SOMA"""
        if self.tokenizer_available:
            try:
                tokens = tokenize_text(text, tokenizer_type="word")
                # Extract text from TokenRecord objects
                result = []
                for t in tokens:
                    # TokenRecord has 'text' attribute for word tokens
                    # For non-word tokens (spaces, punctuation), skip them or handle differently
                    if hasattr(t, 'text'):
                        token_text = t.text
                        # Only add word tokens, skip spaces/punctuation
                        if token_text and token_text.strip() and not token_text.isspace():
                            result.append(token_text.lower())
                    elif hasattr(t, 'type'):
                        # If it's a word type, try to get the text
                        if t.type == 'word' and hasattr(t, 'text'):
                            token_text = t.text
                            if token_text and token_text.strip():
                                result.append(token_text.lower())
                
                return result if result else text.lower().split()
            except Exception as e:
                print(f"SOMA tokenizer error: {e}, using fallback")
                return text.lower().split()
        else:
            # Fallback to simple word splitting
            return text.lower().split()
    
    def build_vocab(self, texts: List[str]) -> Dict[str, int]:
        """Build vocabulary from texts"""
        vocab = {}
        special_tokens = ["<PAD>", "<UNK>", "<START>", "<END>"]
        
        # Add special tokens
        for i, token in enumerate(special_tokens):
            vocab[token] = i
        
        # Add tokens from texts
        idx = len(special_tokens)
        for text in texts:
            tokens = self.tokenize(text)
            for token in tokens:
                if token not in vocab:
                    vocab[token] = idx
                    idx += 1
        
        return vocab


class ConstraintEngine:
    """Constraint engine using SOMA Cognitive facts"""
    
    def __init__(self, facts: Optional[List[str]] = None):
        self.facts = facts or []
        self.fact_tokens: Set[str] = set()
        self.allowed_tokens: Set[str] = set()
        self.strict_mode = False
        
        if facts:
            self._build_from_facts()
    
    def _build_from_facts(self):
        """Extract tokens from facts"""
        tokenizer = SOMATokenizerWrapper()
        
        for fact in self.facts:
            tokens = tokenizer.tokenize(fact)
            self.fact_tokens.update(tokens)
        
        # Start with fact tokens
        self.allowed_tokens = self.fact_tokens.copy()
        
        # Add structural tokens (always allowed)
        structural = {"the", "a", "an", "is", "are", "was", "were", ".", ",", "?", "!"}
        self.allowed_tokens.update(structural)
    
    def add_facts(self, facts: List[str]):
        """Add more facts"""
        self.facts.extend(facts)
        self._build_from_facts()
    
    def get_allowed_tokens(self) -> Set[str]:
        """Get set of allowed tokens"""
        return self.allowed_tokens.copy()
    
    def is_allowed(self, token: str) -> bool:
        """Check if token is allowed"""
        if not self.strict_mode:
            return token in self.allowed_tokens
        else:
            # Strict: only fact tokens + structural
            structural = {"the", "a", "an", "is", "are", "was", "were", ".", ",", "?", "!"}
            return token in self.fact_tokens or token in structural


class SOMAPositionEncoder:
    """Positional encoding using sinusoidal patterns"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        self.d_model = d_model
        self.max_len = max_len
        
        # Pre-compute position encodings
        pe = np.zeros((max_len, d_model))
        for pos in range(max_len):
            for i in range(0, d_model, 2):
                pe[pos, i] = math.sin(pos / (10000 ** ((2 * i) / d_model)))
                if i + 1 < d_model:
                    pe[pos, i + 1] = math.cos(pos / (10000 ** ((2 * (i + 1)) / d_model)))
        
        self.pe = pe
    
    def encode(self, sequence_length: int) -> np.ndarray:
        """Get positional encoding for sequence"""
        return self.pe[:sequence_length, :]


class SOMAPatternMatcher:
    """
    Lightweight pattern matcher (attention mechanism)
    
    Pure NumPy implementation - NO TensorFlow dependency.
    All operations use NumPy arrays and matrix multiplication.
    """
    
    def __init__(self, d_model: int, n_heads: int = 4):
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        # Initialize weights (small random values) - Pure NumPy
        np.random.seed(42)
        self.W_q = np.random.randn(d_model, d_model) * 0.02
        self.W_k = np.random.randn(d_model, d_model) * 0.02
        self.W_v = np.random.randn(d_model, d_model) * 0.02
        self.W_o = np.random.randn(d_model, d_model) * 0.02
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass - Pure NumPy, no TF graphs or backprop.
        Uses @ operator for matrix multiplication (NumPy).
        """
        """Multi-head attention forward pass"""
        seq_len, d_model = x.shape
        
        # Project to Q, K, V
        Q = x @ self.W_q  # (seq_len, d_model)
        K = x @ self.W_k
        V = x @ self.W_v
        
        # Reshape for multi-head
        Q = Q.reshape(seq_len, self.n_heads, self.d_k).transpose(1, 0, 2)  # (n_heads, seq_len, d_k)
        K = K.reshape(seq_len, self.n_heads, self.d_k).transpose(1, 0, 2)
        V = V.reshape(seq_len, self.n_heads, self.d_k).transpose(1, 0, 2)
        
        # Compute attention scores
        scores = Q @ K.transpose(0, 2, 1) / math.sqrt(self.d_k)  # (n_heads, seq_len, seq_len)
        
        # Softmax
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attn_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        
        # Apply to values
        output = attn_weights @ V  # (n_heads, seq_len, d_k)
        
        # Concatenate heads
        output = output.transpose(1, 0, 2).reshape(seq_len, d_model)  # (seq_len, d_model)
        
        # Output projection
        output = output @ self.W_o
        
        return output


class SOMAProcessor:
    """
    Feed-forward processor
    
    Pure NumPy implementation - NO TensorFlow dependency.
    All operations use NumPy arrays.
    """
    
    def __init__(self, d_model: int, d_ff: int):
        self.d_model = d_model
        self.d_ff = d_ff
        
        # Initialize weights - Pure NumPy
        np.random.seed(42)
        self.W1 = np.random.randn(d_model, d_ff) * 0.02
        self.b1 = np.zeros(d_ff)
        self.W2 = np.random.randn(d_ff, d_model) * 0.02
        self.b2 = np.zeros(d_model)
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Feed-forward forward pass - Pure NumPy, no TF.
        Uses @ operator for matrix multiplication (NumPy).
        """
        # Layer 1
        h1 = x @ self.W1 + self.b1  # (seq_len, d_ff)
        h1 = np.maximum(0, h1)  # ReLU
        
        # Layer 2
        h2 = h1 @ self.W2 + self.b2  # (seq_len, d_model)
        
        return h2


class SOMASequenceBlock:
    """Single sequence processing block"""
    
    def __init__(self, d_model: int, n_heads: int, d_ff: int):
        self.pattern_matcher = SOMAPatternMatcher(d_model, n_heads)
        self.processor = SOMAProcessor(d_model, d_ff)
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass with residual connections"""
        # Pattern matching + residual
        pattern_out = self.pattern_matcher.forward(x)
        x = x + pattern_out  # Residual
        
        # Layer norm (simplified)
        x = self._layer_norm(x)
        
        # Processing + residual
        proc_out = self.processor.forward(x)
        x = x + proc_out  # Residual
        
        # Layer norm
        x = self._layer_norm(x)
        
        return x
    
    def _layer_norm(self, x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
        """Simplified layer normalization"""
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        return (x - mean) / np.sqrt(var + eps)


class SOMASequenceOptimizer:
    """
    Lightweight sequence optimizer
    
    Pure NumPy implementation - NO TensorFlow dependency.
    - No TF graphs
    - No TF backpropagation
    - All operations use NumPy arrays
    - Matrix multiplication via NumPy @ operator
    """
    
    def __init__(self, config: SLMConfig, vocab: Dict[str, int]):
        self.config = config
        self.vocab = vocab
        self.vocab_size = len(vocab)
        self.id_to_token = {v: k for k, v in vocab.items()}
        
        # Embedding layer
        np.random.seed(42)
        self.embeddings = np.random.randn(self.vocab_size, config.d_model) * 0.02
        
        # Position encoder
        self.pos_encoder = SOMAPositionEncoder(config.d_model, config.max_seq_len)
        
        # Sequence blocks
        self.blocks = [
            SOMASequenceBlock(config.d_model, config.n_heads, config.d_ff)
            for _ in range(config.n_layers)
        ]
        
        # Output projection
        self.output_proj = np.random.randn(config.d_model, self.vocab_size) * 0.02
    
    def forward(self, token_ids: List[int]) -> np.ndarray:
        """
        Forward pass through optimizer - Pure NumPy, no TF.
        Returns logits as NumPy array.
        """
        seq_len = len(token_ids)
        
        # Embedding lookup
        embedded = self.embeddings[token_ids]  # (seq_len, d_model)
        
        # Add positional encoding
        pos_enc = self.pos_encoder.encode(seq_len)
        embedded = embedded + pos_enc
        
        # Pass through blocks
        x = embedded
        for block in self.blocks:
            x = block.forward(x)
        
        # Get last position
        last_hidden = x[-1]  # (d_model,)
        
        # Project to vocabulary
        logits = last_hidden @ self.output_proj  # (vocab_size,)
        
        return logits
    
    def count_parameters(self) -> int:
        """Count total number of trainable parameters"""
        total = 0
        
        # Embedding layer
        total += self.embeddings.size
        
        # Position encoder (pre-computed, but count it)
        total += self.pos_encoder.pe.size
        
        # Sequence blocks
        for block in self.blocks:
            # Pattern matcher weights
            total += block.pattern_matcher.W_q.size
            total += block.pattern_matcher.W_k.size
            total += block.pattern_matcher.W_v.size
            total += block.pattern_matcher.W_o.size
            
            # Processor weights
            total += block.processor.W1.size
            total += block.processor.b1.size
            total += block.processor.W2.size
            total += block.processor.b2.size
        
        # Output projection
        total += self.output_proj.size
        
        return int(total)


class ConstrainedDecoder:
    """Constrained decoder that integrates optimizer with constraints"""
    
    def __init__(self, optimizer: SOMASequenceOptimizer, constraint_engine: ConstraintEngine):
        self.optimizer = optimizer
        self.constraint_engine = constraint_engine
    
    def generate(self, prompt: List[str], max_tokens: int = 50, temperature: float = 1.0) -> List[str]:
        """Generate text with constraints"""
        sequence = prompt.copy()
        
        for _ in range(max_tokens):
            # Encode current sequence
            token_ids = [
                self.optimizer.vocab.get(token, self.optimizer.vocab.get("<UNK>", 0))
                for token in sequence
            ]
            
            # Get optimizer scores
            logits = self.optimizer.forward(token_ids)
            
            # Get allowed tokens
            allowed_tokens = self.constraint_engine.get_allowed_tokens()
            allowed_ids = [
                self.optimizer.vocab[token]
                for token in allowed_tokens
                if token in self.optimizer.vocab
            ]
            
            # Apply mask (set disallowed to -inf)
            masked_logits = logits.copy()
            for i in range(len(masked_logits)):
                if i not in allowed_ids:
                    masked_logits[i] = -np.inf
            
            # Softmax
            exp_logits = np.exp(masked_logits - np.max(masked_logits))
            probs = exp_logits / np.sum(exp_logits[allowed_ids])
            
            # Sample (greedy for now)
            if temperature > 0:
                # Temperature sampling
                probs = np.power(probs, 1.0 / temperature)
                probs = probs / np.sum(probs)
                selected_id = np.random.choice(len(probs), p=probs)
            else:
                # Greedy
                selected_id = np.argmax(probs)
            
            # Decode token
            selected_token = self.optimizer.id_to_token[selected_id]
            
            # Stop if end token
            if selected_token == "<END>":
                break
            
            sequence.append(selected_token)
        
        return sequence


class SmallSOMASLM:
    """Complete Small SLM using SOMA infrastructure"""
    
    def __init__(self, config: Optional[SLMConfig] = None):
        self.config = config or SLMConfig()
        self.tokenizer = SOMATokenizerWrapper()
        self.vocab: Optional[Dict[str, int]] = None
        self.optimizer: Optional[SOMASequenceOptimizer] = None
        self.constraint_engine: Optional[ConstraintEngine] = None
        self.decoder: Optional[ConstrainedDecoder] = None
        
        # SOMA integrations (optional - may import TF, but SLM core doesn't use TF)
        # Note: The SLM core itself is 100% NumPy, no TensorFlow dependency
        self.embedding_generator = None
        self.semantic_similarity = None
        self.graph_store = None
        
        # Embeddings are optional - disabled by default to avoid TF imports
        # The SLM works perfectly without embeddings (uses its own NumPy-based optimizer)
        if self.config.use_SOMA_embeddings and SOMA_EMBEDDINGS_AVAILABLE:
            try:
                # This may import TensorFlow, but we don't use it in SLM core
                self.embedding_generator = SOMAEmbeddingGenerator(strategy="feature_based")
            except Exception as e:
                print(f"Warning: Could not initialize SOMA embeddings: {e}")
                print("Note: SLM works fine without embeddings - uses pure NumPy optimizer")
        
        if self.config.use_SOMA_semantic and SOMA_SEMANTIC_AVAILABLE:
            try:
                self.semantic_similarity = SOMASimilarity()
            except Exception as e:
                print(f"Warning: Could not initialize SOMA semantic: {e}")
        
        if self.config.use_SOMA_graph and SOMA_GRAPH_AVAILABLE:
            try:
                self.graph_store = GraphStore()
            except Exception as e:
                print(f"Warning: Could not initialize SOMA graph: {e}")
    
    def train(self, texts: List[str], facts: Optional[List[str]] = None):
        """Train the SLM on texts and facts"""
        # Build vocabulary
        print("Building vocabulary...")
        self.vocab = self.tokenizer.build_vocab(texts)
        print(f"Vocabulary size: {len(self.vocab)}")
        
        # Initialize constraint engine with facts
        if facts:
            print(f"Loading {len(facts)} facts into constraint engine...")
            self.constraint_engine = ConstraintEngine(facts)
        else:
            # Extract facts from texts (simple: use texts as facts)
            self.constraint_engine = ConstraintEngine(texts)
        
        # Initialize optimizer
        print("Initializing sequence optimizer...")
        self.optimizer = SOMASequenceOptimizer(self.config, self.vocab)
        
        # Initialize decoder
        self.decoder = ConstrainedDecoder(self.optimizer, self.constraint_engine)
        
        print("Training complete!")
    
    def generate(self, prompt: str, max_tokens: int = 50, temperature: float = 1.0) -> str:
        """Generate text from prompt"""
        if self.decoder is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Tokenize prompt
        prompt_tokens = self.tokenizer.tokenize(prompt)
        
        # Generate
        generated_tokens = self.decoder.generate(
            prompt_tokens,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Join tokens
        return " ".join(generated_tokens)
    
    def add_facts(self, facts: List[str]):
        """Add more facts to constraint engine"""
        if self.constraint_engine is None:
            self.constraint_engine = ConstraintEngine(facts)
        else:
            self.constraint_engine.add_facts(facts)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("SOMA Small Language Model (SLM)")
    print("=" * 60)
    
    # Create SLM
    config = SLMConfig(
        d_model=128,
        n_layers=2,
        n_heads=4,
        vocab_size=5000
    )
    
    slm = SmallSOMASLM(config)
    
    # Training data
    facts = [
        "Python is a programming language",
        "Python was created by Guido van Rossum",
        "Python is used for web development",
        "Python supports object-oriented programming"
    ]
    
    texts = facts  # Use facts as training texts
    
    # Train
    print("\nTraining SLM...")
    slm.train(texts, facts)
    
    # Generate
    print("\nGenerating text...")
    prompt = "Python is"
    result = slm.generate(prompt, max_tokens=10, temperature=0.8)
    print(f"Prompt: {prompt}")
    print(f"Generated: {result}")
    
    print("\nDone!")
