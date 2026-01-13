"""
Quick Test Script - Run This to Test SOMA SLM
===============================================

This is the simplest way to test if SOMA is working.

Usage:
    python run_model.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from soma_cognitive.slm.soma_slm_model import somaSLMModel, create_soma_slm_model


def main():
    print("=" * 60)
    print("SOMA SLM Model - Quick Test")
    print("=" * 60)
    print()
    
    # Create model
    print("Creating model...")
    model = create_soma_slm_model(
        vocab_size=5000,
        d_model=64,  # Small for quick testing
        n_layers=1,  # Just 1 layer
        use_cognitive=False  # Disable for now to avoid import issues
    )
    print("✅ Model created")
    print()
    
    # Your facts (this is what you test)
    facts = [
        "Python is a programming language",
        "Python was created by Guido van Rossum",
        "Python is used for web development",
        "Python supports object-oriented programming"
    ]
    
    print("Training on facts...")
    print(f"Facts: {facts}")
    print()
    
    # Train
    model.train(facts)
    
    # Test generation
    print("=" * 60)
    print("Testing Generation")
    print("=" * 60)
    print()
    
    queries = [
        "What is Python?",
        "Who created Python?",
        "What can Python do?"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        try:
            result = model.generate(query, max_tokens=15)
            print(f"Generated: {result}")
        except Exception as e:
            print(f"Error: {e}")
        print()
    
    # Show stats
    print("=" * 60)
    print("Model Statistics")
    print("=" * 60)
    stats = model.get_stats()
    for key, value in stats.items():
        if key != "config":
            print(f"{key}: {value}")
    print()
    
    print("=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    print()
    print("If you see generated text above, SOMA is working!")
    print("The model can only generate tokens from your facts.")
    print()


if __name__ == "__main__":
    main()
