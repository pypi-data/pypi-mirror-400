"""
SOMA Sequence Optimizer

A SOMA-native sequence ordering system.
This is NOT intelligence - it only arranges approved tokens.

Key design principles:
    - Weak by design (intelligence stays in SOMA Cognitive)
    - Symbol IDs only (no raw text to prevent leakage)
    - Sequence Optimizer proposes → SOMA Cognitive disposes
    - 2-4 pattern matching blocks (minimal complexity)

NumPy only. No external AI concepts. 100% soma.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np


@dataclass
class SOMASequenceConfig:
    """Configuration for SOMA Sequence Optimizer."""
    vocab_size: int = 10000      # Symbol vocabulary size
    d_model: int = 128           # Model dimension (tiny)
    n_layers: int = 2            # Number of attention blocks
    n_heads: int = 4             # Attention heads
    d_ff: int = 512              # Feed-forward dimension
    max_seq_len: int = 256       # Maximum sequence length
    dropout: float = 0.0         # Dropout (0 for inference)
    
    # Sanity checks
    def __post_init__(self):
        assert self.d_model % self.n_heads == 0, "d_model must be divisible by n_heads"


class SOMAPositionEncoder:
    """
    SOMA position encoding.
    
    Adds position information to symbol embeddings.
    This is PURELY positional - no semantic meaning.
    """
    
    def __init__(self, d_model: int, max_len: int = 256):
        self.d_model = d_model
        self.max_len = max_len
        
        # Create positional encoding matrix
        pe = np.zeros((max_len, d_model))
        position = np.arange(0, max_len, dtype=np.float32).reshape(-1, 1)
        div_term = np.exp(np.arange(0, d_model, 2, dtype=np.float32) * 
                         -(np.log(10000.0) / d_model))
        
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)
        
        self.pe = pe  # Shape: (max_len, d_model)
    
    def __call__(self, x: np.ndarray) -> np.ndarray:
        """
        Add positional encoding to input.
        
        Args:
            x: Input embeddings, shape (seq_len, d_model)
        Returns:
            x + positional_encoding, shape (seq_len, d_model)
        """
        seq_len = x.shape[0]
        return x + self.pe[:seq_len]


class SOMAPatternMatcher:
    """
    SOMA pattern matching.
    
    This learns LOCAL patterns (which tokens go together).
    It does NOT learn facts or reasoning.
    """
    
    def __init__(self, d_model: int, n_heads: int):
        assert d_model % n_heads == 0
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        # Weight matrices (random init, will be trained)
        self.W_q = np.random.randn(d_model, d_model).astype(np.float32) * 0.02
        self.W_k = np.random.randn(d_model, d_model).astype(np.float32) * 0.02
        self.W_v = np.random.randn(d_model, d_model).astype(np.float32) * 0.02
        self.W_o = np.random.randn(d_model, d_model).astype(np.float32) * 0.02
    
    def forward(self, x: np.ndarray, mask: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Forward pass.
        
        Args:
            x: Input, shape (seq_len, d_model)
            mask: Optional mask, shape (seq_len, seq_len)
        Returns:
            Output, shape (seq_len, d_model)
        """
        seq_len, d_model = x.shape
        
        # Linear projections
        Q = x @ self.W_q  # (seq_len, d_model)
        K = x @ self.W_k  # (seq_len, d_model)
        V = x @ self.W_v  # (seq_len, d_model)
        
        # Reshape for multi-head
        Q = Q.reshape(seq_len, self.n_heads, self.d_k).transpose(1, 0, 2)  # (n_heads, seq_len, d_k)
        K = K.reshape(seq_len, self.n_heads, self.d_k).transpose(1, 0, 2)
        V = V.reshape(seq_len, self.n_heads, self.d_k).transpose(1, 0, 2)
        
        # Attention scores
        scores = Q @ K.transpose(0, 2, 1) / np.sqrt(self.d_k)  # (n_heads, seq_len, seq_len)
        
        # Apply mask if provided
        if mask is not None:
            scores = np.where(mask, scores, -1e9)
        
        # Softmax
        attn_weights = self._softmax(scores, axis=-1)  # (n_heads, seq_len, seq_len)
        
        # Apply attention to values
        attn_output = attn_weights @ V  # (n_heads, seq_len, d_k)
        
        # Concatenate heads
        attn_output = attn_output.transpose(1, 0, 2).reshape(seq_len, d_model)
        
        # Output projection
        output = attn_output @ self.W_o
        
        return output
    
    @staticmethod
    def _softmax(x: np.ndarray, axis: int) -> np.ndarray:
        """Stable softmax."""
        x_shifted = x - np.max(x, axis=axis, keepdims=True)
        exp_x = np.exp(x_shifted)
        return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


