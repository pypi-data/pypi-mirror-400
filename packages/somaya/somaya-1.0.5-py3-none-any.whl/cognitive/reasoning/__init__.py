"""
SOMA Cognitive - Reasoning Module
===================================

100% SOMA-native symbolic reasoning.
NO GPT. NO TRANSFORMERS. NO NEURAL NETWORKS. NO EXTERNAL AI.

Core Components:
- PathFinder: Find paths through knowledge graph
- QueryEngine: Execute complex queries
- Explainer: Generate human-readable explanations

Symbolic Reasoning:
- InferenceEngine: Rule chaining, transitivity, confidence propagation
- RuleBase: Inference rules (IS_A, PART_OF, CAUSES transitivity)
- ContradictionDetector: Find conflicts in knowledge

PURE SOMA (RECOMMENDED):
- SOMAReasoner: Complete reasoning + verbalization
- SOMAVerbalizer: Template-based text generation (NO neural)

Optional External Integration:
- HybridReasoner: For those who want LLM integration
"""

# Core reasoning
from .path_finder import PathFinder, ReasoningPath
from .query_engine import QueryEngine, QueryResult, QueryType
from .explainer import Explainer, Explanation

# Symbolic reasoning
from .rule_base import RuleBase, InferenceRule, RuleType
from .inference_engine import InferenceEngine, InferredFact, InferenceResult
from .contradiction_detector import (
    ContradictionDetector,
    Contradiction,
    ContradictionReport,
    ContradictionType,
)

# Hybrid reasoning (for external LLM integration if needed)
from .hybrid_reasoner import (
    HybridReasoner,
    HybridAnswer,
    StructuredContext,
    ContextType,
)

# PURE SOMA (NO external AI)
from .SOMA_verbalizer import somaVerbalizer, VerbalizationResult
from .SOMA_reasoner import somaReasoner, SOMAAnswer, StructuredKnowledge

__all__ = [
    # Core
    "PathFinder",
    "ReasoningPath",
    "QueryEngine",
    "QueryResult",
    "QueryType",
    "Explainer",
    "Explanation",
    
    # Symbolic
    "RuleBase",
    "InferenceRule",
    "RuleType",
    "InferenceEngine",
    "InferredFact",
    "InferenceResult",
    "ContradictionDetector",
    "Contradiction",
    "ContradictionReport",
    "ContradictionType",
    
    # Hybrid (optional external integration)
    "HybridReasoner",
    "HybridAnswer",
    "StructuredContext",
    "ContextType",
    
    # PURE SOMA (NO external AI) - RECOMMENDED
    "SOMAVerbalizer",
    "VerbalizationResult",
    "SOMAReasoner",
    "SOMAAnswer",
    "StructuredKnowledge",
]
