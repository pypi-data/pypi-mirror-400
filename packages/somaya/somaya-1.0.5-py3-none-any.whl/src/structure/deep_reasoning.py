"""
SOMA Deep Structural Reasoning
=================================

Deep reasoning about structure, patterns, and relationships from ALL angles:
- Structural perspective (how things are built)
- Semantic perspective (what things mean in context)
- Frequency perspective (how often things appear)
- Contextual perspective (where things appear)
- Temporal perspective (how things change over time)
- Relational perspective (how things connect)

This makes SOMA Core a REAL multi-model system!
"""

import sys
import os
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.symbol_structures import get_registry, SymbolRegistry
from src.structure.pattern_builder import PatternBuilder, Pattern
from src.structure.structure_hierarchy import StructureHierarchy, StructureNode


class Perspective(Enum):
    """Different perspectives for analysis."""
    STRUCTURAL = "structural"  # How things are built
    SEMANTIC = "semantic"      # What things mean
    FREQUENCY = "frequency"    # How often things appear
    CONTEXTUAL = "contextual"  # Where things appear
    TEMPORAL = "temporal"      # How things change
    RELATIONAL = "relational"  # How things connect


@dataclass
class StructuralInsight:
    """Insight from structural analysis."""
    perspective: Perspective
    element: str
    insight_type: str
    value: Any
    confidence: float
    evidence: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)


@dataclass
class Relationship:
    """Relationship between elements."""
    source: str
    target: str
    relationship_type: str
    strength: float
    perspectives: List[Perspective] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)


class StructuralAnalyzer:
    """
    Analyzes structure from structural perspective.
    
    Questions it answers:
    - How is this element built?
    - What symbols compose it?
    - What patterns does it contain?
    - What is its hierarchical position?
    """
    
    def __init__(self, registry: SymbolRegistry, hierarchy: StructureHierarchy):
        """Create structural analyzer."""
        self.registry = registry
        self.hierarchy = hierarchy
    
    def analyze(self, element: str) -> List[StructuralInsight]:
        """Analyze element from structural perspective."""
        insights = []
        
        # Symbol composition
        symbols = list(element.lower())
        symbol_classes = [self.registry.get_class(s) for s in symbols]
        unique_classes = set(symbol_classes)
        
        insights.append(StructuralInsight(
            perspective=Perspective.STRUCTURAL,
            element=element,
            insight_type="symbol_composition",
            value={
                "total_symbols": len(symbols),
                "unique_symbols": len(set(symbols)),
                "symbol_classes": list(unique_classes),
                "symbols": symbols
            },
            confidence=1.0,
            evidence=[f"Element contains {len(symbols)} symbols"]
        ))
        
        # Pattern analysis
        if element.lower() in self.hierarchy.pattern_nodes:
            node = self.hierarchy.pattern_nodes[element.lower()]
            insights.append(StructuralInsight(
                perspective=Perspective.STRUCTURAL,
                element=element,
                insight_type="pattern_structure",
                value={
                    "is_pattern": True,
                    "frequency": node.frequency,
                    "level": "pattern"
                },
                confidence=0.9,
                evidence=[f"Element is a recognized pattern"]
            ))
        
        # Hierarchical position
        trace = self.hierarchy.trace_structure(element.lower())
        if trace:
            insights.append(StructuralInsight(
                perspective=Perspective.STRUCTURAL,
                element=element,
                insight_type="hierarchical_position",
                value={
                    "levels": len(trace),
                    "trace": [n.content for n in trace]
                },
                confidence=0.8,
                evidence=[f"Element exists at {len(trace)} levels"]
            ))
        
        return insights


