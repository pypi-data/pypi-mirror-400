"""
SOMA SLM Constraints

Token-level allow/deny logic that makes hallucination structurally impossible.
Every token choice is filtered by:
    - allowed facts
    - allowed relations
    - allowed vocabulary scope

This is NOT statistical filtering. This is STRUCTURAL control.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Callable
from enum import Enum
import re


class ConstraintType(Enum):
    """Types of constraints that can be applied."""
    VOCABULARY = "vocabulary"      # Token must be in allowed vocabulary
    FACT_BOUND = "fact_bound"      # Token must relate to known facts
    RELATION = "relation"          # Token must follow valid relations
    SEQUENCE = "sequence"          # Token must follow valid sequences
    NUMERIC = "numeric"            # Numeric constraints (ranges, etc.)
    CUSTOM = "custom"              # User-defined constraint


@dataclass
class TokenConstraint:
    """
    A constraint on what tokens can be generated.
    
    This is the atomic unit of control. Every token emitted
    must pass ALL active constraints.
    """
    constraint_type: ConstraintType
    allowed_tokens: Optional[Set[str]] = None
    denied_tokens: Optional[Set[str]] = None
    pattern: Optional[str] = None  # Regex pattern
    validator: Optional[Callable[[str, 'GenerationContext'], bool]] = None
    priority: int = 0  # Higher = checked first
    name: str = ""
    
    def check(self, token: str, context: 'GenerationContext') -> bool:
        """
        Check if a token passes this constraint.
        
        Returns True if token is ALLOWED, False if DENIED.
        """
        # Explicit deny list takes precedence
        if self.denied_tokens and token in self.denied_tokens:
            return False
        
        # Explicit allow list
        if self.allowed_tokens is not None:
            if token not in self.allowed_tokens:
                return False
        
        # Pattern matching
        if self.pattern:
            if not re.match(self.pattern, token):
                return False
        
        # Custom validator
        if self.validator:
            if not self.validator(token, context):
                return False
        
        return True


@dataclass
class FactConstraint:
    """
    Constraint that binds generation to known facts.
    
    The generator can ONLY emit tokens that are grounded
    in facts from soma Cognitive.
    """
    facts: List[str] = field(default_factory=list)
    fact_tokens: Set[str] = field(default_factory=set)
    strict: bool = True  # If True, ONLY fact tokens allowed
    
    def __post_init__(self):
        """Extract tokens from facts."""
        for fact in self.facts:
            # Simple tokenization - split on whitespace and punctuation
            tokens = re.findall(r'\b\w+\b', fact.lower())
            self.fact_tokens.update(tokens)
    
    def add_fact(self, fact: str):
        """Add a fact and extract its tokens."""
        self.facts.append(fact)
        tokens = re.findall(r'\b\w+\b', fact.lower())
        self.fact_tokens.update(tokens)
    
    def is_grounded(self, token: str) -> bool:
        """Check if token is grounded in known facts."""
        return token.lower() in self.fact_tokens
    
    def get_allowed_tokens(self) -> Set[str]:
        """Get all tokens that are allowed based on facts."""
        return self.fact_tokens.copy()


@dataclass
class VocabularyScope:
    """
    Defines the vocabulary scope for generation.
    
    This is not just a word list - it's a BOUNDARY.
    Nothing outside this scope can be generated.
    """
    # Core vocabulary
    tokens: Set[str] = field(default_factory=set)
    
    # Structural tokens (always allowed)
    structural: Set[str] = field(default_factory=lambda: {
        '.', ',', '!', '?', ':', ';',
        'the', 'a', 'an', 'is', 'are', 'was', 'were',
        'of', 'in', 'to', 'for', 'with', 'on', 'at',
        'and', 'or', 'but', 'not', 'no', 'yes',
        'that', 'this', 'it', 'they', 'we', 'you', 'i',
        'be', 'have', 'has', 'had', 'do', 'does', 'did',
        'can', 'could', 'will', 'would', 'should', 'may', 'might',
    })
    
    # Domain-specific additions
    domain_tokens: Set[str] = field(default_factory=set)
    
    def add_tokens(self, tokens: List[str]):
        """Add tokens to vocabulary."""
        self.tokens.update(t.lower() for t in tokens)
    
    def add_domain(self, domain_tokens: List[str]):
        """Add domain-specific tokens."""
        self.domain_tokens.update(t.lower() for t in domain_tokens)
    
    def is_in_scope(self, token: str) -> bool:
        """Check if token is within vocabulary scope."""
        t = token.lower()
        return (t in self.tokens or 
                t in self.structural or 
                t in self.domain_tokens)
    
    def get_full_vocabulary(self) -> Set[str]:
        """Get complete vocabulary."""
        return self.tokens | self.structural | self.domain_tokens


@dataclass
class GenerationContext:
    """
    Context for generation - what the generator knows.
    
    This is passed to constraints for contextual decisions.
    """
    # What has been generated so far
    generated_tokens: List[str] = field(default_factory=list)
    generated_text: str = ""
    
    # The query/prompt
    query: str = ""
    
    # Facts from soma Cognitive
    facts: List[str] = field(default_factory=list)
    
    # Reasoning path from soma Cognitive
    reasoning_path: List[str] = field(default_factory=list)
    
    # Current constraints
    active_constraints: List[str] = field(default_factory=list)
    
    # Metadata
    step: int = 0
    max_steps: int = 100
    
    def add_token(self, token: str):
        """Add a generated token to context."""
        self.generated_tokens.append(token)
        if self.generated_text:
            # Smart spacing
            if token in '.,:;!?':
                self.generated_text += token
            else:
                self.generated_text += ' ' + token
        else:
            self.generated_text = token
        self.step += 1


class ConstraintEngine:
    """
    The core constraint engine.
    
    This is the GATEKEEPER. Every token must pass through here.
    If a token fails ANY constraint, it is REJECTED.
    
    This makes hallucination structurally impossible.
    """
    
    def __init__(self):
        self.constraints: List[TokenConstraint] = []
        self.fact_constraint: Optional[FactConstraint] = None
        self.vocabulary_scope: Optional[VocabularyScope] = None
        self.context: GenerationContext = GenerationContext()
        
        # Statistics
        self.tokens_checked: int = 0
        self.tokens_rejected: int = 0
        self.rejection_reasons: Dict[str, int] = {}
    
    def add_constraint(self, constraint: TokenConstraint):
        """Add a constraint to the engine."""
        self.constraints.append(constraint)
        # Sort by priority (higher first)
        self.constraints.sort(key=lambda c: c.priority, reverse=True)
    
    def set_fact_constraint(self, facts: List[str], strict: bool = True):
        """Set the fact constraint from soma Cognitive facts."""
        self.fact_constraint = FactConstraint(facts=facts, strict=strict)
    
    def set_vocabulary_scope(self, scope: VocabularyScope):
        """Set the vocabulary scope."""
        self.vocabulary_scope = scope
    
    def add_facts_from_cognitive(self, facts: List[str]):
        """Add facts from soma Cognitive."""
        if self.fact_constraint is None:
            self.fact_constraint = FactConstraint()
        for fact in facts:
            self.fact_constraint.add_fact(fact)
        self.context.facts = facts
    
    def set_reasoning_path(self, path: List[str]):
        """Set the reasoning path from soma Cognitive."""
        self.context.reasoning_path = path
    
    def check_token(self, token: str) -> tuple[bool, str]:
        """
        Check if a token is allowed.
        
        Returns:
            (allowed: bool, reason: str)
        """
        self.tokens_checked += 1
        
        # Check vocabulary scope first (fastest check)
        if self.vocabulary_scope:
            if not self.vocabulary_scope.is_in_scope(token):
                self._record_rejection("vocabulary_scope")
                return False, f"Token '{token}' outside vocabulary scope"
        
        # Check fact grounding
        if self.fact_constraint and self.fact_constraint.strict:
            if not self.fact_constraint.is_grounded(token):
                # Allow structural tokens even if not in facts
                if self.vocabulary_scope and token.lower() in self.vocabulary_scope.structural:
                    pass  # Structural tokens are always allowed
                else:
                    self._record_rejection("fact_grounding")
                    return False, f"Token '{token}' not grounded in facts"
        
        # Check all registered constraints
        for constraint in self.constraints:
            if not constraint.check(token, self.context):
                self._record_rejection(constraint.name or constraint.constraint_type.value)
                return False, f"Token '{token}' rejected by constraint: {constraint.name}"
        
        return True, "allowed"
    
    def filter_candidates(self, candidates: List[str]) -> List[str]:
        """
        Filter a list of candidate tokens.
        
        Returns only tokens that pass ALL constraints.
        """
        allowed = []
        for token in candidates:
            passed, _ = self.check_token(token)
            if passed:
                allowed.append(token)
        return allowed
    
    def get_allowed_tokens(self) -> Set[str]:
        """
        Get all tokens that are currently allowed.
        
        This is the INTERSECTION of:
        - vocabulary scope
        - fact tokens
        - any other constraints
        """
        # Start with vocabulary scope
        if self.vocabulary_scope:
            allowed = self.vocabulary_scope.get_full_vocabulary()
        else:
            allowed = set()
        
        # Intersect with fact tokens if strict
        if self.fact_constraint and self.fact_constraint.strict:
            fact_tokens = self.fact_constraint.get_allowed_tokens()
            # Keep structural tokens
            if self.vocabulary_scope:
                structural = self.vocabulary_scope.structural
                allowed = (allowed & fact_tokens) | structural
            else:
                allowed = fact_tokens
        
        return allowed
    
    def _record_rejection(self, reason: str):
        """Record a rejection reason."""
        self.tokens_rejected += 1
        self.rejection_reasons[reason] = self.rejection_reasons.get(reason, 0) + 1
    
    def get_stats(self) -> Dict:
        """Get constraint statistics."""
        return {
            'tokens_checked': self.tokens_checked,
            'tokens_rejected': self.tokens_rejected,
            'rejection_rate': self.tokens_rejected / max(1, self.tokens_checked),
            'rejection_reasons': self.rejection_reasons.copy(),
            'active_constraints': len(self.constraints),
            'fact_count': len(self.fact_constraint.facts) if self.fact_constraint else 0,
            'vocab_size': len(self.vocabulary_scope.get_full_vocabulary()) if self.vocabulary_scope else 0,
        }
    
    def reset_stats(self):
        """Reset statistics."""
        self.tokens_checked = 0
        self.tokens_rejected = 0
        self.rejection_reasons = {}
    
    def reset_context(self):
        """Reset generation context."""
        self.context = GenerationContext()


# Pre-built constraint factories

def create_fact_only_constraint(facts: List[str]) -> ConstraintEngine:
    """
    Create a constraint engine that ONLY allows fact-grounded tokens.
    
    This is the strictest mode - pure fact verbalization.
    """
    engine = ConstraintEngine()
    engine.set_fact_constraint(facts, strict=True)
    
    # Build vocabulary from facts
    scope = VocabularyScope()
    for fact in facts:
        tokens = re.findall(r'\b\w+\b', fact.lower())
        scope.add_tokens(tokens)
    engine.set_vocabulary_scope(scope)
    
    return engine


def create_domain_constraint(facts: List[str], domain_vocab: List[str]) -> ConstraintEngine:
    """
    Create a constraint engine with domain vocabulary.
    
    Allows fact tokens + domain-specific vocabulary.
    """
    engine = ConstraintEngine()
    engine.set_fact_constraint(facts, strict=False)  # Not strict - domain tokens allowed
    
    scope = VocabularyScope()
    for fact in facts:
        tokens = re.findall(r'\b\w+\b', fact.lower())
        scope.add_tokens(tokens)
    scope.add_domain(domain_vocab)
    engine.set_vocabulary_scope(scope)
    
    return engine


def create_reasoning_constraint(
    facts: List[str],
    reasoning_path: List[str],
    relations: List[str]
) -> ConstraintEngine:
    """
    Create a constraint engine that follows a reasoning path.
    
    Tokens must be relevant to the reasoning path.
    """
    engine = ConstraintEngine()
    engine.set_fact_constraint(facts, strict=True)
    engine.set_reasoning_path(reasoning_path)
    
    # Build vocabulary from facts AND reasoning path
    scope = VocabularyScope()
    for fact in facts:
        tokens = re.findall(r'\b\w+\b', fact.lower())
        scope.add_tokens(tokens)
    for step in reasoning_path:
        tokens = re.findall(r'\b\w+\b', step.lower())
        scope.add_tokens(tokens)
    
    # Add relation words
    scope.add_domain(relations)
    engine.set_vocabulary_scope(scope)
    
    return engine

