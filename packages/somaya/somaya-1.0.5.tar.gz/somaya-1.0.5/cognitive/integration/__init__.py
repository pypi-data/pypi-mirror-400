"""
SOMA Cognitive - Integration Module
=====================================

Bridges SOMA_cognitive with src:
- TokenBridge: Convert tokens to graph nodes
- VectorBridge: Connect to vector stores
- EmbeddingBridge: Use src embeddings
- CognitivePipeline: Full end-to-end pipeline
"""

from .token_bridge import TokenBridge
from .vector_bridge import VectorBridge
from .embedding_bridge import EmbeddingBridge
from .cognitive_pipeline import CognitivePipeline

__all__ = [
    "TokenBridge",
    "VectorBridge",
    "EmbeddingBridge",
    "CognitivePipeline",
]

