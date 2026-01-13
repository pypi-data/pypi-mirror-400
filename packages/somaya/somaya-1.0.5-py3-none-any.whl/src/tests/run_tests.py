#!/usr/bin/env python3
"""
TEST RUNNER - SOMA Tokenizer
===============================

This script runs all test suites and generates comprehensive reports.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def run_test_script(script_path):
    """Run a test script and return results"""
    try:
        print(f"[INFO] Running {script_path}...")
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"[OK] {script_path} - PASSED")
            return True, result.stdout
        else:
            print(f"[FAIL] {script_path} - FAILED")
            print(f"Error: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {script_path} - TIMEOUT")
        return False, "Test timed out"
    except Exception as e:
        print(f"[ERROR] {script_path} - CRASHED: {e}")
        return False, str(e)

def main():
    """Main test runner"""
    print("[START] SOMA TOKENIZER - TEST RUNNER")
    print("=" * 50)
    
    # Change to tests directory
    tests_dir = Path(__file__).parent
    os.chdir(tests_dir)
    
    # Find all test scripts
    test_scripts = [
        "test_scripts/test_comprehensive.py",
        "test_scripts/test_stable_tokenization.py", 
        "test_scripts/test_full_reversibility.py",
        "test_scripts/test_compression_efficiency.py"
    ]
    
    results = []
    start_time = time.time()
    
    for script in test_scripts:
        if os.path.exists(script):
            passed, output = run_test_script(script)
            results.append((script, passed, output))
        else:
            print(f"[WARNING] {script} not found, skipping...")
    
    # Generate summary
    end_time = time.time()
    duration = end_time - start_time
    
    passed_tests = sum(1 for _, passed, _ in results if passed)
    total_tests = len(results)
    
    print(f"\n{'='*50}")
    print(f"TEST RUNNER SUMMARY")
    print(f"{'='*50}")
    print(f"Total test suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests*100):.1f}%")
    print(f"Total time: {duration:.2f} seconds")
    
    # Save detailed results
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = results_dir / f"test_report_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write("SOMA TOKENIZER - TEST REPORT\n")
        f.write("=" * 40 + "\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {duration:.2f} seconds\n\n")
        
        for script, passed, output in results:
            f.write(f"{'PASSED' if passed else 'FAILED'}: {script}\n")
            f.write("-" * 40 + "\n")
            f.write(output)
            f.write("\n\n")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    if passed_tests == total_tests:
        print("\n[SUCCESS] ALL TEST SUITES PASSED!")
        return 0
    else:
        print(f"\n[WARNING] {total_tests - passed_tests} test suites failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
