"""
Backend Test Script for Vocabulary Adapter

This script tests the vocabulary adapter integration in the backend.
You can run this directly or use it as a reference for API calls.

Usage:
    python tests/test_vocabulary_adapter_backend.py
"""

import sys
import os
import json
import requests
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_ENDPOINT = f"{BACKEND_URL}/test/vocabulary-adapter"
QUICK_TEST_ENDPOINT = f"{BACKEND_URL}/test/vocabulary-adapter/quick"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_server_health():
    """Test if the server is running"""
    print_section("1. Checking Server Health")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Server is running!")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"[ERROR] Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {BACKEND_URL}")
        print(f"   Make sure the server is running:")
        print(f"   python src/servers/main_server.py")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_quick_endpoint():
    """Test the quick test endpoint"""
    print_section("2. Testing Quick Endpoint (GET)")
    print("   Note: First request may take 10-30 seconds to download model files...")
    try:
        response = requests.get(QUICK_TEST_ENDPOINT, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("[OK] Quick test passed!")
                print(f"   SOMA tokens: {len(data['SOMA']['tokens'])}")
                print(f"   Model tokens: {len(data['model']['input_ids'])}")
                print(f"   Model: {data['input']['model_name']}")
                return True
            else:
                print(f"[ERROR] Test failed: {data.get('error', 'Unknown error')}")
                return False
        elif response.status_code == 503:
            print("[WARNING]  Vocabulary adapter not available")
            print("   Install transformers: pip install transformers")
            return False
        else:
            print(f"[ERROR] Server returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_custom_request():
    """Test with custom request"""
    print_section("3. Testing Custom Request (POST)")
    
    test_cases = [
        {
            "name": "Simple text with BERT",
            "data": {
                "text": "Hello world! SOMA is amazing.",
                "model_name": "bert-base-uncased",
                "tokenizer_type": "word"
            }
        },
        {
            "name": "Text with GPT-2",
            "data": {
                "text": "The quick brown fox jumps over the lazy dog.",
                "model_name": "gpt2",
                "tokenizer_type": "word"
            }
        },
        {
            "name": "Character tokenization",
            "data": {
                "text": "Hello",
                "model_name": "bert-base-uncased",
                "tokenizer_type": "char"
            }
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        if i == 1:
            print("      Note: First request may take 10-30 seconds to download model files...")
        try:
            response = requests.post(
                TEST_ENDPOINT,
                json=test_case["data"],
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    SOMA_count = len(data['SOMA']['tokens'])
                    model_count = len(data['model']['input_ids'])
                    ratio = data['comparison']['ratio']
                    
                    print(f"      [OK] Success!")
                    print(f"         SOMA: {SOMA_count} tokens")
                    print(f"         Model:  {model_count} tokens")
                    print(f"         Ratio:  {ratio:.2f}x")
                    results.append(True)
                else:
                    print(f"      [ERROR] Failed: {data.get('error', 'Unknown error')}")
                    results.append(False)
            else:
                print(f"      [ERROR] HTTP {response.status_code}: {response.text[:100]}")
                results.append(False)
        except Exception as e:
            print(f"      [ERROR] Error: {e}")
            results.append(False)
    
    return all(results)


def test_comparison():
    """Test comparing different models"""
    print_section("4. Comparing Different Models")
    
    text = "SOMA provides superior tokenization."
    models = ["bert-base-uncased", "distilbert-base-uncased"]
    
    # Try GPT-2 if available (may not be available in all environments)
    try:
        models.append("gpt2")
    except Exception:
        pass
    
    print(f"\n   Text: {text}\n")
    
    for model in models:
        print(f"   Testing with {model}:")
        try:
            response = requests.post(
                TEST_ENDPOINT,
                json={
                    "text": text,
                    "model_name": model,
                    "tokenizer_type": "word"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    SOMA_tokens = data['SOMA']['tokens']
                    model_tokens = data['model']['tokens']
                    vocab_size = data['model']['vocab_size']
                    
                    print(f"      [OK] Vocab size: {vocab_size:,}")
                    print(f"         SOMA tokens: {SOMA_tokens}")
                    print(f"         Model tokens:  {model_tokens[:5]}..." if len(model_tokens) > 5 else f"         Model tokens:  {model_tokens}")
                else:
                    print(f"      [ERROR] {data.get('error', 'Unknown error')}")
            else:
                print(f"      [ERROR] HTTP {response.status_code}")
        except Exception as e:
            print(f"      [ERROR] Error: {e}")
        print()


def print_usage_instructions():
    """Print instructions for using the API"""
    print_section("API Usage Instructions")
    print("""
You can test the vocabulary adapter using curl or any HTTP client:

1. Quick Test (GET):
   curl http://localhost:8000/test/vocabulary-adapter/quick

2. Custom Test (POST):
   curl -X POST http://localhost:8000/test/vocabulary-adapter \\
        -H "Content-Type: application/json" \\
        -d '{
          "text": "Hello world!",
          "model_name": "bert-base-uncased",
          "tokenizer_type": "word"
        }'

3. Python requests:
   import requests
   response = requests.post(
       "http://localhost:8000/test/vocabulary-adapter",
       json={
           "text": "Hello world!",
           "model_name": "bert-base-uncased",
           "tokenizer_type": "word"
       }
   )
   print(response.json())

4. Interactive API Docs:
   Open http://localhost:8000/docs in your browser
   Navigate to /test/vocabulary-adapter endpoint
   Click "Try it out" and test interactively
""")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  Vocabulary Adapter Backend Test Suite")
    print("=" * 70)
    
    # Check if server is running
    if not test_server_health():
        print("\n[WARNING]  Please start the server first:")
        print("   python src/servers/main_server.py")
        print("\nThen run this test script again.")
        return
    
    # Run tests
    print()
    quick_test_passed = test_quick_endpoint()
    custom_test_passed = test_custom_request()
    test_comparison()
    
    # Print summary
    print_section("Test Summary")
    if quick_test_passed and custom_test_passed:
        print("[OK] All tests passed!")
    else:
        print("[WARNING]  Some tests failed. Check the output above for details.")
    
    # Print usage instructions
    print_usage_instructions()
    
    print("\n" + "=" * 70)
    print("  Test Suite Complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
