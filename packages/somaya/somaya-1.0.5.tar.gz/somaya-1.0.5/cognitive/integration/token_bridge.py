"""
TokenBridge - Connect src tokenizer to cognitive graph.

Converts SOMA tokens into graph nodes while preserving:
- Token UIDs (for deterministic identity)
- Token metadata (frontend, backend, stream)
- Token relationships (sequence, co-occurrence)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from ..graph import GraphStore, GraphNode, RelationType


@dataclass
class TokenInfo:
    """Information extracted from a SOMA token."""
    uid: int
    text: str
    stream: str
    index: int
    content_id: Optional[int] = None
    frontend: Optional[int] = None
    backend_huge: Optional[int] = None
    global_id: Optional[int] = None


class TokenBridge:
    """
    Bridge between src's tokenizer and SOMA_cognitive's graph.
    
    Converts tokens to graph nodes and establishes relationships:
    - PRECEDES/FOLLOWS for sequential tokens
    - RELATED_TO for co-occurring tokens
    - PART_OF for subword relationships
    
    Example:
        from src.core.core_tokenizer import TextTokenizationEngine
        
        tokenizer = TextTokenizationEngine()
        bridge = TokenBridge(graph_store)
        
        # Tokenize text
        result = tokenizer.tokenize("Machine learning is amazing")
        
        # Add to graph
        node_ids = bridge.add_tokens(result.tokens)
        
        # Tokens are now in the knowledge graph with relationships
    """
    
    def __init__(self, graph: GraphStore):
        """
        Initialize TokenBridge.
        
        Args:
            graph: GraphStore to add nodes to
        """
        self.graph = graph
        
        # Cache: token_uid -> node_id
        self._uid_to_node: Dict[int, int] = {}
        
        # Statistics
        self._stats = {
            "tokens_processed": 0,
            "nodes_created": 0,
            "edges_created": 0,
        }
    
    def add_tokens(
        self,
        tokens: List[Any],
        create_sequence_edges: bool = True,
        create_cooccurrence_edges: bool = True,
        window_size: int = 5
    ) -> List[int]:
        """
        Add tokens to the graph.
        
        Args:
            tokens: List of TokenRecord objects from src
            create_sequence_edges: Create PRECEDES/FOLLOWS edges
            create_cooccurrence_edges: Create RELATED_TO for nearby tokens
            window_size: Window size for co-occurrence
            
        Returns:
            List of created node IDs
        """
        if not tokens:
            return []
        
        node_ids = []
        
        # Create nodes for each token
        for token in tokens:
            info = self._extract_token_info(token)
            node_id = self._create_or_get_node(info)
            node_ids.append(node_id)
            self._stats["tokens_processed"] += 1
        
        # Create sequence edges
        if create_sequence_edges and len(node_ids) > 1:
            for i in range(len(node_ids) - 1):
                self._create_sequence_edge(node_ids[i], node_ids[i + 1])
        
        # Create co-occurrence edges
        if create_cooccurrence_edges:
            self._create_cooccurrence_edges(node_ids, window_size)
        
        return node_ids
    
    def add_token(self, token: Any) -> int:
        """
        Add a single token to the graph.
        
        Args:
            token: TokenRecord from src
            
        Returns:
            Node ID
        """
        info = self._extract_token_info(token)
        node_id = self._create_or_get_node(info)
        self._stats["tokens_processed"] += 1
        return node_id
    
    def _extract_token_info(self, token: Any) -> TokenInfo:
        """Extract information from a token object."""
        # Handle different token formats
        if hasattr(token, 'uid'):
            return TokenInfo(
                uid=token.uid,
                text=getattr(token, 'text', str(token)),
                stream=getattr(token, 'stream', 'word'),
                index=getattr(token, 'index', 0),
                content_id=getattr(token, 'content_id', None),
                frontend=getattr(token, 'frontend', None),
                backend_huge=getattr(token, 'backend_huge', None),
                global_id=getattr(token, 'global_id', None),
            )
        elif isinstance(token, dict):
            return TokenInfo(
                uid=token.get('uid', hash(token.get('text', ''))),
                text=token.get('text', ''),
                stream=token.get('stream', 'word'),
                index=token.get('index', 0),
                content_id=token.get('content_id'),
                frontend=token.get('frontend'),
                backend_huge=token.get('backend_huge'),
                global_id=token.get('global_id'),
            )
        else:
            # Fallback for string or unknown type
            text = str(token)
            return TokenInfo(
                uid=hash(text) & 0x7FFFFFFF,
                text=text,
                stream='word',
                index=0,
            )
    
    def _create_or_get_node(self, info: TokenInfo) -> int:
        """Create a node for a token or return existing node ID."""
        # Check cache
        if info.uid in self._uid_to_node:
            return self._uid_to_node[info.uid]
        
        # Create node
        node = GraphNode(
            node_id=info.uid,
            text=info.text,
            node_type="token",
            stream=info.stream,
            properties={
                "content_id": info.content_id,
                "frontend": info.frontend,
                "backend_huge": info.backend_huge,
                "global_id": info.global_id,
                "index": info.index,
            }
        )
        
        self.graph.add_node(node)
        self._uid_to_node[info.uid] = node.node_id
        self._stats["nodes_created"] += 1
        
        return node.node_id
    
    def _create_sequence_edge(self, prev_id: int, next_id: int) -> None:
        """Create PRECEDES edge between sequential tokens."""
        if not self.graph.has_edge_between(prev_id, next_id, RelationType.PRECEDES):
            self.graph.add_edge(prev_id, next_id, RelationType.PRECEDES, weight=1.0)
            self._stats["edges_created"] += 1
    
    def _create_cooccurrence_edges(
        self,
        node_ids: List[int],
        window_size: int
    ) -> None:
        """Create RELATED_TO edges for co-occurring tokens."""
        for i, node_id in enumerate(node_ids):
            # Look at tokens within window
            start = max(0, i - window_size)
            end = min(len(node_ids), i + window_size + 1)
            
            for j in range(start, end):
                if i == j:
                    continue
                
                other_id = node_ids[j]
                
                # Calculate weight based on distance
                distance = abs(i - j)
                weight = 1.0 / (distance + 1)
                
                # Only create if significant
                if weight >= 0.2:
                    if not self.graph.has_edge_between(node_id, other_id, RelationType.RELATED_TO):
                        self.graph.add_edge(
                            node_id, other_id,
                            RelationType.RELATED_TO,
                            weight=weight
                        )
                        self._stats["edges_created"] += 1
    
    def get_node_for_token(self, token: Any) -> Optional[int]:
        """Get the graph node ID for a token."""
        info = self._extract_token_info(token)
        return self._uid_to_node.get(info.uid)
    
    def get_stats(self) -> Dict[str, int]:
        """Get bridge statistics."""
        return self._stats.copy()
    
    def clear_cache(self) -> None:
        """Clear the UID to node cache."""
        self._uid_to_node.clear()
    
    def __repr__(self) -> str:
        return f"TokenBridge(nodes={self._stats['nodes_created']}, edges={self._stats['edges_created']})"

