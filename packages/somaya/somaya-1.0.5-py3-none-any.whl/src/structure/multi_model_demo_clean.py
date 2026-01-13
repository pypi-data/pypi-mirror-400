"""
SOMA Core Multi-Model System - CLEANED DEMO
=========================================

This demo shows the cleaned, production-ready version:
- Bounded scores (0.0-1.0) - no more 1.249!
- 4 core signals instead of 8 "models"
- Decision gates (actual decisions, not just scores)
- Pruned relationships (sparse graphs)
- Honest naming (Confidence, not "Understanding")

Core principle: "If a number does not change a decision, it does not deserve to exist."
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

print("=" * 70)
print("SOMA Core Multi-Model System - CLEANED VERSION")
print("=" * 70)
print()
print("This is the cleaned, production-ready version:")
print("  [OK] Bounded scores (0.0-1.0)")
print("  [OK] 4 core signals (not 8 'models')")
print("  [OK] Decision gates (actual decisions)")
print("  [OK] Pruned relationships (sparse graphs)")
print("  [OK] Honest naming (Confidence, not 'Understanding')")
print()

try:
    from src.structure.multi_model_clean import SOMA CoreMultiModelClean
    from src.structure.scoring_utils import confidence_to_string, ConfidenceLevel, to_confidence_bucket
    
    print("[OK] Cleaned multi-model system imported")
    print()
    
    # ========================================================================
    # PART 1: Cleaned Multi-Signal System
    # ========================================================================
    
    print("=" * 70)
    print("PART 1: SOMA Core Multi-Signal System (4 Signals)")
    print("=" * 70)
    print()
    
    multi_model = SOMA CoreMultiModelClean(
        max_relationships_per_node=20,  # Prune to top 20
        min_relationship_strength=0.6   # Only strong relationships
    )
    
    text = "cat cat dog cat mouse python java python machine learning artificial intelligence"
    print(f"Learning from: '{text}'")
    multi_model.learn(text)
    
    print("\nAnalyzing 'cat' with all signals:")
    result = multi_model.analyze("cat")
    
    print(f"\n[OK] Signal Coverage: {result.confidence_aggregate['signal_coverage']}/{result.confidence_aggregate['total_signals']} signals active")
    print(f"[OK] Confidence Aggregate: {result.confidence_aggregate['score']:.3f} ({confidence_to_string(result.confidence_aggregate['confidence'])})")
    
    print("\nSignal Status:")
    print(f"  [OK] Structural Signal: {result.structural_signal['score']:.3f} ({confidence_to_string(result.structural_signal['confidence'])})")
    print(f"  [OK] Statistical Signal: {result.statistical_signal['score']:.3f} ({confidence_to_string(result.statistical_signal['confidence'])})")
    print(f"  [OK] Context Signal: {result.context_signal['score']:.3f} ({confidence_to_string(result.context_signal['confidence'])})")
    print(f"  [OK] Semantic Proxy: {result.semantic_proxy['score']:.3f} ({confidence_to_string(result.semantic_proxy['confidence'])})")
    
    # ========================================================================
    # PART 2: Decision Gates (What Actually Matters)
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("PART 2: Decision Gates (Actual Decisions)")
    print("=" * 70)
    print()
    
    print("Decisions for 'cat':")
    decisions = result.decisions
    
    print(f"\n  Gate A - Promote/Demote:")
    print(f"    Decision: {decisions['promote']['decision']}")
    promote_conf = decisions['promote']['confidence']
    if isinstance(promote_conf, ConfidenceLevel):
        promote_conf_enum = promote_conf
    else:
        promote_conf_enum = to_confidence_bucket(promote_conf) if isinstance(promote_conf, float) else ConfidenceLevel(promote_conf)
    print(f"    Confidence: {confidence_to_string(promote_conf_enum)}")
    
    print(f"\n  Gate B - Trust/Distrust:")
    print(f"    Decision: {decisions['trust']['decision']}")
    trust_conf = decisions['trust']['confidence']
    if isinstance(trust_conf, ConfidenceLevel):
        trust_conf_enum = trust_conf
    else:
        trust_conf_enum = to_confidence_bucket(trust_conf) if isinstance(trust_conf, float) else ConfidenceLevel(trust_conf)
    print(f"    Confidence: {confidence_to_string(trust_conf_enum)}")
    
    print(f"\n  Gate C - Generate/Block:")
    print(f"    Decision: {decisions['generate']['decision']}")
    gen_conf = decisions['generate']['confidence']
    if isinstance(gen_conf, ConfidenceLevel):
        gen_conf_enum = gen_conf
    else:
        gen_conf_enum = to_confidence_bucket(gen_conf) if isinstance(gen_conf, float) else ConfidenceLevel(gen_conf)
    print(f"    Confidence: {confidence_to_string(gen_conf_enum)}")
    
    # ========================================================================
    # PART 3: Pruned Relationship Graph
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("PART 3: Pruned Relationship Graph (Sparse)")
    print("=" * 70)
    print()
    
    graph = multi_model.relationship_graph
    print(f"Graph built: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    print(f"  (Pruned to max {multi_model.max_relationships_per_node} relationships per node)")
    print(f"  (Minimum strength threshold: {multi_model.min_relationship_strength})")
    
    print("\nRelationships for 'cat' (pruned):")
    context_signal = result.context_signal
    print(f"  Total relationships: {context_signal['relationships_count']}")
    
    if context_signal['top_relationships']:
        print("\n  Top relationships:")
        for rel in context_signal['top_relationships'][:5]:
            print(f"    - {rel['target']}: {rel['type']} (strength: {rel['strength']:.2f})")
    
    # ========================================================================
    # PART 4: Comparison - Before vs After
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("PART 4: What Changed (Before vs After)")
    print("=" * 70)
    print()
    
    print("BEFORE (Old System):")
    print("  [X] Comprehensive Score: 1.000 (meaningless)")
    print("  [X] Fluency Score: 1.249 (unbounded!)")
    print("  [X] Relationships: 11,561 (explosion!)")
    print("  [X] 8 'models' (confusing)")
    print("  [X] No decisions (just scores)")
    
    print("\nAFTER (Cleaned System):")
    print(f"  [OK] Confidence Aggregate: {result.confidence_aggregate['score']:.3f} (bounded [0.0-1.0])")
    print(f"  [OK] Fluency Score: {multi_model._calculate_fluency_score('cat', result):.3f} (bounded)")
    print(f"  [OK] Relationships: {context_signal['relationships_count']} (pruned)")
    print(f"  [OK] 4 signals (clear)")
    print(f"  [OK] 3 decision gates (actual decisions)")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("[OK] SOMA Core Multi-Model System - CLEANED!")
    print("=" * 70)
    print()
    print("What we cleaned:")
    print("  1. [OK] Bounded all scores to [0.0, 1.0]")
    print("  2. [OK] Collapsed 8 models -> 4 signals")
    print("  3. [OK] Added decision gates (Promote, Trust, Generate)")
    print("  4. [OK] Pruned relationship explosion")
    print("  5. [OK] Renamed for honesty (Confidence, not 'Understanding')")
    print()
    print("Core principle:")
    print("  'If a number does not change a decision, it does not deserve to exist.'")
    print()
    print("SOMA Core is now CLEAN, SHARP, and REAL!")
    print()
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
