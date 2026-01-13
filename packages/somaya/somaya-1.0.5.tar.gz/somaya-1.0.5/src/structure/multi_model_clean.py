"""
SOMA Core Multi-Model System - CLEANED VERSION
===========================================

This is the cleaned, production-ready version that:
- Uses bounded scores (0.0-1.0)
- Collapses 8 models into 4 core signals
- Implements decision gates
- Prunes relationship explosion
- Uses honest naming (Confidence, not "Understanding")

Core principle: "If a number does not change a decision, it does not deserve to exist."
"""

import sys
import os
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.symbol_structures import get_registry, SymbolRegistry
from src.structure.pattern_builder import PatternBuilder
from src.structure.structure_hierarchy import StructureHierarchy
from src.structure.deep_reasoning import DeepStructuralReasoner
from src.structure.relationship_graph import RelationshipGraph
from src.structure.fluency_understanding import DataUnderstanding, FluencyEnhancer
from src.structure.scoring_utils import (
    bound_score, aggregate_scores, ConfidenceLevel, to_confidence_bucket
)
from src.structure.decision_gates import DecisionGates, GateInputs, PromotionDecision, TrustLevel, GenerationDecision


@dataclass
class SignalOutput:
    """Output from a signal (not a "model")."""
    structural_signal: Dict[str, Any] = field(default_factory=dict)
    statistical_signal: Dict[str, Any] = field(default_factory=dict)
    context_signal: Dict[str, Any] = field(default_factory=dict)
    semantic_proxy: Dict[str, Any] = field(default_factory=dict)
    confidence_aggregate: Dict[str, Any] = field(default_factory=dict)
    decisions: Dict[str, Any] = field(default_factory=dict)


