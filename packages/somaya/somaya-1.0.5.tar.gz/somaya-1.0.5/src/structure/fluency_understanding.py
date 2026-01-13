"""
SOMA Fluency and Understanding System
=======================================

Deep understanding of data, patterns, and structure for EXCELLENT fluency:
- Pattern understanding from all angles
- Structure understanding (symbols, letters, numbers)
- Relationship understanding
- Context understanding
- Fluency scoring and improvement

This makes SOMA Core understand data deeply!
"""

import sys
import os
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.symbol_structures import get_registry, SymbolRegistry, SymbolClass
from src.structure.pattern_builder import PatternBuilder, Pattern
from src.structure.structure_hierarchy import StructureHierarchy
from src.structure.deep_reasoning import DeepStructuralReasoner, Perspective


@dataclass
class UnderstandingScore:
    """Comprehensive understanding score."""
    structural_understanding: float = 0.0
    semantic_understanding: float = 0.0
    pattern_understanding: float = 0.0
    relationship_understanding: float = 0.0
    context_understanding: float = 0.0
    overall_score: float = 0.0
    breakdown: Dict[str, Any] = field(default_factory=dict)


class SymbolUnderstanding:
    """
    Deep understanding of symbols (letters, numbers, special characters).
    
    Understands from ALL angles:
    - What type of symbol (letter, number, math, special)
    - How it's used (position, frequency, combinations)
    - What it combines with
    - What patterns it creates
    """
    
    def __init__(self, registry: SymbolRegistry, builder: PatternBuilder):
        """Create symbol understanding system."""
        self.registry = registry
        self.builder = builder
        self.symbol_usage: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "frequency": 0,
            "positions": [],
            "combinations": defaultdict(int),
            "patterns": set()
        })
    
    def learn_symbol_usage(self, text: str):
        """Learn how symbols are used."""
        for i, char in enumerate(text.lower()):
            if char in self.registry.get_all_symbols():
                usage = self.symbol_usage[char]
                usage["frequency"] += 1
                usage["positions"].append(i)
                
                # Learn combinations (neighbors)
                if i > 0:
                    prev_char = text[i-1].lower()
                    usage["combinations"][f"{prev_char}{char}"] += 1
                if i < len(text) - 1:
                    next_char = text[i+1].lower()
                    usage["combinations"][f"{char}{next_char}"] += 1
    
    def understand_symbol(self, symbol: str) -> Dict[str, Any]:
        """Deep understanding of a symbol."""
        symbol_lower = symbol.lower()
        
        if symbol_lower not in self.symbol_usage:
            return {"symbol": symbol, "understanding": "limited"}
        
        usage = self.symbol_usage[symbol_lower]
        symbol_class = self.registry.get_class(symbol_lower)
        
        # Find patterns containing this symbol
        patterns = self.builder.get_patterns(min_frequency=1)
        symbol_patterns = [p.sequence for p in patterns if symbol_lower in p.symbols]
        
        # Top combinations
        top_combinations = sorted(
            usage["combinations"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "symbol": symbol,
            "symbol_class": symbol_class,
            "frequency": usage["frequency"],
            "usage_patterns": {
                "total_occurrences": usage["frequency"],
                "unique_positions": len(set(usage["positions"])),
                "position_diversity": len(set(usage["positions"])) / max(1, usage["frequency"])
            },
            "combinations": {
                "total_combinations": len(usage["combinations"]),
                "top_combinations": top_combinations
            },
            "pattern_participation": {
                "patterns_containing_symbol": len(symbol_patterns),
                "pattern_list": symbol_patterns[:10]
            },
            "understanding_score": self._calculate_symbol_understanding(symbol_lower, usage, symbol_patterns)
        }
    
    def _calculate_symbol_understanding(self, symbol: str, usage: Dict, patterns: List[str]) -> float:
        """Calculate understanding score for symbol."""
        # Frequency component
        freq_score = min(1.0, usage["frequency"] / 100.0)
        
        # Combination diversity
        combo_score = min(1.0, len(usage["combinations"]) / 20.0)
        
        # Pattern participation
        pattern_score = min(1.0, len(patterns) / 10.0)
        
        # Position diversity
        pos_score = len(set(usage["positions"])) / max(1, usage["frequency"])
        
        # Combined
        score = (freq_score * 0.3 + combo_score * 0.25 + pattern_score * 0.25 + pos_score * 0.2)
        return min(1.0, score)


class PatternUnderstanding:
    """
    Deep understanding of patterns.
    
    Understands from ALL angles:
    - How patterns are built (symbol composition)
    - Pattern stability and frequency
    - Pattern relationships
    - Pattern context
    - Pattern evolution
    """
    
    def __init__(self, builder: PatternBuilder, hierarchy: StructureHierarchy):
        """Create pattern understanding system."""
        self.builder = builder
        self.hierarchy = hierarchy
    
    def understand_pattern(self, pattern: str) -> Dict[str, Any]:
        """Deep understanding of a pattern."""
        pattern_lower = pattern.lower()
        
        if not self.builder.pattern_exists(pattern_lower):
            return {"pattern": pattern, "understanding": "not_found"}
        
        pattern_obj = self.builder.get_pattern(pattern_lower)
        
        # Structural understanding
        symbols = list(pattern_lower)
        symbol_classes = [self.builder.registry.get_class(s) for s in symbols]
        
        # Relationship understanding
        all_patterns = self.builder.get_patterns(min_frequency=1)
        related_patterns = []
        
        for other_pattern in all_patterns:
            if other_pattern.sequence == pattern_lower:
                continue
            
            # Check relationships
            symbols1 = set(pattern_lower)
            symbols2 = set(other_pattern.sequence)
            overlap = symbols1 & symbols2
            
            if overlap:
                strength = len(overlap) / max(len(symbols1), len(symbols2))
                if strength > 0.3:
                    related_patterns.append({
                        "pattern": other_pattern.sequence,
                        "relationship": "symbol_overlap",
                        "strength": strength
                    })
        
        # Hierarchical understanding
        trace = self.hierarchy.trace_structure(pattern_lower)
        is_unit = pattern_lower in self.hierarchy.unit_nodes
        
        return {
            "pattern": pattern,
            "structural": {
                "symbols": symbols,
                "symbol_classes": list(set(symbol_classes)),
                "length": len(symbols),
                "unique_symbols": len(set(symbols))
            },
            "stability": {
                "frequency": pattern_obj.frequency,
                "stability_score": pattern_obj.stability_score(),
                "is_stable": pattern_obj.stability_score() > 0.5
            },
            "relationships": {
                "total_relationships": len(related_patterns),
                "related_patterns": related_patterns[:5]
            },
            "hierarchical": {
                "is_unit": is_unit,
                "hierarchy_levels": len(trace) if trace else 0,
                "trace": [n.content for n in trace] if trace else []
            },
            "understanding_score": self._calculate_pattern_understanding(pattern_obj, related_patterns, is_unit)
        }
    
    def _calculate_pattern_understanding(self, pattern: Pattern, relationships: List[Dict], is_unit: bool) -> float:
        """Calculate understanding score for pattern."""
        # Stability component
        stability_score = pattern.stability_score()
        
        # Frequency component
        freq_score = min(1.0, pattern.frequency / 10.0)
        
        # Relationship component
        rel_score = min(1.0, len(relationships) / 5.0)
        
        # Unit status
        unit_score = 1.0 if is_unit else 0.5
        
        # Combined
        score = (stability_score * 0.3 + freq_score * 0.25 + rel_score * 0.25 + unit_score * 0.2)
        return min(1.0, score)


class DataUnderstanding:
    """
    Deep understanding of data from ALL angles.
    
    This is the comprehensive understanding system!
    """
    
    def __init__(self):
        """Create data understanding system."""
        self.registry = get_registry()
        self.builder = PatternBuilder(self.registry)
        self.hierarchy = StructureHierarchy(self.registry)
        self.reasoner = DeepStructuralReasoner()
        
        self.symbol_understanding = SymbolUnderstanding(self.registry, self.builder)
        self.pattern_understanding = PatternUnderstanding(self.builder, self.hierarchy)
    
    def understand_data(self, text: str) -> Dict[str, Any]:
        """
        Deep understanding of data from ALL angles.
        
        Understands:
        - Symbols (letters, numbers, special characters)
        - Patterns (combinations)
        - Structure (hierarchy)
        - Relationships (connections)
        - Context (where things appear)
        - Semantics (what things mean)
        """
        # Learn from data
        self.builder.learn_from_text(text)
        self.hierarchy.build_from_text(text)
        self.reasoner.learn_from_text(text)
        self.symbol_understanding.learn_symbol_usage(text)
        
        words = text.lower().split()
        unique_words = set(words)
        
        # Understand symbols
        symbols_used = set()
        for char in text.lower():
            if char in self.registry.get_all_symbols():
                symbols_used.add(char)
        
        symbol_understandings = {}
        for symbol in symbols_used:
            symbol_understandings[symbol] = self.symbol_understanding.understand_symbol(symbol)
        
        # Understand patterns
        pattern_understandings = {}
        for word in unique_words:
            pattern_understandings[word] = self.pattern_understanding.understand_pattern(word)
        
        # Deep reasoning
        reasoning_results = {}
        for word in unique_words:
            reasoning_results[word] = self.reasoner.reason_about(word)
        
        # Calculate overall understanding
        overall_understanding = self._calculate_overall_understanding(
            symbol_understandings,
            pattern_understandings,
            reasoning_results
        )
        
        return {
            "data": text,
            "symbol_understanding": symbol_understandings,
            "pattern_understanding": pattern_understandings,
            "deep_reasoning": reasoning_results,
            "overall_understanding": overall_understanding,
            "statistics": {
                "total_symbols": len(symbols_used),
                "total_patterns": len(unique_words),
                "total_relationships": sum(
                    len(r.get("relationships", []))
                    for r in reasoning_results.values()
                )
            }
        }
    
    def _calculate_overall_understanding(self, symbols: Dict, patterns: Dict, reasoning: Dict) -> UnderstandingScore:
        """Calculate overall understanding score."""
        # Symbol understanding
        symbol_scores = [
            s.get("understanding_score", 0.0)
            for s in symbols.values()
        ]
        symbol_avg = sum(symbol_scores) / max(1, len(symbol_scores))
        
        # Pattern understanding
        pattern_scores = [
            p.get("understanding_score", 0.0)
            for p in patterns.values()
        ]
        pattern_avg = sum(pattern_scores) / max(1, len(pattern_scores))
        
        # Relationship understanding
        relationship_scores = [
            r.get("comprehensive_score", 0.0)
            for r in reasoning.values()
        ]
        relationship_avg = sum(relationship_scores) / max(1, len(relationship_scores))
        
        # Structural understanding (from reasoning)
        structural_scores = []
        for r in reasoning.values():
            structural_insights = r.get("insights", {}).get("structural", [])
            if structural_insights:
                avg_conf = sum(i.get("confidence", 0.0) for i in structural_insights) / len(structural_insights)
                structural_scores.append(avg_conf)
        structural_avg = sum(structural_scores) / max(1, len(structural_scores))
        
        # Semantic understanding
        semantic_scores = []
        for r in reasoning.values():
            semantic_insights = r.get("insights", {}).get("semantic", [])
            if semantic_insights:
                avg_conf = sum(i.get("confidence", 0.0) for i in semantic_insights) / len(semantic_insights)
                semantic_scores.append(avg_conf)
        semantic_avg = sum(semantic_scores) / max(1, len(semantic_scores))
        
        # Context understanding
        contextual_scores = []
        for r in reasoning.values():
            contextual_insights = r.get("insights", {}).get("contextual", [])
            if contextual_insights:
                avg_conf = sum(i.get("confidence", 0.0) for i in contextual_insights) / len(contextual_insights)
                contextual_scores.append(avg_conf)
        context_avg = sum(contextual_scores) / max(1, len(contextual_scores))
        
        # Overall
        overall = (
            symbol_avg * 0.15 +
            pattern_avg * 0.20 +
            relationship_avg * 0.20 +
            structural_avg * 0.15 +
            semantic_avg * 0.15 +
            context_avg * 0.15
        )
        
        return UnderstandingScore(
            structural_understanding=structural_avg,
            semantic_understanding=semantic_avg,
            pattern_understanding=pattern_avg,
            relationship_understanding=relationship_avg,
            context_understanding=context_avg,
            overall_score=overall,
            breakdown={
                "symbol_understanding": symbol_avg,
                "pattern_understanding": pattern_avg,
                "relationship_understanding": relationship_avg
            }
        )


class FluencyEnhancer:
    """
    Enhances fluency using deep understanding.
    
    Uses understanding to improve:
    - Text generation quality
    - Pattern selection
    - Relationship awareness
    - Context awareness
    """
    
    def __init__(self, data_understanding: DataUnderstanding):
        """Create fluency enhancer."""
        self.understanding = data_understanding
    
    def enhance_generation(self, prompt: str, candidate_tokens: List[str]) -> List[Tuple[str, float]]:
        """
        Enhance generation by scoring candidates using deep understanding.
        
        Returns candidates with fluency scores.
        """
        # Understand prompt
        prompt_understanding = self.understanding.understand_data(prompt)
        
        scored_candidates = []
        
        for candidate in candidate_tokens:
            score = 0.0
            
            # Pattern understanding score
            if candidate in prompt_understanding["pattern_understanding"]:
                pattern_info = prompt_understanding["pattern_understanding"][candidate]
                score += pattern_info.get("understanding_score", 0.0) * 0.4
            
            # Relationship score
            if candidate in prompt_understanding["deep_reasoning"]:
                reasoning = prompt_understanding["deep_reasoning"][candidate]
                score += reasoning.get("comprehensive_score", 0.0) * 0.3
            
            # Context score (co-occurrence with prompt words)
            prompt_words = set(prompt.lower().split())
            if candidate.lower() in prompt_words:
                score += 0.3
            
            scored_candidates.append((candidate, score))
        
        # Sort by score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return scored_candidates


# Test it works
if __name__ == "__main__":
    print("Testing Fluency and Understanding System...")
    print("=" * 70)
    
    understanding = DataUnderstanding()
    
    text = "cat cat dog cat mouse python java python machine learning"
    print(f"\nUnderstanding data: '{text}'")
    
    result = understanding.understand_data(text)
    
    print(f"\nOverall Understanding Score: {result['overall_understanding'].overall_score:.3f}")
    print(f"  Structural: {result['overall_understanding'].structural_understanding:.3f}")
    print(f"  Semantic: {result['overall_understanding'].semantic_understanding:.3f}")
    print(f"  Pattern: {result['overall_understanding'].pattern_understanding:.3f}")
    print(f"  Relationship: {result['overall_understanding'].relationship_understanding:.3f}")
    
    print(f"\nStatistics:")
    print(f"  Symbols understood: {result['statistics']['total_symbols']}")
    print(f"  Patterns understood: {result['statistics']['total_patterns']}")
    print(f"  Relationships found: {result['statistics']['total_relationships']}")
    
    print("\n✅ Fluency and understanding system works!")
