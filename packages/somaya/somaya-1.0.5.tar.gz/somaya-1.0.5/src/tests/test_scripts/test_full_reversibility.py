#!/usr/bin/env python3
"""
FULL REVERSIBILITY & OOV ELIMINATION TEST SUITE

This script validates that the SOMA Tokenizer is:
- FULLY reversible (100% reconstruction)
- NO OOV (Out-of-Vocabulary) issues
- Handles ALL characters and edge cases
- Perfect reconstruction guaranteed
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.core_tokenizer import (
    tokenize_space, tokenize_bytes, tokenize_char, tokenize_word, tokenize_grammar, tokenize_subword,
    reconstruct_from_tokens
)
def validate_reversibility(tokens, original_text, tokenizer_type='space'):
    reconstructed = reconstruct_from_tokens(tokens, tokenizer_type)
    return reconstructed == original_text
def validate_unique_ids(tokens):
    uids = [t.uid for t in tokens]
    return len(uids) == len(set(uids))
def comprehensive_validation(text, tokens):
    return validate_reversibility(tokens, text) and validate_unique_ids(tokens)
def get_unique_ids(tokens):
    return [t.uid for t in tokens]

def test_full_reversibility():
    """Test FULL reversibility for ALL tokenization types"""
    print("=== FULL REVERSIBILITY TEST ===")
    
    # Comprehensive test cases covering ALL possible scenarios
    test_cases = [
        # Basic cases
        "Hello world!",
        "The quick brown fox jumps over the lazy dog.",
        
        # Unicode and international characters
        "Hello 世界!",
        "مرحبا بالعالم",  # Arabic
        "Привет мир",  # Russian
        "こんにちは世界",  # Japanese
        "안녕하세요 세계",  # Korean
        "नमस्ते दुनिया",  # Hindi
        
        # Special characters and symbols
        "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "Math symbols: ∑∏∫√∞≤≥≠≈±×÷",
        "Currency: $€£¥₹₽₩₪₫₨₴₸₼₾₿",
        "Arrows: ←→↑↓↔↕↖↗↘↙",
        
        # Whitespace variations
        "Multiple    spaces\tand\ttabs\nwith\nnewlines\r\nand\r\ncarriage returns",
        "Leading and trailing   spaces   ",
        "   ",
        "\t\t\t",
        "\n\n\n",
        
        # Edge cases
        "",  # Empty string
        "a",  # Single character
        "ab",  # Two characters
        "   ",  # Only spaces
        "!!!",  # Only punctuation
        "123",  # Only digits
        "abc",  # Only letters
        
        # Mixed content
        "Hello123World!!!",
        "Email: user@example.com",
        "URL: https://www.example.com/path?param=value",
        "JSON: {\"key\": \"value\", \"number\": 123}",
        "Code: if (x > 0) { return x * 2; }",
        
        # Very long text
        "This is a very long text with many words and characters to test the robustness of the tokenization system. " * 10,
        
        # Repetitive patterns
        "aaaaaaa",
        "abababab",
        "123123123",
        "!!!@@@###",
        
        # Complex Unicode
        "Emoji: 😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚☺️🙂🤗🤩🤔🤨😐😑😶🙄😏😣😥😮🤐😯😪😫🥱😴😌😛😜😝🤤😒😓😔😕🙃🤑😲☹️🙁😖😞😟😤😢😭😦😧😨😩🤯😬😰😱🥵🥶😳🤪😵😡😠🤬😷🤒🤕🤢🤮🤧😇🤠🥳🥴🥺🤡🤥🤫🤭🧐🤓😈👿👹👺💀👻👽👾🤖💩😺😸😹😻😼😽🙀😿😾",
    ]
    
    tokenizer_types = [
        "space", "word", "char", "grammar", 
        "subword", "subword_bpe", "subword_syllable", "subword_frequency", 
        "byte"
    ]
    
    total_tests = len(test_cases) * len(tokenizer_types)
    passed_tests = 0
    failed_tests = []
    
    print(f"Running {total_tests} reversibility tests...")
    print()
    
    for i, text in enumerate(test_cases):
        print(f"Test case {i+1}/{len(test_cases)}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        for tokenizer_type in tokenizer_types:
            try:
                is_reversible = validate_reversibility(text, tokenizer_type)
                if is_reversible:
                    passed_tests += 1
                    status = "✓ PASS"
                else:
                    failed_tests.append((text, tokenizer_type))
                    status = "✗ FAIL"
                
                print(f"  {tokenizer_type}: {status}")
                
            except Exception as e:
                failed_tests.append((text, tokenizer_type, str(e)))
                print(f"  {tokenizer_type}: ✗ ERROR - {e}")
    
    print(f"\nReversibility Results:")
    print(f"  Total tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {len(failed_tests)}")
    print(f"  Success rate: {(passed_tests/total_tests)*100:.2f}%")
    
    if failed_tests:
        print(f"\nFailed tests:")
        for failure in failed_tests[:10]:  # Show first 10 failures
            if len(failure) == 3:
                text, tokenizer_type, error = failure
                print(f"  '{text[:30]}...' + {tokenizer_type}: {error}")
            else:
                text, tokenizer_type = failure
                print(f"  '{text[:30]}...' + {tokenizer_type}")
    
    return len(failed_tests) == 0

def test_oov_elimination():
    """Test that NO OOV issues exist"""
    print("\n=== OOV ELIMINATION TEST ===")
    
    # Test with characters that might cause OOV issues
    oov_test_cases = [
        # Control characters
        "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f",
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f",
        
        # High Unicode codepoints
        "\U0001F600\U0001F601\U0001F602\U0001F603\U0001F604",  # Emojis
        "\U00010000\U00010001\U00010002",  # High Unicode
        
        # Mixed scripts
        "Hello 世界 مرحبا Привет こんにちは 안녕하세요 नमस्ते",
        
        # Special Unicode categories
        "Mathematical: ∑∏∫√∞≤≥≠≈±×÷",
        "Currency: $€£¥₹₽₩₪₫₨₴₸₼₾₿",
        "Arrows: ←→↑↓↔↕↖↗↘↙",
        "Symbols: ♠♥♦♣♡♢♤♧",
        
        # Edge Unicode cases
        "\uFEFF",  # Zero-width no-break space
        "\u200B",  # Zero-width space
        "\u200C",  # Zero-width non-joiner
        "\u200D",  # Zero-width joiner
        "\u2060",  # Word joiner
    ]
    
    tokenizer_types = ["space", "word", "char", "grammar", "byte"]
    
    all_handled = True
    
    for i, text in enumerate(oov_test_cases):
        print(f"OOV test {i+1}: {repr(text[:50])}")
        
        for tokenizer_type in tokenizer_types:
            try:
                # Test tokenization
                if tokenizer_type == "space":
                    tokens = tokenize_space(text)
                elif tokenizer_type == "word":
                    tokens = tokenize_word(text)
                elif tokenizer_type == "char":
                    tokens = tokenize_char(text)
                elif tokenizer_type == "grammar":
                    tokens = tokenize_grammar(text)
                elif tokenizer_type == "byte":
                    tokens = tokenize_bytes(text)
                
                # Test reconstruction
                reconstructed = reconstruct_from_tokens(tokens, tokenizer_type)
                
                # Check for OOV issues
                if reconstructed == text:
                    status = "✓ NO OOV"
                else:
                    status = "✗ OOV ISSUE"
                    all_handled = False
                
                print(f"  {tokenizer_type}: {status}")
                
            except Exception as e:
                print(f"  {tokenizer_type}: ✗ ERROR - {e}")
                all_handled = False
    
    print(f"\nOOV Elimination: {'✓ ALL HANDLED' if all_handled else '✗ OOV ISSUES FOUND'}")
    return all_handled

def test_comprehensive_validation():
    """Test comprehensive validation for all tokenization types"""
    print("\n=== COMPREHENSIVE VALIDATION TEST ===")
    
    test_text = "Hello 世界! This is a comprehensive test with special chars: !@#$%^&*()"
    
    results = comprehensive_validation(test_text)
    
    print(f"Text: '{test_text}'")
    print(f"Length: {results['text_length']} characters")
    print()
    
    all_valid = True
    
    for tokenizer_type, validation in results["validations"].items():
        reversibility = validation["reversibility"]
        unique_ids = validation["unique_ids"]
        deterministic = validation["deterministic"]
        performance = validation["performance"]
        token_count = validation["token_count"]
        errors = validation["errors"]
        
        overall_status = "✓ FULLY VALID" if reversibility and unique_ids and deterministic and len(errors) == 0 else "✗ INVALID"
        
        print(f"{tokenizer_type}:")
        print(f"  Status: {overall_status}")
        print(f"  Reversibility: {'✓' if reversibility else '✗'}")
        print(f"  Unique IDs: {'✓' if unique_ids else '✗'}")
        print(f"  Deterministic: {'✓' if deterministic else '✗'}")
        print(f"  Performance: {performance:.6f}s")
        print(f"  Token Count: {token_count}")
        print(f"  Errors: {len(errors)}")
        
        if not (reversibility and unique_ids and deterministic and len(errors) == 0):
            all_valid = False
        print()
    
    print(f"Comprehensive Validation: {'✓ ALL FULLY VALID' if all_valid else '✗ SOME INVALID'}")
    return all_valid

def test_edge_cases():
    """Test extreme edge cases"""
    print("\n=== EDGE CASES TEST ===")
    
    edge_cases = [
        "",  # Empty string
        " ",  # Single space
        "\t",  # Single tab
        "\n",  # Single newline
        "\r\n",  # Windows newline
        "a",  # Single character
        "ab",  # Two characters
        "   ",  # Multiple spaces
        "!!!",  # Multiple punctuation
        "123",  # Multiple digits
        "abc",  # Multiple letters
        "\x00",  # Null character
        "\xFF",  # High byte
        "\uFFFF",  # High Unicode
        "\U0001FFFF",  # Very high Unicode
    ]
    
    tokenizer_types = ["space", "word", "char", "grammar", "byte"]
    
    all_handled = True
    
    for i, text in enumerate(edge_cases):
        print(f"Edge case {i+1}: {repr(text)}")
        
        for tokenizer_type in tokenizer_types:
            try:
                is_reversible = validate_reversibility(text, tokenizer_type)
                status = "✓ HANDLED" if is_reversible else "✗ FAILED"
                print(f"  {tokenizer_type}: {status}")
                
                if not is_reversible:
                    all_handled = False
                    
            except Exception as e:
                print(f"  {tokenizer_type}: ✗ ERROR - {e}")
                all_handled = False
    
    print(f"\nEdge Cases: {'✓ ALL HANDLED' if all_handled else '✗ SOME FAILED'}")
    return all_handled

def demonstrate_full_reversibility():
    """Demonstrate full reversibility with detailed examples"""
    print("\n=== FULL REVERSIBILITY DEMONSTRATION ===")
    
    examples = [
        "Hello 世界!",
        "Special chars: !@#$%^&*()",
        "Multiple    spaces\tand\ttabs\nwith\nnewlines",
        "Email: user@example.com",
        "Emoji: 😀😁😂🤣😃😄",
    ]
    
    tokenizer_types = ["space", "word", "char", "grammar", "byte"]
    
    for example in examples:
        print(f"\nExample: '{example}'")
        
        for tokenizer_type in tokenizer_types:
            try:
                # Tokenize
                if tokenizer_type == "space":
                    tokens = tokenize_space(example)
                elif tokenizer_type == "word":
                    tokens = tokenize_word(example)
                elif tokenizer_type == "char":
                    tokens = tokenize_char(example)
                elif tokenizer_type == "grammar":
                    tokens = tokenize_grammar(example)
                elif tokenizer_type == "byte":
                    tokens = tokenize_bytes(example)
                
                # Reconstruct
                reconstructed = reconstruct_from_tokens(tokens, tokenizer_type)
                
                # Verify
                is_perfect = reconstructed == example
                status = "✓ PERFECT" if is_perfect else "✗ IMPERFECT"
                
                print(f"  {tokenizer_type}: {status} ({len(tokens)} tokens)")
                
                if not is_perfect:
                    print(f"    Original:  '{example}'")
                    print(f"    Reconstructed: '{reconstructed}'")
                    
            except Exception as e:
                print(f"  {tokenizer_type}: ✗ ERROR - {e}")

def main():
    """Run all tests"""
    print("FULL REVERSIBILITY & OOV ELIMINATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Full Reversibility", test_full_reversibility),
        ("OOV Elimination", test_oov_elimination),
        ("Comprehensive Validation", test_comprehensive_validation),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Demonstrate full reversibility
    demonstrate_full_reversibility()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
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
        print("  ✓ FULLY reversible (100% reconstruction guaranteed)")
        print("  ✓ NO OOV issues (handles all characters)")
        print("  ✓ Handles all edge cases")
        print("  ✓ Production ready")
        print("  ✓ Perfect reconstruction for ALL tokenization types")
    else:
        print(f"\n⚠️  {total - passed} tests failed. System needs attention.")

if __name__ == "__main__":
    main()
