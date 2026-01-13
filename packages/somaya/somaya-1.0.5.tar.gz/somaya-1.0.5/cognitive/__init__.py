"""
SOMA Cognitive System
=======================

A cognitive knowledge system that adds:
- Knowledge Graph (nodes + edges + inference)
- Concept Trees (hierarchical organization)
- Unified Memory (links vectors + graphs + trees)
- Symbolic Reasoning (rule chaining, transitivity, contradictions)
- Hybrid Reasoning (symbolic cognition → neural verbalization)
- Integration Layer (bridges to src)

This is a SEPARATE module from src.
It imports from src but never modifies it.

Quick Start (Standalone):
    from soma_cognitive import UnifiedMemory, RelationType, HybridReasoner
    
    memory = UnifiedMemory()
    t1 = memory.add("Dog is a mammal", "fact", auto_link_graph=True)
    t2 = memory.add("Mammal is an animal", "fact", auto_link_graph=True)
    memory.add_relation(t1.uid, t2.uid, RelationType.IS_A)
    
    reasoner = HybridReasoner(memory)
    answer = reasoner.answer("What is a dog?")

Full Integration (with src):
    from soma_cognitive import CognitivePipeline
    from src.core.core_tokenizer import TextTokenizationEngine
    from src.embeddings.embedding_generator import somaEmbeddingGenerator
    
    pipeline = CognitivePipeline()
    pipeline.set_tokenizer(TextTokenizationEngine())
    pipeline.set_embedding_generator(SOMAEmbeddingGenerator())
    
    # Process knowledge
    pipeline.process("Transformers use attention mechanisms")
    pipeline.process("Attention computes weighted sums")
    
    # Query
    answer = pipeline.query("How does attention work?")
    print(answer.answer)
    print(answer.explain())

Architecture:
    Text → Tokenizer → Graph + Embeddings → Inference → Context → LLM → Answer
    
    The LLM becomes a SPEAKER, not a THINKER.
    SOMA Cognitive does the reasoning; LLM just verbalizes.
"""

__version__ = "0.3.0"
__author__ = "Santosh Chavala"

# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH
# ═══════════════════════════════════════════════════════════════════════════════
from .graph import (
    GraphNode,
    GraphEdge,
    GraphStore,
    RelationType,
    RelationExtractor,
    ExtractedRelation,
)

# ═══════════════════════════════════════════════════════════════════════════════
# TREES
# ═══════════════════════════════════════════════════════════════════════════════
from .trees import (
    TreeNode,
    Tree,
    TreeStore,
)

# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY
# ═══════════════════════════════════════════════════════════════════════════════
from .memory import (
    MemoryObject,
    UnifiedMemory,
)

# ═══════════════════════════════════════════════════════════════════════════════
# REASONING - Core
# ═══════════════════════════════════════════════════════════════════════════════
from .reasoning import (
    PathFinder,
    ReasoningPath,
    QueryEngine,
    QueryResult,
    Explainer,
    Explanation,
)

# ═══════════════════════════════════════════════════════════════════════════════
# REASONING - Symbolic
# ═══════════════════════════════════════════════════════════════════════════════
from .reasoning import (
    RuleBase,
    InferenceRule,
    RuleType,
    InferenceEngine,
    InferredFact,
    ContradictionDetector,
    Contradiction,
    ContradictionType,
)

# ═══════════════════════════════════════════════════════════════════════════════
# REASONING - PURE SOMA (RECOMMENDED - NO external AI)
# ═══════════════════════════════════════════════════════════════════════════════
from .reasoning import (
    SOMAReasoner,
    SOMAAnswer,
    SOMAVerbalizer,
    StructuredKnowledge,
)

# ═══════════════════════════════════════════════════════════════════════════════
# REASONING - Hybrid (optional external integration)
# ═══════════════════════════════════════════════════════════════════════════════
from .reasoning import (
    HybridReasoner,
    HybridAnswer,
    StructuredContext,
)

# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION (bridges to src)
# ═══════════════════════════════════════════════════════════════════════════════
from .integration import (
    TokenBridge,
    VectorBridge,
    EmbeddingBridge,
    CognitivePipeline,
)

# ═══════════════════════════════════════════════════════════════════════════════
# ALGORITHMS - SOMA-ORIGINAL (100% UNIQUE)
# ═══════════════════════════════════════════════════════════════════════════════
from .algorithms import (
    # Ranking
    SOMARanker,
    RankingResult,
    # Pattern Matching
    SOMAPatternMatcher,
    PatternMatch,
    # 9-Centric
    SOMA9Scorer,
    # Graph Walking
    SOMAGraphWalker,
    WalkResult,
    WalkMode,
    # Semantic Similarity
    SOMASimilarity,
    SimilarityResult,
    # Query Parsing
    SOMAQueryParser,
    ParsedQuery,
)

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
from .utils import (
    ExplanationScorer,
    ContextScorer,
    ContextFormatter,
    PromptBuilder,
    KnowledgeValidator,
)

__all__ = [
    # Version
    "__version__",
    
    # Graph
    "GraphNode",
    "GraphEdge",
    "GraphStore",
    "RelationType",
    "RelationExtractor",
    "ExtractedRelation",
    
    # Trees
    "TreeNode",
    "Tree",
    "TreeStore",
    
    # Memory
    "MemoryObject",
    "UnifiedMemory",
    
    # Reasoning - Core
    "PathFinder",
    "ReasoningPath",
    "QueryEngine",
    "QueryResult",
    "Explainer",
    "Explanation",
    
    # Reasoning - Symbolic
    "RuleBase",
    "InferenceRule",
    "RuleType",
    "InferenceEngine",
    "InferredFact",
    "ContradictionDetector",
    "Contradiction",
    "ContradictionType",
    
    # Reasoning - PURE SOMA (RECOMMENDED)
    "SOMAReasoner",
    "SOMAAnswer",
    "SOMAVerbalizer",
    "StructuredKnowledge",
    
    # Reasoning - Hybrid (optional)
    "HybridReasoner",
    "HybridAnswer",
    "StructuredContext",
    
    # Integration
    "TokenBridge",
    "VectorBridge",
    "EmbeddingBridge",
    "CognitivePipeline",
    
    # Algorithms - SOMA-ORIGINAL
    "SOMARanker",
    "RankingResult",
    "SOMAPatternMatcher",
    "PatternMatch",
    "SOMA9Scorer",
    "SOMAGraphWalker",
    "WalkResult",
    "WalkMode",
    "SOMASimilarity",
    "SimilarityResult",
    "SOMAQueryParser",
    "ParsedQuery",
    
    # Utilities
    "ExplanationScorer",
    "ContextScorer",
    "ContextFormatter",
    "PromptBuilder",
    "KnowledgeValidator",
]