class SOMA CoreMultiModelClean:
    """
    SOMA Core Multi-Model System - CLEANED.
    
    Collapses 8 "models" into 4 core signals:
    1. Structural Signal (how things are built)
    2. Statistical Signal (frequency + temporal)
    3. Context Signal (contextual + relational)
    4. Semantic Proxy (semantic approximation)
    
    All scores are bounded [0.0, 1.0].
    All signals feed decision gates.
    """
    
    def __init__(self, max_relationships_per_node: int = 20, min_relationship_strength: float = 0.6):
        """
        Create cleaned multi-model system.
        
        Args:
            max_relationships_per_node: Maximum relationships to keep per node (prunes explosion)
            min_relationship_strength: Minimum strength threshold for relationships
        """
        # Core components
        self.registry = get_registry()
        self.builder = PatternBuilder(self.registry)
        self.hierarchy = StructureHierarchy(self.registry)
        
        # Specialized analyzers
        self.reasoner = DeepStructuralReasoner()
        self.relationship_graph = RelationshipGraph(self.registry, self.builder, self.hierarchy)
        self.understanding = DataUnderstanding()
        self.fluency_enhancer = FluencyEnhancer(self.understanding)
        
        # Decision gates
        self.gates = DecisionGates()
        
        # Pruning parameters
        self.max_relationships_per_node = max_relationships_per_node
        self.min_relationship_strength = min_relationship_strength
    
    def learn(self, text: str):
        """
        Learn from data using all signals.
        
        This is the multi-signal learning!
        """
        # Learn in all analyzers
        self.builder.learn_from_text(text)
        self.hierarchy.build_from_text(text)
        self.reasoner.learn_from_text(text)
        self.relationship_graph.build_from_text(text)
        self.understanding.understand_data(text)
        
        # Prune relationship explosion
        self._prune_relationships()
    
    def _prune_relationships(self):
        """
        Prune relationship explosion.
        
        Keeps only top N relationships per node, above strength threshold.
        """
        # Group edges by node
        node_edges: Dict[str, List] = {}
        for edge in self.relationship_graph.edges:
            # Add to source
            if edge.source not in node_edges:
                node_edges[edge.source] = []
            node_edges[edge.source].append(edge)
            
            # Add to target
            if edge.target not in node_edges:
                node_edges[edge.target] = []
            node_edges[edge.target].append(edge)
        
        # Prune each node
        pruned_edges = []
        for node_id, edges in node_edges.items():
            # Filter by strength threshold
            strong_edges = [e for e in edges if e.strength >= self.min_relationship_strength]
            
            # Sort by strength and take top N
            strong_edges.sort(key=lambda e: e.strength, reverse=True)
            top_edges = strong_edges[:self.max_relationships_per_node]
            
            pruned_edges.extend(top_edges)
        
        # Remove duplicates (edges appear twice - once per node)
        seen_edges = set()
        final_edges = []
        for edge in pruned_edges:
            edge_key = (min(edge.source, edge.target), max(edge.source, edge.target), edge.relationship_type)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                final_edges.append(edge)
        
        # Update graph
        self.relationship_graph.edges = final_edges
        # Rebuild index
        self.relationship_graph.edge_index = {}
        for edge in final_edges:
            if edge.source not in self.relationship_graph.edge_index:
                self.relationship_graph.edge_index[edge.source] = []
            if edge.target not in self.relationship_graph.edge_index:
                self.relationship_graph.edge_index[edge.target] = []
            self.relationship_graph.edge_index[edge.source].append(edge)
            self.relationship_graph.edge_index[edge.target].append(edge)
    
    def analyze(self, element: str) -> SignalOutput:
        """
        Analyze element using all signals.
        
        Returns bounded scores and decisions.
        """
        output = SignalOutput()
        
        # 1. Structural Signal (combines structural + hierarchical)
        structural_insights = self.reasoner.structural_analyzer.analyze(element)
        structural_confidences = [bound_score(i.confidence) for i in structural_insights]
        structural_score = aggregate_scores(structural_confidences) if structural_confidences else 0.0
        
        output.structural_signal = {
            "score": structural_score,
            "confidence": to_confidence_bucket(structural_score),
            "insights_count": len(structural_insights),
            "symbol_composition": self._get_symbol_composition(element),
            "hierarchical_position": self._get_hierarchical_position(element)
        }
        
        # 2. Statistical Signal (combines frequency + temporal)
        frequency_insights = self.reasoner.frequency_analyzer.analyze(element)
        temporal_insights = self.reasoner.temporal_analyzer.analyze(element)
        
        freq_confidences = [bound_score(i.confidence) for i in frequency_insights]
        temp_confidences = [bound_score(i.confidence) for i in temporal_insights]
        
        freq_score = aggregate_scores(freq_confidences) if freq_confidences else 0.0
        temp_score = aggregate_scores(temp_confidences) if temp_confidences else 0.0
        
        # Combine frequency and temporal
        statistical_score = aggregate_scores([freq_score, temp_score], weights=[0.7, 0.3])
        
        output.statistical_signal = {
            "score": statistical_score,
            "confidence": to_confidence_bucket(statistical_score),
            "frequency": self._get_frequency(element),
            "temporal_pattern": self._get_temporal_pattern(element)
        }
        
        # 3. Context Signal (combines contextual + relational)
        contextual_insights = self.reasoner.contextual_analyzer.analyze(element)
        relational_insights = self.reasoner.relational_analyzer.analyze(element)
        relationships = self.reasoner.relational_analyzer.find_relationships(element)
        
        # Prune relationships
        relationships = [r for r in relationships if r.strength >= self.min_relationship_strength]
        relationships.sort(key=lambda r: r.strength, reverse=True)
        relationships = relationships[:self.max_relationships_per_node]
        
        ctx_confidences = [bound_score(i.confidence) for i in contextual_insights]
        rel_strengths = [bound_score(r.strength) for r in relationships]
        
        ctx_score = aggregate_scores(ctx_confidences) if ctx_confidences else 0.0
        rel_score = aggregate_scores(rel_strengths) if rel_strengths else 0.0
        
        # Combine contextual and relational
        context_score = aggregate_scores([ctx_score, rel_score], weights=[0.5, 0.5])
        
        output.context_signal = {
            "score": context_score,
            "confidence": to_confidence_bucket(context_score),
            "context_diversity": self._get_context_diversity(element),
            "relationships_count": len(relationships),
            "top_relationships": [
                {"target": r.target, "type": r.relationship_type, "strength": bound_score(r.strength)}
                for r in relationships[:5]
            ]
        }
        
        # 4. Semantic Proxy (semantic approximation)
        semantic_insights = self.reasoner.semantic_analyzer.analyze(element)
        semantic_confidences = [bound_score(i.confidence) for i in semantic_insights]
        semantic_score = aggregate_scores(semantic_confidences) if semantic_confidences else 0.0
        
        output.semantic_proxy = {
            "score": semantic_score,
            "confidence": to_confidence_bucket(semantic_score),
            "cooccurrence": self._get_cooccurrence(element),
            "semantic_stability": self._get_semantic_stability(element)
        }
        
        # 5. Confidence Aggregate (combines all signals)
        all_scores = [
            structural_score,
            statistical_score,
            context_score,
            semantic_score
        ]
        confidence_aggregate = aggregate_scores(all_scores, weights=[0.25, 0.25, 0.25, 0.25])
        
        output.confidence_aggregate = {
            "score": confidence_aggregate,
            "confidence": to_confidence_bucket(confidence_aggregate),
            "signal_coverage": sum(1 for s in all_scores if s > 0.3),
            "total_signals": len(all_scores)
        }
        
        # 6. Decisions (the actual outputs that matter)
        gate_inputs = GateInputs(
            frequency=self._get_frequency_value(element),
            stability=self._get_stability_value(element),
            structural_consistency=structural_score,
            context_diversity=self._get_context_diversity_value(element),
            relational_consistency=rel_score,
            fluency_score=self._calculate_fluency_score(element, output),
            repetition_risk=0.0,  # Would need history for this
            instability=1.0 - self._get_stability_value(element)
        )
        
        promote_decision, promote_confidence = self.gates.should_be_unit(gate_inputs)
        trust_decision, trust_confidence = self.gates.should_trust_pattern(gate_inputs)
        generate_decision, generate_confidence = self.gates.should_generate(gate_inputs)
        
        output.decisions = {
            "promote": {
                "decision": promote_decision.value,
                "confidence": promote_confidence
            },
            "trust": {
                "decision": trust_decision.value,
                "confidence": trust_confidence
            },
            "generate": {
                "decision": generate_decision.value,
                "confidence": generate_confidence
            }
        }
        
        return output
    
    def _get_symbol_composition(self, element: str) -> Dict:
        """Get symbol composition."""
        symbols = list(element.lower())
        return {
            "symbols": symbols,
            "length": len(symbols)
        }
    
    def _get_hierarchical_position(self, element: str) -> Dict:
        """Get hierarchical position."""
        trace = self.hierarchy.trace_structure(element.lower())
        return {
            "levels": len(trace) if trace else 0,
            "is_unit": element.lower() in self.hierarchy.unit_nodes
        }
    
    def _get_frequency(self, element: str) -> Dict:
        """Get frequency information."""
        if self.builder.pattern_exists(element.lower()):
            pattern = self.builder.get_pattern(element.lower())
            return {"frequency": pattern.frequency}
        return {"frequency": 0}
    
    def _get_frequency_value(self, element: str) -> float:
        """Get frequency as normalized value [0.0, 1.0]."""
        freq_dict = self._get_frequency(element)
        freq = freq_dict.get("frequency", 0)
        # Normalize: assume max frequency of 10 for now
        return bound_score(freq / 10.0)
    
    def _get_temporal_pattern(self, element: str) -> Dict:
        """Get temporal pattern."""
        if element.lower() in self.reasoner.temporal_analyzer.timeline:
            timeline = self.reasoner.temporal_analyzer.timeline[element.lower()]
            return {
                "occurrences": len(timeline),
                "time_span": max(t for t, _ in timeline) - min(t for t, _ in timeline) if len(timeline) > 1 else 0
            }
        return {}
    
    def _get_context_diversity(self, element: str) -> Dict:
        """Get context diversity."""
        if element.lower() in self.reasoner.contextual_analyzer.contexts:
            contexts = self.reasoner.contextual_analyzer.contexts[element.lower()]
            return {
                "total_contexts": len(contexts),
                "diversity": len(set(str(c) for c in contexts)) / max(1, len(contexts))
            }
        return {}
    
    def _get_context_diversity_value(self, element: str) -> float:
        """Get context diversity as normalized value [0.0, 1.0]."""
        div_dict = self._get_context_diversity(element)
        return bound_score(div_dict.get("diversity", 0.0))
    
    def _get_cooccurrence(self, element: str) -> Dict:
        """Get co-occurrence information."""
        if element.lower() in self.reasoner.semantic_analyzer.cooccurrence:
            cooccur = self.reasoner.semantic_analyzer.cooccurrence[element.lower()]
            return {
                "total_contexts": len(cooccur),
                "top_associations": sorted(cooccur.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        return {}
    
    def _get_semantic_stability(self, element: str) -> Dict:
        """Get semantic stability."""
        if self.builder.pattern_exists(element.lower()):
            pattern = self.builder.get_pattern(element.lower())
            stability = pattern.stability_score()
            return {
                "stability": bound_score(stability),
                "frequency": pattern.frequency
            }
        return {}
    
    def _get_stability_value(self, element: str) -> float:
        """Get stability as normalized value [0.0, 1.0]."""
        stability_dict = self._get_semantic_stability(element)
        return bound_score(stability_dict.get("stability", 0.0))
    
    def _calculate_fluency_score(self, element: str, output: SignalOutput) -> float:
        """Calculate fluency score (bounded)."""
        scores = []
        
        # Structural fluency
        if output.structural_signal.get("score", 0.0) > 0:
            scores.append(output.structural_signal["score"])
        
        # Semantic fluency
        if output.semantic_proxy.get("score", 0.0) > 0:
            scores.append(output.semantic_proxy["score"])
        
        # Pattern stability
        stability = self._get_stability_value(element)
        if stability > 0:
            scores.append(stability)
        
        # Relationship strength (from context signal)
        if output.context_signal.get("score", 0.0) > 0:
            scores.append(output.context_signal["score"])
        
        if not scores:
            return 0.0
        
        return aggregate_scores(scores)
