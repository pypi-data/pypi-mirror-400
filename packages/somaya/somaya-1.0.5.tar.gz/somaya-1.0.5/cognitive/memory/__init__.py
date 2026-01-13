"""
SOMA Cognitive - Memory Module
================================

Unified memory that links:
- Vector embeddings (similarity)
- Graph nodes (relationships)
- Tree nodes (hierarchy)

Core classes:
- MemoryObject: Single knowledge unit with all links
- UnifiedMemory: Central hub for all operations
"""

from .memory_object import MemoryObject
from .unified_memory import UnifiedMemory

__all__ = ["MemoryObject", "UnifiedMemory"]

