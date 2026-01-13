"""
HybridReasoner - Bridge between symbolic cognition and neural generation.

The key insight:
    Query → Graph + Tree + Memory → Structured Context → LLM → Natural Answer

The LLM becomes a SPEAKER, not a THINKER.
SOMA Cognitive does the reasoning; LLM just verbalizes.
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..graph import GraphStore, GraphNode, RelationType
from ..trees import TreeStore, Tree
from ..memory import UnifiedMemory, MemoryObject
from .inference_engine import InferenceEngine, InferredFact
from .path_finder import PathFinder, ReasoningPath
from .query_engine import QueryEngine, QueryResult
from .contradiction_detector import ContradictionDetector


class ContextType(Enum):
    """Types of context that can be provided to the generator."""
    FACTS = "facts"                   # Direct facts from memory
    INFERENCES = "inferences"         # Derived facts
    PATHS = "paths"                   # Reasoning paths
    HIERARCHY = "hierarchy"           # Tree context
    CONTRADICTIONS = "contradictions" # Flagged conflicts


@dataclass
class StructuredContext:
    """
    Structured context for the neural generator.
    
    This is what SOMA Cognitive produces for the LLM.
    The LLM's job is to turn this into natural language.
    """
    query: str
    
    # Retrieved knowledge
    relevant_facts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Inferred knowledge
    inferences: List[Dict[str, Any]] = field(default_factory=list)
    
    # Reasoning paths
    reasoning_paths: List[Dict[str, Any]] = field(default_factory=list)
    
    # Hierarchical context
    hierarchy: Optional[Dict[str, Any]] = None
    
    # Potential issues
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Confidence score for the context
    confidence: float = 1.0
    
    # Suggested answer structure
    answer_hints: List[str] = field(default_factory=list)
    
    def to_prompt(self) -> str:
        """
        Convert structured context to a prompt for the LLM.
        
        This is the key function - it formats cognitive output
        for neural verbalization.
        """
        sections = []
        
        # Header
        sections.append("=== STRUCTURED KNOWLEDGE CONTEXT ===")
        sections.append(f"Query: {self.query}")
        sections.append("")
        
        # Facts
        if self.relevant_facts:
            sections.append("## RELEVANT FACTS")
            for i, fact in enumerate(self.relevant_facts, 1):
                content = fact.get("content", "")
                conf = fact.get("confidence", 1.0)
                sections.append(f"{i}. {content} (confidence: {conf:.0%})")
            sections.append("")
        
        # Inferences
        if self.inferences:
            sections.append("## INFERRED KNOWLEDGE")
            for inf in self.inferences:
                src = inf.get("source", "?")
                rel = inf.get("relation", "?")
                tgt = inf.get("target", "?")
                conf = inf.get("confidence", 0)
                rule = inf.get("rule", "unknown")
                sections.append(f"- {src} --[{rel}]--> {tgt}")
                sections.append(f"  (via {rule}, confidence: {conf:.0%})")
            sections.append("")
        
        # Reasoning paths
        if self.reasoning_paths:
            sections.append("## REASONING PATHS")
            for i, path in enumerate(self.reasoning_paths, 1):
                sections.append(f"Path {i}:")
                steps = path.get("steps", [])
                for step in steps:
                    sections.append(f"  → {step}")
                sections.append(f"  Score: {path.get('score', 0):.2f}")
            sections.append("")
        
        # Hierarchy
        if self.hierarchy:
            sections.append("## HIERARCHICAL CONTEXT")
            path = self.hierarchy.get("path", [])
            if path:
                sections.append(f"Position: {' > '.join(path)}")
            siblings = self.hierarchy.get("siblings", [])
            if siblings:
                sections.append(f"Related: {', '.join(siblings)}")
            sections.append("")
        
        # Contradictions (important!)
        if self.contradictions:
            sections.append("## ⚠️ CONTRADICTIONS DETECTED")
            for cont in self.contradictions:
                sections.append(f"- {cont.get('description', '?')}")
                sections.append(f"  Suggestion: {cont.get('suggestion', 'Review knowledge')}")
            sections.append("")
        
        # Answer hints
        if self.answer_hints:
            sections.append("## ANSWER GUIDELINES")
            for hint in self.answer_hints:
                sections.append(f"- {hint}")
            sections.append("")
        
        # Confidence
        sections.append(f"Overall context confidence: {self.confidence:.0%}")
        sections.append("=== END CONTEXT ===")
        
        return "\n".join(sections)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "relevant_facts": self.relevant_facts,
            "inferences": self.inferences,
            "reasoning_paths": self.reasoning_paths,
            "hierarchy": self.hierarchy,
            "contradictions": self.contradictions,
            "confidence": self.confidence,
            "answer_hints": self.answer_hints,
        }


@dataclass
class HybridAnswer:
    """
    Answer produced by hybrid reasoning.
    
    Contains both the generated text and the reasoning trace.
    """
    answer: str
    context: StructuredContext
    confidence: float
    
    # For explainability
    sources_used: List[str] = field(default_factory=list)
    rules_applied: List[str] = field(default_factory=list)
    
    def explain(self) -> str:
        """Generate explanation of how answer was produced."""
        lines = [
            "## How this answer was produced:",
            "",
            f"Query: {self.context.query}",
            f"Confidence: {self.confidence:.0%}",
            "",
        ]
        
        if self.sources_used:
            lines.append("Sources used:")
            for src in self.sources_used:
                lines.append(f"  - {src}")
            lines.append("")
        
        if self.rules_applied:
            lines.append("Inference rules applied:")
            for rule in self.rules_applied:
                lines.append(f"  - {rule}")
            lines.append("")
        
        if self.context.contradictions:
            lines.append("⚠️ Note: Some contradictions were detected in the knowledge base.")
        
        return "\n".join(lines)


class HybridReasoner:
    """
    Hybrid symbolic + neural reasoning system.
    
    Architecture:
        Query
         ↓
        Graph + Tree + Memory (symbolic retrieval)
         ↓
        Inference Engine (symbolic reasoning)
         ↓
        Structured Context (formatted knowledge)
         ↓
        Generator (LLM/NumPy GPT)
         ↓
        Natural Language Answer
    
    Example:
        # Setup
        memory = UnifiedMemory()
        reasoner = HybridReasoner(memory)
        
        # Add a generator (your NumPy GPT or any LLM)
        reasoner.set_generator(my_gpt.generate)
        
        # Query
        answer = reasoner.answer("What is attention in transformers?")
        
        # Get explanation
        print(answer.explain())
    """
    
    def __init__(self, memory: UnifiedMemory):
        """
        Initialize hybrid reasoner.
        
        Args:
            memory: UnifiedMemory instance with knowledge
        """
        self.memory = memory
        
        # Initialize reasoning components
        self.inference = InferenceEngine(memory.graph)
        self.inference.rules.add_builtin_rules()
        
        self.path_finder = PathFinder(memory.graph)
        self.query_engine = QueryEngine(memory)
        self.contradiction_detector = ContradictionDetector(memory.graph)
        
        # Generator function (to be set by user)
        self._generator: Optional[Callable[[str], str]] = None
        
        # Configuration
        self.config = {
            "max_facts": 10,
            "max_inferences": 5,
            "max_paths": 3,
            "include_hierarchy": True,
            "check_contradictions": True,
            "min_confidence": 0.3,
        }
    
    def set_generator(self, generator_fn: Callable[[str], str]) -> None:
        """
        Set the neural generator function.
        
        Args:
            generator_fn: Function that takes prompt string and returns generated text
            
        Example:
            # Using your NumPy GPT
            reasoner.set_generator(lambda prompt: my_gpt.generate(prompt, max_tokens=200))
            
            # Using OpenAI
            reasoner.set_generator(lambda prompt: openai.complete(prompt))
        """
        self._generator = generator_fn
    
    def build_context(self, query: str) -> StructuredContext:
        """
        Build structured context for a query.
        
        This does all the symbolic reasoning:
        1. Search memory for relevant facts
        2. Run inference to derive new facts
        3. Find reasoning paths
        4. Get hierarchical context
        5. Check for contradictions
        
        Args:
            query: The user's query
            
        Returns:
            StructuredContext ready for the generator
        """
        context = StructuredContext(query=query)
        
        # 1. Search for relevant facts
        search_result = self.query_engine.search(
            query,
            limit=self.config["max_facts"]
        )
        
        for obj in search_result.objects:
            context.relevant_facts.append({
                "content": obj.content,
                "type": obj.content_type,
                "confidence": 1.0,  # Direct facts have full confidence
                "uid": obj.uid,
            })
        
        # 2. Run inference
        inference_result = self.inference.infer_all(
            max_iterations=50,
            min_confidence=self.config["min_confidence"]
        )
        
        # Add relevant inferences
        for fact in inference_result.inferred_facts[:self.config["max_inferences"]]:
            src_node = self.memory.graph.get_node(fact.source_id)
            tgt_node = self.memory.graph.get_node(fact.target_id)
            
            context.inferences.append({
                "source": src_node.text if src_node else f"Node({fact.source_id})",
                "relation": fact.relation.value,
                "target": tgt_node.text if tgt_node else f"Node({fact.target_id})",
                "confidence": fact.confidence,
                "rule": fact.rule_id,
                "depth": fact.depth,
            })
        
        # 3. Find reasoning paths between relevant concepts
        if len(search_result.objects) >= 2:
            obj1 = search_result.objects[0]
            obj2 = search_result.objects[1]
            
            if obj1.graph_node_id and obj2.graph_node_id:
                path = self.path_finder.find_best_path(
                    obj1.graph_node_id,
                    obj2.graph_node_id
                )
                
                if path:
                    context.reasoning_paths.append({
                        "from": obj1.content[:50],
                        "to": obj2.content[:50],
                        "steps": [n.text for n in path.nodes],
                        "score": path.score,
                        "explanation": path.explanation,
                    })
        
        # 4. Get hierarchical context
        if self.config["include_hierarchy"] and search_result.objects:
            obj = search_result.objects[0]
            if obj.tree_id and obj.tree_node_id:
                tree = self.memory.trees.get_tree(obj.tree_id)
                if tree:
                    path_nodes = tree.get_path_from_root(obj.tree_node_id)
                    siblings = tree.get_siblings(obj.tree_node_id)
                    
                    context.hierarchy = {
                        "tree": obj.tree_id,
                        "path": [n.content for n in path_nodes],
                        "depth": path_nodes[-1].depth if path_nodes else 0,
                        "siblings": [s.content for s in siblings[:5]],
                    }
        
        # 5. Check for contradictions
        if self.config["check_contradictions"]:
            report = self.contradiction_detector.detect_all()
            
            for cont in report.contradictions[:3]:  # Limit to top 3
                context.contradictions.append({
                    "type": cont.contradiction_type.value,
                    "description": cont.description,
                    "severity": cont.severity,
                    "suggestion": cont.suggestion,
                })
        
        # 6. Calculate overall confidence
        fact_confidence = 1.0 if context.relevant_facts else 0.5
        inference_confidence = min(
            1.0,
            sum(inf["confidence"] for inf in context.inferences) / max(1, len(context.inferences))
        ) if context.inferences else 0.8
        
        contradiction_penalty = 0.1 * len(context.contradictions)
        
        context.confidence = max(0.1, (fact_confidence + inference_confidence) / 2 - contradiction_penalty)
        
        # 7. Generate answer hints
        if context.relevant_facts:
            context.answer_hints.append("Base your answer on the provided facts")
        
        if context.inferences:
            context.answer_hints.append("Consider the inferred relationships")
        
        if context.contradictions:
            context.answer_hints.append("Note: Some knowledge may be contradictory - be cautious")
        
        if context.confidence < 0.5:
            context.answer_hints.append("Confidence is low - acknowledge uncertainty")
        
        return context
    
    def answer(
        self,
        query: str,
        return_context: bool = False
    ) -> HybridAnswer:
        """
        Answer a query using hybrid reasoning.
        
        Args:
            query: The user's question
            return_context: If True, include full context in answer
            
        Returns:
            HybridAnswer with generated text and reasoning trace
        """
        # Build context
        context = self.build_context(query)
        
        # Generate answer
        if self._generator:
            prompt = context.to_prompt()
            prompt += f"\n\nBased on the above context, answer: {query}\n\nAnswer:"
            
            generated = self._generator(prompt)
        else:
            # No generator - return structured summary
            generated = self._summarize_context(context)
        
        # Build answer
        sources = [f["content"][:50] for f in context.relevant_facts]
        rules = list(set(inf["rule"] for inf in context.inferences))
        
        return HybridAnswer(
            answer=generated,
            context=context,
            confidence=context.confidence,
            sources_used=sources,
            rules_applied=rules
        )
    
    def _summarize_context(self, context: StructuredContext) -> str:
        """Generate a summary when no neural generator is available."""
        lines = []
        
        if context.relevant_facts:
            lines.append("Based on the knowledge base:")
            for fact in context.relevant_facts[:3]:
                lines.append(f"• {fact['content']}")
        
        if context.inferences:
            lines.append("\nAdditionally inferred:")
            for inf in context.inferences[:2]:
                lines.append(f"• {inf['source']} {inf['relation']} {inf['target']}")
        
        if context.contradictions:
            lines.append("\n⚠️ Note: Some contradictions exist in the knowledge.")
        
        if not lines:
            lines.append("No relevant information found in the knowledge base.")
        
        return "\n".join(lines)
    
    def explain_answer(self, answer: HybridAnswer) -> str:
        """Get detailed explanation of how an answer was produced."""
        return answer.explain()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reasoning statistics."""
        return {
            "memory_objects": len(self.memory),
            "graph_nodes": self.memory.graph.node_count,
            "graph_edges": self.memory.graph.edge_count,
            "trees": len(self.memory.trees),
            "inference_rules": len(self.inference.rules),
            "has_generator": self._generator is not None,
        }
    
    def __repr__(self) -> str:
        has_gen = "with generator" if self._generator else "no generator"
        return f"HybridReasoner({has_gen}, memory={len(self.memory)} objects)"

