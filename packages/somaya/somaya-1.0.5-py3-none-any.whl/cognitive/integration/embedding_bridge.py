"""
EmbeddingBridge - Use src's embedding system.

Connects:
- SOMAEmbeddingGenerator for creating embeddings
- Feature-based, semantic, and hybrid embedding strategies
- Embedding to graph node linking
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import numpy as np

from ..graph import GraphStore, GraphNode
from ..memory import UnifiedMemory


@dataclass  
class EmbeddingConfig:
    """Configuration for embedding generation."""
    dimension: int = 768
    strategy: str = "hybrid"  # feature, semantic, hybrid, hash
    normalize: bool = True


class EmbeddingBridge:
    """
    Bridge to src's embedding system.
    
    Provides:
    - Generate embeddings using SOMA's custom algorithms
    - Link embeddings to graph nodes
    - Support for different embedding strategies
    
    Example:
        from src.embeddings.embedding_generator import somaEmbeddingGenerator
        from src.core.core_tokenizer import TextTokenizationEngine
        
        tokenizer = TextTokenizationEngine()
        generator = SOMAEmbeddingGenerator()
        
        bridge = EmbeddingBridge(memory)
        bridge.set_generator(generator, tokenizer)
        
        # Generate embedding for content
        embedding = bridge.generate("Machine learning is powerful")
        
        # Add to memory with embedding
        obj = bridge.add_with_embedding("Machine learning", "concept")
    """
    
    def __init__(
        self,
        memory: UnifiedMemory,
        config: Optional[EmbeddingConfig] = None
    ):
        """
        Initialize EmbeddingBridge.
        
        Args:
            memory: UnifiedMemory instance
            config: Embedding configuration
        """
        self.memory = memory
        self.config = config or EmbeddingConfig()
        
        # External components (to be set)
        self._generator = None
        self._tokenizer = None
        
        # Fallback generator
        self._fallback_fn: Optional[Callable[[str], np.ndarray]] = None
        
        # Embedding cache
        self._embedding_cache: Dict[str, np.ndarray] = {}
        
        # Node to embedding mapping
        self._node_embeddings: Dict[int, str] = {}  # node_id -> embedding_key
        
        # Statistics
        self._stats = {
            "embeddings_generated": 0,
            "cache_hits": 0,
        }
    
    def set_generator(
        self,
        generator: Any,
        tokenizer: Optional[Any] = None
    ) -> None:
        """
        Set the embedding generator from src.
        
        Args:
            generator: SOMAEmbeddingGenerator instance
            tokenizer: TextTokenizationEngine instance (optional)
        """
        self._generator = generator
        self._tokenizer = tokenizer
    
    def set_fallback(self, fn: Callable[[str], np.ndarray]) -> None:
        """Set a fallback embedding function."""
        self._fallback_fn = fn
    
    def generate(
        self,
        text: str,
        use_cache: bool = True
    ) -> Optional[np.ndarray]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector or None
        """
        # Check cache
        cache_key = f"{text}_{self.config.strategy}"
        if use_cache and cache_key in self._embedding_cache:
            self._stats["cache_hits"] += 1
            return self._embedding_cache[cache_key]
        
        embedding = None
        
        # Try src generator
        if self._generator:
            try:
                if self._tokenizer:
                    # Full pipeline
                    result = self._tokenizer.tokenize(text)
                    tokens = result.tokens if hasattr(result, 'tokens') else result
                    embedding = self._generator.generate(
                        tokens,
                        strategy=self.config.strategy
                    )
                else:
                    # Direct generation if supported
                    embedding = self._generator.generate_from_text(text)
            except Exception:
                pass
        
        # Fallback
        if embedding is None and self._fallback_fn:
            try:
                embedding = self._fallback_fn(text)
            except Exception:
                pass
        
        # Last resort: simple hash-based embedding
        if embedding is None:
            embedding = self._generate_simple_embedding(text)
        
        # Normalize if configured
        if embedding is not None and self.config.normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
        
        # Cache
        if embedding is not None:
            self._embedding_cache[cache_key] = embedding
            self._stats["embeddings_generated"] += 1
        
        return embedding
    
    def _generate_simple_embedding(self, text: str) -> np.ndarray:
        """Generate a simple hash-based embedding as fallback."""
        # Use text hash for deterministic generation
        np.random.seed(hash(text) & 0x7FFFFFFF)
        embedding = np.random.randn(self.config.dimension).astype(np.float32)
        return embedding
    
    def add_with_embedding(
        self,
        content: str,
        content_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
        auto_link_graph: bool = True
    ):
        """
        Add content to memory with embedding.
        
        Args:
            content: Text content
            content_type: Type of content
            metadata: Additional properties
            auto_link_graph: Auto-link to graph
            
        Returns:
            Created MemoryObject
        """
        # Create memory object
        obj = self.memory.add(content, content_type, metadata, auto_link_graph)
        
        # Generate embedding
        embedding = self.generate(content)
        
        if embedding is not None:
            # Store embedding reference
            embedding_key = f"emb_{obj.uid}"
            self._embedding_cache[embedding_key] = embedding
            obj.embedding_id = embedding_key
            obj.embedding_vector = embedding.tolist()[:10]  # Store first 10 dims for preview
            
            # Link to graph node if exists
            if obj.graph_node_id:
                self._node_embeddings[obj.graph_node_id] = embedding_key
        
        return obj
    
    def link_to_node(self, node_id: int, embedding: np.ndarray) -> None:
        """Link an embedding to a graph node."""
        key = f"node_{node_id}"
        self._embedding_cache[key] = embedding
        self._node_embeddings[node_id] = key
    
    def get_node_embedding(self, node_id: int) -> Optional[np.ndarray]:
        """Get embedding for a graph node."""
        key = self._node_embeddings.get(node_id)
        if key:
            return self._embedding_cache.get(key)
        return None
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        emb1 = self.generate(text1)
        emb2 = self.generate(text2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def find_similar_nodes(
        self,
        query: str,
        top_k: int = 10
    ) -> List[tuple]:
        """
        Find graph nodes similar to query.
        
        Returns:
            List of (node_id, similarity) tuples
        """
        query_emb = self.generate(query)
        if query_emb is None:
            return []
        
        similarities = []
        
        for node_id, emb_key in self._node_embeddings.items():
            node_emb = self._embedding_cache.get(emb_key)
            if node_emb is not None:
                sim = float(np.dot(query_emb, node_emb) / 
                           (np.linalg.norm(query_emb) * np.linalg.norm(node_emb)))
                similarities.append((node_id, sim))
        
        similarities.sort(key=lambda x: -x[1])
        return similarities[:top_k]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        return {
            "embeddings_generated": self._stats["embeddings_generated"],
            "cache_hits": self._stats["cache_hits"],
            "cached_embeddings": len(self._embedding_cache),
            "node_embeddings": len(self._node_embeddings),
            "has_generator": self._generator is not None,
            "has_tokenizer": self._tokenizer is not None,
        }
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._embedding_cache.clear()
    
    def __repr__(self) -> str:
        has_gen = "with generator" if self._generator else "fallback"
        return f"EmbeddingBridge({has_gen}, cached={len(self._embedding_cache)})"

