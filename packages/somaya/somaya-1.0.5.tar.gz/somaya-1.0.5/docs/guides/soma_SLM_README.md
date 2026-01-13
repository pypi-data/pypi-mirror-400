# SOMA SLM - Simple Usage Guide

## Quick Start

You have a working SLM from SOMA. Here's how to use it:

```python
from soma_slm import SOMASLM

# Create SLM
slm = SOMASLM()

# Load facts
slm.load_facts([
    "Python is a programming language",
    "Python was created by Guido van Rossum",
    "Python is used for web development"
])

# Generate response
result = slm.generate("What is Python?")
print(result)
```

## That's It!

The SLM is ready to use. It:
- ✅ Runs on CPU (no GPU needed)
- ✅ Uses minimal memory
- ✅ Only generates text from your facts (no hallucination)
- ✅ Works with SOMA Cognitive

## Available SLMs

You have **two SLM options**:

### 1. Simple SLM (`soma_slm.py`)
```python
from soma_slm import SOMASLM
slm = SOMASLM()
slm.load_facts(["Python is a language"])
print(slm.generate("What is Python?"))
```

### 2. TinySLM (Ultra-lightweight)
```python
from soma_cognitive.slm import TinySLMWrapper
slm = TinySLMWrapper()
slm.load_knowledge(["Python is a language"])
result = slm.generate("What is Python?")
print(result.text)
```

### 3. Full SOMA SLM
```python
from soma_cognitive.slm import SOMASLM
slm = SOMASLM()
slm.load_knowledge(["Python is a language"])
result = slm.generate("What is Python?")
print(result.text)
```

## Integration with SOMA Cognitive

```python
from soma_cognitive import UnifiedMemory
from soma_slm import SOMASLM

# Setup SOMA Cognitive
memory = UnifiedMemory()
memory.add("Python is a programming language", "fact")

# Query and get facts
query = "What is Python?"
search_result = memory.search(query, limit=5)
facts = [obj.content for obj in search_result.objects]

# Use SLM
slm = SOMASLM()
slm.load_facts(facts)
result = slm.generate(query)
print(result)
```

## Examples

See:
- `examples/simple_tiny_slm.py` - Basic TinySLM usage
- `examples/soma_with_tiny_slm.py` - Full integration
- `test_soma_slm.py` - Quick test

## Notes

- The SLM uses constraint-based generation (only facts you provide)
- Output quality depends on your facts
- Works best with clear, structured facts
- No GPU required - runs on any CPU
- Minimal memory footprint

## API

### SOMASLM

```python
slm = SOMASLM()
slm.load_facts(facts)           # Load facts
result = slm.generate(query)    # Generate response
slm.add_fact(fact)              # Add one fact
slm.clear()                     # Clear all facts
stats = slm.get_stats()        # Get statistics
```

That's all you need!
