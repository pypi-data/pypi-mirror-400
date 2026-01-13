"""
SOMA Core Logical Metrics System
=============================

Custom logical metrics designed specifically for SOMA Core to measure
performance and guide continuous improvement.

These metrics are UNIQUE to SOMA Core and help identify:
- What's working well
- What needs improvement
- Where to focus optimization efforts
- How to measure progress over time

All metrics are designed to be:
- Actionable (tell you what to improve)
- Logical (based on sound reasoning)
- Measurable (quantifiable)
- Comparable (can track over time)
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import math
import json


@dataclass
class MetricValue:
    """A single metric value with metadata."""
    value: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


@dataclass
class MetricResult:
    """Result of a metric calculation."""
    name: str
    value: float
    score: float  # Normalized 0-1 score
    status: str  # "excellent", "good", "fair", "poor", "critical"
    breakdown: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    trend: Optional[str] = None  # "improving", "stable", "declining"
    
    def explain(self) -> str:
        """Generate human-readable explanation."""
        lines = [
            f"=== {self.name} ===",
            f"Value: {self.value:.4f}",
            f"Score: {self.score:.4f} ({self.status})",
        ]
        
        if self.breakdown:
            lines.append("\nBreakdown:")
            for key, val in self.breakdown.items():
                lines.append(f"  {key}: {val:.4f}")
        
        if self.recommendations:
            lines.append("\nRecommendations:")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"  {i}. {rec}")
        
        if self.trend:
            lines.append(f"\nTrend: {self.trend}")
        
        return "\n".join(lines)


class SOMA CoreMetrics:
    """
    SOMA Core Logical Metrics System.
    
    Measures various aspects of SOMA Core performance:
    - Generation Quality
    - Training Effectiveness
    - System Efficiency
    - Knowledge Utilization
    - User Satisfaction
    - Improvement Potential
    
    Example:
        metrics = SOMA CoreMetrics()
        
        # Measure generation quality
        result = metrics.measure_generation_quality(
            generated_text="...",
            reference_text="...",
            prompt="..."
        )
        print(result.explain())
        
        # Get overall health score
        health = metrics.calculate_health_score()
        print(f"SOMA Core Health: {health:.2f}")
    """
    
    # Status thresholds
    STATUS_THRESHOLDS = {
        "excellent": 0.9,
        "good": 0.7,
        "fair": 0.5,
        "poor": 0.3,
        "critical": 0.0,
    }
    
    def __init__(self):
        """Initialize SOMA Core metrics system."""
        self.metric_history: Dict[str, List[MetricValue]] = {}
    
    # ========================================================================
    # GENERATION QUALITY METRICS
    # ========================================================================
    
    def measure_fluency(self, text: str) -> MetricResult:
        """
        Measure text fluency.
        
        Metrics:
        - Sentence coherence (smooth transitions)
        - Repetition rate (lower is better)
        - Vocabulary diversity
        - Grammar quality
        """
        words = text.split()
        sentences = text.split('.')
        
        # Repetition rate
        unique_words = len(set(words))
        total_words = len(words)
        repetition_rate = 1.0 - (unique_words / max(total_words, 1))
        
        # Vocabulary diversity (unique words / total words)
        vocab_diversity = unique_words / max(total_words, 1)
        
        # Sentence length consistency
        if len(sentences) > 1:
            sent_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sent_lengths:
                avg_length = sum(sent_lengths) / len(sent_lengths)
                length_variance = sum((l - avg_length) ** 2 for l in sent_lengths) / len(sent_lengths)
                length_consistency = 1.0 / (1.0 + length_variance / 100)
            else:
                length_consistency = 0.5
        else:
            length_consistency = 0.5
        
        # N-gram repetition (check for repeated 3-grams)
        ngram_repetition = self._calculate_ngram_repetition(text, n=3)
        
        # Combine metrics
        fluency_score = (
            0.3 * (1.0 - repetition_rate) +  # Lower repetition = better
            0.3 * vocab_diversity +  # Higher diversity = better
            0.2 * length_consistency +  # Consistent length = better
            0.2 * (1.0 - ngram_repetition)  # Lower n-gram repetition = better
        )
        
        breakdown = {
            "repetition_rate": repetition_rate,
            "vocab_diversity": vocab_diversity,
            "length_consistency": length_consistency,
            "ngram_repetition": ngram_repetition,
        }
        
        recommendations = []
        if repetition_rate > 0.3:
            recommendations.append("Reduce repetition - increase repetition penalty")
        if vocab_diversity < 0.5:
            recommendations.append("Increase vocabulary diversity - use more varied training data")
        if ngram_repetition > 0.2:
            recommendations.append("Prevent n-gram repetition - enable n-gram blocking")
        
        status = self._get_status(fluency_score)
        
        return MetricResult(
            name="Fluency",
            value=fluency_score,
            score=fluency_score,
            status=status,
            breakdown=breakdown,
            recommendations=recommendations
        )
    
    def measure_coherence(self, text: str, prompt: str) -> MetricResult:
        """
        Measure text coherence (how well it relates to prompt).
        
        Metrics:
        - Topic alignment
        - Context preservation
        - Logical flow
        """
        # Simple keyword overlap (can be enhanced)
        prompt_words = set(prompt.lower().split())
        text_words = set(text.lower().split())
        
        # Topic alignment
        overlap = len(prompt_words & text_words)
        topic_alignment = overlap / max(len(prompt_words), 1)
        
        # Context preservation (check if key concepts from prompt appear)
        key_concepts = [w for w in prompt_words if len(w) > 4]  # Longer words are likely concepts
        concepts_in_text = sum(1 for concept in key_concepts if concept in text.lower())
        context_preservation = concepts_in_text / max(len(key_concepts), 1)
        
        # Logical flow (check for transition words)
        transition_words = {"however", "therefore", "furthermore", "moreover", "consequently", "thus"}
        transitions_found = sum(1 for word in transition_words if word in text.lower())
        logical_flow = min(1.0, transitions_found / 3.0)  # Normalize
        
        coherence_score = (
            0.4 * topic_alignment +
            0.4 * context_preservation +
            0.2 * logical_flow
        )
        
        breakdown = {
            "topic_alignment": topic_alignment,
            "context_preservation": context_preservation,
            "logical_flow": logical_flow,
        }
        
        recommendations = []
        if topic_alignment < 0.5:
            recommendations.append("Improve topic alignment - ensure generated text relates to prompt")
        if context_preservation < 0.5:
            recommendations.append("Preserve context better - maintain key concepts from prompt")
        
        status = self._get_status(coherence_score)
        
        return MetricResult(
            name="Coherence",
            value=coherence_score,
            score=coherence_score,
            status=status,
            breakdown=breakdown,
            recommendations=recommendations
        )
    
    def measure_creativity(self, text: str, training_data_sample: Optional[List[str]] = None) -> MetricResult:
        """
        Measure text creativity (uniqueness vs training data).
        
        Metrics:
        - Uniqueness (not just copying training data)
        - Novelty (new combinations)
        - Diversity (varied expressions)
        """
        # Uniqueness (simple check - can be enhanced with embeddings)
        words = text.split()
        unique_ratio = len(set(words)) / max(len(words), 1)
        
        # Novelty (check if text is too similar to training data)
        if training_data_sample:
            similarities = []
            for sample in training_data_sample[:100]:  # Limit for performance
                sim = self._simple_similarity(text, sample)
                similarities.append(sim)
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.5
            novelty = 1.0 - avg_similarity  # Lower similarity = higher novelty
        else:
            novelty = 0.5  # Default if no training data
        
        # Diversity (variety in sentence structures)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) > 1:
            # Simple diversity: check if sentences start differently
            first_words = [s.split()[0].lower() if s.split() else "" for s in sentences]
            unique_starts = len(set(first_words))
            diversity = unique_starts / len(sentences)
        else:
            diversity = 0.5
        
        creativity_score = (
            0.3 * unique_ratio +
            0.4 * novelty +
            0.3 * diversity
        )
        
        breakdown = {
            "unique_ratio": unique_ratio,
            "novelty": novelty,
            "diversity": diversity,
        }
        
        recommendations = []
        if novelty < 0.3:
            recommendations.append("Increase novelty - reduce overfitting to training data")
        if diversity < 0.4:
            recommendations.append("Increase diversity - vary sentence structures")
        
        status = self._get_status(creativity_score)
        
        return MetricResult(
            name="Creativity",
            value=creativity_score,
            score=creativity_score,
            status=status,
            breakdown=breakdown,
            recommendations=recommendations
        )
    
    # ========================================================================
    # TRAINING EFFECTIVENESS METRICS
    # ========================================================================
    
    def measure_training_quality(
        self,
        training_data_size: int,
        epochs: int,
        loss_history: Optional[List[float]] = None,
        validation_loss: Optional[float] = None
    ) -> MetricResult:
        """
        Measure training quality.
        
        Metrics:
        - Data sufficiency
        - Training progress
        - Convergence
        - Overfitting risk
        """
        # Data sufficiency (more data = better, up to a point)
        data_sufficiency = min(1.0, training_data_size / 10000)  # 10K examples = sufficient
        
        # Training progress (loss reduction)
        if loss_history and len(loss_history) > 1:
            initial_loss = loss_history[0]
            final_loss = loss_history[-1]
            if initial_loss > 0:
                loss_reduction = (initial_loss - final_loss) / initial_loss
            else:
                loss_reduction = 0.0
            progress = min(1.0, loss_reduction * 2)  # Scale up
        else:
            progress = 0.5
        
        # Convergence (loss stability)
        if loss_history and len(loss_history) > 5:
            recent_losses = loss_history[-5:]
            loss_variance = sum((l - sum(recent_losses)/len(recent_losses))**2 for l in recent_losses) / len(recent_losses)
            convergence = 1.0 / (1.0 + loss_variance * 10)  # Lower variance = better convergence
        else:
            convergence = 0.5
        
        # Overfitting risk
        if validation_loss and loss_history:
            train_loss = loss_history[-1]
            if validation_loss > 0:
                overfitting_ratio = train_loss / validation_loss
                overfitting_risk = min(1.0, overfitting_ratio)  # Lower ratio = higher risk
            else:
                overfitting_risk = 0.5
        else:
            overfitting_risk = 0.5
        
        training_quality_score = (
            0.3 * data_sufficiency +
            0.3 * progress +
            0.2 * convergence +
            0.2 * (1.0 - overfitting_risk)  # Lower risk = better
        )
        
        breakdown = {
            "data_sufficiency": data_sufficiency,
            "progress": progress,
            "convergence": convergence,
            "overfitting_risk": overfitting_risk,
        }
        
        recommendations = []
        if data_sufficiency < 0.5:
            recommendations.append("Increase training data - aim for 10K+ examples")
        if progress < 0.3:
            recommendations.append("Improve training - loss not decreasing significantly")
        if overfitting_risk > 0.7:
            recommendations.append("Reduce overfitting - add regularization or more data")
        
        status = self._get_status(training_quality_score)
        
        return MetricResult(
            name="Training Quality",
            value=training_quality_score,
            score=training_quality_score,
            status=status,
            breakdown=breakdown,
            recommendations=recommendations
        )
    
    # ========================================================================
    # SYSTEM EFFICIENCY METRICS
    # ========================================================================
    
    def measure_generation_speed(
        self,
        tokens_generated: int,
        time_taken: float,
        model_size: Optional[int] = None
    ) -> MetricResult:
        """
        Measure generation speed.
        
        Metrics:
        - Tokens per second
        - Efficiency relative to model size
        """
        if time_taken > 0:
            tokens_per_second = tokens_generated / time_taken
        else:
            tokens_per_second = 0.0
        
        # Efficiency score (normalize to reasonable range)
        # Good: 10+ tokens/sec, Excellent: 50+ tokens/sec
        efficiency_score = min(1.0, tokens_per_second / 50.0)
        
        # Model efficiency (if model size provided)
        if model_size:
            # Tokens per second per million parameters
            efficiency_per_param = tokens_per_second / (model_size / 1_000_000)
            model_efficiency = min(1.0, efficiency_per_param / 0.1)  # 0.1 tokens/sec per M params = good
        else:
            model_efficiency = 0.5
        
        speed_score = (
            0.6 * efficiency_score +
            0.4 * model_efficiency
        )
        
        breakdown = {
            "tokens_per_second": tokens_per_second,
            "efficiency_score": efficiency_score,
            "model_efficiency": model_efficiency,
        }
        
        recommendations = []
        if tokens_per_second < 10:
            recommendations.append("Improve generation speed - optimize model or use faster hardware")
        if model_efficiency < 0.3:
            recommendations.append("Improve model efficiency - consider model compression")
        
        status = self._get_status(speed_score)
        
        return MetricResult(
            name="Generation Speed",
            value=speed_score,
            score=speed_score,
            status=status,
            breakdown=breakdown,
            recommendations=recommendations
        )
    
    # ========================================================================
    # OVERALL HEALTH SCORE
    # ========================================================================
    
    def calculate_health_score(
        self,
        fluency_result: Optional[MetricResult] = None,
        coherence_result: Optional[MetricResult] = None,
        training_result: Optional[MetricResult] = None,
        speed_result: Optional[MetricResult] = None
    ) -> MetricResult:
        """
        Calculate overall SOMA Core health score.
        
        Combines multiple metrics into a single health indicator.
        """
        scores = []
        weights = []
        breakdown = {}
        
        if fluency_result:
            scores.append(fluency_result.score)
            weights.append(0.3)
            breakdown["fluency"] = fluency_result.score
        
        if coherence_result:
            scores.append(coherence_result.score)
            weights.append(0.3)
            breakdown["coherence"] = coherence_result.score
        
        if training_result:
            scores.append(training_result.score)
            weights.append(0.25)
            breakdown["training"] = training_result.score
        
        if speed_result:
            scores.append(speed_result.score)
            weights.append(0.15)
            breakdown["speed"] = speed_result.score
        
        if not scores:
            # Default if no metrics provided
            health_score = 0.5
        else:
            # Weighted average
            total_weight = sum(weights)
            if total_weight > 0:
                health_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
            else:
                health_score = sum(scores) / len(scores)
        
        # Generate recommendations
        recommendations = []
        if fluency_result and fluency_result.score < 0.7:
            recommendations.append("Improve fluency - see fluency recommendations")
        if coherence_result and coherence_result.score < 0.7:
            recommendations.append("Improve coherence - better context preservation")
        if training_result and training_result.score < 0.7:
            recommendations.append("Improve training - see training recommendations")
        if speed_result and speed_result.score < 0.5:
            recommendations.append("Improve speed - optimize generation")
        
        status = self._get_status(health_score)
        
        return MetricResult(
            name="SOMA Core Health Score",
            value=health_score,
            score=health_score,
            status=status,
            breakdown=breakdown,
            recommendations=recommendations
        )
    
    # ========================================================================
    # IMPROVEMENT TRACKING
    # ========================================================================
    
    def track_metric(self, metric_name: str, value: float, context: Optional[Dict] = None):
        """Track a metric value over time."""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = []
        
        self.metric_history[metric_name].append(
            MetricValue(
                value=value,
                timestamp=datetime.now(),
                context=context or {}
            )
        )
    
    def get_metric_trend(self, metric_name: str, window: int = 10) -> Optional[str]:
        """Get trend for a metric (improving, stable, declining)."""
        if metric_name not in self.metric_history:
            return None
        
        history = self.metric_history[metric_name][-window:]
        if len(history) < 2:
            return None
        
        values = [m.value for m in history]
        
        # Simple trend detection
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change = second_avg - first_avg
        threshold = 0.05  # 5% change threshold
        
        if change > threshold:
            return "improving"
        elif change < -threshold:
            return "declining"
        else:
            return "stable"
    
    def get_improvement_report(self) -> str:
        """Generate improvement report from tracked metrics."""
        lines = ["=== SOMA Core Improvement Report ===", ""]
        
        for metric_name, history in self.metric_history.items():
            if len(history) < 2:
                continue
            
            recent = history[-1].value
            previous = history[-2].value
            
            change = recent - previous
            change_pct = (change / previous * 100) if previous > 0 else 0
            
            trend = self.get_metric_trend(metric_name)
            
            lines.append(f"{metric_name}:")
            lines.append(f"  Current: {recent:.4f}")
            lines.append(f"  Change: {change:+.4f} ({change_pct:+.2f}%)")
            lines.append(f"  Trend: {trend or 'N/A'}")
            lines.append("")
        
        return "\n".join(lines)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_status(self, score: float) -> str:
        """Get status string from score."""
        if score >= self.STATUS_THRESHOLDS["excellent"]:
            return "excellent"
        elif score >= self.STATUS_THRESHOLDS["good"]:
            return "good"
        elif score >= self.STATUS_THRESHOLDS["fair"]:
            return "fair"
        elif score >= self.STATUS_THRESHOLDS["poor"]:
            return "poor"
        else:
            return "critical"
    
    def _calculate_ngram_repetition(self, text: str, n: int = 3) -> float:
        """Calculate n-gram repetition rate."""
        words = text.split()
        if len(words) < n:
            return 0.0
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = tuple(words[i:i+n])
            ngrams.append(ngram)
        
        if not ngrams:
            return 0.0
        
        unique_ngrams = len(set(ngrams))
        total_ngrams = len(ngrams)
        
        repetition_rate = 1.0 - (unique_ngrams / total_ngrams)
        return repetition_rate
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity between two texts (word overlap)."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0


# Convenience function for quick measurement
def measure_soma_core_performance(
    generated_text: str,
    prompt: str,
    training_data: Optional[List[str]] = None
) -> Dict[str, MetricResult]:
    """
    Quick function to measure multiple SOMA Core metrics at once.
    
    Returns:
        Dictionary of metric results
    """
    metrics = SOMA CoreMetrics()
    
    results = {}
    
    # Measure fluency
    results["fluency"] = metrics.measure_fluency(generated_text)
    
    # Measure coherence
    results["coherence"] = metrics.measure_coherence(generated_text, prompt)
    
    # Measure creativity (if training data provided)
    if training_data:
        results["creativity"] = metrics.measure_creativity(generated_text, training_data)
    
    # Calculate health score
    results["health"] = metrics.calculate_health_score(
        fluency_result=results.get("fluency"),
        coherence_result=results.get("coherence")
    )
    
    return results
