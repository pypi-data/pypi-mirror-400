"""
Test Real-Time Data Interpretation System
=========================================

Tests the data interpretation system with various inputs.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.interpretation.data_interpreter import DataInterpreter
import os
from pathlib import Path
from dotenv import load_dotenv

# Try to load Weaviate credentials from weaviate_codes/.env
weaviate_env_path = Path(__file__).parent.parent / "weaviate_codes" / ".env"
if weaviate_env_path.exists():
    load_dotenv(weaviate_env_path)
else:
    # Fallback to root .env
    load_dotenv()


def test_basic_interpretation():
    """Test basic interpretation using YOUR Weaviate database."""
    print("\n" + "=" * 80)
    print("TEST 1: Basic Interpretation (YOUR Weaviate Database)")
    print("=" * 80)
    
    # Credentials will be auto-loaded from weaviate_codes/.env
    interpreter = DataInterpreter(
        embedding_strategy="feature_based",  # YOUR SOMA embeddings
        embedding_dim=768,  # Must match your Weaviate collection
        collection_name="SOMA_Token"  # YOUR collection
    )
    
    input_text = "Sales dropped 20% last month."
    print(f"\nInput: {input_text}")
    
    result = interpreter.interpret(input_text)
    
    print(f"\nToken Clues: {result['token_clues']}")
    print(f"Related Concepts: {result['related_concepts']}")
    print(f"\nInterpretation:")
    print(f"  {result['interpretation']}")


def test_multiple_inputs():
    """Test with multiple different inputs using YOUR Weaviate."""
    print("\n" + "=" * 80)
    print("TEST 2: Multiple Inputs (YOUR Weaviate Database)")
    print("=" * 80)
    
    # Credentials will be auto-loaded from weaviate_codes/.env
    interpreter = DataInterpreter(
        embedding_strategy="feature_based",  # YOUR SOMA embeddings
        embedding_dim=768,
        collection_name="SOMA_Token"
    )
    
    test_cases = [
        "Sales dropped 20% last month.",
        "Revenue increased 15% this quarter.",
        "Customer complaints rose significantly.",
        "Marketing campaign showed positive results.",
        "Website traffic decreased by 30%."
    ]
    
    for i, input_text in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {input_text}")
        
        result = interpreter.interpret(input_text)
        
        print(f"Token Clues: {result['token_clues']}")
        print(f"Related Concepts: {result['related_concepts']}")
        print(f"Interpretation: {result['interpretation']}")


def test_custom_knowledge_base():
    """Test with YOUR Weaviate database."""
    print("\n" + "=" * 80)
    print("TEST 3: YOUR Weaviate Database (5.5M objects)")
    print("=" * 80)
    
    # Credentials will be auto-loaded from weaviate_codes/.env
    interpreter = DataInterpreter(
        embedding_strategy="feature_based",  # YOUR SOMA embeddings
        embedding_dim=768,
        collection_name="SOMA_Token"  # YOUR collection with 5.5M objects
    )
    
    # Add custom concepts (this would be done in the class)
    # For now, just test with existing knowledge base
    
    input_text = "Sales dropped 20% last month."
    result = interpreter.interpret(input_text)
    
    print(f"\nInput: {input_text}")
    print(f"Token Clues: {result['token_clues']}")
    print(f"Related Concepts: {result['related_concepts']}")
    print(f"Interpretation: {result['interpretation']}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("DATA INTERPRETATION SYSTEM TEST SUITE")
    print("=" * 80)
    
    try:
        test_basic_interpretation()
        test_multiple_inputs()
        test_custom_knowledge_base()
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
