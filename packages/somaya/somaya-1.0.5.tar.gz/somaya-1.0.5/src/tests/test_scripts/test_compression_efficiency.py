#!/usr/bin/env python3
"""
COMPRESSION EFFICIENCY TEST SUITE

This script validates the compression capabilities of the SOMA Tokenizer:
- Multiple compression algorithms (RLE, Pattern, Frequency, Adaptive)
- Compression efficiency analysis
- Full reversibility with compression
- Performance impact assessment
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.core_tokenizer import (
    tokenize_space, tokenize_bytes, tokenize_char, tokenize_word, tokenize_grammar, tokenize_subword,
    reconstruct_from_tokens
)
from src.compression.compression_algorithms import compress_tokens, decompress_tokens
def calculate_compression_ratio(original_size, compressed_size):
    return original_size / compressed_size if compressed_size > 0 else 0
def analyze_compression_efficiency(tokens):
    # Placeholder - implement compression analysis
    return {"ratio": 1.0, "saved": 0}

def test_compression_algorithms():
    """Test all compression algorithms"""
    print("=== COMPRESSION ALGORITHMS TEST ===")
    
    # Test cases with different compression potential
    test_cases = [
        ("Repeated characters", "aaaaaaa"),
        ("Repeated words", "hello hello hello world world world"),
        ("Repeated patterns", "abababababab"),
        ("Mixed content", "Hello world! This is a test with multiple spaces."),
        ("Unicode content", "Hello 世界! 世界 世界"),
        ("Special characters", "!!!@@@###$$$"),
        ("Whitespace patterns", "   \t\t\t\n\n\n"),
        ("Complex text", "The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog."),
    ]
    
    compression_methods = ["rle", "pattern", "frequency", "adaptive"]
    tokenizer_types = ["space", "word", "char", "grammar"]
    
    all_passed = True
    
    for test_name, text in test_cases:
        print(f"\nTest: {test_name}")
        print(f"Text: '{text}'")
        
        for tokenizer_type in tokenizer_types:
            print(f"\n  {tokenizer_type}:")
            
            # Get tokens
            if tokenizer_type == "space":
                tokens = tokenize_space(text)
            elif tokenizer_type == "word":
                tokens = tokenize_word(text)
            elif tokenizer_type == "char":
                tokens = tokenize_char(text)
            elif tokenizer_type == "grammar":
                tokens = tokenize_grammar(text)
            
            original_count = len(tokens)
            print(f"    Original tokens: {original_count}")
            
            for method in compression_methods:
                try:
                    # Compress
                    compressed = compress_tokens(tokens, method)
                    compressed_count = len(compressed)
                    
                    # Decompress
                    decompressed = decompress_tokens(compressed)
                    decompressed_count = len(decompressed)
                    
                    # Verify reconstruction
                    reconstructed = reconstruct_from_tokens(decompressed, tokenizer_type)
                    is_perfect = reconstructed == text
                    
                    # Calculate compression ratio
                    ratio = calculate_compression_ratio(tokens, compressed)
                    percentage_saved = (1 - ratio) * 100
                    
                    status = "✓ PASS" if is_perfect and decompressed_count == original_count else "✗ FAIL"
                    print(f"      {method}: {status} ({compressed_count} tokens, {ratio:.3f} ratio, {percentage_saved:.1f}% saved)")
                    
                    if not (is_perfect and decompressed_count == original_count):
                        all_passed = False
                        
                except Exception as e:
                    print(f"      {method}: ✗ ERROR - {e}")
                    all_passed = False
    
    print(f"\nCompression Algorithms Test: {'✓ ALL PASSED' if all_passed else '✗ SOME FAILED'}")
    return all_passed

def test_compression_efficiency():
    """Test compression efficiency analysis"""
    print("\n=== COMPRESSION EFFICIENCY TEST ===")
    
    test_cases = [
        ("Simple repetition", "hello hello hello"),
        ("Pattern repetition", "abababababab"),
        ("Character repetition", "aaaaaaaaaa"),
        ("Mixed content", "Hello world! This is a test."),
        ("Unicode content", "Hello 世界! 世界 世界"),
        ("Complex patterns", "The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog."),
    ]
    
    tokenizer_types = ["space", "word", "char", "grammar"]
    
    all_efficient = True
    
    for test_name, text in test_cases:
        print(f"\nTest: {test_name}")
        print(f"Text: '{text}'")
        
        for tokenizer_type in tokenizer_types:
            print(f"\n  {tokenizer_type}:")
            
            try:
                # Analyze compression efficiency
                analysis = analyze_compression_efficiency(text, tokenizer_type)
                
                if "error" in analysis:
                    print(f"    ✗ ERROR - {analysis['error']}")
                    all_efficient = False
                    continue
                
                original_tokens = analysis["original_tokens"]
                print(f"    Original tokens: {original_tokens}")
                
                for method, stats in analysis["compression_methods"].items():
                    if "error" in stats:
                        print(f"      {method}: ✗ ERROR - {stats['error']}")
                        all_efficient = False
                        continue
                    
                    compressed_tokens = stats["compressed_tokens"]
                    ratio = stats["compression_ratio"]
                    percentage = stats["compression_percentage"]
                    space_saved = stats["space_saved"]
                    is_reversible = stats["is_reversible"]
                    perfect_reconstruction = stats["perfect_reconstruction"]
                    
                    status = "✓ EFFICIENT" if is_reversible and perfect_reconstruction else "✗ INEFFICIENT"
                    print(f"      {method}: {status} ({compressed_tokens} tokens, {ratio:.3f} ratio, {percentage:.1f}% saved, {space_saved} tokens saved)")
                    
                    if not (is_reversible and perfect_reconstruction):
                        all_efficient = False
                        
            except Exception as e:
                print(f"    ✗ ERROR - {e}")
                all_efficient = False
    
    print(f"\nCompression Efficiency Test: {'✓ ALL EFFICIENT' if all_efficient else '✗ SOME INEFFICIENT'}")
    return all_efficient

def test_compression_performance():
    """Test compression performance impact"""
    print("\n=== COMPRESSION PERFORMANCE TEST ===")
    
    import time
    
    # Test with longer text for performance measurement
    test_text = "The quick brown fox jumps over the lazy dog. " * 100  # 4000+ characters
    tokenizer_types = ["space", "word", "char", "grammar"]
    compression_methods = ["rle", "pattern", "frequency", "adaptive"]
    
    print(f"Test text length: {len(test_text)} characters")
    
    all_performant = True
    
    for tokenizer_type in tokenizer_types:
        print(f"\n{tokenizer_type}:")
        
        # Get tokens
        if tokenizer_type == "space":
            tokens = tokenize_space(test_text)
        elif tokenizer_type == "word":
            tokens = tokenize_word(test_text)
        elif tokenizer_type == "char":
            tokens = tokenize_char(test_text)
        elif tokenizer_type == "grammar":
            tokens = tokenize_grammar(test_text)
        
        original_count = len(tokens)
        print(f"  Original tokens: {original_count}")
        
        for method in compression_methods:
            try:
                # Measure compression time
                start_time = time.time()
                compressed = compress_tokens(tokens, method)
                compression_time = time.time() - start_time
                
                # Measure decompression time
                start_time = time.time()
                decompressed = decompress_tokens(compressed)
                decompression_time = time.time() - start_time
                
                # Calculate metrics
                compressed_count = len(compressed)
                ratio = calculate_compression_ratio(tokens, compressed)
                percentage_saved = (1 - ratio) * 100
                
                # Performance assessment
                total_time = compression_time + decompression_time
                is_performant = total_time < 0.1  # Should be fast
                
                status = "✓ FAST" if is_performant else "⚠ SLOW"
                print(f"    {method}: {status} ({compressed_count} tokens, {ratio:.3f} ratio, {percentage_saved:.1f}% saved)")
                print(f"      Compression: {compression_time:.6f}s, Decompression: {decompression_time:.6f}s, Total: {total_time:.6f}s")
                
                if not is_performant:
                    all_performant = False
                    
            except Exception as e:
                print(f"    {method}: ✗ ERROR - {e}")
                all_performant = False
    
    print(f"\nCompression Performance Test: {'✓ ALL FAST' if all_performant else '⚠ SOME SLOW'}")
    return all_performant

def test_compression_edge_cases():
    """Test compression with edge cases"""
    print("\n=== COMPRESSION EDGE CASES TEST ===")
    
    edge_cases = [
        ("Empty string", ""),
        ("Single character", "a"),
        ("Two characters", "ab"),
        ("Single token", "hello"),
        ("No repetition", "abcdefghijklmnopqrstuvwxyz"),
        ("All same", "aaaaaaaaaa"),
        ("Mixed repetition", "aabbccddeeff"),
        ("Whitespace only", "   \t\t\t\n\n\n"),
        ("Special characters", "!@#$%^&*()"),
        ("Unicode", "世界世界世界"),
    ]
    
    tokenizer_types = ["space", "word", "char", "grammar"]
    compression_methods = ["rle", "pattern", "frequency", "adaptive"]
    
    all_handled = True
    
    for test_name, text in edge_cases:
        print(f"\nEdge case: {test_name}")
        print(f"Text: '{text}'")
        
        for tokenizer_type in tokenizer_types:
            print(f"  {tokenizer_type}:")
            
            # Get tokens
            if tokenizer_type == "space":
                tokens = tokenize_space(text)
            elif tokenizer_type == "word":
                tokens = tokenize_word(text)
            elif tokenizer_type == "char":
                tokens = tokenize_char(text)
            elif tokenizer_type == "grammar":
                tokens = tokenize_grammar(text)
            
            original_count = len(tokens)
            
            for method in compression_methods:
                try:
                    # Test compression and decompression
                    compressed = compress_tokens(tokens, method)
                    decompressed = decompress_tokens(compressed)
                    
                    # Verify reconstruction
                    reconstructed = reconstruct_from_tokens(decompressed, tokenizer_type)
                    is_perfect = reconstructed == text
                    
                    # Check token count
                    is_reversible = len(decompressed) == original_count
                    
                    status = "✓ HANDLED" if is_perfect and is_reversible else "✗ FAILED"
                    compressed_count = len(compressed)
                    ratio = calculate_compression_ratio(tokens, compressed)
                    print(f"    {method}: {status} ({compressed_count} tokens, {ratio:.3f} ratio)")
                    
                    if not (is_perfect and is_reversible):
                        all_handled = False
                        
                except Exception as e:
                    print(f"    {method}: ✗ ERROR - {e}")
                    all_handled = False
    
    print(f"\nCompression Edge Cases Test: {'✓ ALL HANDLED' if all_handled else '✗ SOME FAILED'}")
    return all_handled

def demonstrate_compression():
    """Demonstrate compression capabilities"""
    print("\n=== COMPRESSION DEMONSTRATION ===")
    
    examples = [
        ("Repeated words", "hello hello hello world world world"),
        ("Repeated characters", "aaaaaaaaaa"),
        ("Pattern repetition", "abababababab"),
        ("Mixed content", "Hello world! This is a test with multiple spaces."),
        ("Unicode content", "Hello 世界! 世界 世界"),
    ]
    
    tokenizer_types = ["space", "word", "char", "grammar"]
    compression_methods = ["rle", "pattern", "frequency", "adaptive"]
    
    for example_name, text in examples:
        print(f"\nExample: {example_name}")
        print(f"Text: '{text}'")
        
        for tokenizer_type in tokenizer_types:
            print(f"\n  {tokenizer_type}:")
            
            # Get tokens
            if tokenizer_type == "space":
                tokens = tokenize_space(text)
            elif tokenizer_type == "word":
                tokens = tokenize_word(text)
            elif tokenizer_type == "char":
                tokens = tokenize_char(text)
            elif tokenizer_type == "grammar":
                tokens = tokenize_grammar(text)
            
            original_count = len(tokens)
            print(f"    Original: {original_count} tokens")
            
            for method in compression_methods:
                try:
                    # Compress
                    compressed = compress_tokens(tokens, method)
                    compressed_count = len(compressed)
                    
                    # Calculate metrics
                    ratio = calculate_compression_ratio(tokens, compressed)
                    percentage_saved = (1 - ratio) * 100
                    space_saved = original_count - compressed_count
                    
                    print(f"      {method}: {compressed_count} tokens ({ratio:.3f} ratio, {percentage_saved:.1f}% saved, {space_saved} tokens saved)")
                    
                    # Show some compressed tokens
                    if compressed_count > 0:
                        sample_tokens = compressed[:3]  # Show first 3
                        for token in sample_tokens:
                            if token.get("compressed", False):
                                print(f"        Compressed: '{token['text']}' (count: {token.get('count', 1)})")
                            else:
                                print(f"        Regular: '{token['text']}'")
                        
                except Exception as e:
                    print(f"      {method}: ✗ ERROR - {e}")

def main():
    """Run all compression tests"""
    print("COMPRESSION EFFICIENCY TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Compression Algorithms", test_compression_algorithms),
        ("Compression Efficiency", test_compression_efficiency),
        ("Compression Performance", test_compression_performance),
        ("Compression Edge Cases", test_compression_edge_cases),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Demonstrate compression
    demonstrate_compression()
    
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
        print("\n🎉 ALL TESTS PASSED! The compression system provides:")
        print("  ✓ Multiple compression algorithms (RLE, Pattern, Frequency, Adaptive)")
        print("  ✓ Efficient compression with space savings")
        print("  ✓ Full reversibility with compression")
        print("  ✓ Fast compression and decompression")
        print("  ✓ Handles all edge cases")
        print("  ✓ Production ready")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Compression system needs attention.")

if __name__ == "__main__":
    main()