class SOMAProcessor:
    """
    SOMA processing layer.
    
    Simple two-layer processing for local token transformation.
    """
    
    def __init__(self, d_model: int, d_ff: int):
        self.W1 = np.random.randn(d_model, d_ff).astype(np.float32) * 0.02
        self.b1 = np.zeros(d_ff, dtype=np.float32)
        self.W2 = np.random.randn(d_ff, d_model).astype(np.float32) * 0.02
        self.b2 = np.zeros(d_model, dtype=np.float32)
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass.
        
        Args:
            x: Input, shape (seq_len, d_model)
        Returns:
            Output, shape (seq_len, d_model)
        """
        # Layer 1
        out = x @ self.W1 + self.b1
        out = np.maximum(out, 0)  # ReLU
        
        # Layer 2
        out = out @ self.W2 + self.b2
        return out


class SOMASequenceBlock:
    """
    SOMA sequence processing block.
    
    Pattern Matching → Add & Norm → Processing → Add & Norm
    
    This learns LOCAL token ordering patterns.
    """
    
    def __init__(self, d_model: int, n_heads: int, d_ff: int):
        self.pattern_matcher = SOMAPatternMatcher(d_model, n_heads)
        self.processor = SOMAProcessor(d_model, d_ff)
        
        # Layer normalization (simplified - just variance normalization)
        self.norm1_scale = np.ones(d_model, dtype=np.float32)
        self.norm2_scale = np.ones(d_model, dtype=np.float32)
    
    def forward(self, x: np.ndarray, mask: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Forward pass.
        
        Args:
            x: Input, shape (seq_len, d_model)
            mask: Optional attention mask
        Returns:
            Output, shape (seq_len, d_model)
        """
        # Pattern matching + residual
        pattern_out = self.pattern_matcher.forward(x, mask)
        x = x + pattern_out
        
        # Layer norm 1 (simplified)
        x = self._layer_norm(x, self.norm1_scale)
        
        # Processing + residual
        proc_out = self.processor.forward(x)
        x = x + proc_out
        
        # Layer norm 2
        x = self._layer_norm(x, self.norm2_scale)
        
        return x
    
    @staticmethod
    def _layer_norm(x: np.ndarray, scale: np.ndarray) -> np.ndarray:
        """Simplified layer normalization."""
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        x_norm = (x - mean) / np.sqrt(var + 1e-6)
        return x_norm * scale


