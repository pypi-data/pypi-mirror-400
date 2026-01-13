"""
Test script for Small SOMA SLM
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from soma_cognitive.slm import SmallSOMASLM, SLMConfig


def test_basic_generation():
    """Test basic text generation"""
    print("=" * 60)
    print("Test 1: Basic Generation")
    print("=" * 60)
    
    config = SLMConfig(
        d_model=64,      # Very small for testing
        n_layers=1,      # Just 1 layer
        n_heads=2,       # 2 heads
        vocab_size=1000
    )
    
    slm = SmallSOMASLM(config)
    
    # Simple facts
    facts = [
        "Python is a programming language",
        "Python is used for data science",
        "Python has many libraries"
    ]
    
    slm.train(facts, facts)
    
    # Generate
    result = slm.generate("Python is", max_tokens=10)
    print(f"Prompt: 'Python is'")
    print(f"Generated: {result}")
    print()


def test_constraint_enforcement():
    """Test that constraints are enforced"""
    print("=" * 60)
    print("Test 2: Constraint Enforcement")
    print("=" * 60)
    
    config = SLMConfig(d_model=64, n_layers=1, vocab_size=1000)
    slm = SmallSOMASLM(config)
    
    # Facts about Python only
    facts = [
        "Python is a language",
        "Python is interpreted",
        "Python has dynamic typing"
    ]
    
    slm.train(facts, facts)
    
    # Try to generate - should only use fact tokens
    result = slm.generate("Python", max_tokens=10)
    print(f"Generated: {result}")
    print("All tokens should be from facts!")
    print()


def test_fact_addition():
    """Test adding facts dynamically"""
    print("=" * 60)
    print("Test 3: Dynamic Fact Addition")
    print("=" * 60)
    
    config = SLMConfig(d_model=64, n_layers=1, vocab_size=1000)
    slm = SmallSOMASLM(config)
    
    # Initial facts
    initial_facts = ["Python is a language"]
    slm.train(initial_facts, initial_facts)
    
    # Add more facts
    new_facts = ["Python supports classes", "Python has inheritance"]
    slm.add_facts(new_facts)
    
    # Generate with new facts
    result = slm.generate("Python", max_tokens=10)
    print(f"Generated: {result}")
    print()


def test_different_temperatures():
    """Test generation with different temperatures"""
    print("=" * 60)
    print("Test 4: Temperature Sampling")
    print("=" * 60)
    
    config = SLMConfig(d_model=64, n_layers=1, vocab_size=1000)
    slm = SmallSOMASLM(config)
    
    facts = [
        "Python is a language",
        "Python is interpreted",
        "Python is dynamic"
    ]
    
    slm.train(facts, facts)
    
    # Low temperature (deterministic)
    result1 = slm.generate("Python is", max_tokens=5, temperature=0.1)
    print(f"Temperature 0.1: {result1}")
    
    # High temperature (more random)
    result2 = slm.generate("Python is", max_tokens=5, temperature=1.5)
    print(f"Temperature 1.5: {result2}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SOMA Small SLM - Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_basic_generation()
        test_constraint_enforcement()
        test_fact_addition()
        test_different_temperatures()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
