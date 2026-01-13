"""
VectorBridge - Connect src vector stores to cognitive memory.

Enables:
- Vector similarity search
- Embedding-based retrieval
- Hybrid search (vector + graph + tree)
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
import numpy as np

from ..memory import UnifiedMemory, MemoryObject


@dataclass
class VectorSearchResult:
    """Result from vector search."""
    memory_object: MemoryObject
    similarity: float
    vector_id: Optional[str] = None


class VectorBridge:
    """
    Bridge between src's vector stores and SOMA_cognitive.
    
    Provides:
    - Add embeddings to memory objects
    - Vector similarity search
    - Hybrid retrieval (vector + symbolic)
    
    Example:
        from src.embeddings.vector_store import FAISSVectorStore
        from src.embeddings.embedding_generator import somaEmbeddingGenerator
        
        # Setup
        generator = SOMAEmbeddingGenerator()
        vector_store = FAISSVectorStore(dimension=768)
        
        memory = UnifiedMemory()
        bridge = VectorBridge(memory, vector_store, generator.generate)
        
        # Add with embedding
        obj = bridge.add_with_embedding("Transformers use attention", "fact")
        
        # Search
        results = bridge.search("how does attention work", top_k=5)
    """
    
    def __init__(
        self,
        memory: UnifiedMemory,
        vector_store: Optional[Any] = None,
        embedding_fn: Optional[Callable[[str], np.ndarray]] = None
    ):
        """
        Initialize VectorBridge.
        
        Args:
            memory: UnifiedMemory instance
            vector_store: Vector store from src (optional)
            embedding_fn: Function to generate embeddings (optional)
        """
        self.memory = memory
        self.vector_store = vector_store
        self.embedding_fn = embedding_fn
        
        # Internal embedding storage if no external store
        self._embeddings: Dict[str, np.ndarray] = {}
        
        # Statistics
        self._stats = {
            "embeddings_created": 0,
            "searches_performed": 0,
        }
    
    def add_with_embedding(
        self,
        content: str,
        content_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
        auto_link_graph: bool = True
    ) -> MemoryObject:
        """
        Add content to memory with embedding.
        
        Args:
            content: Text content
            content_type: Type (fact, concept, etc.)
            metadata: Additional properties
            auto_link_graph: Auto-link to graph
            
        Returns:
            Created MemoryObject with embedding reference
        """
        # Create memory object
        obj = self.memory.add(content, content_type, metadata, auto_link_graph)
        
        # Generate and store embedding
        if self.embedding_fn:
            embedding = self.embedding_fn(content)
            self._store_embedding(obj.uid, embedding)
            obj.embedding_id = obj.uid  # Use UID as embedding ID
            self._stats["embeddings_created"] += 1
        
        return obj
    
    def add_embedding(
        self,
        uid: str,
        embedding: np.ndarray
    ) -> bool:
        """
        Add embedding to existing memory object.
        
        Args:
            uid: Memory object UID
            embedding: Embedding vector
            
        Returns:
            True if successful
        """
        obj = self.memory.get(uid)
        if not obj:
            return False
        
        self._store_embedding(uid, embedding)
        obj.embedding_id = uid
        self._stats["embeddings_created"] += 1
        return True
    
    def _store_embedding(self, uid: str, embedding: np.ndarray) -> None:
        """Store embedding in vector store or internal dict."""
        if self.vector_store:
            # Use external vector store
            try:
                self.vector_store.add(uid, embedding)
            except Exception:
                # Fallback to internal storage
                self._embeddings[uid] = embedding
        else:
            # Internal storage
            self._embeddings[uid] = embedding
    
    def get_embedding(self, uid: str) -> Optional[np.ndarray]:
        """Get embedding for a memory object."""
        if self.vector_store:
            try:
                return self.vector_store.get(uid)
            except Exception:
                pass
        
        return self._embeddings.get(uid)
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        min_similarity: float = 0.0
    ) -> List[VectorSearchResult]:
        """
        Search for similar content using vector similarity.
        
        Args:
            query: Query text
            top_k: Number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of VectorSearchResult
        """
        self._stats["searches_performed"] += 1
        
        # Generate query embedding
        if not self.embedding_fn:
            return []
        
        query_embedding = self.embedding_fn(query)
        
        # Search
        if self.vector_store:
            return self._search_external(query_embedding, top_k, min_similarity)
        else:
            return self._search_internal(query_embedding, top_k, min_similarity)
    
    def _search_external(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        min_similarity: float
    ) -> List[VectorSearchResult]:
        """Search using external vector store."""
        try:
            results = self.vector_store.search(query_embedding, top_k)
            
            output = []
            for uid, similarity in results:
                if similarity >= min_similarity:
                    obj = self.memory.get(uid)
                    if obj:
                        output.append(VectorSearchResult(
                            memory_object=obj,
                            similarity=similarity,
                            vector_id=uid
                        ))
            
            return output
        except Exception:
            return self._search_internal(query_embedding, top_k, min_similarity)
    
    def _search_internal(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        min_similarity: float
    ) -> List[VectorSearchResult]:
        """Search using internal embedding storage."""
        if not self._embeddings:
            return []
        
        # Calculate similarities
        similarities = []
        
        for uid, embedding in self._embeddings.items():
            sim = self._cosine_similarity(query_embedding, embedding)
            if sim >= min_similarity:
                similarities.append((uid, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: -x[1])
        
        # Convert to results
        results = []
        for uid, sim in similarities[:top_k]:
            obj = self.memory.get(uid)
            if obj:
                results.append(VectorSearchResult(
                    memory_object=obj,
                    similarity=sim,
                    vector_id=uid
                ))
        
        return results
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        a = a.flatten()
        b = b.flatten()
        
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot / (norm_a * norm_b))
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        vector_weight: float = 0.6,
        content_weight: float = 0.4
    ) -> List[Tuple[MemoryObject, float]]:
        """
        Hybrid search combining vector and content matching.
        
        Args:
            query: Query text
            top_k: Number of results
            vector_weight: Weight for vector similarity
            content_weight: Weight for content matching
            
        Returns:
            List of (MemoryObject, combined_score) tuples
        """
        scores: Dict[str, float] = {}
        
        # Vector search
        if self.embedding_fn:
            vector_results = self.search(query, top_k * 2)
            for result in vector_results:
                uid = result.memory_object.uid
                scores[uid] = scores.get(uid, 0) + result.similarity * vector_weight
        
        # Content search
        content_results = self.memory.search_by_content(query, top_k * 2)
        for obj in content_results:
            # Simple content score (1.0 for match)
            scores[obj.uid] = scores.get(obj.uid, 0) + 1.0 * content_weight
        
        # Sort and return
        sorted_items = sorted(scores.items(), key=lambda x: -x[1])
        
        results = []
        for uid, score in sorted_items[:top_k]:
            obj = self.memory.get(uid)
            if obj:
                results.append((obj, score))
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get bridge statistics."""
        stats = self._stats.copy()
        stats["internal_embeddings"] = len(self._embeddings)
        return stats
    
    def __repr__(self) -> str:
        has_store = "with store" if self.vector_store else "internal"
        return f"VectorBridge({has_store}, embeddings={len(self._embeddings)})"

