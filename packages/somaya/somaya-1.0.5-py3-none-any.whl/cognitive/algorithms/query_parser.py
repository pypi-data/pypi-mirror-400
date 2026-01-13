"""
SOMA Query Parser - Natural Language to Structured Query
=========================================================

SOMA-ORIGINAL. NO NLP LIBRARIES. NO NEURAL PARSING.

Parses natural language queries into structured representations
using pure pattern matching and rule-based analysis.

Supported Query Types:
- Definition: "What is X?"
- Relation: "How is X related to Y?"
- List: "What are the parts of X?"
- Boolean: "Is X a Y?"
- Comparison: "What is the difference between X and Y?"
- Process: "How does X work?"
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re


class QueryType(Enum):
    """Types of parsed queries."""
    DEFINITION = "definition"       # What is X?
    RELATION = "relation"           # How is X related to Y?
    LIST = "list"                   # What are the parts of X?
    BOOLEAN = "boolean"             # Is X a Y?
    COMPARISON = "comparison"       # Difference between X and Y?
    PROCESS = "process"             # How does X work?
    COUNT = "count"                 # How many X?
    CAUSE = "cause"                 # Why does X happen?
    EXAMPLE = "example"             # Give example of X
    UNKNOWN = "unknown"


@dataclass
class ParsedQuery:
    """A parsed query structure."""
    original: str
    query_type: QueryType
    
    # Extracted entities
    subject: Optional[str] = None
    object: Optional[str] = None
    
    # For relation queries
    relation_hint: Optional[str] = None
    
    # Modifiers
    negated: bool = False
    quantifier: Optional[str] = None  # "all", "some", "any"
    
    # Confidence
    confidence: float = 1.0
    
    # For advanced queries
    filters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original": self.original,
            "type": self.query_type.value,
            "subject": self.subject,
            "object": self.object,
            "relation_hint": self.relation_hint,
            "negated": self.negated,
            "quantifier": self.quantifier,
            "confidence": self.confidence,
            "filters": self.filters,
        }
    
    def explain(self) -> str:
        """Explain the parsed query."""
        lines = [
            f"Query: \"{self.original}\"",
            f"Type: {self.query_type.value}",
            f"Subject: {self.subject or '(none)'}",
        ]
        
        if self.object:
            lines.append(f"Object: {self.object}")
        
        if self.relation_hint:
            lines.append(f"Relation hint: {self.relation_hint}")
        
        if self.negated:
            lines.append("Negated: Yes")
        
        if self.quantifier:
            lines.append(f"Quantifier: {self.quantifier}")
        
        lines.append(f"Confidence: {self.confidence:.0%}")
        
        return "\n".join(lines)


class SOMAQueryParser:
    """
    SOMA Natural Language Query Parser.
    
    100% RULE-BASED. NO NLP. NO NEURAL NETWORKS.
    
    Parses natural language questions into structured queries
    that can be executed against the knowledge base.
    
    Example:
        parser = SOMAQueryParser()
        
        parsed = parser.parse("What is machine learning?")
        print(parsed.query_type)  # QueryType.DEFINITION
        print(parsed.subject)     # "machine learning"
    """
    
    # Question patterns: (regex, query_type, subject_group, object_group)
    PATTERNS = [
        # Definition patterns
        (r"what\s+(?:is|are)\s+(?:a\s+|an\s+|the\s+)?(.+?)[\?\.]?$", 
         QueryType.DEFINITION, 1, None),
        (r"define\s+(.+?)[\?\.]?$", 
         QueryType.DEFINITION, 1, None),
        (r"(?:tell|explain)\s+(?:me\s+)?(?:about\s+)?(.+?)[\?\.]?$", 
         QueryType.DEFINITION, 1, None),
        
        # Relation patterns
        (r"how\s+(?:is|are)\s+(.+?)\s+related\s+to\s+(.+?)[\?\.]?$", 
         QueryType.RELATION, 1, 2),
        (r"what\s+(?:is\s+)?(?:the\s+)?relation(?:ship)?\s+between\s+(.+?)\s+and\s+(.+?)[\?\.]?$", 
         QueryType.RELATION, 1, 2),
        (r"(?:is|are)\s+(.+?)\s+(?:connected|linked|related)\s+to\s+(.+?)[\?\.]?$", 
         QueryType.RELATION, 1, 2),
        
        # List patterns
        (r"what\s+are\s+(?:the\s+)?(?:parts|components|elements)\s+of\s+(.+?)[\?\.]?$", 
         QueryType.LIST, 1, None),
        (r"list\s+(?:all\s+)?(?:the\s+)?(.+?)[\?\.]?$", 
         QueryType.LIST, 1, None),
        (r"(?:name|give)\s+(?:me\s+)?(?:all\s+)?(?:the\s+)?(.+?)[\?\.]?$", 
         QueryType.LIST, 1, None),
        (r"what\s+(?:does|do)\s+(.+?)\s+(?:contain|include|have)[\?\.]?$", 
         QueryType.LIST, 1, None),
        
        # Boolean patterns
        (r"(?:is|are)\s+(.+?)\s+(?:a|an)\s+(.+?)[\?\.]?$", 
         QueryType.BOOLEAN, 1, 2),
        (r"(?:does|do)\s+(.+?)\s+(.+?)[\?\.]?$", 
         QueryType.BOOLEAN, 1, 2),
        (r"(?:can|could)\s+(.+?)\s+(.+?)[\?\.]?$", 
         QueryType.BOOLEAN, 1, 2),
        
        # Comparison patterns
        (r"what\s+(?:is\s+)?(?:the\s+)?difference\s+between\s+(.+?)\s+and\s+(.+?)[\?\.]?$", 
         QueryType.COMPARISON, 1, 2),
        (r"(?:compare|contrast)\s+(.+?)\s+(?:and|with|to)\s+(.+?)[\?\.]?$", 
         QueryType.COMPARISON, 1, 2),
        (r"how\s+(?:is|are)\s+(.+?)\s+different\s+from\s+(.+?)[\?\.]?$", 
         QueryType.COMPARISON, 1, 2),
        
        # Process patterns
        (r"how\s+(?:does|do)\s+(.+?)\s+work[\?\.]?$", 
         QueryType.PROCESS, 1, None),
        (r"how\s+(?:does|do)\s+(.+?)\s+(.+?)[\?\.]?$", 
         QueryType.PROCESS, 1, 2),
        (r"(?:explain|describe)\s+how\s+(.+?)[\?\.]?$", 
         QueryType.PROCESS, 1, None),
        
        # Count patterns
        (r"how\s+many\s+(.+?)[\?\.]?$", 
         QueryType.COUNT, 1, None),
        (r"(?:count|number\s+of)\s+(.+?)[\?\.]?$", 
         QueryType.COUNT, 1, None),
        
        # Cause patterns
        (r"why\s+(?:does|do|is|are)\s+(.+?)[\?\.]?$", 
         QueryType.CAUSE, 1, None),
        (r"what\s+(?:causes|caused)\s+(.+?)[\?\.]?$", 
         QueryType.CAUSE, 1, None),
        
        # Example patterns
        (r"(?:give|show)\s+(?:me\s+)?(?:an?\s+)?example(?:s)?\s+of\s+(.+?)[\?\.]?$", 
         QueryType.EXAMPLE, 1, None),
        (r"what\s+(?:is|are)\s+(?:an?\s+)?example(?:s)?\s+of\s+(.+?)[\?\.]?$", 
         QueryType.EXAMPLE, 1, None),
    ]
    
    # Negation words
    NEGATION_WORDS = {"not", "no", "never", "neither", "nor", "none", "isn't", "aren't", "doesn't", "don't"}
    
    # Quantifier words
    QUANTIFIERS = {"all", "some", "any", "every", "each", "most", "few", "many"}
    
    # Noise words to remove
    NOISE_WORDS = {"please", "could", "would", "can", "tell", "me", "i", "want", "to", "know"}
    
    def __init__(self):
        """Initialize SOMA Query Parser."""
        # Compile patterns
        self._compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), qtype, subj_grp, obj_grp)
            for pattern, qtype, subj_grp, obj_grp in self.PATTERNS
        ]
    
    def parse(self, query: str) -> ParsedQuery:
        """
        Parse a natural language query.
        
        Args:
            query: Natural language question
            
        Returns:
            ParsedQuery structure
        """
        # Preprocess
        cleaned = self._preprocess(query)
        
        # Check for negation
        negated = self._check_negation(cleaned)
        
        # Check for quantifier
        quantifier = self._extract_quantifier(cleaned)
        
        # Try pattern matching
        for compiled, qtype, subj_grp, obj_grp in self._compiled_patterns:
            match = compiled.search(cleaned)
            if match:
                subject = self._clean_entity(match.group(subj_grp)) if subj_grp else None
                obj = self._clean_entity(match.group(obj_grp)) if obj_grp else None
                
                # Extract relation hint for relation queries
                relation_hint = None
                if qtype == QueryType.RELATION:
                    relation_hint = self._extract_relation_hint(cleaned)
                
                return ParsedQuery(
                    original=query,
                    query_type=qtype,
                    subject=subject,
                    object=obj,
                    relation_hint=relation_hint,
                    negated=negated,
                    quantifier=quantifier,
                    confidence=0.9,
                )
        
        # Fallback: extract subject using heuristics
        subject = self._extract_subject_fallback(cleaned)
        
        return ParsedQuery(
            original=query,
            query_type=QueryType.UNKNOWN,
            subject=subject,
            negated=negated,
            quantifier=quantifier,
            confidence=0.5,
        )
    
    def _preprocess(self, query: str) -> str:
        """Preprocess query text."""
        # Lowercase
        query = query.lower()
        
        # Remove noise words at start
        words = query.split()
        while words and words[0] in self.NOISE_WORDS:
            words.pop(0)
        
        return " ".join(words)
    
    def _check_negation(self, query: str) -> bool:
        """Check if query contains negation."""
        words = set(query.lower().split())
        return bool(words & self.NEGATION_WORDS)
    
    def _extract_quantifier(self, query: str) -> Optional[str]:
        """Extract quantifier from query."""
        words = query.lower().split()
        for word in words:
            if word in self.QUANTIFIERS:
                return word
        return None
    
    def _clean_entity(self, entity: str) -> str:
        """Clean extracted entity."""
        if not entity:
            return ""
        
        # Remove leading/trailing whitespace and punctuation
        entity = entity.strip().rstrip("?.,!")
        
        # Remove leading articles
        for article in ["the ", "a ", "an "]:
            if entity.lower().startswith(article):
                entity = entity[len(article):]
        
        return entity.strip()
    
    def _extract_relation_hint(self, query: str) -> Optional[str]:
        """Extract relation hint from relation query."""
        # Look for relation keywords
        relation_keywords = {
            "type": "is_a",
            "kind": "is_a",
            "part": "part_of",
            "component": "part_of",
            "cause": "causes",
            "use": "uses",
            "depend": "depends_on",
            "similar": "similar_to",
            "before": "precedes",
            "after": "follows",
        }
        
        query_lower = query.lower()
        for keyword, relation in relation_keywords.items():
            if keyword in query_lower:
                return relation
        
        return None
    
    def _extract_subject_fallback(self, query: str) -> Optional[str]:
        """Extract subject using fallback heuristics."""
        # Remove question words
        question_words = {"what", "how", "why", "when", "where", "who", "which", "is", "are", "does", "do"}
        
        words = query.split()
        significant = [w for w in words if w.lower() not in question_words and len(w) > 2]
        
        if significant:
            # Return longest phrase of significant words
            return " ".join(significant[:3])
        
        return None
    
    def batch_parse(self, queries: List[str]) -> List[ParsedQuery]:
        """Parse multiple queries."""
        return [self.parse(q) for q in queries]
    
    def suggest_reformulation(self, parsed: ParsedQuery) -> List[str]:
        """
        Suggest better query formulations.
        
        Returns list of suggested queries.
        """
        suggestions = []
        
        if parsed.query_type == QueryType.UNKNOWN and parsed.subject:
            # Suggest standard formulations
            suggestions.extend([
                f"What is {parsed.subject}?",
                f"How does {parsed.subject} work?",
                f"What are the parts of {parsed.subject}?",
            ])
        
        elif parsed.query_type == QueryType.DEFINITION and parsed.subject:
            # Suggest related queries
            suggestions.extend([
                f"How does {parsed.subject} work?",
                f"What are examples of {parsed.subject}?",
                f"What are the types of {parsed.subject}?",
            ])
        
        return suggestions
    
    def __repr__(self) -> str:
        return f"SOMAQueryParser(patterns={len(self.PATTERNS)})"

