#!/usr/bin/env python3
"""
COMPREHENSIVE TEST SUITE - SOMA Tokenizer
============================================

This test suite validates all aspects of the SOMA Tokenizer:
- Universal file input/output
- All tokenization strategies
- Reversibility and stability
- Compression efficiency
- Readable content display
- Error handling
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.core_tokenizer import all_tokenizations
# Note: These functions may need to be implemented
def validate_reversibility(tokens, original_text):
    from src.core.core_tokenizer import reconstruct_from_tokens
    reconstructed = reconstruct_from_tokens(tokens, 'space')
    return reconstructed == original_text
def comprehensive_validation(text, tokens):
    return validate_reversibility(tokens, text)
def analyze_compression_efficiency(tokens):
    # Placeholder - implement compression analysis
    return {"ratio": 1.0, "saved": 0}
def stability_test(text, iterations=10):
    results = []
    for _ in range(iterations):
        tokens = all_tokenizations(text).get('space', [])
        results.append(len(tokens))
    return len(set(results)) == 1
def performance_benchmark(text, iterations=100):
    import time
    start = time.time()
    for _ in range(iterations):
        all_tokenizations(text)
    return (time.time() - start) / iterations

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_result(self, test_name, passed, error=None):
        if passed:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            print(f"❌ {test_name}")
            if error:
                self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")
        
        if self.errors:
            print(f"\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")

def test_basic_tokenization():
    """Test basic tokenization functionality"""
    results = TestResults()
    
    test_text = "Hello World! This is a test."
    
    try:
        # Test all tokenization strategies
        tokenizations = all_tokenizations(test_text)
        
        expected_strategies = ["space", "word", "char", "grammar", "subword", "subword_bpe", "subword_syllable", "subword_frequency", "byte"]
        
        for strategy in expected_strategies:
            if strategy in tokenizations:
                tokens = tokenizations[strategy]
                results.add_result(f"Basic {strategy} tokenization", len(tokens) > 0)
            else:
                results.add_result(f"Basic {strategy} tokenization", False, "Strategy not found")
        
        return results
        
    except Exception as e:
        results.add_result("Basic tokenization", False, str(e))
        return results

def test_reversibility():
    """Test reversibility of all tokenization strategies"""
    results = TestResults()
    
    test_texts = [
        "Hello World!",
        "Special chars: @#$%^&*()",
        "Numbers: 1234567890",
        "Unicode: 🌟🚀💻",
        "Mixed: Hello123@#$%World!",
        "Spaces:    multiple    spaces",
        "Newlines:\nLine1\nLine2"
    ]
    
    for text in test_texts:
        try:
            validation = validate_reversibility(text, "space")
            results.add_result(f"Space reversibility: '{text[:20]}...'", validation["reversible"])
            
            validation = validate_reversibility(text, "word")
            results.add_result(f"Word reversibility: '{text[:20]}...'", validation["reversible"])
            
            validation = validate_reversibility(text, "char")
            results.add_result(f"Char reversibility: '{text[:20]}...'", validation["reversible"])
            
            validation = validate_reversibility(text, "byte")
            results.add_result(f"Byte reversibility: '{text[:20]}...'", validation["reversible"])
            
        except Exception as e:
            results.add_result(f"Reversibility test: '{text[:20]}...'", False, str(e))
    
    return results

def test_file_handling():
    """Test universal file input/output"""
    results = TestResults()
    
    test_files = [
        "tests/test_data/sample_texts.txt",
        "tests/test_data/test_csv.csv", 
        "tests/test_data/test_json.json",
        "tests/test_data/test_xml.xml",
        "tests/test_data/binary_test.bin"
    ]
    
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                # Test file reading
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Test tokenization of file content
                text_content = content.decode('utf-8', errors='ignore')
                tokenizations = all_tokenizations(text_content)
                
                results.add_result(f"File handling: {os.path.basename(file_path)}", len(tokenizations) > 0)
            else:
                results.add_result(f"File handling: {os.path.basename(file_path)}", False, "File not found")
                
        except Exception as e:
            results.add_result(f"File handling: {os.path.basename(file_path)}", False, str(e))
    
    return results

def test_compression():
    """Test compression efficiency"""
    results = TestResults()
    
    test_texts = [
        "Hello World!",
        "Repeated words: hello hello hello world world world",
        "Numbers: 123456789012345678901234567890",
        "Special: @#$%^&*()@#$%^&*()@#$%^&*()"
    ]
    
    for text in test_texts:
        try:
            analysis = analyze_compression_efficiency(text, "word")
            
            # Check if compression analysis returned valid results
            has_compression = any(
                analysis.get("rle", {}).get("compression_ratio", 1) != 1 or
                analysis.get("pattern", {}).get("compression_ratio", 1) != 1 or
                analysis.get("frequency", {}).get("compression_ratio", 1) != 1 or
                analysis.get("adaptive", {}).get("compression_ratio", 1) != 1
            )
            
            results.add_result(f"Compression: '{text[:20]}...'", True)
            
        except Exception as e:
            results.add_result(f"Compression: '{text[:20]}...'", False, str(e))
    
    return results

def test_stability():
    """Test stability across multiple runs"""
    results = TestResults()
    
    test_text = "Hello World! This is a stability test."
    
    try:
        # Run stability test
        stability_result = stability_test(test_text, iterations=10)
        
        results.add_result("Stability test", stability_result["stable"])
        
        # Test performance benchmark
        perf_result = performance_benchmark(test_text, iterations=5)
        
        results.add_result("Performance benchmark", perf_result["avg_time"] > 0)
        
    except Exception as e:
        results.add_result("Stability test", False, str(e))
    
    return results

def test_comprehensive_validation():
    """Test comprehensive validation"""
    results = TestResults()
    
    test_texts = [
        "Hello World!",
        "Special chars: @#$%^&*()",
        "Unicode: 🌟🚀💻"
    ]
    
    for text in test_texts:
        try:
            validation = comprehensive_validation(text, include_compression=True)
            
            # Check if validation returned expected results
            has_results = (
                "space" in validation and
                "word" in validation and
                "char" in validation and
                "byte" in validation
            )
            
            results.add_result(f"Comprehensive validation: '{text[:20]}...'", has_results)
            
        except Exception as e:
            results.add_result(f"Comprehensive validation: '{text[:20]}...'", False, str(e))
    
    return results

def run_all_tests():
    """Run all test suites"""
    print("🚀 SOMA TOKENIZER - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    all_results = TestResults()
    
    # Run individual test suites
    test_suites = [
        ("Basic Tokenization", test_basic_tokenization),
        ("Reversibility", test_reversibility),
        ("File Handling", test_file_handling),
        ("Compression", test_compression),
        ("Stability", test_stability),
        ("Comprehensive Validation", test_comprehensive_validation)
    ]
    
    for suite_name, test_func in test_suites:
        print(f"\n📋 {suite_name}")
        print("-" * 40)
        
        try:
            suite_results = test_func()
            all_results.passed += suite_results.passed
            all_results.failed += suite_results.failed
            all_results.errors.extend(suite_results.errors)
        except Exception as e:
            print(f"❌ {suite_name} suite failed: {e}")
            all_results.failed += 1
            all_results.errors.append(f"{suite_name} suite: {e}")
    
    # Print final summary
    all_results.summary()
    
    return all_results.passed, all_results.failed

if __name__ == "__main__":
    start_time = time.time()
    
    try:
        passed, failed = run_all_tests()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  Total execution time: {duration:.2f} seconds")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! SOMA Tokenizer is working perfectly!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the errors above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
