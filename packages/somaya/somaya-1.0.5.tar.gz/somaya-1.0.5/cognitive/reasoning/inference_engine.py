"""
InferenceEngine - Core symbolic reasoning engine.

Performs:
- Rule chaining
- Transitive inference (IS_A, PART_OF, etc.)
- Confidence propagation
- Derived fact generation
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import time

from ..graph import GraphStore, GraphNode, GraphEdge, RelationType
from .rule_base import RuleBase, InferenceRule, RuleType


@dataclass
class InferredFact:
    """
    A fact derived through inference.
    
    Tracks:
    - The derived relation
    - The reasoning chain that produced it
    - Confidence (propagated through chain)
    - Which rule was used
    """
    source_id: int
    target_id: int
    relation: RelationType
    confidence: float
    
    # Reasoning trace
    rule_id: str
    chain: List[Tuple[int, RelationType, int]]  # [(from, rel, to), ...]
    depth: int
    
    # Metadata
    timestamp: float = field(default_factory=time.time)
    
    def __hash__(self):
        return hash((self.source_id, self.target_id, self.relation))
    
    def __eq__(self, other):
        if isinstance(other, InferredFact):
            return (self.source_id == other.source_id and 
                    self.target_id == other.target_id and
                    self.relation == other.relation)
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation.value,
            "confidence": self.confidence,
            "rule_id": self.rule_id,
            "chain": [(s, r.value, t) for s, r, t in self.chain],
            "depth": self.depth,
        }
    
    def explain(self) -> str:
        """Generate human-readable explanation."""
        if not self.chain:
            return f"Direct: {self.source_id} --{self.relation.value}--> {self.target_id}"
        
        steps = []
        for src, rel, tgt in self.chain:
            steps.append(f"{src} --{rel.value}--> {tgt}")
        
        return (
            f"Inferred: {self.source_id} --{self.relation.value}--> {self.target_id}\n"
            f"  Via rule: {self.rule_id}\n"
            f"  Chain: {' → '.join(steps)}\n"
            f"  Confidence: {self.confidence:.2%}\n"
            f"  Depth: {self.depth}"
        )


@dataclass
class InferenceResult:
    """Result of running inference."""
    inferred_facts: List[InferredFact]
    rules_applied: Dict[str, int]  # rule_id -> count
    total_iterations: int
    time_elapsed: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "facts_count": len(self.inferred_facts),
            "rules_applied": self.rules_applied,
            "iterations": self.total_iterations,
            "time_ms": self.time_elapsed * 1000,
        }


class InferenceEngine:
    """
    Symbolic inference engine for the knowledge graph.
    
    Capabilities:
    - Transitive closure (IS_A, PART_OF, etc.)
    - Rule chaining
    - Confidence propagation
    - Inverse relation inference
    - Property inheritance
    
    Example:
        engine = InferenceEngine(graph_store)
        engine.rules.add_builtin_rules()
        
        # Run inference
        result = engine.infer_all()
        
        # Check specific inference
        is_dog_animal = engine.can_infer(dog_id, animal_id, RelationType.IS_A)
        
        # Get all inferred relations for a node
        inferred = engine.get_inferred_relations(dog_id)
    """
    
    def __init__(self, graph: GraphStore, rules: Optional[RuleBase] = None):
        """
        Initialize inference engine.
        
        Args:
            graph: The knowledge graph to reason over
            rules: RuleBase to use (creates default if None)
        """
        self.graph = graph
        self.rules = rules or RuleBase()
        
        # Cache of inferred facts
        self._inferred: Dict[Tuple[int, int, RelationType], InferredFact] = {}
        
        # Index: node_id -> set of inferred facts involving this node
        self._by_node: Dict[int, Set[InferredFact]] = defaultdict(set)
        
        # Statistics
        self._stats = {
            "total_inferences": 0,
            "cache_hits": 0,
            "rules_fired": defaultdict(int),
        }
    
    def infer_all(
        self,
        max_iterations: int = 100,
        min_confidence: float = 0.1
    ) -> InferenceResult:
        """
        Run full inference over the graph.
        
        Applies all enabled rules until no new facts are derived
        or max_iterations is reached.
        
        Args:
            max_iterations: Maximum inference iterations
            min_confidence: Minimum confidence for derived facts
            
        Returns:
            InferenceResult with all inferred facts
        """
        start_time = time.time()
        rules_applied = defaultdict(int)
        iteration = 0
        
        # Clear previous inferences
        self._inferred.clear()
        self._by_node.clear()
        
        # Get all enabled rules
        all_rules = self.rules.get_all_enabled_rules()
        
        # Iterate until fixpoint
        new_facts_found = True
        while new_facts_found and iteration < max_iterations:
            new_facts_found = False
            iteration += 1
            
            for rule in all_rules:
                new_facts = self._apply_rule(rule, min_confidence)
                
                if new_facts:
                    new_facts_found = True
                    rules_applied[rule.rule_id] += len(new_facts)
                    
                    for fact in new_facts:
                        self._add_inferred_fact(fact)
        
        elapsed = time.time() - start_time
        
        return InferenceResult(
            inferred_facts=list(self._inferred.values()),
            rules_applied=dict(rules_applied),
            total_iterations=iteration,
            time_elapsed=elapsed
        )
    
    def _apply_rule(
        self,
        rule: InferenceRule,
        min_confidence: float
    ) -> List[InferredFact]:
        """Apply a single rule and return new facts."""
        
        if rule.rule_type == RuleType.TRANSITIVITY:
            return self._apply_transitivity(rule, min_confidence)
        
        elif rule.rule_type == RuleType.INHERITANCE:
            return self._apply_inheritance(rule, min_confidence)
        
        elif rule.rule_type == RuleType.INVERSE:
            return self._apply_inverse(rule, min_confidence)
        
        elif rule.rule_type == RuleType.SYMMETRY:
            return self._apply_symmetry(rule, min_confidence)
        
        elif rule.rule_type == RuleType.COMPOSITION:
            return self._apply_composition(rule, min_confidence)
        
        elif rule.rule_type == RuleType.CHAIN:
            return self._apply_chain(rule, min_confidence)
        
        return []
    
    def _apply_transitivity(
        self,
        rule: InferenceRule,
        min_confidence: float
    ) -> List[InferredFact]:
        """
        Apply transitive rule.
        
        If A->B and B->C exist with the antecedent relation,
        derive A->C with the consequent relation.
        """
        if len(rule.antecedent_relations) != 2:
            return []
        
        rel1, rel2 = rule.antecedent_relations
        new_facts = []
        
        # Get all edges of the first relation type
        edges1 = self.graph.get_edges_by_type(rel1)
        
        for edge1 in edges1:
            # Find edges that continue from edge1's target
            mid_node = edge1.target_id
            
            for edge2 in self.graph.get_outgoing_edges(mid_node):
                if edge2.relation_type != rel2:
                    continue
                
                # Found a chain: edge1.source -> mid -> edge2.target
                source = edge1.source_id
                target = edge2.target_id
                
                # Skip if same node or already exists
                if source == target:
                    continue
                
                key = (source, target, rule.consequent_relation)
                if key in self._inferred:
                    continue
                
                if self.graph.has_edge_between(source, target, rule.consequent_relation):
                    continue
                
                # Calculate confidence
                confidence = edge1.weight * edge2.weight * rule.confidence_decay
                
                if confidence >= min_confidence:
                    fact = InferredFact(
                        source_id=source,
                        target_id=target,
                        relation=rule.consequent_relation,
                        confidence=confidence,
                        rule_id=rule.rule_id,
                        chain=[
                            (edge1.source_id, rel1, mid_node),
                            (mid_node, rel2, edge2.target_id)
                        ],
                        depth=2
                    )
                    new_facts.append(fact)
        
        return new_facts
    
    def _apply_inheritance(
        self,
        rule: InferenceRule,
        min_confidence: float
    ) -> List[InferredFact]:
        """
        Apply inheritance rule.
        
        If A IS_A B and B has property P, then A inherits P.
        """
        if len(rule.antecedent_relations) != 2:
            return []
        
        is_a_rel, prop_rel = rule.antecedent_relations
        new_facts = []
        
        # For each IS_A edge
        is_a_edges = self.graph.get_edges_by_type(is_a_rel)
        
        for is_a_edge in is_a_edges:
            subclass = is_a_edge.source_id
            superclass = is_a_edge.target_id
            
            # Find properties of superclass
            for prop_edge in self.graph.get_outgoing_edges(superclass):
                if prop_edge.relation_type != prop_rel:
                    continue
                
                property_target = prop_edge.target_id
                
                # Check if subclass already has this property
                key = (subclass, property_target, rule.consequent_relation)
                if key in self._inferred:
                    continue
                
                if self.graph.has_edge_between(subclass, property_target, rule.consequent_relation):
                    continue
                
                confidence = is_a_edge.weight * prop_edge.weight * rule.confidence_decay
                
                if confidence >= min_confidence:
                    fact = InferredFact(
                        source_id=subclass,
                        target_id=property_target,
                        relation=rule.consequent_relation,
                        confidence=confidence,
                        rule_id=rule.rule_id,
                        chain=[
                            (subclass, is_a_rel, superclass),
                            (superclass, prop_rel, property_target)
                        ],
                        depth=2
                    )
                    new_facts.append(fact)
        
        return new_facts
    
    def _apply_inverse(
        self,
        rule: InferenceRule,
        min_confidence: float
    ) -> List[InferredFact]:
        """
        Apply inverse rule.
        
        If A->B exists, derive B->A with inverse relation.
        """
        if len(rule.antecedent_relations) != 1:
            return []
        
        source_rel = rule.antecedent_relations[0]
        new_facts = []
        
        for edge in self.graph.get_edges_by_type(source_rel):
            # Inverse: swap source and target
            key = (edge.target_id, edge.source_id, rule.consequent_relation)
            
            if key in self._inferred:
                continue
            
            if self.graph.has_edge_between(edge.target_id, edge.source_id, rule.consequent_relation):
                continue
            
            confidence = edge.weight * rule.confidence_decay
            
            if confidence >= min_confidence:
                fact = InferredFact(
                    source_id=edge.target_id,
                    target_id=edge.source_id,
                    relation=rule.consequent_relation,
                    confidence=confidence,
                    rule_id=rule.rule_id,
                    chain=[(edge.source_id, source_rel, edge.target_id)],
                    depth=1
                )
                new_facts.append(fact)
        
        return new_facts
    
    def _apply_symmetry(
        self,
        rule: InferenceRule,
        min_confidence: float
    ) -> List[InferredFact]:
        """
        Apply symmetry rule.
        
        If A->B exists, derive B->A with same relation.
        """
        if len(rule.antecedent_relations) != 1:
            return []
        
        rel = rule.antecedent_relations[0]
        new_facts = []
        
        for edge in self.graph.get_edges_by_type(rel):
            # Check if reverse already exists
            key = (edge.target_id, edge.source_id, rel)
            
            if key in self._inferred:
                continue
            
            if self.graph.has_edge_between(edge.target_id, edge.source_id, rel):
                continue
            
            confidence = edge.weight * rule.confidence_decay
            
            if confidence >= min_confidence:
                fact = InferredFact(
                    source_id=edge.target_id,
                    target_id=edge.source_id,
                    relation=rel,
                    confidence=confidence,
                    rule_id=rule.rule_id,
                    chain=[(edge.source_id, rel, edge.target_id)],
                    depth=1
                )
                new_facts.append(fact)
        
        return new_facts
    
    def _apply_composition(
        self,
        rule: InferenceRule,
        min_confidence: float
    ) -> List[InferredFact]:
        """Apply composition rule (same as transitivity but for mixed relations)."""
        return self._apply_transitivity(rule, min_confidence)
    
    def _apply_chain(
        self,
        rule: InferenceRule,
        min_confidence: float
    ) -> List[InferredFact]:
        """Apply custom chain rule (multi-hop)."""
        if len(rule.antecedent_relations) < 2:
            return []
        
        # For now, handle 2-hop chains
        if len(rule.antecedent_relations) == 2:
            return self._apply_transitivity(rule, min_confidence)
        
        # TODO: Support longer chains
        return []
    
    def _add_inferred_fact(self, fact: InferredFact) -> None:
        """Add an inferred fact to the cache."""
        key = (fact.source_id, fact.target_id, fact.relation)
        
        # Keep highest confidence version
        if key in self._inferred:
            if self._inferred[key].confidence >= fact.confidence:
                return
        
        self._inferred[key] = fact
        self._by_node[fact.source_id].add(fact)
        self._by_node[fact.target_id].add(fact)
        self._stats["total_inferences"] += 1
    
    def can_infer(
        self,
        source_id: int,
        target_id: int,
        relation: RelationType,
        min_confidence: float = 0.1
    ) -> Tuple[bool, Optional[InferredFact]]:
        """
        Check if a relation can be inferred between two nodes.
        
        Returns:
            (can_infer, InferredFact or None)
        """
        key = (source_id, target_id, relation)
        
        # Check cache
        if key in self._inferred:
            fact = self._inferred[key]
            if fact.confidence >= min_confidence:
                self._stats["cache_hits"] += 1
                return True, fact
        
        # Check direct edge
        if self.graph.has_edge_between(source_id, target_id, relation):
            return True, None
        
        return False, None
    
    def get_inferred_relations(
        self,
        node_id: int,
        direction: str = "both"
    ) -> List[InferredFact]:
        """
        Get all inferred relations for a node.
        
        Args:
            node_id: The node to query
            direction: "outgoing", "incoming", or "both"
        """
        facts = self._by_node.get(node_id, set())
        
        if direction == "both":
            return list(facts)
        elif direction == "outgoing":
            return [f for f in facts if f.source_id == node_id]
        else:
            return [f for f in facts if f.target_id == node_id]
    
    def get_transitive_closure(
        self,
        node_id: int,
        relation: RelationType,
        direction: str = "outgoing",
        max_depth: int = 10
    ) -> List[Tuple[int, float, int]]:
        """
        Get transitive closure for a node and relation.
        
        Returns:
            List of (node_id, confidence, depth) tuples
        """
        results = []
        visited = {node_id}
        
        # BFS with confidence tracking
        current = [(node_id, 1.0, 0)]  # (node, confidence, depth)
        
        while current:
            next_level = []
            
            for curr_id, curr_conf, depth in current:
                if depth >= max_depth:
                    continue
                
                # Get edges in specified direction
                if direction == "outgoing":
                    edges = self.graph.get_outgoing_edges(curr_id)
                    get_next = lambda e: e.target_id
                else:
                    edges = self.graph.get_incoming_edges(curr_id)
                    get_next = lambda e: e.source_id
                
                for edge in edges:
                    if edge.relation_type != relation:
                        continue
                    
                    next_id = get_next(edge)
                    if next_id in visited:
                        continue
                    
                    visited.add(next_id)
                    new_conf = curr_conf * edge.weight * 0.95  # Decay per hop
                    
                    results.append((next_id, new_conf, depth + 1))
                    next_level.append((next_id, new_conf, depth + 1))
            
            current = next_level
        
        return results
    
    def explain_inference(
        self,
        source_id: int,
        target_id: int,
        relation: RelationType
    ) -> str:
        """Get human-readable explanation for an inference."""
        key = (source_id, target_id, relation)
        
        if key in self._inferred:
            fact = self._inferred[key]
            
            # Get node names
            source = self.graph.get_node(source_id)
            target = self.graph.get_node(target_id)
            
            source_name = source.text if source else f"Node({source_id})"
            target_name = target.text if target else f"Node({target_id})"
            
            explanation = f"'{source_name}' {relation.value} '{target_name}'\n\n"
            explanation += f"Reasoning:\n"
            
            for i, (src, rel, tgt) in enumerate(fact.chain):
                src_node = self.graph.get_node(src)
                tgt_node = self.graph.get_node(tgt)
                src_name = src_node.text if src_node else f"Node({src})"
                tgt_name = tgt_node.text if tgt_node else f"Node({tgt})"
                
                explanation += f"  {i+1}. '{src_name}' --[{rel.value}]--> '{tgt_name}'\n"
            
            explanation += f"\nRule: {fact.rule_id}\n"
            explanation += f"Confidence: {fact.confidence:.1%}\n"
            
            return explanation
        
        return f"No inference found for {source_id} --{relation.value}--> {target_id}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get inference statistics."""
        return {
            "total_inferences": len(self._inferred),
            "cache_hits": self._stats["cache_hits"],
            "rules_fired": dict(self._stats["rules_fired"]),
            "nodes_with_inferences": len(self._by_node),
        }
    
    def clear_cache(self) -> None:
        """Clear the inference cache."""
        self._inferred.clear()
        self._by_node.clear()
        self._stats = {
            "total_inferences": 0,
            "cache_hits": 0,
            "rules_fired": defaultdict(int),
        }
    
    def __repr__(self) -> str:
        return f"InferenceEngine(inferred={len(self._inferred)}, rules={len(self.rules)})"

