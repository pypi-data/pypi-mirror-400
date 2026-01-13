"""
RelationExtractor - Extract relationships from text.

Uses pattern matching and heuristics to identify
relationships between concepts in text.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import re

from .graph_edge import RelationType


@dataclass
class ExtractedRelation:
    """
    A relationship extracted from text.
    
    Attributes:
        subject: The source entity/concept
        relation: Type of relationship
        obj: The target entity/concept
        confidence: Extraction confidence (0-1)
        source_text: Original text this was extracted from
    """
    subject: str
    relation: RelationType
    obj: str
    confidence: float = 1.0
    source_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "relation": self.relation.value,
            "object": self.obj,
            "confidence": self.confidence,
            "source_text": self.source_text,
        }


class RelationExtractor:
    """
    Extract relationships from text using pattern matching.
    
    This is a rule-based extractor. For production, consider
    integrating with NER/RE models.
    
    Example:
        extractor = RelationExtractor()
        
        relations = extractor.extract(
            "Transformers are a type of neural network. "
            "They use attention mechanisms."
        )
        
        for rel in relations:
            print(f"{rel.subject} --{rel.relation.value}--> {rel.obj}")
    """
    
    # Pattern templates for each relation type
    # Format: (pattern, subject_group, object_group, confidence)
    PATTERNS = {
        RelationType.IS_A: [
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+(?:a|an)\s+(?:type\s+of\s+)?(\w+(?:\s+\w+)?)", 1, 2, 0.9),
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+(?:kind|form)\s+of\s+(\w+(?:\s+\w+)?)", 1, 2, 0.9),
            (r"(\w+(?:\s+\w+)?),?\s+(?:which|that)\s+(?:is|are)\s+(?:a|an)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.8),
        ],
        RelationType.PART_OF: [
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+(?:a\s+)?part\s+of\s+(\w+(?:\s+\w+)?)", 1, 2, 0.9),
            (r"(\w+(?:\s+\w+)?)\s+(?:belongs?\s+to|within)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.8),
        ],
        RelationType.HAS_PART: [
            (r"(\w+(?:\s+\w+)?)\s+(?:has|have|contains?|includes?)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.8),
            (r"(\w+(?:\s+\w+)?)\s+(?:consists?\s+of|comprises?)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.85),
        ],
        RelationType.CAUSES: [
            (r"(\w+(?:\s+\w+)?)\s+(?:causes?|leads?\s+to|results?\s+in)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.85),
            (r"(\w+(?:\s+\w+)?)\s+(?:triggers?|induces?)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.8),
        ],
        RelationType.CAUSED_BY: [
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+caused\s+by\s+(\w+(?:\s+\w+)?)", 1, 2, 0.85),
            (r"(\w+(?:\s+\w+)?)\s+(?:results?\s+from|due\s+to)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.8),
        ],
        RelationType.USES: [
            (r"(\w+(?:\s+\w+)?)\s+(?:uses?|utilizes?|employs?)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.85),
            (r"(\w+(?:\s+\w+)?)\s+(?:relies?\s+on|depends?\s+on)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.8),
        ],
        RelationType.SIMILAR_TO: [
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+similar\s+to\s+(\w+(?:\s+\w+)?)", 1, 2, 0.9),
            (r"(\w+(?:\s+\w+)?)\s+(?:resembles?|like)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.7),
        ],
        RelationType.OPPOSITE_OF: [
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+(?:the\s+)?opposite\s+of\s+(\w+(?:\s+\w+)?)", 1, 2, 0.9),
            (r"(\w+(?:\s+\w+)?)\s+(?:contrasts?\s+with|differs?\s+from)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.7),
        ],
        RelationType.PRECEDES: [
            (r"(\w+(?:\s+\w+)?)\s+(?:comes?\s+before|precedes?)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.9),
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+followed\s+by\s+(\w+(?:\s+\w+)?)", 1, 2, 0.85),
        ],
        RelationType.FOLLOWS: [
            (r"(\w+(?:\s+\w+)?)\s+(?:comes?\s+after|follows?)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.9),
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+preceded\s+by\s+(\w+(?:\s+\w+)?)", 2, 1, 0.85),
        ],
        RelationType.DERIVED_FROM: [
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+derived\s+from\s+(\w+(?:\s+\w+)?)", 1, 2, 0.9),
            (r"(\w+(?:\s+\w+)?)\s+(?:comes?\s+from|originates?\s+from)\s+(\w+(?:\s+\w+)?)", 1, 2, 0.8),
        ],
        RelationType.RELATED_TO: [
            (r"(\w+(?:\s+\w+)?)\s+(?:is|are)\s+related\s+to\s+(\w+(?:\s+\w+)?)", 1, 2, 0.8),
            (r"(\w+(?:\s+\w+)?)\s+(?:and|with)\s+(\w+(?:\s+\w+)?)\s+(?:are\s+)?related", 1, 2, 0.7),
        ],
    }
    
    # Stop words to filter out
    STOP_WORDS = {
        "a", "an", "the", "this", "that", "these", "those",
        "it", "its", "they", "their", "them",
        "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might",
        "very", "also", "just", "even", "only", "more",
    }
    
    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize RelationExtractor.
        
        Args:
            min_confidence: Minimum confidence for extracted relations
        """
        self.min_confidence = min_confidence
        
        # Compile patterns
        self._compiled_patterns: Dict[RelationType, List[Tuple]] = {}
        for rel_type, patterns in self.PATTERNS.items():
            self._compiled_patterns[rel_type] = [
                (re.compile(pattern, re.IGNORECASE), subj, obj, conf)
                for pattern, subj, obj, conf in patterns
            ]
    
    def extract(
        self,
        text: str,
        relation_types: Optional[List[RelationType]] = None
    ) -> List[ExtractedRelation]:
        """
        Extract relationships from text.
        
        Args:
            text: Text to extract from
            relation_types: Types to extract (None = all)
            
        Returns:
            List of ExtractedRelation objects
        """
        relations = []
        
        # Determine which relation types to check
        types_to_check = relation_types or list(self._compiled_patterns.keys())
        
        for rel_type in types_to_check:
            if rel_type not in self._compiled_patterns:
                continue
            
            for pattern, subj_group, obj_group, base_conf in self._compiled_patterns[rel_type]:
                for match in pattern.finditer(text):
                    subject = self._clean_entity(match.group(subj_group))
                    obj = self._clean_entity(match.group(obj_group))
                    
                    # Skip if entities are too short or are stop words
                    if not subject or not obj:
                        continue
                    if subject.lower() in self.STOP_WORDS:
                        continue
                    if obj.lower() in self.STOP_WORDS:
                        continue
                    if subject.lower() == obj.lower():
                        continue
                    
                    # Calculate confidence
                    confidence = base_conf * self._calculate_confidence_modifier(
                        subject, obj, match.group(0)
                    )
                    
                    if confidence >= self.min_confidence:
                        relations.append(ExtractedRelation(
                            subject=subject,
                            relation=rel_type,
                            obj=obj,
                            confidence=confidence,
                            source_text=match.group(0)
                        ))
        
        # Remove duplicates
        return self._deduplicate(relations)
    
    def _clean_entity(self, entity: str) -> str:
        """Clean and normalize an entity string."""
        if not entity:
            return ""
        
        # Remove leading/trailing whitespace
        entity = entity.strip()
        
        # Remove common determiners at start
        for det in ["a ", "an ", "the "]:
            if entity.lower().startswith(det):
                entity = entity[len(det):]
        
        return entity.strip()
    
    def _calculate_confidence_modifier(
        self,
        subject: str,
        obj: str,
        matched_text: str
    ) -> float:
        """Calculate confidence modifier based on match quality."""
        modifier = 1.0
        
        # Longer entities are more specific
        if len(subject) < 3 or len(obj) < 3:
            modifier *= 0.8
        
        # Multi-word entities are more specific
        if " " in subject or " " in obj:
            modifier *= 1.1
        
        # Cap modifier
        return min(1.0, modifier)
    
    def _deduplicate(
        self,
        relations: List[ExtractedRelation]
    ) -> List[ExtractedRelation]:
        """Remove duplicate relations, keeping highest confidence."""
        seen = {}
        
        for rel in relations:
            key = (rel.subject.lower(), rel.relation, rel.obj.lower())
            
            if key not in seen or rel.confidence > seen[key].confidence:
                seen[key] = rel
        
        return list(seen.values())
    
    def extract_entities(self, text: str) -> List[str]:
        """
        Extract potential entities from text.
        
        Simple implementation using capitalization and noun patterns.
        """
        entities = []
        
        # Find capitalized phrases (potential proper nouns)
        cap_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        for match in re.finditer(cap_pattern, text):
            entity = match.group(0)
            if entity.lower() not in self.STOP_WORDS:
                entities.append(entity)
        
        # Find quoted terms
        quote_pattern = r'"([^"]+)"|\'([^\']+)\''
        for match in re.finditer(quote_pattern, text):
            entity = match.group(1) or match.group(2)
            if entity:
                entities.append(entity)
        
        return list(set(entities))
    
    def suggest_relations(
        self,
        entity1: str,
        entity2: str,
        context: Optional[str] = None
    ) -> List[Tuple[RelationType, float]]:
        """
        Suggest possible relations between two entities.
        
        Args:
            entity1: First entity
            entity2: Second entity
            context: Optional context text
            
        Returns:
            List of (RelationType, confidence) tuples
        """
        suggestions = []
        
        # If we have context, try to extract
        if context:
            relations = self.extract(context)
            for rel in relations:
                if (rel.subject.lower() == entity1.lower() and
                    rel.obj.lower() == entity2.lower()):
                    suggestions.append((rel.relation, rel.confidence))
        
        # Default suggestions based on entity types
        if not suggestions:
            # Generic suggestions
            suggestions = [
                (RelationType.RELATED_TO, 0.5),
                (RelationType.IS_A, 0.3),
                (RelationType.PART_OF, 0.3),
            ]
        
        return suggestions
    
    def __repr__(self) -> str:
        return f"RelationExtractor(min_confidence={self.min_confidence})"

