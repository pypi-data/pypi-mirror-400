"""
Test Script for SOMA SLM Model
================================

This script tests if SOMA is working correctly.

Run this to verify:
- SOMA tokenization works
- SOMA constraints work
- Hallucination is prevented
- Facts are grounded
"""

from soma_slm_model import somaSLMModel, create_soma_slm_model


def test_basic_functionality():
    """Test basic model functionality"""
    print("=" * 60)
    print("Test 1: Basic Functionality")
    print("=" * 60)
    
    # Create model
    model = create_soma_slm_model()
    
    # Facts about Python
    facts = [
        "Python is a programming language",
        "Python was created by Guido van Rossum",
        "Python is used for web development",
        "Python supports object-oriented programming"
    ]
    
    # Train
    model.train(facts)
    
    # Generate
    result = model.generate("What is Python?", max_tokens=15)
    print(f"Query: 'What is Python?'")
    print(f"Generated: {result}")
    print()
    
    # Check stats
    stats = model.get_stats()
    print("Model Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()


def test_hallucination_prevention():
    """Test that hallucination is prevented"""
    print("=" * 60)
    print("Test 2: Hallucination Prevention")
    print("=" * 60)
    
    model = create_soma_slm_model()
    
    # Only facts about Python (no Java, no C++)
    facts = [
        "Python is a programming language",
        "Python is interpreted",
        "Python has dynamic typing"
    ]
    
    model.train(facts)
    
    # Try to generate something about Java (should fail)
    print("Query: 'What is Java?'")
    print("Expected: Should NOT mention Java (not in facts)")
    
    result = model.generate("What is Java?", max_tokens=10)
    print(f"Generated: {result}")
    
    # Check if Java appears
    if "java" in result.lower():
        print("❌ FAILED: Model mentioned 'java' (hallucination!)")
    else:
        print("✅ PASSED: Model did NOT mention 'java' (no hallucination)")
    print()


def test_constraint_enforcement():
    """Test that constraints are enforced"""
    print("=" * 60)
    print("Test 3: Constraint Enforcement")
    print("=" * 60)
    
    model = create_soma_slm_model()
    
    # Specific facts
    facts = [
        "Python is a language",
        "Python is interpreted",
        "Python has dynamic typing"
    ]
    
    model.train(facts)
    
    # Explain what will happen
    explanation = model.explain("What is Python?")
    print(explanation)
    print()
    
    # Generate
    result = model.generate("What is Python?", max_tokens=10)
    print(f"Generated: {result}")
    
    # Verify all tokens are from facts
    allowed = model.constraint_engine.get_allowed_tokens()
    generated_tokens = result.lower().split()
    
    unexpected = [t for t in generated_tokens if t not in allowed]
    if unexpected:
        print(f"❌ FAILED: Unexpected tokens: {unexpected}")
    else:
        print("✅ PASSED: All tokens from allowed set")
    print()


def test_SOMA_integration():
    """Test SOMA integration"""
    print("=" * 60)
    print("Test 4: SOMA Integration")
    print("=" * 60)
    
    model = create_soma_slm_model(use_cognitive=True)
    
    facts = [
        "SOMA is a tokenization system",
        "SOMA has custom embeddings",
        "SOMA uses 9-centric numerology",
        "SOMA has deterministic UIDs"
    ]
    
    model.train(facts)
    
    # Test generation
    queries = [
        "What is SOMA?",
        "How does SOMA work?",
        "What makes SOMA unique?"
    ]
    
    for query in queries:
        result = model.generate(query, max_tokens=15)
        print(f"Query: {query}")
        print(f"Generated: {result}")
        print()
    
    # Check if SOMA Cognitive is being used
    stats = model.get_stats()
    if stats.get("SOMA_cognitive"):
        print("✅ SOMA Cognitive is integrated")
    else:
        print("⚠️ SOMA Cognitive not available")
    print()


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SOMA SLM Model - Complete Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_basic_functionality()
        test_hallucination_prevention()
        test_constraint_enforcement()
        test_SOMA_integration()
        
        print("=" * 60)
        print("✅ All Tests Completed!")
        print("=" * 60)
        print()
        print("If all tests passed, SOMA is working correctly!")
        print("The model can only generate tokens from your facts.")
        print("Hallucination is structurally impossible.")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
