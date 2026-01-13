"""
SOMA Embedding Generation System

This module provides embedding generation from soma tokens,
enabling inference-ready vector representations.
"""

from .embedding_generator import somaEmbeddingGenerator
from .vector_store import somaVectorStore, ChromaVectorStore, FAISSVectorStore

# Try importing WeaviateVectorStore (optional dependency)
try:
    from .weaviate_vector_store import WeaviateVectorStore
    WEAVIATE_AVAILABLE = True
except ImportError:
    WeaviateVectorStore = None
    WEAVIATE_AVAILABLE = False

from .inference_pipeline import somaInferencePipeline

__all__ = [
    "SOMAEmbeddingGenerator",
    "SOMAVectorStore",
    "ChromaVectorStore",
    "FAISSVectorStore",
    "SOMAInferencePipeline",
]

# Conditionally add WeaviateVectorStore to __all__ if available
if WEAVIATE_AVAILABLE:
    __all__.append("WeaviateVectorStore")