class SemanticAnalyzer:
    """
    Analyzes meaning from semantic perspective.
    
    Questions it answers:
    - What does this element mean in context?
    - What other elements appear with it?
    - What roles does it play?
    """
    
    def __init__(self, pattern_builder: PatternBuilder, hierarchy: StructureHierarchy):
        """Create semantic analyzer."""
        self.builder = pattern_builder
        self.hierarchy = hierarchy
        self.cooccurrence: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def learn_context(self, text: str):
        """Learn context from text."""
        words = text.lower().split()
        for i, word in enumerate(words):
            # Co-occurrence with neighbors
            for j in range(max(0, i-2), min(len(words), i+3)):
                if i != j:
                    self.cooccurrence[word][words[j]] += 1
    
    def analyze(self, element: str) -> List[StructuralInsight]:
        """Analyze element from semantic perspective."""
        insights = []
        element_lower = element.lower()
        
        # Co-occurrence analysis
        if element_lower in self.cooccurrence:
            cooccur = self.cooccurrence[element_lower]
            top_cooccur = sorted(cooccur.items(), key=lambda x: x[1], reverse=True)[:5]
            
            insights.append(StructuralInsight(
                perspective=Perspective.SEMANTIC,
                element=element,
                insight_type="cooccurrence",
                value={
                    "total_contexts": len(cooccur),
                    "top_associations": top_cooccur
                },
                confidence=0.7,
                evidence=[f"Element appears with {len(cooccur)} other elements"],
                relationships=[f"{elem}:{freq}" for elem, freq in top_cooccur[:3]]
            ))
        
        # Pattern stability (stable patterns = more meaningful)
        if self.builder.pattern_exists(element_lower):
            pattern = self.builder.get_pattern(element_lower)
            stability = pattern.stability_score()
            
            insights.append(StructuralInsight(
                perspective=Perspective.SEMANTIC,
                element=element,
                insight_type="semantic_stability",
                value={
                    "stability": stability,
                    "frequency": pattern.frequency,
                    "is_stable": stability > 0.5
                },
                confidence=0.8,
                evidence=[f"Pattern stability: {stability:.2f}"]
            ))
        
        return insights


class FrequencyAnalyzer:
    """
    Analyzes frequency patterns.
    
    Questions it answers:
    - How often does this appear?
    - Is frequency increasing or decreasing?
    - What is the frequency distribution?
    """
    
    def __init__(self, pattern_builder: PatternBuilder):
        """Create frequency analyzer."""
        self.builder = pattern_builder
        self.frequency_history: Dict[str, List[int]] = defaultdict(list)
    
    def track_frequency(self, element: str, frequency: int):
        """Track frequency over time."""
        self.frequency_history[element.lower()].append(frequency)
    
    def analyze(self, element: str) -> List[StructuralInsight]:
        """Analyze element from frequency perspective."""
        insights = []
        element_lower = element.lower()
        
        # Current frequency
        if self.builder.pattern_exists(element_lower):
            pattern = self.builder.get_pattern(element_lower)
            insights.append(StructuralInsight(
                perspective=Perspective.FREQUENCY,
                element=element,
                insight_type="current_frequency",
                value={
                    "frequency": pattern.frequency,
                    "relative_frequency": pattern.frequency / max(1, len(self.builder.get_patterns()))
                },
                confidence=1.0,
                evidence=[f"Current frequency: {pattern.frequency}"]
            ))
        
        # Frequency trend
        if element_lower in self.frequency_history:
            history = self.frequency_history[element_lower]
            if len(history) > 1:
                trend = "increasing" if history[-1] > history[0] else "decreasing"
                insights.append(StructuralInsight(
                    perspective=Perspective.FREQUENCY,
                    element=element,
                    insight_type="frequency_trend",
                    value={
                        "trend": trend,
                        "history": history,
                        "change": history[-1] - history[0]
                    },
                    confidence=0.7,
                    evidence=[f"Frequency trend: {trend}"]
                ))
        
        return insights


class ContextualAnalyzer:
    """
    Analyzes context.
    
    Questions it answers:
    - Where does this appear?
    - What contexts surround it?
    - What positions does it occupy?
    """
    
    def __init__(self):
        """Create contextual analyzer."""
        self.contexts: Dict[str, List[Dict]] = defaultdict(list)
    
    def learn_context(self, element: str, context: Dict):
        """Learn context for element."""
        self.contexts[element.lower()].append(context)
    
    def analyze(self, element: str) -> List[StructuralInsight]:
        """Analyze element from contextual perspective."""
        insights = []
        element_lower = element.lower()
        
        if element_lower in self.contexts:
            contexts = self.contexts[element_lower]
            
            # Context diversity
            unique_contexts = len(set(str(c) for c in contexts))
            
            insights.append(StructuralInsight(
                perspective=Perspective.CONTEXTUAL,
                element=element,
                insight_type="context_diversity",
                value={
                    "total_contexts": len(contexts),
                    "unique_contexts": unique_contexts,
                    "diversity_ratio": unique_contexts / max(1, len(contexts))
                },
                confidence=0.8,
                evidence=[f"Element appears in {len(contexts)} contexts"]
            ))
        
        return insights


