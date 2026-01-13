"""
Use SOMA Core Metrics - Quick Start Guide
======================================

This script shows you how to use SOMA Core's custom logical metrics
to measure performance and guide improvements.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

print("\n" + "=" * 70)
print("SOMA Core Logical Metrics System")
print("=" * 70)
print()
print("Custom metrics designed to help SOMA Core improve!")
print()

try:
    from soma_cognitive.algorithms.soma_core_metrics import (
        SOMA CoreMetrics,
        measure_soma_core_performance
    )
    
    print("[OK] SOMA Core Metrics imported")
    print()
    
    # Create metrics instance
    metrics = SOMA CoreMetrics()
    
    # Example 1: Measure fluency
    print("=" * 70)
    print("Example 1: Measuring Fluency")
    print("=" * 70)
    print()
    
    test_text = """
    The quick brown fox jumps over the lazy dog. It gracefully lands on the other side,
    its tail swishing through the air. The dog watches with mild interest, too lazy to
    give chase. The fox continues its journey through the forest, searching for food.
    """
    
    fluency_result = metrics.measure_fluency(test_text)
    print(fluency_result.explain())
    print()
    
    # Example 2: Measure coherence
    print("=" * 70)
    print("Example 2: Measuring Coherence")
    print("=" * 70)
    print()
    
    prompt = "Tell me about machine learning"
    generated = "Machine learning is a subset of artificial intelligence. It enables computers to learn from data without explicit programming. Deep learning uses neural networks with multiple layers."
    
    coherence_result = metrics.measure_coherence(generated, prompt)
    print(coherence_result.explain())
    print()
    
    # Example 3: Measure training quality
    print("=" * 70)
    print("Example 3: Measuring Training Quality")
    print("=" * 70)
    print()
    
    training_result = metrics.measure_training_quality(
        training_data_size=5000,
        epochs=20,
        loss_history=[2.5, 2.1, 1.8, 1.5, 1.2, 1.0, 0.9, 0.85, 0.82, 0.80],
        validation_loss=0.85
    )
    print(training_result.explain())
    print()
    
    # Example 4: Measure generation speed
    print("=" * 70)
    print("Example 4: Measuring Generation Speed")
    print("=" * 70)
    print()
    
    speed_result = metrics.measure_generation_speed(
        tokens_generated=100,
        time_taken=2.5,  # seconds
        model_size=10_000_000  # 10M parameters
    )
    print(speed_result.explain())
    print()
    
    # Example 5: Overall health score
    print("=" * 70)
    print("Example 5: Overall SOMA Core Health Score")
    print("=" * 70)
    print()
    
    health_result = metrics.calculate_health_score(
        fluency_result=fluency_result,
        coherence_result=coherence_result,
        training_result=training_result,
        speed_result=speed_result
    )
    print(health_result.explain())
    print()
    
    # Example 6: Track metrics over time
    print("=" * 70)
    print("Example 6: Tracking Metrics Over Time")
    print("=" * 70)
    print()
    
    # Simulate tracking metrics
    metrics.track_metric("fluency", 0.75)
    metrics.track_metric("fluency", 0.78)
    metrics.track_metric("fluency", 0.82)
    metrics.track_metric("fluency", 0.85)
    
    metrics.track_metric("coherence", 0.70)
    metrics.track_metric("coherence", 0.72)
    metrics.track_metric("coherence", 0.75)
    metrics.track_metric("coherence", 0.77)
    
    print("Improvement Report:")
    print(metrics.get_improvement_report())
    print()
    
    # Example 7: Quick measurement function
    print("=" * 70)
    print("Example 7: Quick Performance Measurement")
    print("=" * 70)
    print()
    
    results = measure_soma_core_performance(
        generated_text=generated,
        prompt=prompt,
        training_data=["Machine learning is AI", "Deep learning uses neural networks"]
    )
    
    print("Quick Measurement Results:")
    for name, result in results.items():
        print(f"\n{name.upper()}:")
        print(f"  Score: {result.score:.4f} ({result.status})")
        if result.recommendations:
            print(f"  Recommendations: {len(result.recommendations)}")
    
    print()
    print("=" * 70)
    print("[OK] SOMA Core Metrics Demo Complete!")
    print("=" * 70)
    print()
    print("Key Features:")
    print("  ✅ Measure fluency, coherence, creativity")
    print("  ✅ Track training quality")
    print("  ✅ Monitor generation speed")
    print("  ✅ Calculate overall health score")
    print("  ✅ Track improvements over time")
    print("  ✅ Get actionable recommendations")
    print()
    print("Use these metrics to guide SOMA Core improvements!")
    print()
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print()
    print("Please make sure you're in the correct directory.")
    print()
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    print()
