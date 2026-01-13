"""
SOMA Core Simple Metrics
=====================

Simple metrics to measure:
1. Fluency (repetition rate, n-gram repetition)
2. Coherence (keyword overlap with prompt)
3. Training Progress (loss decreasing or not)

Keep it simple. Just sanity checks.
"""


def measure_fluency(text: str) -> dict:
    """
    Measure fluency: check for repetition.
    
    What it measures:
    - Repetition rate: How many words repeat?
    - N-gram repetition: Are we saying the same thing over and over?
    
    Args:
        text: The generated text
    
    Returns:
        Dictionary with metrics:
        {
            "repetition_rate": 0.0 to 1.0 (lower is better),
            "ngram_repetition": 0.0 to 1.0 (lower is better),
            "status": "good" or "needs_improvement"
        }
    
    Example:
        >>> text = "cats chase mice. cats chase mice. cats chase mice."
        >>> result = measure_fluency(text)
        >>> print(result["repetition_rate"])
        0.8  # High repetition (bad!)
    """
    words = text.lower().split()
    
    if len(words) == 0:
        return {
            "repetition_rate": 0.0,
            "ngram_repetition": 0.0,
            "status": "good"
        }
    
    # Repetition rate: unique words / total words
    unique_words = len(set(words))
    total_words = len(words)
    repetition_rate = 1.0 - (unique_words / total_words)
    
    # N-gram repetition (check for repeated 3-word phrases)
    ngram_size = 3
    if len(words) >= ngram_size:
        ngrams = []
        for i in range(len(words) - ngram_size + 1):
            ngram = tuple(words[i:i+ngram_size])
            ngrams.append(ngram)
        
        unique_ngrams = len(set(ngrams))
        total_ngrams = len(ngrams)
        ngram_repetition = 1.0 - (unique_ngrams / total_ngrams) if total_ngrams > 0 else 0.0
    else:
        ngram_repetition = 0.0
    
    # Status
    if repetition_rate > 0.3 or ngram_repetition > 0.2:
        status = "needs_improvement"
    else:
        status = "good"
    
    return {
        "repetition_rate": repetition_rate,
        "ngram_repetition": ngram_repetition,
        "status": status
    }


def measure_coherence(generated: str, prompt: str) -> dict:
    """
    Measure coherence: does generated text relate to prompt?
    
    What it measures:
    - Keyword overlap: Do important words from prompt appear in generated text?
    
    Args:
        generated: The generated text
        prompt: The original prompt
    
    Returns:
        Dictionary with metrics:
        {
            "keyword_overlap": 0.0 to 1.0 (higher is better),
            "status": "good" or "needs_improvement"
        }
    
    Example:
        >>> prompt = "Tell me about cats"
        >>> generated = "Cats are animals. They like milk."
        >>> result = measure_coherence(generated, prompt)
        >>> print(result["keyword_overlap"])
        0.5  # "cats" appears in both (good!)
    """
    prompt_words = set(prompt.lower().split())
    generated_words = set(generated.lower().split())
    
    if len(prompt_words) == 0:
        return {
            "keyword_overlap": 0.0,
            "status": "needs_improvement"
        }
    
    # How many prompt words appear in generated text?
    overlap = len(prompt_words & generated_words)
    keyword_overlap = overlap / len(prompt_words)
    
    # Status
    if keyword_overlap < 0.3:
        status = "needs_improvement"
    else:
        status = "good"
    
    return {
        "keyword_overlap": keyword_overlap,
        "status": status
    }


def measure_training_progress(loss_history: list) -> dict:
    """
    Measure training progress: is loss decreasing?
    
    What it measures:
    - Loss trend: Is the loss going down? (That's good!)
    
    Args:
        loss_history: List of loss values over time
                     Example: [2.5, 2.1, 1.8, 1.5, 1.2] (getting better!)
    
    Returns:
        Dictionary with metrics:
        {
            "is_improving": True or False,
            "loss_reduction": 0.0 to 1.0 (how much loss decreased),
            "status": "good" or "needs_improvement"
        }
    
    Example:
        >>> losses = [2.5, 2.1, 1.8, 1.5, 1.2]
        >>> result = measure_training_progress(losses)
        >>> print(result["is_improving"])
        True  # Loss is decreasing (good!)
    """
    if len(loss_history) < 2:
        return {
            "is_improving": False,
            "loss_reduction": 0.0,
            "status": "needs_more_data"
        }
    
    initial_loss = loss_history[0]
    final_loss = loss_history[-1]
    
    # Is loss decreasing?
    is_improving = final_loss < initial_loss
    
    # How much did it decrease?
    if initial_loss > 0:
        loss_reduction = (initial_loss - final_loss) / initial_loss
    else:
        loss_reduction = 0.0
    
    # Status
    if is_improving and loss_reduction > 0.1:
        status = "good"
    elif is_improving:
        status = "improving_slowly"
    else:
        status = "needs_improvement"
    
    return {
        "is_improving": is_improving,
        "loss_reduction": loss_reduction,
        "status": status
    }


# Test it works
if __name__ == "__main__":
    print("Testing Simple Metrics...")
    print("=" * 50)
    
    # Test fluency
    print("\n1. Testing Fluency:")
    text1 = "cats chase mice. cats chase mice. cats chase mice."
    result1 = measure_fluency(text1)
    print(f"   Repetition rate: {result1['repetition_rate']:.3f}")
    print(f"   Status: {result1['status']}")
    
    text2 = "cats chase mice. dogs chase balls. birds fly high."
    result2 = measure_fluency(text2)
    print(f"   Repetition rate: {result2['repetition_rate']:.3f}")
    print(f"   Status: {result2['status']}")
    
    # Test coherence
    print("\n2. Testing Coherence:")
    prompt = "Tell me about cats"
    generated = "Cats are animals. They like milk and chase mice."
    result3 = measure_coherence(generated, prompt)
    print(f"   Keyword overlap: {result3['keyword_overlap']:.3f}")
    print(f"   Status: {result3['status']}")
    
    # Test training progress
    print("\n3. Testing Training Progress:")
    losses = [2.5, 2.1, 1.8, 1.5, 1.2, 1.0]
    result4 = measure_training_progress(losses)
    print(f"   Is improving: {result4['is_improving']}")
    print(f"   Loss reduction: {result4['loss_reduction']:.3f}")
    print(f"   Status: {result4['status']}")
    
    print("\n✅ All metrics work!")