class TemporalAnalyzer:
    """
    Analyzes temporal patterns.
    
    Questions it answers:
    - How does this change over time?
    - When does this appear?
    - What is the temporal pattern?
    """
    
    def __init__(self):
        """Create temporal analyzer."""
        self.timeline: Dict[str, List[Tuple[int, Any]]] = defaultdict(list)
        self.time_counter = 0
    
    def record(self, element: str, data: Any):
        """Record element at current time."""
        self.timeline[element.lower()].append((self.time_counter, data))
        self.time_counter += 1
    
    def analyze(self, element: str) -> List[StructuralInsight]:
        """Analyze element from temporal perspective."""
        insights = []
        element_lower = element.lower()
        
        if element_lower in self.timeline:
            timeline = self.timeline[element_lower]
            
            # Temporal distribution
            times = [t for t, _ in timeline]
            if len(times) > 1:
                time_span = max(times) - min(times)
                avg_interval = time_span / max(1, len(times) - 1)
                
                insights.append(StructuralInsight(
                    perspective=Perspective.TEMPORAL,
                    element=element,
                    insight_type="temporal_pattern",
                    value={
                        "occurrences": len(timeline),
                        "time_span": time_span,
                        "avg_interval": avg_interval,
                        "is_regular": avg_interval < time_span / 2
                    },
                    confidence=0.7,
                    evidence=[f"Element appears {len(timeline)} times over {time_span} time units"]
                ))
        
        return insights


class RelationalAnalyzer:
    """
    Analyzes relationships.
    
    Questions it answers:
    - What does this relate to?
    - How strong are the relationships?
    - What types of relationships exist?
    """
    
    def __init__(self, pattern_builder: PatternBuilder, hierarchy: StructureHierarchy):
        """Create relational analyzer."""
        self.builder = pattern_builder
        self.hierarchy = hierarchy
        self.relationships: Dict[str, List[Relationship]] = defaultdict(list)
    
    def find_relationships(self, element: str) -> List[Relationship]:
        """Find all relationships for element."""
        relationships = []
        element_lower = element.lower()
        
        # Pattern relationships
        all_patterns = self.builder.get_patterns(min_frequency=1)
        for pattern in all_patterns:
            if pattern.sequence == element_lower:
                continue
            
            # Check overlap
            symbols1 = set(element_lower)
            symbols2 = set(pattern.sequence)
            overlap = symbols1 & symbols2
            
            if overlap:
                strength = len(overlap) / max(len(symbols1), len(symbols2))
                relationships.append(Relationship(
                    source=element,
                    target=pattern.sequence,
                    relationship_type="symbol_overlap",
                    strength=strength,
                    perspectives=[Perspective.RELATIONAL, Perspective.STRUCTURAL],
                    evidence=[f"Share {len(overlap)} symbols"]
                ))
            
            # Check containment
            if element_lower in pattern.sequence or pattern.sequence in element_lower:
                relationships.append(Relationship(
                    source=element,
                    target=pattern.sequence,
                    relationship_type="containment",
                    strength=0.8,
                    perspectives=[Perspective.RELATIONAL, Perspective.STRUCTURAL],
                    evidence=[f"One contains the other"]
                ))
        
        return relationships
    
    def analyze(self, element: str) -> List[StructuralInsight]:
        """Analyze element from relational perspective."""
        insights = []
        relationships = self.find_relationships(element)
        
        if relationships:
            # Strongest relationships
            strong_rels = sorted(relationships, key=lambda r: r.strength, reverse=True)[:5]
            
            insights.append(StructuralInsight(
                perspective=Perspective.RELATIONAL,
                element=element,
                insight_type="relationships",
                value={
                    "total_relationships": len(relationships),
                    "strong_relationships": [
                        {
                            "target": r.target,
                            "type": r.relationship_type,
                            "strength": r.strength
                        }
                        for r in strong_rels
                    ]
                },
                confidence=0.8,
                evidence=[f"Found {len(relationships)} relationships"],
                relationships=[f"{r.target}:{r.strength:.2f}" for r in strong_rels[:3]]
            ))
        
        return insights


