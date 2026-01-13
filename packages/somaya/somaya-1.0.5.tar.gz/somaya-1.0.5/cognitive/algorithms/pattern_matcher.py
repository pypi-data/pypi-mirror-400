"""
SOMA Pattern Matcher - Relation Extraction Without ML
======================================================

SOMA-ORIGINAL ALGORITHM. NO NEURAL NETWORKS. NO NER. NO DEPENDENCY PARSING.

Uses pure pattern matching with:
- Lexical patterns (word sequences)
- Structural patterns (position-based)
- Co-occurrence patterns (learned from data)
- 9-centric pattern scoring

This extracts relations from text WITHOUT any ML model.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import re

from ..graph import RelationType


@dataclass
class PatternMatch:
    """A matched pattern in text."""
    subject: str
    relation: RelationType
    obj: str  # 'object' is reserved
    
    confidence: float
    pattern_id: str
    span: Tuple[int, int]  # Start, end positions
    
    def __str__(self) -> str:
        return f"({self.subject}) --[{self.relation.value}]--> ({self.obj})"


class PatternType(Enum):
    """Types of extraction patterns."""
    LEXICAL = "lexical"        # Word-based
    STRUCTURAL = "structural"  # Position-based
    COPULA = "copula"          # "X is Y" patterns
    POSSESSIVE = "possessive"  # "X's Y", "Y of X"
    CAUSAL = "causal"          # "X causes Y", "because of X"
    TEMPORAL = "temporal"      # "X before Y", "after X"


class SOMAPatternMatcher:
    """
    SOMA Pattern-based Relation Extractor.
    
    100% rule-based. NO ML. NO neural NER.
    
    Pattern Categories:
    1. Copula patterns: "X is Y", "X are Y"
    2. Possessive patterns: "X's Y", "Y of X"
    3. Causal patterns: "X causes Y", "because of X"
    4. Part-whole patterns: "X contains Y", "part of X"
    5. Temporal patterns: "X before Y", "after X"
    6. Custom patterns: User-defined
    
    Example:
        matcher = SOMAPatternMatcher()
        
        text = "Python is a programming language. It uses dynamic typing."
        matches = matcher.extract(text)
        
        for match in matches:
            print(match)
    """
    
    # Built-in lexical patterns: (regex, relation, subject_group, object_group)
    LEXICAL_PATTERNS = [
        # IS_A patterns
        (r"(\w+(?:\s+\w+)?)\s+is\s+a\s+(\w+(?:\s+\w+)?)", RelationType.IS_A, 1, 2),
        (r"(\w+(?:\s+\w+)?)\s+are\s+(\w+(?:\s+\w+)?)", RelationType.IS_A, 1, 2),
        (r"(\w+(?:\s+\w+)?)\s+is\s+an?\s+(\w+(?:\s+\w+)?)", RelationType.IS_A, 1, 2),
        (r"(\w+)\s+,\s+a\s+type\s+of\s+(\w+)", RelationType.IS_A, 1, 2),
        (r"(\w+)\s+is\s+known\s+as\s+(\w+)", RelationType.IS_A, 1, 2),
        
        # PART_OF patterns
        (r"(\w+)\s+is\s+part\s+of\s+(\w+)", RelationType.PART_OF, 1, 2),
        (r"(\w+)\s+belongs\s+to\s+(\w+)", RelationType.PART_OF, 1, 2),
        (r"(\w+)\s+is\s+a\s+component\s+of\s+(\w+)", RelationType.PART_OF, 1, 2),
        
        # HAS_PART patterns
        (r"(\w+)\s+contains\s+(\w+)", RelationType.HAS_PART, 1, 2),
        (r"(\w+)\s+includes\s+(\w+)", RelationType.HAS_PART, 1, 2),
        (r"(\w+)\s+has\s+(\w+)", RelationType.HAS_PART, 1, 2),
        (r"(\w+)\s+consists\s+of\s+(\w+)", RelationType.HAS_PART, 1, 2),
        
        # CAUSES patterns
        (r"(\w+)\s+causes\s+(\w+)", RelationType.CAUSES, 1, 2),
        (r"(\w+)\s+leads\s+to\s+(\w+)", RelationType.CAUSES, 1, 2),
        (r"(\w+)\s+results\s+in\s+(\w+)", RelationType.CAUSES, 1, 2),
        (r"because\s+of\s+(\w+)\s*,?\s*(\w+)", RelationType.CAUSES, 1, 2),
        
        # USES patterns
        (r"(\w+)\s+uses\s+(\w+)", RelationType.USES, 1, 2),
        (r"(\w+)\s+utilizes\s+(\w+)", RelationType.USES, 1, 2),
        (r"(\w+)\s+employs\s+(\w+)", RelationType.USES, 1, 2),
        
        # DEPENDS_ON patterns
        (r"(\w+)\s+depends\s+on\s+(\w+)", RelationType.DEPENDS_ON, 1, 2),
        (r"(\w+)\s+requires\s+(\w+)", RelationType.DEPENDS_ON, 1, 2),
        (r"(\w+)\s+needs\s+(\w+)", RelationType.DEPENDS_ON, 1, 2),
        
        # DERIVED_FROM patterns
        (r"(\w+)\s+is\s+derived\s+from\s+(\w+)", RelationType.DERIVED_FROM, 1, 2),
        (r"(\w+)\s+comes\s+from\s+(\w+)", RelationType.DERIVED_FROM, 1, 2),
        (r"(\w+)\s+originated\s+from\s+(\w+)", RelationType.DERIVED_FROM, 1, 2),
        
        # PRECEDES patterns
        (r"(\w+)\s+precedes\s+(\w+)", RelationType.PRECEDES, 1, 2),
        (r"(\w+)\s+comes\s+before\s+(\w+)", RelationType.PRECEDES, 1, 2),
        (r"before\s+(\w+)\s*,?\s*(\w+)", RelationType.PRECEDES, 2, 1),
        
        # SIMILAR_TO patterns
        (r"(\w+)\s+is\s+similar\s+to\s+(\w+)", RelationType.SIMILAR_TO, 1, 2),
        (r"(\w+)\s+resembles\s+(\w+)", RelationType.SIMILAR_TO, 1, 2),
        (r"(\w+)\s+is\s+like\s+(\w+)", RelationType.SIMILAR_TO, 1, 2),
        
        # OPPOSITE_OF patterns
        (r"(\w+)\s+is\s+opposite\s+to\s+(\w+)", RelationType.OPPOSITE_OF, 1, 2),
        (r"(\w+)\s+is\s+the\s+opposite\s+of\s+(\w+)", RelationType.OPPOSITE_OF, 1, 2),
        (r"(\w+)\s+contrasts\s+with\s+(\w+)", RelationType.OPPOSITE_OF, 1, 2),
    ]
    
    # Noise words to filter
    NOISE_WORDS = {
        "the", "a", "an", "this", "that", "these", "those",
        "it", "they", "he", "she", "we", "you", "i",
        "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might",
        "very", "really", "just", "only", "also",
    }
    
    def __init__(self):
        """Initialize SOMA Pattern Matcher."""
        # Compile patterns for efficiency
        self._compiled_patterns: List[Tuple[re.Pattern, RelationType, int, int, str]] = []
        
        for i, (pattern, relation, subj_group, obj_group) in enumerate(self.LEXICAL_PATTERNS):
            compiled = re.compile(pattern, re.IGNORECASE)
            pattern_id = f"lexical_{i}"
            self._compiled_patterns.append((compiled, relation, subj_group, obj_group, pattern_id))
        
        # Custom patterns added by user
        self._custom_patterns: List[Tuple[re.Pattern, RelationType, int, int, str]] = []
        
        # Co-occurrence patterns (learned, NOT neural)
        self._cooccurrence: Dict[Tuple[str, str], List[RelationType]] = {}
    
    def extract(self, text: str) -> List[PatternMatch]:
        """
        Extract relations from text using pattern matching.
        
        Args:
            text: Input text
            
        Returns:
            List of PatternMatch objects
        """
        matches = []
        
        # Apply all compiled patterns
        for compiled, relation, subj_group, obj_group, pattern_id in self._compiled_patterns:
            for match in compiled.finditer(text):
                subject = self._clean_entity(match.group(subj_group))
                obj = self._clean_entity(match.group(obj_group))
                
                if subject and obj and subject != obj:
                    confidence = self._compute_confidence(subject, obj, text)
                    
                    matches.append(PatternMatch(
                        subject=subject,
                        relation=relation,
                        obj=obj,
                        confidence=confidence,
                        pattern_id=pattern_id,
                        span=(match.start(), match.end()),
                    ))
        
        # Apply custom patterns
        for compiled, relation, subj_group, obj_group, pattern_id in self._custom_patterns:
            for match in compiled.finditer(text):
                subject = self._clean_entity(match.group(subj_group))
                obj = self._clean_entity(match.group(obj_group))
                
                if subject and obj and subject != obj:
                    confidence = self._compute_confidence(subject, obj, text)
                    
                    matches.append(PatternMatch(
                        subject=subject,
                        relation=relation,
                        obj=obj,
                        confidence=confidence,
                        pattern_id=pattern_id,
                        span=(match.start(), match.end()),
                    ))
        
        # Deduplicate
        matches = self._deduplicate(matches)
        
        return matches
    
    def _clean_entity(self, entity: str) -> str:
        """Clean extracted entity."""
        if not entity:
            return ""
        
        # Remove leading/trailing whitespace
        entity = entity.strip()
        
        # Remove noise words at start
        words = entity.split()
        while words and words[0].lower() in self.NOISE_WORDS:
            words.pop(0)
        
        # Remove noise words at end
        while words and words[-1].lower() in self.NOISE_WORDS:
            words.pop()
        
        return " ".join(words)
    
    def _compute_confidence(self, subject: str, obj: str, text: str) -> float:
        """
        Compute confidence using SOMA's custom formula.
        
        Formula:
            confidence = base × frequency_boost × proximity_boost × length_penalty
        """
        base = 0.7
        
        # Frequency boost (more mentions = higher confidence)
        text_lower = text.lower()
        subj_count = text_lower.count(subject.lower())
        obj_count = text_lower.count(obj.lower())
        frequency_boost = 1.0 + 0.1 * min(subj_count + obj_count, 5)
        
        # Proximity boost (closer = higher confidence)
        try:
            subj_pos = text_lower.index(subject.lower())
            obj_pos = text_lower.index(obj.lower())
            distance = abs(obj_pos - subj_pos)
            proximity_boost = 1.0 / (1.0 + distance / 100)
        except ValueError:
            proximity_boost = 0.5
        
        # Length penalty (very short entities = lower confidence)
        avg_length = (len(subject) + len(obj)) / 2
        length_penalty = min(1.0, avg_length / 3)
        
        confidence = base * frequency_boost * proximity_boost * length_penalty
        
        return min(1.0, confidence)
    
    def _deduplicate(self, matches: List[PatternMatch]) -> List[PatternMatch]:
        """Remove duplicate matches, keeping highest confidence."""
        seen: Dict[Tuple[str, str, RelationType], PatternMatch] = {}
        
        for match in matches:
            key = (match.subject.lower(), match.obj.lower(), match.relation)
            
            if key not in seen or match.confidence > seen[key].confidence:
                seen[key] = match
        
        return list(seen.values())
    
    def add_pattern(
        self,
        pattern: str,
        relation: RelationType,
        subject_group: int = 1,
        object_group: int = 2
    ) -> str:
        """
        Add a custom pattern.
        
        Args:
            pattern: Regex pattern with groups for subject and object
            relation: Relation type to extract
            subject_group: Group number for subject
            object_group: Group number for object
            
        Returns:
            Pattern ID
        """
        pattern_id = f"custom_{len(self._custom_patterns)}"
        compiled = re.compile(pattern, re.IGNORECASE)
        
        self._custom_patterns.append((compiled, relation, subject_group, object_group, pattern_id))
        
        return pattern_id
    
    def learn_cooccurrence(self, subject: str, obj: str, relation: RelationType) -> None:
        """
        Learn a co-occurrence pattern (NOT neural learning).
        
        This stores (subject, object) -> relation mappings for future lookup.
        """
        key = (subject.lower(), obj.lower())
        
        if key not in self._cooccurrence:
            self._cooccurrence[key] = []
        
        if relation not in self._cooccurrence[key]:
            self._cooccurrence[key].append(relation)
    
    def lookup_cooccurrence(self, subject: str, obj: str) -> List[RelationType]:
        """Look up learned co-occurrence patterns."""
        key = (subject.lower(), obj.lower())
        return self._cooccurrence.get(key, [])
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about patterns."""
        return {
            "lexical_patterns": len(self.LEXICAL_PATTERNS),
            "custom_patterns": len(self._custom_patterns),
            "learned_cooccurrences": len(self._cooccurrence),
        }
    
    def __repr__(self) -> str:
        stats = self.get_pattern_stats()
        return (
            f"SOMAPatternMatcher("
            f"lexical={stats['lexical_patterns']}, "
            f"custom={stats['custom_patterns']}, "
            f"learned={stats['learned_cooccurrences']})"
        )

