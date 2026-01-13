"""
RuleBase - Inference rules for symbolic reasoning.

Defines rules that the InferenceEngine uses to derive new knowledge.
Each rule has:
- Antecedents (conditions that must be true)
- Consequent (what can be derived)
- Confidence factor (how much confidence decays)
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..graph import RelationType


class RuleType(Enum):
    """Types of inference rules."""
    TRANSITIVITY = "transitivity"       # A→B, B→C ⟹ A→C
    INHERITANCE = "inheritance"         # IS_A inheritance
    COMPOSITION = "composition"         # PART_OF composition
    INVERSE = "inverse"                 # R(A,B) ⟹ R⁻¹(B,A)
    CHAIN = "chain"                     # Custom multi-hop chains
    CONTRADICTION = "contradiction"     # Detects conflicts
    SYMMETRY = "symmetry"               # R(A,B) ⟹ R(B,A)


@dataclass
class InferenceRule:
    """
    A single inference rule.
    
    Example (Transitivity):
        If A IS_A B and B IS_A C, then A IS_A C
        
        rule = InferenceRule(
            rule_id="transitive_is_a",
            rule_type=RuleType.TRANSITIVITY,
            antecedent_relations=[RelationType.IS_A, RelationType.IS_A],
            consequent_relation=RelationType.IS_A,
            confidence_decay=0.9
        )
    """
    rule_id: str
    rule_type: RuleType
    name: str = ""
    description: str = ""
    
    # What relations must exist
    antecedent_relations: List[RelationType] = field(default_factory=list)
    
    # What can be derived
    consequent_relation: Optional[RelationType] = None
    
    # How confidence decays through this rule (0.0 to 1.0)
    confidence_decay: float = 0.9
    
    # Priority (higher = applied first)
    priority: int = 0
    
    # Whether this rule is enabled
    enabled: bool = True
    
    # Maximum chain depth for this rule
    max_depth: int = 5
    
    def __post_init__(self):
        if not self.name:
            self.name = self.rule_id.replace("_", " ").title()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type.value,
            "name": self.name,
            "description": self.description,
            "antecedent_relations": [r.value for r in self.antecedent_relations],
            "consequent_relation": self.consequent_relation.value if self.consequent_relation else None,
            "confidence_decay": self.confidence_decay,
            "priority": self.priority,
            "enabled": self.enabled,
            "max_depth": self.max_depth,
        }


class RuleBase:
    """
    Collection of inference rules.
    
    Provides:
    - Built-in rules for common patterns
    - Custom rule creation
    - Rule lookup by type/relation
    
    Example:
        rules = RuleBase()
        rules.add_builtin_rules()
        
        # Get all transitivity rules
        trans_rules = rules.get_rules_by_type(RuleType.TRANSITIVITY)
        
        # Get rules that involve IS_A
        is_a_rules = rules.get_rules_for_relation(RelationType.IS_A)
    """
    
    def __init__(self):
        self.rules: Dict[str, InferenceRule] = {}
    
    def add_rule(self, rule: InferenceRule) -> None:
        """Add a rule to the base."""
        self.rules[rule.rule_id] = rule
    
    def get_rule(self, rule_id: str) -> Optional[InferenceRule]:
        """Get a rule by ID."""
        return self.rules.get(rule_id)
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule. Returns True if removed."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False
    
    def get_rules_by_type(self, rule_type: RuleType) -> List[InferenceRule]:
        """Get all rules of a specific type."""
        return [r for r in self.rules.values() if r.rule_type == rule_type and r.enabled]
    
    def get_rules_for_relation(self, relation: RelationType) -> List[InferenceRule]:
        """Get all rules that involve a specific relation."""
        result = []
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            if relation in rule.antecedent_relations:
                result.append(rule)
            if rule.consequent_relation == relation:
                result.append(rule)
        return result
    
    def get_all_enabled_rules(self) -> List[InferenceRule]:
        """Get all enabled rules, sorted by priority (highest first)."""
        enabled = [r for r in self.rules.values() if r.enabled]
        return sorted(enabled, key=lambda r: -r.priority)
    
    def add_builtin_rules(self) -> None:
        """Add all built-in inference rules."""
        
        # ═══════════════════════════════════════════════════════════════
        # TRANSITIVITY RULES
        # ═══════════════════════════════════════════════════════════════
        
        # IS_A is transitive: Dog IS_A Mammal, Mammal IS_A Animal ⟹ Dog IS_A Animal
        self.add_rule(InferenceRule(
            rule_id="transitive_is_a",
            rule_type=RuleType.TRANSITIVITY,
            name="Transitive IS_A",
            description="If A IS_A B and B IS_A C, then A IS_A C",
            antecedent_relations=[RelationType.IS_A, RelationType.IS_A],
            consequent_relation=RelationType.IS_A,
            confidence_decay=0.95,
            priority=100,
            max_depth=10
        ))
        
        # PART_OF is transitive: Wheel PART_OF Car, Car PART_OF Fleet ⟹ Wheel PART_OF Fleet
        self.add_rule(InferenceRule(
            rule_id="transitive_part_of",
            rule_type=RuleType.TRANSITIVITY,
            name="Transitive PART_OF",
            description="If A PART_OF B and B PART_OF C, then A PART_OF C",
            antecedent_relations=[RelationType.PART_OF, RelationType.PART_OF],
            consequent_relation=RelationType.PART_OF,
            confidence_decay=0.9,
            priority=90,
            max_depth=5
        ))
        
        # CONTAINS is transitive
        self.add_rule(InferenceRule(
            rule_id="transitive_contains",
            rule_type=RuleType.TRANSITIVITY,
            name="Transitive CONTAINS",
            description="If A CONTAINS B and B CONTAINS C, then A CONTAINS C",
            antecedent_relations=[RelationType.CONTAINS, RelationType.CONTAINS],
            consequent_relation=RelationType.CONTAINS,
            confidence_decay=0.9,
            priority=85,
            max_depth=5
        ))
        
        # PRECEDES is transitive
        self.add_rule(InferenceRule(
            rule_id="transitive_precedes",
            rule_type=RuleType.TRANSITIVITY,
            name="Transitive PRECEDES",
            description="If A PRECEDES B and B PRECEDES C, then A PRECEDES C",
            antecedent_relations=[RelationType.PRECEDES, RelationType.PRECEDES],
            consequent_relation=RelationType.PRECEDES,
            confidence_decay=0.85,
            priority=80,
            max_depth=10
        ))
        
        # CAUSES can chain (with faster decay)
        self.add_rule(InferenceRule(
            rule_id="transitive_causes",
            rule_type=RuleType.TRANSITIVITY,
            name="Causal Chain",
            description="If A CAUSES B and B CAUSES C, then A (indirectly) CAUSES C",
            antecedent_relations=[RelationType.CAUSES, RelationType.CAUSES],
            consequent_relation=RelationType.CAUSES,
            confidence_decay=0.7,  # Faster decay for causal chains
            priority=70,
            max_depth=3  # Limit causal chain depth
        ))
        
        # ═══════════════════════════════════════════════════════════════
        # INHERITANCE RULES
        # ═══════════════════════════════════════════════════════════════
        
        # Property inheritance: If Dog IS_A Mammal and Mammal HAS_PART Spine, then Dog HAS_PART Spine
        self.add_rule(InferenceRule(
            rule_id="inherit_has_part",
            rule_type=RuleType.INHERITANCE,
            name="Inherit HAS_PART",
            description="Subclasses inherit parts from superclasses",
            antecedent_relations=[RelationType.IS_A, RelationType.HAS_PART],
            consequent_relation=RelationType.HAS_PART,
            confidence_decay=0.85,
            priority=75
        ))
        
        # Capability inheritance: If Dog IS_A Mammal and Mammal USES Lungs, then Dog USES Lungs
        self.add_rule(InferenceRule(
            rule_id="inherit_uses",
            rule_type=RuleType.INHERITANCE,
            name="Inherit USES",
            description="Subclasses inherit capabilities from superclasses",
            antecedent_relations=[RelationType.IS_A, RelationType.USES],
            consequent_relation=RelationType.USES,
            confidence_decay=0.8,
            priority=70
        ))
        
        # ═══════════════════════════════════════════════════════════════
        # INVERSE RULES
        # ═══════════════════════════════════════════════════════════════
        
        # PART_OF ↔ HAS_PART
        self.add_rule(InferenceRule(
            rule_id="inverse_part_of",
            rule_type=RuleType.INVERSE,
            name="PART_OF Inverse",
            description="If A PART_OF B, then B HAS_PART A",
            antecedent_relations=[RelationType.PART_OF],
            consequent_relation=RelationType.HAS_PART,
            confidence_decay=1.0,  # No decay for inverse
            priority=95
        ))
        
        # HAS_PART ↔ PART_OF
        self.add_rule(InferenceRule(
            rule_id="inverse_has_part",
            rule_type=RuleType.INVERSE,
            name="HAS_PART Inverse",
            description="If A HAS_PART B, then B PART_OF A",
            antecedent_relations=[RelationType.HAS_PART],
            consequent_relation=RelationType.PART_OF,
            confidence_decay=1.0,
            priority=95
        ))
        
        # CAUSES ↔ CAUSED_BY
        self.add_rule(InferenceRule(
            rule_id="inverse_causes",
            rule_type=RuleType.INVERSE,
            name="CAUSES Inverse",
            description="If A CAUSES B, then B CAUSED_BY A",
            antecedent_relations=[RelationType.CAUSES],
            consequent_relation=RelationType.CAUSED_BY,
            confidence_decay=1.0,
            priority=95
        ))
        
        # PRECEDES ↔ FOLLOWS
        self.add_rule(InferenceRule(
            rule_id="inverse_precedes",
            rule_type=RuleType.INVERSE,
            name="PRECEDES Inverse",
            description="If A PRECEDES B, then B FOLLOWS A",
            antecedent_relations=[RelationType.PRECEDES],
            consequent_relation=RelationType.FOLLOWS,
            confidence_decay=1.0,
            priority=95
        ))
        
        # USES ↔ USED_BY
        self.add_rule(InferenceRule(
            rule_id="inverse_uses",
            rule_type=RuleType.INVERSE,
            name="USES Inverse",
            description="If A USES B, then B USED_BY A",
            antecedent_relations=[RelationType.USES],
            consequent_relation=RelationType.USED_BY,
            confidence_decay=1.0,
            priority=95
        ))
        
        # ═══════════════════════════════════════════════════════════════
        # SYMMETRY RULES
        # ═══════════════════════════════════════════════════════════════
        
        # SIMILAR_TO is symmetric
        self.add_rule(InferenceRule(
            rule_id="symmetric_similar_to",
            rule_type=RuleType.SYMMETRY,
            name="Symmetric SIMILAR_TO",
            description="If A SIMILAR_TO B, then B SIMILAR_TO A",
            antecedent_relations=[RelationType.SIMILAR_TO],
            consequent_relation=RelationType.SIMILAR_TO,
            confidence_decay=1.0,
            priority=90
        ))
        
        # RELATED_TO is symmetric
        self.add_rule(InferenceRule(
            rule_id="symmetric_related_to",
            rule_type=RuleType.SYMMETRY,
            name="Symmetric RELATED_TO",
            description="If A RELATED_TO B, then B RELATED_TO A",
            antecedent_relations=[RelationType.RELATED_TO],
            consequent_relation=RelationType.RELATED_TO,
            confidence_decay=1.0,
            priority=90
        ))
        
        # OPPOSITE_OF is symmetric
        self.add_rule(InferenceRule(
            rule_id="symmetric_opposite_of",
            rule_type=RuleType.SYMMETRY,
            name="Symmetric OPPOSITE_OF",
            description="If A OPPOSITE_OF B, then B OPPOSITE_OF A",
            antecedent_relations=[RelationType.OPPOSITE_OF],
            consequent_relation=RelationType.OPPOSITE_OF,
            confidence_decay=1.0,
            priority=90
        ))
        
        # ═══════════════════════════════════════════════════════════════
        # CONTRADICTION RULES
        # ═══════════════════════════════════════════════════════════════
        
        # OPPOSITE_OF + SIMILAR_TO = contradiction
        self.add_rule(InferenceRule(
            rule_id="contradict_opposite_similar",
            rule_type=RuleType.CONTRADICTION,
            name="Opposite-Similar Contradiction",
            description="A cannot be both OPPOSITE_OF and SIMILAR_TO B",
            antecedent_relations=[RelationType.OPPOSITE_OF, RelationType.SIMILAR_TO],
            consequent_relation=None,  # No derived relation, just flags contradiction
            confidence_decay=0.0,
            priority=100
        ))
        
        # PRECEDES + FOLLOWS on same pair = contradiction
        self.add_rule(InferenceRule(
            rule_id="contradict_precedes_follows",
            rule_type=RuleType.CONTRADICTION,
            name="Temporal Contradiction",
            description="A cannot both PRECEDE and FOLLOW B",
            antecedent_relations=[RelationType.PRECEDES, RelationType.FOLLOWS],
            consequent_relation=None,
            confidence_decay=0.0,
            priority=100
        ))
        
        # ═══════════════════════════════════════════════════════════════
        # COMPOSITION RULES (multi-relation chains)
        # ═══════════════════════════════════════════════════════════════
        
        # If A PART_OF B and B IS_A C, then A PART_OF C
        self.add_rule(InferenceRule(
            rule_id="compose_part_of_is_a",
            rule_type=RuleType.COMPOSITION,
            name="Part-Of through IS_A",
            description="Parts of a subclass are parts of the superclass context",
            antecedent_relations=[RelationType.PART_OF, RelationType.IS_A],
            consequent_relation=RelationType.PART_OF,
            confidence_decay=0.8,
            priority=60
        ))
    
    def create_custom_rule(
        self,
        rule_id: str,
        antecedent_relations: List[RelationType],
        consequent_relation: RelationType,
        name: str = "",
        description: str = "",
        confidence_decay: float = 0.9,
        max_depth: int = 5
    ) -> InferenceRule:
        """
        Create and add a custom inference rule.
        
        Example:
            # If A ENABLES B and B CAUSES C, then A indirectly CAUSES C
            rule = rules.create_custom_rule(
                "enable_cause_chain",
                [RelationType.ENABLES, RelationType.CAUSES],
                RelationType.CAUSES,
                confidence_decay=0.7
            )
        """
        rule = InferenceRule(
            rule_id=rule_id,
            rule_type=RuleType.CHAIN,
            name=name or rule_id.replace("_", " ").title(),
            description=description,
            antecedent_relations=antecedent_relations,
            consequent_relation=consequent_relation,
            confidence_decay=confidence_decay,
            max_depth=max_depth
        )
        self.add_rule(rule)
        return rule
    
    def __len__(self) -> int:
        return len(self.rules)
    
    def __repr__(self) -> str:
        enabled = sum(1 for r in self.rules.values() if r.enabled)
        return f"RuleBase(rules={len(self.rules)}, enabled={enabled})"

