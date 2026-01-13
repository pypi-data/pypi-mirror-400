"""
SOMA SLM Training Data Generator

Generates training sequences from soma Cognitive knowledge.
This is SOMA-native only - no external corpora.

Key principle:
    Training data comes from facts, reasoning paths, and templates.
    The transformer learns ORDERING patterns, not facts.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import random
import re


@dataclass
class TrainingSequence:
    """A single training sequence."""
    tokens: List[str]  # Input sequence
    target: str        # Next token
    allowed_tokens: List[str]  # Set of allowed tokens at this position


class SOMADataGenerator:
    """
    Generates training sequences from soma knowledge.
    
    This creates sequences that:
    - Come from verified facts
    - Follow reasoning paths
    - Use only approved vocabulary
    - Maintain constraint boundaries
    """
    
    def __init__(self):
        self.facts: List[str] = []
        self.reasoning_paths: List[List[str]] = []
        self.vocabulary: set = set()
        self.rng = random.Random()
    
    def load_knowledge(
        self,
        facts: List[str],
        reasoning_paths: Optional[List[List[str]]] = None,
        relations: Optional[List[str]] = None
    ):
        """Load knowledge from soma Cognitive."""
        self.facts = facts
        self.reasoning_paths = reasoning_paths or []
        
        # Extract vocabulary
        self.vocabulary = set()
        for fact in facts:
            tokens = self._tokenize(fact)
            self.vocabulary.update(tokens)
        
        if relations:
            self.vocabulary.update(relations)
        
        # Add structural tokens
        structural = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were',
            'of', 'in', 'to', 'for', 'with', 'on', 'at',
            'and', 'or', 'but', 'not', 'no', 'yes',
            'that', 'this', 'it', 'they', 'we', 'you', 'i',
            '.', ',', '!', '?', ':', ';',
        }
        self.vocabulary.update(structural)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b|[.,!?:;]', text.lower())
        return tokens
    
    def generate_sequences_from_facts(
        self,
        max_length: int = 20,
        num_sequences: int = 100
    ) -> List[TrainingSequence]:
        """
        Generate training sequences from facts.
        
        Creates next-token prediction tasks from fact text.
        """
        sequences = []
        
        for _ in range(num_sequences):
            # Pick a random fact
            fact = self.rng.choice(self.facts)
            tokens = self._tokenize(fact)
            
            if len(tokens) < 2:
                continue
            
            # Create sequences of increasing length
            for prefix_len in range(1, min(len(tokens), max_length)):
                prefix = tokens[:prefix_len]
                target = tokens[prefix_len]
                
                # Allowed tokens = all tokens in vocabulary that appear in facts
                allowed = list(self.vocabulary)
                
                sequences.append(TrainingSequence(
                    tokens=prefix,
                    target=target,
                    allowed_tokens=allowed
                ))
        
        return sequences
    
    def generate_sequences_from_reasoning(
        self,
        num_sequences: int = 50
    ) -> List[TrainingSequence]:
        """
        Generate sequences from reasoning paths.
        
        This teaches the transformer about logical flow.
        """
        sequences = []
        
        for path in self.reasoning_paths:
            # Convert reasoning path to tokens
            path_tokens = []
            for step in path:
                tokens = self._tokenize(step)
                path_tokens.extend(tokens)
            
            if len(path_tokens) < 2:
                continue
            
            # Create sequences
            for i in range(1, len(path_tokens)):
                prefix = path_tokens[:i]
                target = path_tokens[i]
                
                sequences.append(TrainingSequence(
                    tokens=prefix,
                    target=target,
                    allowed_tokens=list(self.vocabulary)
                ))
        
        return sequences
    
    def generate_template_sequences(
        self,
        templates: List[str],
        num_per_template: int = 10
    ) -> List[TrainingSequence]:
        """
        Generate sequences from templates.
        
        Templates are patterns like:
        - "X is a Y"
        - "X uses Y"
        - "X was created by Y"
        
        This teaches common grammatical patterns.
        """
        sequences = []
        
        for template in templates:
            template_tokens = self._tokenize(template)
            
            for _ in range(num_per_template):
                # Fill template with vocabulary tokens
                filled = []
                for token in template_tokens:
                    if token in ['x', 'y', 'z']:  # Placeholder
                        # Fill with random vocabulary token
                        filled.append(self.rng.choice(list(self.vocabulary)))
                    else:
                        filled.append(token)
                
                # Create sequences
                for i in range(1, len(filled)):
                    prefix = filled[:i]
                    target = filled[i]
                    
                    sequences.append(TrainingSequence(
                        tokens=prefix,
                        target=target,
                        allowed_tokens=list(self.vocabulary)
                    ))
        
        return sequences
    
    def generate_all(
        self,
        templates: Optional[List[str]] = None,
        num_fact_sequences: int = 100,
        num_reasoning_sequences: int = 50,
        num_template_sequences: int = 50
    ) -> List[TrainingSequence]:
        """
        Generate all training sequences.
        
        Combines sequences from facts, reasoning paths, and templates.
        """
        all_sequences = []
        
        # From facts
        fact_sequences = self.generate_sequences_from_facts(
            num_sequences=num_fact_sequences
        )
        all_sequences.extend(fact_sequences)
        
        # From reasoning paths
        if self.reasoning_paths:
            reasoning_sequences = self.generate_sequences_from_reasoning(
                num_sequences=num_reasoning_sequences
            )
            all_sequences.extend(reasoning_sequences)
        
        # From templates
        if templates:
            template_sequences = self.generate_template_sequences(
                templates=templates,
                num_per_template=num_template_sequences
            )
            all_sequences.extend(template_sequences)
        
        # Shuffle
        self.rng.shuffle(all_sequences)
        
        return all_sequences
    
    def split_train_val(
        self,
        sequences: List[TrainingSequence],
        val_ratio: float = 0.1
    ) -> Tuple[List[TrainingSequence], List[TrainingSequence]]:
        """Split sequences into train and validation."""
        split_idx = int(len(sequences) * (1 - val_ratio))
        train = sequences[:split_idx]
        val = sequences[split_idx:]
        return train, val


def create_default_templates() -> List[str]:
    """
    Default templates for common patterns.
    
    These are syntactic patterns only - no semantic content.
    """
    return [
        "X is a Y",
        "X uses Y",
        "X was created by Y",
        "X is used for Y",
        "X has Y",
        "X supports Y",
        "X is part of Y",
        "X contains Y",
        "X can Y",
        "X does Y",
    ]


def create_training_data(
    facts: List[str],
    reasoning_paths: Optional[List[List[str]]] = None,
    templates: Optional[List[str]] = None,
    num_sequences: int = 1000
) -> Tuple[List[TrainingSequence], List[TrainingSequence]]:
    """
    Convenience function to create training data.
    
    Args:
        facts: Facts from soma Cognitive
        reasoning_paths: Reasoning paths (optional)
        templates: Template patterns (optional, uses defaults if None)
        num_sequences: Total number of sequences to generate
    
    Returns:
        (train_sequences, val_sequences)
    """
    generator = SOMADataGenerator()
    generator.load_knowledge(facts, reasoning_paths)
    
    if templates is None:
        templates = create_default_templates()
    
    # Generate sequences
    all_sequences = generator.generate_all(
        templates=templates,
        num_fact_sequences=num_sequences // 2,
        num_reasoning_sequences=num_sequences // 4,
        num_template_sequences=num_sequences // 4,
    )
    
    # Split
    train, val = generator.split_train_val(all_sequences)
    
    return train, val

