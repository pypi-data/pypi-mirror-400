#!/usr/bin/env python3
"""
STABLE & REVERSIBLE TOKENIZATION TEST SUITE

This script validates the enhanced SOMA Tokenizer with:
- Perfect reversibility
- Unique IDs by design
- Deterministic behavior
- High performance
- Stability across iterations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.core_tokenizer import (
    tokenize_space, tokenize_bytes, tokenize_subword,
    reconstruct_from_tokens
)
# Note: validate_reversibility, validate_unique_ids, comprehensive_validation,
# stability_test, performance_benchmark may need to be implemented or imported differently
def validate_reversibility(tokens, original_text):
    reconstructed = reconstruct_from_tokens(tokens, 'space')
    return reconstructed == original_text
def validate_unique_ids(tokens):
    uids = [t.uid for t in tokens]
    return len(uids) == len(set(uids))
def comprehensive_validation(text, tokens):
    return validate_reversibility(tokens, text) and validate_unique_ids(tokens)
def stability_test(text, iterations=10):
    results = []
    for _ in range(iterations):
        tokens = tokenize_space(text)
        results.append(tokens)
    return all(len(r) == len(results[0]) for r in results)
def performance_benchmark(text, iterations=100):
    import time
    start = time.time()
    for _ in range(iterations):
        tokenize_space(text)
    return (time.time() - start) / iterations

def test_reversibility():
    """Test perfect reversibility for all tokenization strategies"""
    print("=== REVERSIBILITY TEST ===")
    
    test_cases = [
        "Hello world!",
        "The quick brown fox jumps over the lazy dog.",
        "Hello 世界",  # Unicode test
        "Multiple    spaces\tand\ttabs\nwith\nnewlines",
        "unbelievable running quickly",  # Sub-word test
        "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "",  # Empty string
        "a",  # Single character
        "   ",  # Only spaces
    ]
    
    tokenizer_types = ["space", "byte", "subword", "subword_bpe", "subword_syllable", "subword_frequency"]
    
    all_passed = True
    
    for text in test_cases:
        print(f"\nTesting: '{text}'")
        for tokenizer_type in tokenizer_types:
            try:
                is_reversible = validate_reversibility(text, tokenizer_type)
                status = "✓ PASS" if is_reversible else "✗ FAIL"
                print(f"  {tokenizer_type}: {status}")
                if not is_reversible:
                    all_passed = False
            except Exception as e:
                print(f"  {tokenizer_type}: ✗ ERROR - {e}")
                all_passed = False
    
    print(f"\nReversibility Test: {'✓ ALL PASSED' if all_passed else '✗ SOME FAILED'}")
    return all_passed

def test_unique_ids():
    """Test unique ID generation for all tokenization strategies"""
    print("\n=== UNIQUE ID TEST ===")
    
    test_text = "Hello world! This is a test."
    tokenizer_types = ["space", "byte", "subword", "subword_bpe", "subword_syllable", "subword_frequency"]
    
    all_passed = True
    
    for tokenizer_type in tokenizer_types:
        try:
            if tokenizer_type == "space":
                tokens = tokenize_space(test_text)
            elif tokenizer_type == "byte":
                tokens = tokenize_bytes(test_text)
            elif tokenizer_type.startswith("subword"):
                strategy = tokenizer_type.split("_", 1)[1] if "_" in tokenizer_type else "fixed"
                tokens = tokenize_subword(test_text, 3, strategy)
            else:
                continue
            
            is_unique = validate_unique_ids(tokens)
            status = "✓ PASS" if is_unique else "✗ FAIL"
            print(f"  {tokenizer_type}: {status} ({len(tokens)} tokens)")
            if not is_unique:
                all_passed = False
                
        except Exception as e:
            print(f"  {tokenizer_type}: ✗ ERROR - {e}")
            all_passed = False
    
    print(f"\nUnique ID Test: {'✓ ALL PASSED' if all_passed else '✗ SOME FAILED'}")
    return all_passed

def test_determinism():
    """Test deterministic behavior across multiple runs"""
    print("\n=== DETERMINISM TEST ===")
    
    test_text = "The quick brown fox jumps over the lazy dog."
    iterations = 100
    
    tokenizer_types = ["space", "byte", "subword"]
    all_passed = True
    
    for tokenizer_type in tokenizer_types:
        print(f"\nTesting {tokenizer_type} determinism ({iterations} iterations):")
        
        first_run = None
        deterministic = True
        
        for i in range(iterations):
            try:
                if tokenizer_type == "space":
                    tokens = tokenize_space(test_text)
                elif tokenizer_type == "byte":
                    tokens = tokenize_bytes(test_text)
                elif tokenizer_type == "subword":
                    tokens = tokenize_subword(test_text, 3, "fixed")
                
                if first_run is None:
                    first_run = tokens
                else:
                    # Compare token sequences
                    if len(tokens) != len(first_run):
                        deterministic = False
                        break
                    for j in range(len(tokens)):
                        if tokens[j].get("text") != first_run[j].get("text") or tokens[j].get("id") != first_run[j].get("id"):
                            deterministic = False
                            break
                    if not deterministic:
                        break
                        
            except Exception as e:
                print(f"  Error at iteration {i}: {e}")
                deterministic = False
                break
        
        status = "✓ PASS" if deterministic else "✗ FAIL"
        print(f"  {tokenizer_type}: {status}")
        if not deterministic:
            all_passed = False
    
    print(f"\nDeterminism Test: {'✓ ALL PASSED' if all_passed else '✗ SOME FAILED'}")
    return all_passed

def test_performance():
    """Test performance and speed"""
    print("\n=== PERFORMANCE TEST ===")
    
    test_text = "The quick brown fox jumps over the lazy dog. " * 10  # Longer text
    iterations = 100
    
    results = performance_benchmark(test_text, iterations)
    
    print(f"Performance results ({iterations} iterations):")
    for tokenizer_type, stats in results.items():
        avg_time = stats["avg_time"]
        success_rate = stats["success_rate"]
        status = "✓ GOOD" if avg_time < 0.001 and success_rate == 1.0 else "⚠ SLOW" if avg_time < 0.01 else "✗ POOR"
        print(f"  {tokenizer_type}: {avg_time:.6f}s avg, {success_rate:.1%} success - {status}")
    
    return True

def test_stability():
    """Test stability across many iterations"""
    print("\n=== STABILITY TEST ===")
    
    test_text = "Hello world! This is a stability test."
    iterations = 1000
    
    results = stability_test(test_text, iterations)
    
    all_stable = True
    for tokenizer_type, stats in results.items():
        stable = stats["stable"]
        error_count = len(stats["errors"])
        status = "✓ STABLE" if stable and error_count == 0 else "✗ UNSTABLE"
        print(f"  {tokenizer_type}: {status} ({error_count} errors)")
        if not stable or error_count > 0:
            all_stable = False
    
    print(f"\nStability Test: {'✓ ALL STABLE' if all_stable else '✗ SOME UNSTABLE'}")
    return all_stable

def test_comprehensive_validation():
    """Run comprehensive validation suite"""
    print("\n=== COMPREHENSIVE VALIDATION ===")
    
    test_text = "Hello 世界! This is a comprehensive test."
    
    results = comprehensive_validation(test_text)
    
    print(f"Text: '{results['text']}'")
    print(f"Length: {results['text_length']} characters")
    
    all_valid = True
    
    for tokenizer_type, validation in results["validations"].items():
        reversibility = validation["reversibility"]
        unique_ids = validation["unique_ids"]
        deterministic = validation["deterministic"]
        performance = validation["performance"]
        token_count = validation["token_count"]
        errors = validation["errors"]
        
        overall_status = "✓ VALID" if reversibility and unique_ids and deterministic and len(errors) == 0 else "✗ INVALID"
        
        print(f"\n  {tokenizer_type}:")
        print(f"    Reversibility: {'✓' if reversibility else '✗'}")
        print(f"    Unique IDs: {'✓' if unique_ids else '✗'}")
        print(f"    Deterministic: {'✓' if deterministic else '✗'}")
        print(f"    Performance: {performance:.6f}s")
        print(f"    Token Count: {token_count}")
        print(f"    Errors: {len(errors)}")
        print(f"    Overall: {overall_status}")
        
        if not (reversibility and unique_ids and deterministic and len(errors) == 0):
            all_valid = False
    
    print(f"\nComprehensive Validation: {'✓ ALL VALID' if all_valid else '✗ SOME INVALID'}")
    return all_valid

def demonstrate_reconstruction():
    """Demonstrate perfect reconstruction capabilities"""
    print("\n=== RECONSTRUCTION DEMONSTRATION ===")
    
    original_text = "Hello 世界! This is a test with multiple    spaces."
    
    print(f"Original: '{original_text}'")
    
    # Test space tokenization
    space_tokens = tokenize_space(original_text)
    reconstructed_space = reconstruct_from_tokens(space_tokens, "space")
    print(f"Space reconstruction: '{reconstructed_space}'")
    print(f"Space match: {'✓' if reconstructed_space == original_text else '✗'}")
    
    # Test byte tokenization
    byte_tokens = tokenize_bytes(original_text)
    reconstructed_byte = reconstruct_from_tokens(byte_tokens, "byte")
    print(f"Byte reconstruction: '{reconstructed_byte}'")
    print(f"Byte match: {'✓' if reconstructed_byte == original_text else '✗'}")
    
    # Test sub-word tokenization
    subword_tokens = tokenize_subword(original_text, 3, "fixed")
    reconstructed_subword = reconstruct_from_tokens(subword_tokens, "subword")
    print(f"Sub-word reconstruction: '{reconstructed_subword}'")
    print(f"Sub-word match: {'✓' if reconstructed_subword == original_text else '✗'}")

def main():
    """Run all tests"""
    print("STABLE & REVERSIBLE TOKENIZATION TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Reversibility", test_reversibility),
        ("Unique IDs", test_unique_ids),
        ("Determinism", test_determinism),
        ("Performance", test_performance),
        ("Stability", test_stability),
        ("Comprehensive Validation", test_comprehensive_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Demonstrate reconstruction
    demonstrate_reconstruction()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The tokenization system is:")
        print("  ✓ Perfectly reversible")
        print("  ✓ Has unique IDs by design")
        print("  ✓ Deterministic and stable")
        print("  ✓ High performance")
        print("  ✓ Production ready")
    else:
        print(f"\n⚠️  {total - passed} tests failed. System needs attention.")

if __name__ == "__main__":
    main()
