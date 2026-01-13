"""
SOMA Core Multi-Model System - Complete Demo
==========================================

Demonstrates the REAL multi-model system with:
- Deep structural reasoning from ALL angles
- Relationship understanding
- Fluency and understanding
- Multi-model integration

This shows SOMA Core as a REAL multi-model system!
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

print("=" * 70)
print("SOMA Core Multi-Model System - COMPLETE DEMO")
print("=" * 70)
print()
print("REAL Multi-Model System with Deep Understanding from ALL Angles!")
print()

try:
    from src.structure import (
        SOMA CoreMultiModel,
        DeepStructuralReasoner,
        RelationshipGraph,
        DataUnderstanding
    )
    
    print("[OK] All multi-model components imported")
    print()
    
    # ========================================================================
    # PART 1: Multi-Model System
    # ========================================================================
    
    print("=" * 70)
    print("PART 1: SOMA Core Multi-Model System")
    print("=" * 70)
    print()
    
    multi_model = SOMA CoreMultiModel()
    
    text = "cat cat dog cat mouse python java python machine learning artificial intelligence"
    print(f"Learning from: '{text}'")
    multi_model.learn(text)
    
    print("\nAnalyzing 'cat' with ALL models:")
    result = multi_model.analyze("cat")
    
    print(f"\n✅ Model Coverage: {result.integrated['model_coverage']}/{result.integrated['total_models']} models active")
    print(f"✅ Comprehensive Score: {result.integrated['comprehensive_score']:.3f}")
    print(f"✅ Multi-Model Understanding: {result.integrated['multi_model_understanding']}")
    
    print("\nModel Status:")
    for model, status in result.integrated['model_status'].items():
        status_symbol = "✓" if status else "✗"
        print(f"  {status_symbol} {model}")
    
    print(f"\nFluency Score: {result.fluency['fluency_score']:.3f}")
    print(f"Generation Quality: {result.fluency['generation_quality']}")
    
    # ========================================================================
    # PART 2: Deep Structural Reasoning
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("PART 2: Deep Structural Reasoning (ALL Perspectives)")
    print("=" * 70)
    print()
    
    reasoner = DeepStructuralReasoner()
    reasoner.learn_from_text(text)
    
    print("Deep reasoning about 'cat' from ALL perspectives:")
    reasoning_result = reasoner.reason_about("cat")
    
    print(f"\nComprehensive Score: {reasoning_result['comprehensive_score']:.3f}")
    print("\nPerspectives analyzed:")
    for perspective, insights in reasoning_result['insights'].items():
        if insights:
            print(f"  ✓ {perspective}: {len(insights)} insights")
            for insight in insights[:1]:  # Show first insight
                print(f"    - {insight['type']}: confidence {insight['confidence']:.2f}")
    
    print(f"\nRelationships found: {len(reasoning_result['relationships'])}")
    for rel in reasoning_result['relationships'][:3]:
        print(f"  - {rel['target']}: {rel['type']} (strength: {rel['strength']:.2f})")
    
    # ========================================================================
    # PART 3: Relationship Graph
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("PART 3: Relationship Graph (ALL Angles)")
    print("=" * 70)
    print()
    
    from src.structure.symbol_structures import get_registry
    from src.structure.pattern_builder import PatternBuilder
    from src.structure.structure_hierarchy import StructureHierarchy
    
    registry = get_registry()
    builder = PatternBuilder(registry)
    hierarchy = StructureHierarchy(registry)
    
    graph = RelationshipGraph(registry, builder, hierarchy)
    graph.build_from_text(text)
    
    print(f"Graph built: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    
    print("\nUnderstanding 'cat' from relationship graph:")
    graph_understanding = graph.get_understanding("cat")
    
    print(f"  Total relationships: {graph_understanding['total_relationships']}")
    print(f"  Relationship types: {list(graph_understanding['relationships_by_type'].keys())}")
    print(f"  Perspectives: {list(graph_understanding['relationships_by_perspective'].keys())}")
    print(f"  Relationship diversity: {graph_understanding['relationship_diversity']}")
    print(f"  Perspective coverage: {graph_understanding['perspective_coverage']}")
    
    print("\nStrongest relationships:")
    for rel in graph_understanding['strongest_relationships'][:3]:
        print(f"  - {rel['target']}: {rel['type']} (strength: {rel['strength']:.2f})")
        print(f"    Perspectives: {', '.join(rel['perspectives'])}")
    
    # ========================================================================
    # PART 4: Data Understanding
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("PART 4: Deep Data Understanding")
    print("=" * 70)
    print()
    
    understanding = DataUnderstanding()
    understanding_result = understanding.understand_data(text)
    
    overall = understanding_result['overall_understanding']
    print(f"Overall Understanding Score: {overall.overall_score:.3f}")
    print(f"  Structural: {overall.structural_understanding:.3f}")
    print(f"  Semantic: {overall.semantic_understanding:.3f}")
    print(f"  Pattern: {overall.pattern_understanding:.3f}")
    print(f"  Relationship: {overall.relationship_understanding:.3f}")
    print(f"  Context: {overall.context_understanding:.3f}")
    
    print(f"\nStatistics:")
    stats = understanding_result['statistics']
    print(f"  Symbols understood: {stats['total_symbols']}")
    print(f"  Patterns understood: {stats['total_patterns']}")
    print(f"  Relationships found: {stats['total_relationships']}")
    
    # ========================================================================
    # PART 5: Symbol Understanding
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("PART 5: Symbol Understanding (Letters, Numbers, Special)")
    print("=" * 70)
    print()
    
    symbol_understandings = understanding_result['symbol_understanding']
    print(f"Symbols understood: {len(symbol_understandings)}")
    
    # Show top symbols by understanding
    symbol_scores = [
        (sym, info.get('understanding_score', 0.0))
        for sym, info in symbol_understandings.items()
    ]
    symbol_scores.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop symbols by understanding:")
    for symbol, score in symbol_scores[:5]:
        info = symbol_understandings[symbol]
        print(f"  '{symbol}': score {score:.3f}")
        print(f"    Class: {info.get('symbol_class', 'unknown')}")
        print(f"    Frequency: {info.get('frequency', 0)}")
        print(f"    Patterns: {len(info.get('pattern_participation', {}).get('pattern_list', []))}")
    
    # ========================================================================
    # PART 6: Pattern Understanding
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("PART 6: Pattern Understanding (Combinations)")
    print("=" * 70)
    print()
    
    pattern_understandings = understanding_result['pattern_understanding']
    print(f"Patterns understood: {len(pattern_understandings)}")
    
    # Show top patterns by understanding
    pattern_scores = [
        (pattern, info.get('understanding_score', 0.0))
        for pattern, info in pattern_understandings.items()
    ]
    pattern_scores.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop patterns by understanding:")
    for pattern, score in pattern_scores[:3]:
        info = pattern_understandings[pattern]
        print(f"  '{pattern}': score {score:.3f}")
        print(f"    Stability: {info.get('stability', {}).get('stability_score', 0.0):.3f}")
        print(f"    Frequency: {info.get('stability', {}).get('frequency', 0)}")
        print(f"    Relationships: {info.get('relationships', {}).get('total_relationships', 0)}")
        print(f"    Is unit: {info.get('hierarchical', {}).get('is_unit', False)}")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("✅ SOMA Core Multi-Model System - COMPLETE!")
    print("=" * 70)
    print()
    print("What we built:")
    print("  1. ✅ Multi-Model System (8 integrated models)")
    print("  2. ✅ Deep Structural Reasoning (6 perspectives)")
    print("  3. ✅ Relationship Graph (all angles)")
    print("  4. ✅ Data Understanding (comprehensive)")
    print("  5. ✅ Symbol Understanding (letters, numbers, special)")
    print("  6. ✅ Pattern Understanding (combinations)")
    print("  7. ✅ Fluency Enhancement (generation quality)")
    print()
    print("Perspectives:")
    print("  ✓ Structural (how things are built)")
    print("  ✓ Semantic (what things mean)")
    print("  ✓ Frequency (how often things appear)")
    print("  ✓ Contextual (where things appear)")
    print("  ✓ Temporal (how things change)")
    print("  ✓ Relational (how things connect)")
    print()
    print("SOMA Core is now a REAL Multi-Model System! 🚀")
    print()
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
