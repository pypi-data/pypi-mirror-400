"""
SOMA Structure System
=======================

Complete structure system for SOMA:
- Symbol structures (foundation)
- Pattern building (combinations)
- Hierarchical structure (symbols → patterns → units → meaning)
- SOMA integration
- Advanced pattern analysis
- Structure optimization

This is the foundation layer: structure enables meaning, doesn't define it!
"""

from .symbol_structures import (
    SymbolClass,
    SymbolStructure,
    SymbolRegistry,
    get_registry,
    classify_symbol,
    is_letter,
    is_digit,
    is_math_symbol
)

from .pattern_builder import (
    Pattern,
    PatternBuilder,
    build_patterns_from_SOMA_tokens
)

from .structure_hierarchy import (
    StructureLevel,
    StructureNode,
    StructureHierarchy,
    build_hierarchy_from_SOMA
)

from .SOMA_integration import (
    SOMAStructureIntegrator,
    integrate_structure_with_SOMA_tokens,
    get_structure_priorities
)

from .advanced_patterns import (
    PatternRelationship,
    PatternAnalyzer
)

from .structure_optimizer import (
    StructureCache,
    StructureIndex,
    StructureOptimizer
)

from .structure_enhanced_tokenizer import (
    StructureEnhancedTokenizer,
    tokenize_with_structure
)

from .deep_reasoning import (
    Perspective,
    StructuralInsight,
    Relationship as ReasoningRelationship,
    StructuralAnalyzer,
    SemanticAnalyzer,
    FrequencyAnalyzer,
    ContextualAnalyzer,
    TemporalAnalyzer,
    RelationalAnalyzer,
    DeepStructuralReasoner
)

from .relationship_graph import (
    GraphNode,
    GraphEdge,
    RelationshipGraph
)

from .fluency_understanding import (
    UnderstandingScore,
    SymbolUnderstanding,
    PatternUnderstanding,
    DataUnderstanding,
    FluencyEnhancer
)

from .multi_model import (
    MultiModelOutput,
    SOMA CoreMultiModel
)

__all__ = [
    # Symbol structures
    "SymbolClass",
    "SymbolStructure",
    "SymbolRegistry",
    "get_registry",
    "classify_symbol",
    "is_letter",
    "is_digit",
    "is_math_symbol",
    
    # Pattern building
    "Pattern",
    "PatternBuilder",
    "build_patterns_from_SOMA_tokens",
    
    # Hierarchy
    "StructureLevel",
    "StructureNode",
    "StructureHierarchy",
    "build_hierarchy_from_SOMA",
    
    # SOMA integration
    "SOMAStructureIntegrator",
    "integrate_structure_with_SOMA_tokens",
    "get_structure_priorities",
    
    # Advanced patterns
    "PatternRelationship",
    "PatternAnalyzer",
    
    # Optimization
    "StructureCache",
    "StructureIndex",
    "StructureOptimizer",
    
    # Enhanced tokenization
    "StructureEnhancedTokenizer",
    "tokenize_with_structure",
    
    # Deep reasoning
    "Perspective",
    "StructuralInsight",
    "ReasoningRelationship",
    "StructuralAnalyzer",
    "SemanticAnalyzer",
    "FrequencyAnalyzer",
    "ContextualAnalyzer",
    "TemporalAnalyzer",
    "RelationalAnalyzer",
    "DeepStructuralReasoner",
    
    # Relationship graph
    "GraphNode",
    "GraphEdge",
    "RelationshipGraph",
    
    # Fluency and understanding
    "UnderstandingScore",
    "SymbolUnderstanding",
    "PatternUnderstanding",
    "DataUnderstanding",
    "FluencyEnhancer",
    
    # Multi-model
    "MultiModelOutput",
    "SOMA CoreMultiModel",
]
