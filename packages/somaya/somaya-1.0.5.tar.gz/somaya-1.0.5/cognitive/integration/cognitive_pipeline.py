"""
CognitivePipeline - Full end-to-end cognitive processing.

Combines:
- Tokenization (src)
- Embedding generation (src)
- Knowledge graph (SOMA_cognitive)
- Inference (SOMA_cognitive)
- Hybrid reasoning (SOMA_cognitive)

This is the main integration point between src and SOMA_cognitive.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
import time

from ..graph import GraphStore, GraphNode, RelationType, RelationExtractor
from ..trees import TreeStore, Tree
from ..memory import UnifiedMemory, MemoryObject
from ..reasoning import (
    InferenceEngine, 
    ContradictionDetector,
    HybridReasoner,
    StructuredContext,
    HybridAnswer
)
from .token_bridge import TokenBridge
from .vector_bridge import VectorBridge
from .embedding_bridge import EmbeddingBridge


@dataclass
class ProcessingResult:
    """Result from processing text through the pipeline."""
    text: str
    tokens_created: int
    nodes_created: int
    edges_created: int
    memory_objects: List[str]  # UIDs
    inferences: int
    contradictions: int
    processing_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text[:100] + "..." if len(self.text) > 100 else self.text,
            "tokens_created": self.tokens_created,
            "nodes_created": self.nodes_created,
            "edges_created": self.edges_created,
            "memory_objects": len(self.memory_objects),
            "inferences": self.inferences,
            "contradictions": self.contradictions,
            "processing_time_ms": self.processing_time * 1000,
        }


@dataclass
class PipelineConfig:
    """Configuration for the cognitive pipeline."""
    # Tokenization
    tokenize_text: bool = True
    token_streams: List[str] = field(default_factory=lambda: ["word"])
    
    # Graph
    create_token_nodes: bool = True
    create_sequence_edges: bool = True
    create_cooccurrence_edges: bool = True
    cooccurrence_window: int = 5
    
    # Embeddings
    generate_embeddings: bool = True
    embedding_strategy: str = "hybrid"
    
    # Inference
    run_inference: bool = True
    max_inference_iterations: int = 50
    min_inference_confidence: float = 0.3
    
    # Validation
    check_contradictions: bool = True
    
    # Relation extraction
    extract_relations: bool = True


class CognitivePipeline:
    """
    Full cognitive processing pipeline.
    
    Architecture:
        Text Input
          ↓
        Tokenization (src)
          ↓
        Graph + Embeddings (SOMA_cognitive + src)
          ↓
        Inference Engine (SOMA_cognitive)
          ↓
        Contradiction Check (SOMA_cognitive)
          ↓
        Hybrid Reasoner (SOMA_cognitive)
          ↓
        Answer + Explanation
    
    Example:
        # Basic usage (standalone)
        pipeline = CognitivePipeline()
        
        result = pipeline.process("Machine learning is a type of AI")
        answer = pipeline.query("What is machine learning?")
        
        # With src integration
        from src.core.core_tokenizer import TextTokenizationEngine
        from src.embeddings.embedding_generator import somaEmbeddingGenerator
        
        tokenizer = TextTokenizationEngine()
        generator = SOMAEmbeddingGenerator()
        
        pipeline = CognitivePipeline()
        pipeline.set_tokenizer(tokenizer)
        pipeline.set_embedding_generator(generator)
        
        result = pipeline.process("Transformers use attention mechanisms")
        answer = pipeline.query("How do transformers work?")
        print(answer.explain())
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the cognitive pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        
        # Core components
        self.memory = UnifiedMemory()
        self.graph = self.memory.graph
        self.trees = self.memory.trees
        
        # Bridges
        self.token_bridge = TokenBridge(self.graph)
        self.vector_bridge = VectorBridge(self.memory)
        self.embedding_bridge = EmbeddingBridge(self.memory)
        
        # Reasoning
        self.inference_engine = InferenceEngine(self.graph)
        self.inference_engine.rules.add_builtin_rules()
        
        self.contradiction_detector = ContradictionDetector(self.graph)
        self.reasoner = HybridReasoner(self.memory)
        
        # External components
        self._tokenizer = None
        self._embedding_generator = None
        self._llm_generator = None
        
        # Relation extractor
        self.relation_extractor = RelationExtractor()
        
        # Statistics
        self._stats = {
            "texts_processed": 0,
            "queries_answered": 0,
            "total_tokens": 0,
            "total_inferences": 0,
        }
    
    def set_tokenizer(self, tokenizer: Any) -> None:
        """
        Set the tokenizer from src.
        
        Args:
            tokenizer: TextTokenizationEngine instance
        """
        self._tokenizer = tokenizer
    
    def set_embedding_generator(self, generator: Any) -> None:
        """
        Set the embedding generator from src.
        
        Args:
            generator: SOMAEmbeddingGenerator instance
        """
        self._embedding_generator = generator
        self.embedding_bridge.set_generator(generator, self._tokenizer)
        
        # Also set for vector bridge
        def embed_fn(text: str):
            return self.embedding_bridge.generate(text)
        
        self.vector_bridge.embedding_fn = embed_fn
    
    def set_llm_generator(self, generator_fn: Callable[[str], str]) -> None:
        """
        Set the LLM/GPT generator for natural language output.
        
        Args:
            generator_fn: Function that takes prompt and returns text
        """
        self._llm_generator = generator_fn
        self.reasoner.set_generator(generator_fn)
    
    def process(self, text: str) -> ProcessingResult:
        """
        Process text through the full pipeline.
        
        Steps:
        1. Tokenize (if tokenizer available)
        2. Create graph nodes
        3. Generate embeddings
        4. Extract relations
        5. Run inference
        6. Check contradictions
        
        Args:
            text: Input text
            
        Returns:
            ProcessingResult with statistics
        """
        start_time = time.time()
        
        tokens_created = 0
        nodes_created = 0
        edges_created = 0
        memory_uids = []
        
        # 1. Tokenize if configured
        tokens = []
        if self.config.tokenize_text and self._tokenizer:
            try:
                result = self._tokenizer.tokenize(text)
                tokens = result.tokens if hasattr(result, 'tokens') else result
                tokens_created = len(tokens)
            except Exception:
                pass
        
        # 2. Create graph nodes from tokens
        if self.config.create_token_nodes and tokens:
            node_ids = self.token_bridge.add_tokens(
                tokens,
                create_sequence_edges=self.config.create_sequence_edges,
                create_cooccurrence_edges=self.config.create_cooccurrence_edges,
                window_size=self.config.cooccurrence_window
            )
            nodes_created = len(node_ids)
        
        # 3. Add to memory with embeddings
        if self.config.generate_embeddings:
            obj = self.embedding_bridge.add_with_embedding(
                text, 
                content_type="text",
                auto_link_graph=True
            )
            memory_uids.append(obj.uid)
        else:
            obj = self.memory.add(text, "text", auto_link_graph=True)
            memory_uids.append(obj.uid)
        
        # 4. Extract relations
        if self.config.extract_relations:
            relations = self.relation_extractor.extract(text)
            
            for rel in relations:
                # Create nodes for subject and object if they don't exist
                subj_nodes = self.graph.get_nodes_by_text(rel.subject)
                obj_nodes = self.graph.get_nodes_by_text(rel.obj)
                
                if not subj_nodes:
                    subj_id = hash(rel.subject) & 0x7FFFFFFF
                    self.graph.add_node(GraphNode(subj_id, rel.subject, "entity"))
                    subj_node_id = subj_id
                else:
                    subj_node_id = subj_nodes[0].node_id
                
                if not obj_nodes:
                    obj_id = hash(rel.obj) & 0x7FFFFFFF
                    self.graph.add_node(GraphNode(obj_id, rel.obj, "entity"))
                    obj_node_id = obj_id
                else:
                    obj_node_id = obj_nodes[0].node_id
                
                # Add edge
                if not self.graph.has_edge_between(subj_node_id, obj_node_id, rel.relation):
                    self.graph.add_edge(
                        subj_node_id, obj_node_id,
                        rel.relation,
                        weight=rel.confidence
                    )
                    edges_created += 1
        
        # 5. Run inference
        inferences = 0
        if self.config.run_inference:
            inf_result = self.inference_engine.infer_all(
                max_iterations=self.config.max_inference_iterations,
                min_confidence=self.config.min_inference_confidence
            )
            inferences = len(inf_result.inferred_facts)
        
        # 6. Check contradictions
        contradictions = 0
        if self.config.check_contradictions:
            cont_report = self.contradiction_detector.detect_all()
            contradictions = len(cont_report.contradictions)
        
        # Update stats
        elapsed = time.time() - start_time
        self._stats["texts_processed"] += 1
        self._stats["total_tokens"] += tokens_created
        self._stats["total_inferences"] += inferences
        
        return ProcessingResult(
            text=text,
            tokens_created=tokens_created,
            nodes_created=nodes_created,
            edges_created=edges_created,
            memory_objects=memory_uids,
            inferences=inferences,
            contradictions=contradictions,
            processing_time=elapsed
        )
    
    def process_batch(self, texts: List[str]) -> List[ProcessingResult]:
        """Process multiple texts."""
        return [self.process(text) for text in texts]
    
    def query(self, question: str) -> HybridAnswer:
        """
        Query the knowledge base.
        
        Args:
            question: Natural language question
            
        Returns:
            HybridAnswer with response and explanation
        """
        self._stats["queries_answered"] += 1
        return self.reasoner.answer(question)
    
    def get_context(self, question: str) -> StructuredContext:
        """
        Get structured context for a question without generating answer.
        
        Useful for debugging or custom generation.
        """
        return self.reasoner.build_context(question)
    
    def add_fact(
        self,
        content: str,
        relations: Optional[List[Tuple[str, RelationType, str]]] = None
    ) -> MemoryObject:
        """
        Add a fact with optional explicit relations.
        
        Args:
            content: Fact text
            relations: List of (subject, relation, object) tuples
            
        Returns:
            Created MemoryObject
        """
        obj = self.embedding_bridge.add_with_embedding(
            content,
            content_type="fact",
            auto_link_graph=True
        )
        
        if relations:
            for subj, rel_type, target in relations:
                # Find or create nodes
                subj_nodes = self.graph.get_nodes_by_text(subj)
                tgt_nodes = self.graph.get_nodes_by_text(target)
                
                subj_id = subj_nodes[0].node_id if subj_nodes else hash(subj) & 0x7FFFFFFF
                tgt_id = tgt_nodes[0].node_id if tgt_nodes else hash(target) & 0x7FFFFFFF
                
                if not subj_nodes:
                    self.graph.add_node(GraphNode(subj_id, subj, "entity"))
                if not tgt_nodes:
                    self.graph.add_node(GraphNode(tgt_id, target, "entity"))
                
                self.graph.add_edge(subj_id, tgt_id, rel_type)
        
        return obj
    
    def create_concept_tree(
        self,
        tree_id: str,
        name: str,
        hierarchy: Dict[str, List[str]]
    ) -> Tree:
        """
        Create a concept tree from a hierarchy dict.
        
        Args:
            tree_id: Unique tree ID
            name: Tree name
            hierarchy: Dict mapping parent -> list of children
            
        Returns:
            Created Tree
        """
        tree = self.trees.create_tree(tree_id, name)
        
        # Add nodes from hierarchy
        added = set()
        
        def add_children(parent_id: Optional[str], children: List[str]):
            for child in children:
                if child not in added:
                    child_id = child.lower().replace(" ", "_")
                    tree.add_node(child_id, child, parent_id=parent_id)
                    added.add(child)
                    
                    # Check if this node has children
                    if child in hierarchy:
                        add_children(child_id, hierarchy[child])
        
        # Start from root
        for parent, children in hierarchy.items():
            if parent not in added:
                parent_id = parent.lower().replace(" ", "_")
                tree.add_node(parent_id, parent)
                added.add(parent)
            
            add_children(parent.lower().replace(" ", "_"), children)
        
        return tree
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "pipeline": self._stats,
            "memory": self.memory.get_stats(),
            "inference": self.inference_engine.get_stats(),
            "token_bridge": self.token_bridge.get_stats(),
            "embedding_bridge": self.embedding_bridge.get_stats(),
            "has_tokenizer": self._tokenizer is not None,
            "has_embedding_generator": self._embedding_generator is not None,
            "has_llm_generator": self._llm_generator is not None,
        }
    
    def save(self, directory: str) -> None:
        """Save the pipeline state to directory."""
        self.memory.save(directory)
    
    def load(self, directory: str) -> None:
        """Load the pipeline state from directory."""
        self.memory.load(directory)
    
    def __repr__(self) -> str:
        return (
            f"CognitivePipeline(memory={len(self.memory)}, "
            f"graph={self.graph.node_count}, trees={len(self.trees)})"
        )

