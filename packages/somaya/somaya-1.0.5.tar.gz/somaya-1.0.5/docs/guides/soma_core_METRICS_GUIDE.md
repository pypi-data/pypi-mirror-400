# SOMA Core Logical Metrics System - Complete Guide

## 🎯 Purpose

SOMA Core Logical Metrics is a **custom metrics system** designed specifically to help SOMA Core improve. These metrics are:

- **Logical**: Based on sound reasoning principles
- **Actionable**: Tell you exactly what to improve
- **Measurable**: Quantifiable and comparable
- **Unique to SOMA Core**: Designed for SOMA Core's specific needs

## 📊 Available Metrics

### 1. Generation Quality Metrics

#### Fluency
Measures how smooth and natural the generated text is.

**What it measures:**
- Repetition rate (lower is better)
- Vocabulary diversity (higher is better)
- Sentence length consistency
- N-gram repetition (prevents stuttering)

**Example:**
```python
from soma_cognitive.algorithms.soma_core_metrics import SOMA CoreMetrics

metrics = SOMA CoreMetrics()
result = metrics.measure_fluency(generated_text)
print(result.explain())
```

**Recommendations:**
- If repetition rate > 0.3: Increase repetition penalty
- If vocab diversity < 0.5: Use more varied training data
- If n-gram repetition > 0.2: Enable n-gram blocking

#### Coherence
Measures how well the text relates to the prompt.

**What it measures:**
- Topic alignment (keyword overlap)
- Context preservation (key concepts maintained)
- Logical flow (transition words)

**Example:**
```python
result = metrics.measure_coherence(generated_text, prompt)
print(result.explain())
```

**Recommendations:**
- If topic alignment < 0.5: Improve prompt following
- If context preservation < 0.5: Better context handling

#### Creativity
Measures uniqueness and novelty of generated text.

**What it measures:**
- Uniqueness (not just copying training data)
- Novelty (new combinations)
- Diversity (varied expressions)

**Example:**
```python
result = metrics.measure_creativity(
    generated_text,
    training_data_sample=training_data
)
print(result.explain())
```

**Recommendations:**
- If novelty < 0.3: Reduce overfitting
- If diversity < 0.4: Vary sentence structures

### 2. Training Effectiveness Metrics

#### Training Quality
Measures how effective the training process is.

**What it measures:**
- Data sufficiency (enough training examples)
- Training progress (loss reduction)
- Convergence (loss stability)
- Overfitting risk

**Example:**
```python
result = metrics.measure_training_quality(
    training_data_size=5000,
    epochs=20,
    loss_history=[2.5, 2.1, 1.8, 1.5, 1.2, 1.0, 0.9, 0.85, 0.82, 0.80],
    validation_loss=0.85
)
print(result.explain())
```

**Recommendations:**
- If data sufficiency < 0.5: Add more training data (aim for 10K+)
- If progress < 0.3: Loss not decreasing - check learning rate
- If overfitting risk > 0.7: Add regularization or more data

### 3. System Efficiency Metrics

#### Generation Speed
Measures how fast SOMA Core generates text.

**What it measures:**
- Tokens per second
- Efficiency relative to model size

**Example:**
```python
result = metrics.measure_generation_speed(
    tokens_generated=100,
    time_taken=2.5,  # seconds
    model_size=10_000_000  # 10M parameters
)
print(result.explain())
```

**Recommendations:**
- If tokens/sec < 10: Optimize model or use faster hardware
- If model efficiency < 0.3: Consider model compression

### 4. Overall Health Score

Combines all metrics into a single health indicator.

**Example:**
```python
health = metrics.calculate_health_score(
    fluency_result=fluency_result,
    coherence_result=coherence_result,
    training_result=training_result,
    speed_result=speed_result
)
print(health.explain())
```

## 📈 Tracking Improvements Over Time

### Track Metrics
```python
# Track a metric value
metrics.track_metric("fluency", 0.75)
metrics.track_metric("fluency", 0.78)
metrics.track_metric("fluency", 0.82)
```

### Get Trends
```python
trend = metrics.get_metric_trend("fluency")
# Returns: "improving", "stable", or "declining"
```

### Improvement Report
```python
report = metrics.get_improvement_report()
print(report)
```

## 🚀 Quick Start

