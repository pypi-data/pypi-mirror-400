"""
SOMA + TinySLM Integration Example

This shows how to use TinySLM with SOMA Cognitive.
The flow is:
  1. SOMA Cognitive thinks (finds facts, reasons)
  2. TinySLM talks (generates text from facts)

Perfect for low-resource environments - runs on any CPU!
"""

from soma_cognitive import UnifiedMemory, RelationType
from soma_cognitive.slm import TinySLMWrapper


def main():
    """Complete example: SOMA Cognitive + TinySLM."""
    
    print("=" * 60)
    print("SOMA Cognitive + TinySLM Integration")
    print("=" * 60)
    print()
    
    # Step 1: Create SOMA Cognitive memory
    print("1. Setting up SOMA Cognitive...")
    memory = UnifiedMemory()
    
    # Add some knowledge
    facts = [
        "Python is a programming language",
        "Python was created by Guido van Rossum",
        "Python is used for web development",
        "Python supports object-oriented programming",
        "Python has a large standard library",
        "Django is a Python web framework",
        "Flask is a Python web framework",
    ]
    
    for fact in facts:
        memory.add(fact, "fact", auto_link_graph=True)
    
    print(f"   ✓ Added {len(facts)} facts to memory")
    print()
    
    # Step 2: Create TinySLM
    print("2. Creating TinySLM (lightweight, CPU-friendly)...")
    slm = TinySLMWrapper()
    print("   ✓ TinySLM ready")
    print()
    
    # Step 3: Query SOMA Cognitive and get facts
    print("3. Querying SOMA Cognitive...")
    query = "What is Python?"
    
    # Search for relevant facts
    search_result = memory.search(query, limit=5)
    relevant_facts = [obj.content for obj in search_result.objects]
    
    print(f"   Query: {query}")
    print(f"   Found {len(relevant_facts)} relevant facts:")
    for i, fact in enumerate(relevant_facts, 1):
        print(f"     {i}. {fact}")
    print()
    
    # Step 4: Load facts into TinySLM
    print("4. Loading facts into TinySLM...")
    slm.load_knowledge(relevant_facts)
    print("   ✓ Facts loaded and model trained")
    print()
    
    # Step 5: Generate response
    print("5. Generating response with TinySLM...")
    result = slm.generate(query)
    
    print(f"\n{'=' * 60}")
    print("RESPONSE:")
    print(f"{'=' * 60}")
    print(result.text)
    print()
    
    # Show stats
    stats = slm.get_stats()
    print("Model Statistics:")
    print(f"  Memory usage: {stats['slm']['memory_estimate_mb']:.2f} MB")
    print(f"  Vocabulary: {stats['slm']['vocab_size']} tokens")
    print(f"  N-grams: {stats['slm']['ngram_count']}")
    print(f"  Facts used: {stats['constraints']['fact_count']}")
    print()
    
    # Try another query
    print("=" * 60)
    print("Another Example:")
    print("=" * 60)
    print()
    
    query2 = "What frameworks use Python?"
    search_result2 = memory.search(query2, limit=5)
    facts2 = [obj.content for obj in search_result2.objects]
    
    slm.load_knowledge(facts2)
    result2 = slm.generate(query2)
    
    print(f"Q: {query2}")
    print(f"A: {result2.text}")
    print()
    
    print("=" * 60)
    print("That's it! TinySLM runs on any CPU with minimal memory.")
    print("Perfect for low-resource environments.")
    print("=" * 60)


if __name__ == "__main__":
    main()
