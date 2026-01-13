"""
SOMA SLM Trainer

Training loop for the SOMA Sequence Optimizer.
Key principle: Loss computed ONLY over allowed tokens.

This is sequence optimization, NOT fact learning.
The sequence optimizer learns ORDERING patterns, nothing more.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import random
import json
from pathlib import Path

from .SOMA_sequence_optimizer import somaSequenceOptimizer, SOMASequenceConfig
from .training_data import TrainingSequence, SOMADataGenerator


@dataclass
class TrainingConfig:
    """Configuration for training."""
    learning_rate: float = 0.001
    batch_size: int = 32
    num_epochs: int = 10
    gradient_clip: float = 1.0
    
    # Logging
    log_every: int = 100
    save_every: int = 1000
    
    # Early stopping
    patience: int = 5
    min_delta: float = 0.001
    
    # Seed for reproducibility
    seed: Optional[int] = 42


class SLMTrainer:
    """
    Trainer for SOMA SLM.
    
    This trains the sequence optimizer to predict next tokens
    ONLY from allowed sets. Hallucination cannot occur
    even during training.
    """
    
    def __init__(
        self,
        transformer: SOMASequenceOptimizer,
        config: Optional[TrainingConfig] = None
    ):
        self.transformer = transformer
        self.config = config or TrainingConfig()
        
        # Set seed for reproducibility
        if self.config.seed is not None:
            np.random.seed(self.config.seed)
            random.seed(self.config.seed)
        
        # Training state
        self.epoch = 0
        self.step = 0
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        
        # History
        self.train_losses: List[float] = []
        self.val_losses: List[float] = []
        
        # Symbol to ID mapping
        self.symbol_to_id: Dict[str, int] = {}
        self.id_to_symbol: Dict[int, str] = {}
    
    def set_vocabulary(self, vocabulary: List[str]):
        """Set vocabulary mapping."""
        self.symbol_to_id = {s: i for i, s in enumerate(sorted(vocabulary))}
        self.id_to_symbol = {v: k for k, v in self.symbol_to_id.items()}
        
        # Update transformer vocabulary
        self.transformer.set_vocabulary(self.symbol_to_id)
    
    def encode_sequence(self, tokens: List[str]) -> List[int]:
        """Encode tokens to IDs."""
        return [self.symbol_to_id.get(t, 0) for t in tokens]
    
    def decode_ids(self, ids: List[int]) -> List[str]:
        """Decode IDs to tokens."""
        return [self.id_to_symbol.get(i, "<UNK>") for i in ids]
    
    def compute_masked_loss(
        self,
        logits: np.ndarray,
        target_id: int,
        allowed_ids: List[int]
    ) -> Tuple[float, np.ndarray]:
        """
        Compute loss ONLY over allowed tokens.
        
        This is the critical function - it ensures the transformer
        never learns to prefer forbidden tokens.
        
        Args:
            logits: Raw logits from transformer, shape (vocab_size,)
            target_id: True target token ID
            allowed_ids: List of allowed token IDs
        
        Returns:
            (loss, gradient_mask)
        """
        # Create mask: 1 for allowed tokens, -inf for disallowed
        mask = np.full_like(logits, -np.inf, dtype=np.float32)
        mask[allowed_ids] = 0.0
        
        # Apply mask to logits
        masked_logits = logits + mask
        
        # Softmax over allowed tokens only
        exp_logits = np.exp(masked_logits - np.max(masked_logits))
        probs = exp_logits / np.sum(exp_logits[allowed_ids])
        
        # Cross-entropy loss (only if target is in allowed set)
        if target_id in allowed_ids:
            loss = -np.log(probs[target_id] + 1e-10)
        else:
            # Target not in allowed set (shouldn't happen, but handle gracefully)
            loss = 10.0  # High loss
        
        # Gradient mask (for backprop)
        gradient_mask = np.zeros_like(logits)
        gradient_mask[allowed_ids] = 1.0
        
        return float(loss), gradient_mask
    
    def compute_gradients(
        self,
        sequence: List[int],
        target_id: int,
        allowed_ids: List[int]
    ) -> Dict[str, np.ndarray]:
        """
        Compute gradients for one sequence.
        
        NOTE: This is a simplified implementation for demonstration.
        
        Full backpropagation through transformers requires:
        - Automatic differentiation (NumPy doesn't have built-in AD)
        - Proper chain rule through all layers (attention, feed-forward, norms)
        - Gradient clipping and normalization
        
        For Phase 3, we demonstrate the MASKED LOSS PRINCIPLE, which is
        the critical architectural component. The actual weight updates
        are simplified.
        
        A production implementation would need:
        - A custom AD system (or use JAX/Micrograd)
        - Full backprop through transformer blocks
        - Proper gradient accumulation and optimization
        
        The key principle demonstrated here is that loss is computed
        ONLY over allowed tokens, making hallucination structurally
        impossible even during training.
        """
        # Forward pass
        logits = self.transformer.forward(sequence)
        
        # Compute loss and mask
        loss, mask = self.compute_masked_loss(logits, target_id, allowed_ids)
        
        # Simplified gradient computation
        # In a full implementation, this would be automatic differentiation
        # For now, we'll use a simple approximation
        
        gradients = {}
        
        # For demonstration, we'll use finite differences approximation
        # In practice, you'd use automatic differentiation (NumPy doesn't have this built-in)
        # This is a placeholder - a real implementation would need a custom AD system
        # or use a library like JAX (but we're staying NumPy-only)
        
        # For now, we'll just return the mask as a signal
        # A full implementation would need proper backprop
        
        return {
            'loss': loss,
            'mask': mask,
            'logits': logits,
        }
    
    def train_step(
        self,
        batch: List[TrainingSequence]
    ) -> float:
        """
        Train on one batch.
        
        This is simplified - a full implementation would need
        proper backpropagation. For Phase 3 demo, we use
        a simplified update rule.
        """
        total_loss = 0.0
        
        for seq in batch:
            # Encode
            sequence_ids = self.encode_sequence(seq.tokens)
            target_id = self.symbol_to_id.get(seq.target, 0)
            allowed_ids = [self.symbol_to_id.get(t, 0) for t in seq.allowed_tokens]
            
            # Forward pass
            logits = self.transformer.forward(sequence_ids)
            
            # Compute masked loss
            loss, mask = self.compute_masked_loss(logits, target_id, allowed_ids)
            total_loss += loss
            
            # Simplified update (gradient descent on logits)
            # In a real implementation, this would update all transformer weights
            # For Phase 3, we demonstrate the masked loss principle
            
            # Compute target probability distribution
            target_probs = np.zeros_like(logits)
            if target_id in allowed_ids:
                target_probs[target_id] = 1.0
            
            # Simple update rule (approximate gradient descent)
            # This is a demonstration - full backprop would update all layers
            error = target_probs - (mask * np.exp(logits) / np.sum(np.exp(logits)[allowed_ids] + 1e-10))
            error = error * mask  # Only update allowed tokens
            
            # Update output projection (simplified - would need full backprop)
            # This is just a demonstration of the principle
            self.transformer.output_proj += self.config.learning_rate * error[:, np.newaxis] / len(batch)
        
        return total_loss / len(batch)
    
    def validate(self, val_sequences: List[TrainingSequence]) -> float:
        """Validate on validation set."""
        total_loss = 0.0
        
        for seq in val_sequences:
            sequence_ids = self.encode_sequence(seq.tokens)
            target_id = self.symbol_to_id.get(seq.target, 0)
            allowed_ids = [self.symbol_to_id.get(t, 0) for t in seq.allowed_tokens]
            
            # Forward pass
            logits = self.transformer.forward(sequence_ids)
            
            # Compute masked loss
            loss, _ = self.compute_masked_loss(logits, target_id, allowed_ids)
            total_loss += loss
        
        return total_loss / len(val_sequences)
    
    def train(
        self,
        train_sequences: List[TrainingSequence],
        val_sequences: Optional[List[TrainingSequence]] = None
    ):
        """
        Main training loop.
        
        Args:
            train_sequences: Training sequences
            val_sequences: Validation sequences (optional)
        """
        print("Starting training...")
        print(f"  Training sequences: {len(train_sequences)}")
        if val_sequences:
            print(f"  Validation sequences: {len(val_sequences)}")
        print(f"  Epochs: {self.config.num_epochs}")
        print(f"  Batch size: {self.config.batch_size}")
        print(f"  Learning rate: {self.config.learning_rate}")
        print()
        
        for epoch in range(self.config.num_epochs):
            self.epoch = epoch
            
            # Shuffle training data
            random.shuffle(train_sequences)
            
            # Batch training
            epoch_loss = 0.0
            num_batches = 0
            
            for i in range(0, len(train_sequences), self.config.batch_size):
                batch = train_sequences[i:i + self.config.batch_size]
                
                # Train step
                loss = self.train_step(batch)
                epoch_loss += loss
                num_batches += 1
                self.step += 1
                
                # Logging
                if self.step % self.config.log_every == 0:
                    print(f"  Step {self.step}: loss = {loss:.4f}")
            
            # Epoch average loss
            avg_loss = epoch_loss / num_batches
            self.train_losses.append(avg_loss)
            
            print(f"Epoch {epoch + 1}/{self.config.num_epochs}: train_loss = {avg_loss:.4f}")
            
            # Validation
            if val_sequences:
                val_loss = self.validate(val_sequences)
                self.val_losses.append(val_loss)
                print(f"  val_loss = {val_loss:.4f}")
                
                # Early stopping
                if val_loss < self.best_val_loss - self.config.min_delta:
                    self.best_val_loss = val_loss
                    self.patience_counter = 0
                    print(f"  ✓ Best validation loss: {val_loss:.4f}")
                else:
                    self.patience_counter += 1
                    if self.patience_counter >= self.config.patience:
                        print(f"  Early stopping (patience={self.config.patience})")
                        break
            
            print()
        
        print("Training complete!")
        print(f"  Final train loss: {self.train_losses[-1]:.4f}")
        if val_sequences:
            print(f"  Final val loss: {self.val_losses[-1]:.4f}")
            print(f"  Best val loss: {self.best_val_loss:.4f}")
    
    def save_checkpoint(self, path: str):
        """Save training checkpoint."""
        checkpoint = {
            'transformer_config': {
                'vocab_size': self.transformer.config.vocab_size,
                'd_model': self.transformer.config.d_model,
                'n_layers': self.transformer.config.n_layers,
                'n_heads': self.transformer.config.n_heads,
                'd_ff': self.transformer.config.d_ff,
            },
            'symbol_to_id': self.symbol_to_id,
            'training_config': {
                'learning_rate': self.config.learning_rate,
                'batch_size': self.config.batch_size,
            },
            'epoch': self.epoch,
            'step': self.step,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
        }
        
        # Note: In a full implementation, you'd also save transformer weights
        # For Phase 3 demo, we save metadata only
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"Checkpoint saved to {path}")
    
    def get_training_stats(self) -> Dict:
        """Get training statistics."""
        return {
            'epoch': self.epoch,
            'step': self.step,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'best_val_loss': self.best_val_loss,
            'num_parameters': self.transformer.count_parameters(),
        }


def create_trainer(
        transformer: Optional[SOMASequenceOptimizer] = None,
    vocab_size: int = 10000,
    d_model: int = 128,
    n_layers: int = 2,
    n_heads: int = 4
) -> SLMTrainer:
    """
    Factory function to create a trainer.
    
    Args:
        transformer: Optional existing transformer
        vocab_size: Vocabulary size (if creating new transformer)
        d_model: Model dimension
        n_layers: Number of layers
        n_heads: Number of heads
    """
    from .SOMA_sequence_optimizer import somaSequenceOptimizer, SOMASequenceConfig
    
    if transformer is None:
        config = SOMASequenceConfig(
            vocab_size=vocab_size,
            d_model=d_model,
            n_layers=n_layers,
            n_heads=n_heads,
            d_ff=d_model * 4,
        )
        transformer = SOMASequenceOptimizer(config)
    
    return SLMTrainer(transformer)