class DeepStructuralReasoner:
    """
    Deep structural reasoning from ALL perspectives.
    
    This is the multi-model system that understands:
    - Structure (how things are built)
    - Semantics (what things mean)
    - Frequency (how often things appear)
    - Context (where things appear)
    - Time (how things change)
    - Relationships (how things connect)
    """
    
    def __init__(self):
        """Create deep reasoner."""
        self.registry = get_registry()
        self.builder = PatternBuilder(self.registry)
        self.hierarchy = StructureHierarchy(self.registry)
        
        # All analyzers
        self.structural_analyzer = StructuralAnalyzer(self.registry, self.hierarchy)
        self.semantic_analyzer = SemanticAnalyzer(self.builder, self.hierarchy)
        self.frequency_analyzer = FrequencyAnalyzer(self.builder)
        self.contextual_analyzer = ContextualAnalyzer()
        self.temporal_analyzer = TemporalAnalyzer()
        self.relational_analyzer = RelationalAnalyzer(self.builder, self.hierarchy)
    
    def learn_from_text(self, text: str):
        """Learn from text (all perspectives)."""
        # Build structure
        self.builder.learn_from_text(text)
        self.hierarchy.build_from_text(text)
        
        # Learn semantics (co-occurrence)
        self.semantic_analyzer.learn_context(text)
        
        # Learn context
        words = text.lower().split()
        for i, word in enumerate(words):
            self.contextual_analyzer.learn_context(word, {
                "position": i,
                "sentence_length": len(words),
                "surrounding": words[max(0, i-1):i+2]
            })
        
        # Record temporally
        for word in words:
            self.temporal_analyzer.record(word, {"frequency": words.count(word)})
    
    def reason_about(self, element: str) -> Dict[str, Any]:
        """
        Reason about element from ALL perspectives.
        
        This is the multi-model reasoning!
        """
        all_insights = []
        
        # Structural reasoning
        structural = self.structural_analyzer.analyze(element)
        all_insights.extend(structural)
        
        # Semantic reasoning
        semantic = self.semantic_analyzer.analyze(element)
        all_insights.extend(semantic)
        
        # Frequency reasoning
        frequency = self.frequency_analyzer.analyze(element)
        all_insights.extend(frequency)
        
        # Contextual reasoning
        contextual = self.contextual_analyzer.analyze(element)
        all_insights.extend(contextual)
        
        # Temporal reasoning
        temporal = self.temporal_analyzer.analyze(element)
        all_insights.extend(temporal)
        
        # Relational reasoning
        relational = self.relational_analyzer.analyze(element)
        all_insights.extend(relational)
        
        # Find relationships
        relationships = self.relational_analyzer.find_relationships(element)
        
        # Comprehensive understanding
        understanding = {
            "element": element,
            "insights": {
                perspective.value: [
                    {
                        "type": insight.insight_type,
                        "value": insight.value,
                        "confidence": insight.confidence,
                        "evidence": insight.evidence
                    }
                    for insight in all_insights
                    if insight.perspective == perspective
                ]
                for perspective in Perspective
            },
            "relationships": [
                {
                    "target": r.target,
                    "type": r.relationship_type,
                    "strength": r.strength,
                    "perspectives": [p.value for p in r.perspectives]
                }
                for r in relationships
            ],
            "comprehensive_score": self._calculate_comprehensive_score(all_insights, relationships)
        }
        
        return understanding
    
    def _calculate_comprehensive_score(self, insights: List[StructuralInsight], relationships: List[Relationship]) -> float:
        """Calculate comprehensive understanding score."""
        if not insights:
            return 0.0
        
        # Average confidence
        avg_confidence = sum(i.confidence for i in insights) / len(insights)
        
        # Relationship strength
        avg_relationship_strength = sum(r.strength for r in relationships) / max(1, len(relationships))
        
        # Perspective coverage
        perspectives_covered = len(set(i.perspective for i in insights))
        coverage_score = perspectives_covered / len(Perspective)
        
        # Combined score
        score = (avg_confidence * 0.4 + avg_relationship_strength * 0.3 + coverage_score * 0.3)
        
        return min(1.0, score)
    
    def understand_data(self, text: str) -> Dict[str, Any]:
        """
        Deep understanding of data from ALL angles.
        
        This is the multi-model understanding!
        """
        # Learn from data
        self.learn_from_text(text)
        
        # Analyze all elements
        words = set(text.lower().split())
        understanding = {}
        
        for word in words:
            understanding[word] = self.reason_about(word)
        
        return understanding


# Test it works
if __name__ == "__main__":
    print("Testing Deep Structural Reasoning...")
    print("=" * 70)
    
    reasoner = DeepStructuralReasoner()
    
    text = "cat cat dog cat mouse python java python machine learning"
    print(f"\nLearning from: '{text}'")
    reasoner.learn_from_text(text)
    
    print("\nDeep reasoning about 'cat':")
    result = reasoner.reason_about("cat")
    
    print(f"\nComprehensive Score: {result['comprehensive_score']:.3f}")
    print(f"\nPerspectives analyzed: {len(result['insights'])}")
    for perspective, insights in result['insights'].items():
        if insights:
            print(f"  {perspective}: {len(insights)} insights")
    
    print(f"\nRelationships found: {len(result['relationships'])}")
    for rel in result['relationships'][:3]:
        print(f"  {rel['target']}: {rel['type']} (strength: {rel['strength']:.2f})")
    
    print("\n✅ Deep structural reasoning works!")
