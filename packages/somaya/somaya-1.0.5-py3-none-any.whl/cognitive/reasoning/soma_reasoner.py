"""
SOMA Reasoner - Pure SOMA symbolic reasoning.

NO GPT. NO TRANSFORMERS. NO NEURAL NETWORKS. NO EXTERNAL AI.

This is 100% SOMA-native:
- Symbolic inference
- Pattern-based reasoning
- Template verbalization
- Knowledge graph traversal

SOMA does the THINKING AND the SPEAKING.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import time

from ..graph import GraphStore, GraphNode, RelationType
from ..trees import TreeStore
from ..memory import UnifiedMemory, MemoryObject
from .inference_engine import InferenceEngine
from .path_finder import PathFinder
from .query_engine import QueryEngine
from .contradiction_detector import ContradictionDetector
from .SOMA_verbalizer import somaVerbalizer, VerbalizationResult


@dataclass
class SOMAAnswer:
    """
    Answer produced by pure SOMA reasoning.
    
    NO neural generation. Pure symbolic + template.
    """
    text: str
    confidence: float
    
    # Reasoning trace
    facts_used: List[str]
    inferences_made: List[str]
    rules_applied: List[str]
    reasoning_path: List[str]
    
    # Metadata
    query: str
    processing_time: float
    contradictions_found: int
    
    def explain(self) -> str:
        """Generate explanation of reasoning."""
        lines = [
            f"Query: {self.query}",
            f"Answer: {self.text}",
            f"Confidence: {self.confidence:.0%}",
            "",
            "Reasoning Process:",
        ]
        
        if self.facts_used:
            lines.append(f"  Facts used ({len(self.facts_used)}):")
            for fact in self.facts_used[:5]:
                lines.append(f"    - {fact[:60]}...")
        
        if self.inferences_made:
            lines.append(f"  Inferences ({len(self.inferences_made)}):")
            for inf in self.inferences_made[:5]:
                lines.append(f"    - {inf}")
        
        if self.rules_applied:
            lines.append(f"  Rules applied: {', '.join(self.rules_applied)}")
        
        if self.reasoning_path:
            lines.append(f"  Path: {' → '.join(self.reasoning_path)}")
        
        if self.contradictions_found > 0:
            lines.append(f"  ⚠️ Contradictions detected: {self.contradictions_found}")
        
        lines.append(f"\nProcessing time: {self.processing_time*1000:.1f}ms")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "facts_used": self.facts_used,
            "inferences_made": self.inferences_made,
            "rules_applied": self.rules_applied,
            "reasoning_path": self.reasoning_path,
            "query": self.query,
            "processing_time_ms": self.processing_time * 1000,
            "contradictions": self.contradictions_found,
        }


@dataclass
class StructuredKnowledge:
    """
    Structured knowledge extracted for a query.
    
    This replaces "StructuredContext" - it's SOMA-native terminology.
    """
    query: str
    
    # Direct knowledge
    relevant_facts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Derived knowledge
    inferences: List[Dict[str, Any]] = field(default_factory=list)
    
    # Graph paths
    reasoning_paths: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tree context
    hierarchy: Optional[Dict[str, Any]] = None
    
    # Issues
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Overall confidence
    confidence: float = 1.0


class SOMAReasoner:
    """
    Pure SOMA reasoning system.
    
    NO external AI. NO neural networks. NO GPT.
    
    Uses:
    - Symbolic inference (rule chaining)
    - Knowledge graph traversal
    - Template-based verbalization
    - Pattern matching
    
    This is what makes SOMA UNIQUE.
    
    Example:
        from soma_cognitive import somaReasoner, UnifiedMemory
        
        memory = UnifiedMemory()
        # ... add knowledge ...
        
        reasoner = SOMAReasoner(memory)
        
        answer = reasoner.ask("What is machine learning?")
        print(answer.text)
        print(answer.explain())
    """
    
    def __init__(self, memory: UnifiedMemory):
        """
        Initialize SOMA Reasoner.
        
        Args:
            memory: UnifiedMemory with knowledge
        """
        self.memory = memory
        
        # Core reasoning components (all SOMA-native)
        self.inference_engine = InferenceEngine(memory.graph)
        self.inference_engine.rules.add_builtin_rules()
        
        self.path_finder = PathFinder(memory.graph)
        self.query_engine = QueryEngine(memory)
        self.contradiction_detector = ContradictionDetector(memory.graph)
        
        # SOMA-native verbalizer (NO GPT)
        self.verbalizer = SOMAVerbalizer(memory)
        
        # Configuration
        self.config = {
            "max_facts": 10,
            "max_inferences": 5,
            "max_paths": 3,
            "run_inference": True,
            "check_contradictions": True,
            "min_confidence": 0.3,
        }
    
    def ask(self, question: str) -> SOMAAnswer:
        """
        Ask a question and get a reasoned answer.
        
        Process:
        1. Retrieve relevant knowledge
        2. Run symbolic inference
        3. Find reasoning paths
        4. Check for contradictions
        5. Verbalize answer (template-based, NOT neural)
        
        Args:
            question: Natural language question
            
        Returns:
            SOMAAnswer with reasoning trace
        """
        start_time = time.time()
        
        # 1. Build structured knowledge
        knowledge = self._build_knowledge(question)
        
        # 2. Verbalize using SOMA templates (NOT GPT)
        verbalization = self.verbalizer.verbalize(knowledge, question)
        
        # 3. Collect reasoning info
        facts_used = [f.get('content', '')[:100] for f in knowledge.relevant_facts]
        inferences = [
            f"{inf.get('source', '?')} {inf.get('relation', '?')} {inf.get('target', '?')}"
            for inf in knowledge.inferences
        ]
        rules = list(set(inf.get('rule', '') for inf in knowledge.inferences if inf.get('rule')))
        
        # Get reasoning path
        path = []
        if knowledge.reasoning_paths:
            first_path = knowledge.reasoning_paths[0]
            path = first_path.get('steps', [])
        
        elapsed = time.time() - start_time
        
        return SOMAAnswer(
            text=verbalization.text,
            confidence=verbalization.confidence,
            facts_used=facts_used,
            inferences_made=inferences,
            rules_applied=rules,
            reasoning_path=path,
            query=question,
            processing_time=elapsed,
            contradictions_found=len(knowledge.contradictions)
        )
    
    def _build_knowledge(self, query: str) -> StructuredKnowledge:
        """Build structured knowledge for a query."""
        knowledge = StructuredKnowledge(query=query)
        
        # 1. Search for relevant facts
        search_result = self.query_engine.search(
            query,
            limit=self.config["max_facts"]
        )
        
        for obj in search_result.objects:
            knowledge.relevant_facts.append({
                "content": obj.content,
                "type": obj.content_type,
                "confidence": 1.0,
                "uid": obj.uid,
            })
        
        # 2. Run inference
        if self.config["run_inference"]:
            inf_result = self.inference_engine.infer_all(
                max_iterations=50,
                min_confidence=self.config["min_confidence"]
            )
            
            for fact in inf_result.inferred_facts[:self.config["max_inferences"]]:
                src_node = self.memory.graph.get_node(fact.source_id)
                tgt_node = self.memory.graph.get_node(fact.target_id)
                
                knowledge.inferences.append({
                    "source": src_node.text if src_node else f"Node({fact.source_id})",
                    "relation": fact.relation.value,
                    "target": tgt_node.text if tgt_node else f"Node({fact.target_id})",
                    "confidence": fact.confidence,
                    "rule": fact.rule_id,
                })
        
        # 3. Find reasoning paths
        if len(search_result.objects) >= 2:
            obj1, obj2 = search_result.objects[0], search_result.objects[1]
            if obj1.graph_node_id and obj2.graph_node_id:
                path = self.path_finder.find_best_path(
                    obj1.graph_node_id,
                    obj2.graph_node_id
                )
                if path:
                    knowledge.reasoning_paths.append({
                        "from": obj1.content[:50],
                        "to": obj2.content[:50],
                        "steps": [n.text for n in path.nodes],
                        "score": path.score,
                    })
        
        # 4. Get hierarchy
        if search_result.objects:
            obj = search_result.objects[0]
            if obj.tree_id and obj.tree_node_id:
                tree = self.memory.trees.get_tree(obj.tree_id)
                if tree:
                    path_nodes = tree.get_path_from_root(obj.tree_node_id)
                    knowledge.hierarchy = {
                        "path": [n.content for n in path_nodes],
                        "depth": path_nodes[-1].depth if path_nodes else 0,
                    }
        
        # 5. Check contradictions
        if self.config["check_contradictions"]:
            report = self.contradiction_detector.detect_all()
            for cont in report.contradictions[:3]:
                knowledge.contradictions.append({
                    "type": cont.contradiction_type.value,
                    "description": cont.description,
                })
        
        # Calculate confidence
        fact_conf = 1.0 if knowledge.relevant_facts else 0.3
        inf_conf = sum(i["confidence"] for i in knowledge.inferences) / max(1, len(knowledge.inferences)) if knowledge.inferences else 0.5
        cont_penalty = 0.1 * len(knowledge.contradictions)
        
        knowledge.confidence = max(0.1, (fact_conf + inf_conf) / 2 - cont_penalty)
        
        return knowledge
    
    def explain(self, question: str) -> str:
        """
        Get detailed explanation for a question.
        
        Returns step-by-step reasoning process.
        """
        answer = self.ask(question)
        return answer.explain()
    
    def get_knowledge(self, query: str) -> StructuredKnowledge:
        """
        Get structured knowledge without verbalization.
        
        Useful for inspection or custom processing.
        """
        return self._build_knowledge(query)
    
    def __repr__(self) -> str:
        return f"SOMAReasoner(memory={len(self.memory)}, inference_rules={len(self.inference_engine.rules)})"

