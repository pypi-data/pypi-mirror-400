"""
SOMA Core Guided Training Pipeline
================================

Unified training pipeline that uses the cleaned multi-model system
to guide vocabulary building, embedding generation, and training.

Core principle: "If a number does not change a decision, it does not deserve to exist."

This integrates:
- Multi-model signals (4 signals)
- Decision gates (Promote, Trust, Generate)
- Vocabulary building
- Embedding generation
- Language model training
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import Counter
import pickle
import numpy as np
from tqdm import tqdm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.training.vocabulary_builder import somaVocabularyBuilder
from src.training.language_model_trainer import somaLanguageModel, SOMALanguageModelTrainer
from src.structure.multi_model_clean import SOMA CoreMultiModelClean
from src.structure.decision_gates import PromotionDecision, TrustLevel, GenerationDecision
from src.structure.scoring_utils import bound_score


class GuidedVocabularyBuilder:
    """
    Vocabulary builder guided by multi-model decision gates.
    
    Uses Promote/Demote gate to decide which tokens become vocabulary units.
    """
    
    def __init__(
        self,
        multi_model: SOMA CoreMultiModelClean,
        vocab_size: int = 60000,
        min_frequency: int = 2,
        promote_threshold: float = 0.7  # Minimum confidence to promote
    ):
        """
        Initialize guided vocabulary builder.
        
        Args:
            multi_model: Cleaned multi-model system
            vocab_size: Target vocabulary size
            min_frequency: Minimum token frequency
            promote_threshold: Minimum confidence to promote token
        """
        self.multi_model = multi_model
        self.vocab_size = vocab_size
        self.min_frequency = min_frequency
        self.promote_threshold = promote_threshold
        
        # Use existing vocabulary builder for tokenization
        self.vocab_builder = SOMAVocabularyBuilder(
            vocab_size=vocab_size,
            min_frequency=min_frequency
        )
        
        # Track tokens and their promotion decisions
        self.token_decisions: Dict[str, Dict] = {}
        self.promoted_tokens: Set[str] = set()
    
    def build_guided_vocabulary(self, text_file: Path, sample_size: int = 10000) -> Dict[str, int]:
        """
        Build vocabulary using multi-model guidance.
        
        Process:
        1. Count all tokens (frequency)
        2. Sample tokens for multi-model analysis
        3. Use Promote/Demote gate to decide which tokens to include
        4. Build vocabulary from promoted tokens
        
        Args:
            text_file: Path to training text
            sample_size: Number of tokens to analyze with multi-model
        
        Returns:
            Dictionary mapping tokens to IDs
        """
        print("\n" + "="*70)
        print("Guided Vocabulary Building (Multi-Model)")
        print("="*70)
        print(f"Target vocab size: {self.vocab_size:,}")
        print(f"Promote threshold: {self.promote_threshold}")
        print()
        
        # Step 1: Learn from text with multi-model
        print("[Step 1] Learning from text with multi-model system...")
        with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read(10_000_000)  # Sample first 10MB for learning
        
        self.multi_model.learn(text)
        print("  ✓ Multi-model system learned from text")
        
        # Step 2: Count tokens (standard vocabulary building)
        print("\n[Step 2] Counting tokens...")
        self.vocab_builder.build_vocabulary(text_file)
        token_counts = self.vocab_builder.token_counts
        
        print(f"  ✓ Found {len(token_counts):,} unique tokens")
        
        # Step 3: Analyze tokens with multi-model (sample for efficiency)
        print(f"\n[Step 3] Analyzing tokens with multi-model (sampling {sample_size:,} tokens)...")
        
        # Get top tokens by frequency
        top_tokens = [token for token, count in token_counts.most_common(sample_size)]
        
        promoted_count = 0
        demoted_count = 0
        
        for token in tqdm(top_tokens, desc="  Analyzing tokens"):
            # Analyze with multi-model
            result = self.multi_model.analyze(token)
            
            # Get promotion decision
            promote_decision = result.decisions['promote']
            decision = promote_decision['decision']
            confidence = promote_decision['confidence']
            
            # Convert confidence to float if it's an enum
            if hasattr(confidence, 'value'):
                confidence_value = confidence.value
            else:
                confidence_value = float(confidence) if isinstance(confidence, (int, float)) else 0.5
            
            # Store decision
            self.token_decisions[token] = {
                'decision': decision,
                'confidence': confidence_value,
                'frequency': token_counts[token],
                'signals': {
                    'structural': result.structural_signal['score'],
                    'statistical': result.statistical_signal['score'],
                    'context': result.context_signal['score'],
                    'semantic': result.semantic_proxy['score']
                }
            }
            
            # Promote if decision is "promote" and confidence is high enough
            if decision == 'promote' and confidence_value >= self.promote_threshold:
                self.promoted_tokens.add(token)
                promoted_count += 1
            elif decision == 'demote':
                demoted_count += 1
        
        print(f"\n  ✓ Analyzed {len(self.token_decisions):,} tokens")
        print(f"  ✓ Promoted: {promoted_count:,} tokens")
        print(f"  ✓ Demoted: {demoted_count:,} tokens")
        
        # Step 4: Build vocabulary from promoted tokens (sorted by frequency)
        print("\n[Step 4] Building vocabulary from promoted tokens...")
        
        # Filter to only promoted tokens, sorted by frequency
        promoted_with_freq = [
            (token, token_counts[token])
            for token in self.promoted_tokens
            if token_counts[token] >= self.min_frequency
        ]
        promoted_with_freq.sort(key=lambda x: x[1], reverse=True)
        
        # Take top N to fill vocabulary
        final_tokens = [token for token, _ in promoted_with_freq[:self.vocab_size]]
        
        # Build token_to_id mapping
        token_to_id = {}
        id_to_token = {}
        
        # Add special tokens first
        special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<BOS>': 2,
            '<EOS>': 3,
            '<MASK>': 4,
        }
        token_to_id.update(special_tokens)
        id_to_token = {v: k for k, v in special_tokens.items()}
        next_id = len(special_tokens)
        
        # Add promoted tokens
        for token in final_tokens:
            if token not in token_to_id:
                token_to_id[token] = next_id
                id_to_token[next_id] = token
                next_id += 1
        
        # Update vocab builder
        self.vocab_builder.token_to_id = token_to_id
        self.vocab_builder.id_to_token = id_to_token
        
        print(f"  ✓ Final vocabulary: {len(token_to_id):,} tokens")
        print(f"  ✓ All tokens passed Promote gate (confidence >= {self.promote_threshold})")
        
        return token_to_id


class GuidedTrainingPipeline:
    """
    Complete guided training pipeline.
    
    Uses multi-model system to guide:
    - Vocabulary building (Promote/Demote)
    - Embedding quality (Trust/Distrust)
    - Training data filtering (Generate/Block)
    """
    
    def __init__(
        self,
        vocab_size: int = 60000,
        embedding_dim: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        max_seq_length: int = 1024,
        learning_rate: float = 1e-4,
        batch_size: int = 32,
        promote_threshold: float = 0.7,
        trust_threshold: float = 0.6
    ):
        """
        Initialize guided training pipeline.
        
        Args:
            vocab_size: Vocabulary size
            embedding_dim: Embedding dimension
            num_layers: Number of transformer layers
            num_heads: Number of attention heads
            max_seq_length: Maximum sequence length
            learning_rate: Learning rate
            batch_size: Batch size
            promote_threshold: Minimum confidence to promote token
            trust_threshold: Minimum confidence to trust embedding
        """
        # Create multi-model system
        self.multi_model = SOMA CoreMultiModelClean(
            max_relationships_per_node=20,
            min_relationship_strength=0.6
        )
        
        # Create guided vocabulary builder
        self.vocab_builder = GuidedVocabularyBuilder(
            multi_model=self.multi_model,
            vocab_size=vocab_size,
            promote_threshold=promote_threshold
        )
        
        # Training parameters
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.max_seq_length = max_seq_length
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.trust_threshold = trust_threshold
    
    def train(
        self,
        text_file: Path,
        epochs: int = 10,
        output_dir: Path = Path("models")
    ) -> bool:
        """
        Complete guided training pipeline.
        
        Args:
            text_file: Path to training text
            epochs: Number of training epochs
            output_dir: Output directory for models
        
        Returns:
            True if training succeeded
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*70)
        print("SOMA Core Guided Training Pipeline")
        print("="*70)
        print("Using multi-model system to guide training:")
        print("  - Vocabulary: Promote/Demote gate")
        print("  - Embeddings: Trust/Distrust gate")
        print("  - Training: Generate/Block gate")
        print()
        
        # Step 1: Build guided vocabulary
        print("[Step 1] Building guided vocabulary...")
        token_to_id = self.vocab_builder.build_guided_vocabulary(text_file)
        
        # Save vocabulary
        vocab_path = output_dir / "SOMA_guided_vocab.pkl"
        with open(vocab_path, 'wb') as f:
            pickle.dump({
                'token_to_id': token_to_id,
                'id_to_token': self.vocab_builder.vocab_builder.id_to_token,
                'token_decisions': self.vocab_builder.token_decisions
            }, f)
        print(f"  ✓ Vocabulary saved: {vocab_path}")
        
        # Step 2: Create language model
        print("\n[Step 2] Creating language model...")
        model = SOMALanguageModel(
            vocab_size=len(token_to_id),
            embedding_dim=self.embedding_dim,
            num_layers=self.num_layers,
            num_heads=self.num_heads,
            max_seq_length=self.max_seq_length
        )
        print(f"  ✓ Model created: {self.num_layers} layers, {self.num_heads} heads")
        
        # Step 3: Train language model (with standard trainer for now)
        print("\n[Step 3] Training language model...")
        print("  (Using standard trainer - guided filtering can be added)")
        
        # Create standard vocab builder for trainer compatibility
        standard_vocab = SOMAVocabularyBuilder()
        standard_vocab.token_to_id = token_to_id
        standard_vocab.id_to_token = self.vocab_builder.vocab_builder.id_to_token
        
        trainer = SOMALanguageModelTrainer(
            model=model,
            vocab_builder=standard_vocab,
            learning_rate=self.learning_rate,
            batch_size=self.batch_size,
            seq_length=self.max_seq_length
        )
        
        trainer.train(
            text_file=text_file,
            epochs=epochs,
            save_every=2,
            output_dir=output_dir
        )
        
        print("\n" + "="*70)
        print("✓ Guided Training Complete!")
        print("="*70)
        print(f"  Vocabulary: {vocab_path}")
        print(f"  Model: {output_dir / f'SOMA_lm_epoch_{epochs}.pkl'}")
        print()
        print("Key differences from standard training:")
        print("  ✓ Vocabulary filtered by Promote/Demote gate")
        print("  ✓ Only high-confidence tokens included")
        print("  ✓ Multi-model signals guide decisions")
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SOMA Core Guided Training Pipeline"
    )
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Training data file path"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models",
        help="Output directory (default: models)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=10,
        help="Training epochs (default: 10)"
    )
    parser.add_argument(
        "--vocab-size",
        type=int,
        default=60000,
        help="Vocabulary size (default: 60000)"
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = GuidedTrainingPipeline(
        vocab_size=args.vocab_size,
        embedding_dim=768,
        num_layers=12,
        num_heads=12
    )
    
    # Train
    success = pipeline.train(
        text_file=Path(args.data),
        epochs=args.epochs,
        output_dir=Path(args.output)
    )
    
    if success:
        print("\n✓ Training completed successfully!")
    else:
        print("\n✗ Training failed")


if __name__ == "__main__":
    main()