class SOMASequenceOptimizer:
    """
    SOMA Sequence Optimizer.
    
    This is WEAK BY DESIGN. It only learns:
    - Which tokens appear together (local patterns)
    - Token ordering (grammar-like)
    - Sequence coherence
    
    It does NOT learn:
    - Facts
    - Reasoning
    - Semantic understanding
    
    Intelligence stays in SOMA Cognitive.
    """
    
    def __init__(self, config: SOMASequenceConfig):
        self.config = config
        
        # Embedding layer (symbol IDs → vectors)
        # This is PURELY a lookup - no semantic meaning
        self.embedding = np.random.randn(config.vocab_size, config.d_model).astype(np.float32) * 0.02
        
        # Position encoding
        self.pos_encoder = SOMAPositionEncoder(config.d_model, config.max_seq_len)
        
        # Sequence processing blocks
        self.blocks = [
            SOMASequenceBlock(config.d_model, config.n_heads, config.d_ff)
            for _ in range(config.n_layers)
        ]
        
        # Output projection (back to vocabulary space)
        self.output_proj = np.random.randn(config.d_model, config.vocab_size).astype(np.float32) * 0.02
        
        # Symbol to ID mapping (will be set externally)
        self.symbol_to_id: Dict[str, int] = {}
        self.id_to_symbol: Dict[int, str] = {}
    
    def set_vocabulary(self, symbol_to_id: Dict[str, int]):
        """
        Set the vocabulary mapping.
        
        This maps SOMA symbols to transformer IDs.
        The transformer only sees IDs, never raw symbols.
        """
        self.symbol_to_id = symbol_to_id
        self.id_to_symbol = {v: k for k, v in symbol_to_id.items()}
        
        # Resize embedding if needed
        max_id = max(symbol_to_id.values()) + 1
        if max_id > self.config.vocab_size:
            # Expand embedding
            old_embedding = self.embedding
            self.embedding = np.random.randn(max_id, self.config.d_model).astype(np.float32) * 0.02
            self.embedding[:old_embedding.shape[0]] = old_embedding
            self.config.vocab_size = max_id
    
    def encode_symbols(self, symbols: List[str]) -> List[int]:
        """Convert symbols to IDs."""
        return [self.symbol_to_id.get(s, 0) for s in symbols]
    
    def decode_ids(self, ids: List[int]) -> List[str]:
        """Convert IDs to symbols."""
        return [self.id_to_symbol.get(i, "<UNK>") for i in ids]
    
    def forward(self, symbol_ids: List[int]) -> np.ndarray:
        """
        Forward pass.
        
        Args:
            symbol_ids: List of symbol IDs
        Returns:
            Logits for next token, shape (vocab_size,)
        
        This generates SCORES, not probabilities.
        SOMA Cognitive will filter these.
        """
        seq_len = len(symbol_ids)
        
        if seq_len == 0:
            # Empty sequence - return uniform scores
            return np.zeros(self.config.vocab_size, dtype=np.float32)
        
        # Embedding lookup
        embedded = self.embedding[symbol_ids]  # (seq_len, d_model)
        
        # Add position encoding
        embedded = self.pos_encoder(embedded)
        
        # Pass through sequence blocks
        x = embedded
        for block in self.blocks:
            x = block.forward(x)
        
        # Use last position for next-token prediction
        last_hidden = x[-1]  # (d_model,)
        
        # Project to vocabulary
        logits = last_hidden @ self.output_proj  # (vocab_size,)
        
        return logits
    
    def get_scores(self, symbol_ids: List[int], candidate_ids: List[int]) -> np.ndarray:
        """
        Get scores for candidate tokens.
        
        Args:
            symbol_ids: Current sequence (IDs)
            candidate_ids: Candidate next tokens (IDs)
        Returns:
            Scores for candidates, shape (len(candidate_ids),)
        
        This is the interface for constrained decoding.
        """
        # Get logits for all tokens
        all_logits = self.forward(symbol_ids)  # (vocab_size,)
        
        # Extract scores for candidates only
        candidate_scores = all_logits[candidate_ids]  # (len(candidates),)
        
        return candidate_scores
    
    def count_parameters(self) -> int:
        """Count trainable parameters."""
        count = 0
        
        # Embedding
        count += self.embedding.size
        
        # Transformer blocks
        for block in self.blocks:
            # Attention
            count += block.attention.W_q.size
            count += block.attention.W_k.size
            count += block.attention.W_v.size
            count += block.attention.W_o.size
            # Feed-forward
            count += block.feed_forward.W1.size
            count += block.feed_forward.b1.size
            count += block.feed_forward.W2.size
            count += block.feed_forward.b2.size
            # Layer norms
            count += block.norm1_scale.size
            count += block.norm2_scale.size
        
        # Output projection
        count += self.output_proj.size
        
        return count


def create_SOMA_sequence_optimizer(
    vocab_size: int = 10000,
    d_model: int = 128,
    n_layers: int = 2,
    n_heads: int = 4,
    d_ff: int = 512
) -> SOMASequenceOptimizer:
    """
    Factory function to create a SOMA Sequence Optimizer.
    
    Defaults create a ~1M parameter model.
    """
    config = SOMASequenceConfig(
        vocab_size=vocab_size,
        d_model=d_model,
        n_layers=n_layers,
        n_heads=n_heads,
        d_ff=d_ff,
    )
    return SOMASequenceOptimizer(config)

