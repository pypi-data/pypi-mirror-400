"""
Simple TinySLM Usage Example

This is a minimal example showing how to use the TinySLM
with soma. It's designed to run on any CPU with minimal resources.

Usage:
    python examples/simple_tiny_slm.py
"""

from soma_cognitive.slm import TinySLMWrapper


def main():
    """Simple example of using TinySLM."""
    
    print("=" * 60)
    print("TinySLM - Simple Usage Example")
    print("=" * 60)
    print()
    
    # Step 1: Create the SLM (that's it!)
    slm = TinySLMWrapper()
    
    # Step 2: Load your facts (from soma Cognitive or anywhere)
    facts = [
        "Python is a programming language",
        "Python was created by Guido van Rossum in 1991",
        "Python is used for web development, data science, and AI",
        "Python has a simple and readable syntax",
        "Python supports multiple programming paradigms",
    ]
    
    print("Loading knowledge...")
    slm.load_knowledge(facts)
    print("✓ Knowledge loaded\n")
    
    # Step 3: Ask questions and get answers
    queries = [
        "What is Python?",
        "Who created Python?",
        "What is Python used for?",
    ]
    
    for query in queries:
        print(f"Q: {query}")
        result = slm.generate(query)
        print(f"A: {result.text}")
        print()
    
    # Show stats
    stats = slm.get_stats()
    print("Model Info:")
    print(f"  Memory: {stats['slm']['memory_estimate_mb']:.2f} MB")
    print(f"  Vocabulary: {stats['slm']['vocab_size']} tokens")
    print(f"  Facts: {stats['constraints']['fact_count']}")
    print()
    
    print("That's it! The SLM runs on CPU with minimal memory.")
    print("Perfect for low-resource environments.")


if __name__ == "__main__":
    main()