### Quick Measurement
```python
from soma_cognitive.algorithms.soma_core_metrics import measure_soma_core_performance

results = measure_soma_core_performance(
    generated_text="Your generated text here",
    prompt="Your prompt here",
    training_data=["sample1", "sample2", ...]
)

# Access results
print(results["fluency"].score)
print(results["coherence"].score)
print(results["health"].score)
```

### Full Example
```python
from soma_cognitive.algorithms.soma_core_metrics import SOMA CoreMetrics

# Create metrics instance
metrics = SOMA CoreMetrics()

# Measure fluency
fluency = metrics.measure_fluency(generated_text)
print(f"Fluency: {fluency.score:.2f} ({fluency.status})")

# Measure coherence
coherence = metrics.measure_coherence(generated_text, prompt)
print(f"Coherence: {coherence.score:.2f} ({coherence.status})")

# Get overall health
health = metrics.calculate_health_score(
    fluency_result=fluency,
    coherence_result=coherence
)
print(f"SOMA Core Health: {health.score:.2f} ({health.status})")

# Get recommendations
for rec in health.recommendations:
    print(f"  - {rec}")
```

## 📊 Status Levels

Metrics use these status levels:

- **Excellent** (≥ 0.9): Outstanding performance
- **Good** (≥ 0.7): Solid performance
- **Fair** (≥ 0.5): Acceptable but needs improvement
- **Poor** (≥ 0.3): Significant issues
- **Critical** (< 0.3): Major problems

## 🎯 Using Metrics to Improve SOMA Core

### Step 1: Measure Current Performance
```python
results = measure_soma_core_performance(generated_text, prompt)
```

### Step 2: Identify Weak Areas
```python
for name, result in results.items():
    if result.status in ["poor", "critical"]:
        print(f"{name} needs improvement!")
        for rec in result.recommendations:
            print(f"  - {rec}")
```

### Step 3: Make Improvements
Follow the recommendations to improve weak areas.

### Step 4: Track Progress
```python
metrics.track_metric("fluency", result.score)
# ... make improvements ...
metrics.track_metric("fluency", new_result.score)
print(metrics.get_improvement_report())
```

## 🔧 Integration with SOMA Core

### In Training Scripts
```python
from soma_cognitive.algorithms.soma_core_metrics import SOMA CoreMetrics

metrics = SOMA CoreMetrics()

# After training
training_result = metrics.measure_training_quality(
    training_data_size=len(training_data),
    epochs=epochs,
    loss_history=losses,
    validation_loss=val_loss
)

print(training_result.explain())
```

### In Generation Scripts
```python
# After generation
fluency = metrics.measure_fluency(generated_text)
coherence = metrics.measure_coherence(generated_text, prompt)

# Track for improvement
metrics.track_metric("fluency", fluency.score)
metrics.track_metric("coherence", coherence.score)
```

## 📝 Example Output

```
=== Fluency ===
Value: 0.8234
Score: 0.8234 (good)

Breakdown:
  repetition_rate: 0.1200
  vocab_diversity: 0.8500
  length_consistency: 0.7800
  ngram_repetition: 0.0500

Recommendations:
  1. Reduce repetition - increase repetition penalty

Trend: improving
```

## ✨ Key Benefits

1. **Actionable**: Every metric comes with specific recommendations
2. **Comprehensive**: Covers all aspects of SOMA Core performance
3. **Trackable**: Monitor improvements over time
4. **Logical**: Based on sound reasoning principles
5. **Unique**: Designed specifically for SOMA Core

## 🎓 Best Practices

1. **Measure regularly**: Track metrics after each improvement
2. **Focus on weak areas**: Prioritize metrics with "poor" or "critical" status
3. **Follow recommendations**: Each recommendation is actionable
4. **Track trends**: Use trend analysis to see if improvements are working
5. **Combine metrics**: Use health score to get overall picture

## 📚 Files

- **`soma_core_metrics.py`**: Main metrics system
- **`USE_SANTEK_METRICS.py`**: Example usage script
- **`SANTEK_METRICS_GUIDE.md`**: This guide

## 🚀 Next Steps

1. Run `USE_SANTEK_METRICS.py` to see examples
2. Integrate metrics into your training/generation scripts
3. Track metrics over time to measure improvements
4. Use recommendations to guide optimization efforts

---

**SOMA Core Metrics**: Helping SOMA Core improve, one measurement at a time! 🎯
