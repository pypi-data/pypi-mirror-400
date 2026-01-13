"""
SOMA SLM - Small Language Model

A constrained language generation system that can ONLY emit tokens
sanctioned by SOMA Cognitive. Hallucination is structurally impossible,
not statistically unlikely.

Architecture:
    SOMA Cognitive (THINKS) → facts, constraints, reasoning path
    SOMA SLM (TALKS)        → constrained verbalization ONLY

NumPy is used strictly as a numerical backend.
No pretrained models. No ML frameworks. 100% soma.
"""

from .slm_constraints import (
    TokenConstraint,
    FactConstraint,
    VocabularyScope,
    ConstraintEngine,
)

from .slm_generator import (
    ConstrainedGenerator,
    GenerationConfig,
    GenerationResult,
    SOMASLM,
)

from .SOMA_sequence_optimizer import (
    SOMASequenceOptimizer,
    SOMASequenceConfig,
    create_SOMA_sequence_optimizer,
)

from .slm_constrained_decoder import (
    ConstrainedDecoder,
    DecoderConfig,
    SOMAConstrainedSLM,
    create_SOMA_constrained_slm,
)

from .training_data import (
    TrainingSequence,
    SOMADataGenerator,
    create_training_data,
    create_default_templates,
)

from .slm_trainer import (
    SLMTrainer,
    TrainingConfig,
    create_trainer,
)

__all__ = [
    # Constraints
    'TokenConstraint',
    'FactConstraint',
    'VocabularyScope',
    'ConstraintEngine',
    # Phase 1 Generator
    'ConstrainedGenerator',
    'GenerationConfig',
    'GenerationResult',
    'SOMASLM',
    # Phase 2 Sequence Optimizer
    'SOMASequenceOptimizer',
    'SOMASequenceConfig',
    'create_SOMA_sequence_optimizer',
    # Phase 2 Decoder
    'ConstrainedDecoder',
    'DecoderConfig',
    'SOMAConstrainedSLM',
    'create_SOMA_constrained_slm',
    # Phase 3 Training
    'TrainingSequence',
    'SOMADataGenerator',
    'create_training_data',
    'create_default_templates',
    'SLMTrainer',
    'TrainingConfig',
    'create_trainer',
]

