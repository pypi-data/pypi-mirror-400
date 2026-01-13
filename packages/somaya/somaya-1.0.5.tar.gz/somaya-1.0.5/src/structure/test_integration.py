"""
Test Integration - Verify All Files Work Together
==================================================

This script tests if all structure system files are properly integrated.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

print("=" * 70)
print("Testing SOMA Structure System Integration")
print("=" * 70)
print()

errors = []
warnings = []

# Test 1: Core imports
print("1. Testing core imports...")
try:
    from src.structure import (
        get_registry,
        PatternBuilder,
        StructureHierarchy,
        classify_symbol
    )
    print("   ✅ Core imports work")
except Exception as e:
    errors.append(f"Core imports failed: {e}")
    print(f"   ❌ Core imports failed: {e}")

# Test 2: Integration imports
print("\n2. Testing integration imports...")
try:
    from src.structure import (
        SOMAStructureIntegrator,
        integrate_structure_with_SOMA_tokens,
        get_structure_priorities
    )
    print("   ✅ Integration imports work")
except Exception as e:
    errors.append(f"Integration imports failed: {e}")
    print(f"   ❌ Integration imports failed: {e}")

# Test 3: Advanced features imports
print("\n3. Testing advanced features imports...")
try:
    from src.structure import (
        PatternAnalyzer,
        PatternRelationship,
        StructureOptimizer,
        StructureCache,
        StructureIndex
    )
    print("   ✅ Advanced features imports work")
except Exception as e:
    errors.append(f"Advanced features imports failed: {e}")
    print(f"   ❌ Advanced features imports failed: {e}")

# Test 4: Enhanced tokenizer imports
print("\n4. Testing enhanced tokenizer imports...")
try:
    from src.structure import (
        StructureEnhancedTokenizer,
        tokenize_with_structure
    )
    print("   ✅ Enhanced tokenizer imports work")
except Exception as e:
    errors.append(f"Enhanced tokenizer imports failed: {e}")
    print(f"   ❌ Enhanced tokenizer imports failed: {e}")

# Test 5: Functional test - Basic usage
print("\n5. Testing basic functionality...")
try:
    registry = get_registry()
    print(f"   ✅ Registry created: {len(registry.get_all_symbols())} symbols")
    
    builder = PatternBuilder()
    builder.learn_from_text("cat cat dog")
    patterns = builder.get_top_patterns(top_k=2)
    print(f"   ✅ Pattern builder works: found {len(patterns)} patterns")
    
    hierarchy = StructureHierarchy()
    hierarchy.build_from_text("cat cat dog")
    print(f"   ✅ Hierarchy works: {hierarchy.get_statistics()}")
except Exception as e:
    errors.append(f"Basic functionality failed: {e}")
    print(f"   ❌ Basic functionality failed: {e}")

# Test 6: Integration functionality
print("\n6. Testing integration functionality...")
try:
    integrator = SOMAStructureIntegrator()
    tokens = [
        {"token": "cat", "position": 0},
        {"token": "dog", "position": 1}
    ]
    result = integrator.process_SOMA_tokens(tokens)
    print(f"   ✅ Integration works: processed {result['tokens_processed']} tokens")
except Exception as e:
    errors.append(f"Integration functionality failed: {e}")
    print(f"   ❌ Integration functionality failed: {e}")

# Test 7: Advanced features functionality
print("\n7. Testing advanced features functionality...")
try:
    builder = PatternBuilder()
    builder.learn_from_text("cat cat dog python java python")
    analyzer = PatternAnalyzer(builder)
    significant = analyzer.get_most_significant_patterns(top_k=2)
    print(f"   ✅ Advanced features work: found {len(significant)} significant patterns")
except Exception as e:
    errors.append(f"Advanced features functionality failed: {e}")
    print(f"   ❌ Advanced features functionality failed: {e}")

# Test 8: Optimizer functionality
print("\n8. Testing optimizer functionality...")
try:
    optimizer = StructureOptimizer()
    optimizer.optimize_for_text("cat cat dog")
    stats = optimizer.get_optimization_stats()
    print(f"   ✅ Optimizer works: cache size = {stats['cache_size']}")
except Exception as e:
    errors.append(f"Optimizer functionality failed: {e}")
    print(f"   ❌ Optimizer functionality failed: {e}")

# Test 9: Enhanced tokenizer functionality
print("\n9. Testing enhanced tokenizer functionality...")
try:
    tokenizer = StructureEnhancedTokenizer()
    tokens = tokenizer.tokenize_with_structure("cat cat dog")
    print(f"   ✅ Enhanced tokenizer works: tokenized {len(tokens)} tokens")
except Exception as e:
    errors.append(f"Enhanced tokenizer functionality failed: {e}")
    print(f"   ❌ Enhanced tokenizer functionality failed: {e}")

# Summary
print("\n" + "=" * 70)
print("INTEGRATION TEST SUMMARY")
print("=" * 70)

if errors:
    print(f"\n❌ ERRORS FOUND: {len(errors)}")
    for error in errors:
        print(f"   - {error}")
else:
    print("\n✅ ALL TESTS PASSED!")
    print("   All files are properly integrated and working!")

if warnings:
    print(f"\n⚠️  WARNINGS: {len(warnings)}")
    for warning in warnings:
        print(f"   - {warning}")

print("\n" + "=" * 70)
