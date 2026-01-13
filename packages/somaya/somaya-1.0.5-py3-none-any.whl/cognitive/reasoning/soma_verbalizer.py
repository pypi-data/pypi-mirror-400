"""
SOMA Verbalizer - Pure SOMA text generation from structured knowledge.

NO GPT. NO TRANSFORMERS. NO NEURAL NETWORKS.

This uses SOMA's own:
- Token patterns
- Co-occurrence learning
- Template-based generation
- Symbolic reasoning

The Verbalizer turns structured context into natural language
using ONLY SOMA-native algorithms.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import re

from ..graph import GraphStore, GraphNode, RelationType
from ..memory import UnifiedMemory, MemoryObject


@dataclass
class VerbalizationResult:
    """Result from soma verbalization."""
    text: str
    confidence: float
    sources: List[str]
    template_used: str
    reasoning_depth: int


class SOMAVerbalizer:
    """
    SOMA-native text generation from structured knowledge.
    
    NO external dependencies. NO neural networks.
    Uses pure symbolic + template-based generation.
    
    Algorithms:
    - Template matching
    - Pattern composition
    - Confidence-weighted selection
    - SOMA token reconstruction
    
    Example:
        verbalizer = SOMAVerbalizer(memory)
        
        result = verbalizer.verbalize(context)
        print(result.text)
    """
    
    # SOMA-native templates for different question types
    TEMPLATES = {
        # Definition questions
        "what_is": [
            "{subject} is {definition}.",
            "Based on the knowledge base, {subject} can be described as {definition}.",
            "{subject} refers to {definition}.",
        ],
        
        # Relationship questions
        "how_related": [
            "{subject} is {relation} {object}.",
            "The relationship between {subject} and {object} is: {subject} {relation} {object}.",
            "{subject} and {object} are connected: {subject} {relation} {object}.",
        ],
        
        # Process questions
        "how_works": [
            "{subject} works by {mechanism}.",
            "The process involves: {steps}.",
            "{subject} operates through {mechanism}.",
        ],
        
        # Comparison questions
        "difference": [
            "The key difference: {subject} {diff1}, while {object} {diff2}.",
            "{subject} differs from {object} in that {explanation}.",
        ],
        
        # Yes/No questions
        "yes_no": [
            "Yes, {explanation}.",
            "No, {explanation}.",
            "Based on the knowledge: {explanation}.",
        ],
        
        # List questions
        "list": [
            "The following are relevant: {items}.",
            "Key items include: {items}.",
        ],
        
        # Explanation questions
        "explain": [
            "{topic} can be explained as follows: {explanation}.",
            "To understand {topic}: {explanation}.",
        ],
        
        # Unknown
        "unknown": [
            "The knowledge base does not contain sufficient information about {query}.",
            "Unable to find relevant information for: {query}.",
        ],
    }
    
    # Relation verbalizations
    RELATION_PHRASES = {
        RelationType.IS_A: "is a type of",
        RelationType.PART_OF: "is part of",
        RelationType.HAS_PART: "contains",
        RelationType.CAUSES: "causes",
        RelationType.CAUSED_BY: "is caused by",
        RelationType.RELATED_TO: "is related to",
        RelationType.SIMILAR_TO: "is similar to",
        RelationType.OPPOSITE_OF: "is opposite to",
        RelationType.PRECEDES: "comes before",
        RelationType.FOLLOWS: "comes after",
        RelationType.DERIVED_FROM: "is derived from",
        RelationType.USES: "uses",
        RelationType.USED_BY: "is used by",
        RelationType.CONTAINS: "contains",
        RelationType.DEPENDS_ON: "depends on",
    }
    
    def __init__(self, memory: UnifiedMemory):
        """
        Initialize SOMA Verbalizer.
        
        Args:
            memory: UnifiedMemory instance
        """
        self.memory = memory
        
        # Pattern learning (co-occurrence based, NOT neural)
        self._phrase_patterns: Dict[str, List[str]] = defaultdict(list)
        self._learned_templates: List[str] = []
    
    def verbalize(
        self,
        context: Any,  # StructuredContext
        query: Optional[str] = None
    ) -> VerbalizationResult:
        """
        Generate natural language from structured context.
        
        Uses SOMA-native algorithms:
        1. Classify query type
        2. Extract key information
        3. Select best template
        4. Fill template with facts
        5. Polish output
        
        Args:
            context: StructuredContext from reasoning
            query: Optional query override
            
        Returns:
            VerbalizationResult
        """
        query = query or getattr(context, 'query', '')
        
        # 1. Classify query type
        query_type = self._classify_query(query)
        
        # 2. Extract key information from context
        key_info = self._extract_key_info(context)
        
        # 3. Select best template
        template = self._select_template(query_type, key_info)
        
        # 4. Fill template
        filled = self._fill_template(template, key_info, query)
        
        # 5. Polish
        polished = self._polish_output(filled)
        
        # Calculate confidence
        confidence = self._calculate_confidence(context, key_info)
        
        return VerbalizationResult(
            text=polished,
            confidence=confidence,
            sources=[f.get('content', '')[:50] for f in getattr(context, 'relevant_facts', [])],
            template_used=query_type,
            reasoning_depth=len(getattr(context, 'inferences', []))
        )
    
    def _classify_query(self, query: str) -> str:
        """Classify query type using pattern matching."""
        query_lower = query.lower()
        
        # Pattern-based classification (NO ML)
        if query_lower.startswith(("what is", "what are", "define")):
            return "what_is"
        
        if query_lower.startswith(("how does", "how do", "how is")):
            if "work" in query_lower:
                return "how_works"
            return "explain"
        
        if query_lower.startswith(("is ", "are ", "does ", "do ", "can ")):
            return "yes_no"
        
        if "difference" in query_lower or "different" in query_lower:
            return "difference"
        
        if "relation" in query_lower or "related" in query_lower or "between" in query_lower:
            return "how_related"
        
        if query_lower.startswith(("list", "what are the", "name")):
            return "list"
        
        if query_lower.startswith(("explain", "describe", "tell")):
            return "explain"
        
        return "explain"  # Default
    
    def _extract_key_info(self, context: Any) -> Dict[str, Any]:
        """Extract key information from context."""
        info = {
            "subjects": [],
            "objects": [],
            "relations": [],
            "facts": [],
            "inferences": [],
        }
        
        # Extract from facts
        for fact in getattr(context, 'relevant_facts', []):
            content = fact.get('content', '')
            info["facts"].append(content)
            
            # Extract subjects (first significant word)
            words = content.split()
            if words:
                info["subjects"].append(words[0])
        
        # Extract from inferences
        for inf in getattr(context, 'inferences', []):
            source = inf.get('source', '')
            target = inf.get('target', '')
            relation = inf.get('relation', '')
            
            info["subjects"].append(source)
            info["objects"].append(target)
            info["relations"].append((source, relation, target))
            info["inferences"].append(f"{source} {relation} {target}")
        
        # Extract from hierarchy
        hierarchy = getattr(context, 'hierarchy', None)
        if hierarchy:
            path = hierarchy.get('path', [])
            if path:
                info["subjects"].extend(path)
        
        return info
    
    def _select_template(self, query_type: str, key_info: Dict) -> str:
        """Select best template based on available information."""
        templates = self.TEMPLATES.get(query_type, self.TEMPLATES["unknown"])
        
        # If we have no facts, use unknown
        if not key_info["facts"] and not key_info["inferences"]:
            templates = self.TEMPLATES["unknown"]
        
        # Select first matching template (could be improved with scoring)
        return templates[0]
    
    def _fill_template(
        self,
        template: str,
        key_info: Dict,
        query: str
    ) -> str:
        """Fill template with extracted information."""
        # Extract subject from query
        subject = self._extract_subject_from_query(query)
        
        # Build definition/explanation from facts
        definition = ""
        if key_info["facts"]:
            definition = key_info["facts"][0]
        elif key_info["inferences"]:
            definition = key_info["inferences"][0]
        
        # Build mechanism from relations
        mechanism = ""
        if key_info["relations"]:
            src, rel, tgt = key_info["relations"][0]
            rel_phrase = self.RELATION_PHRASES.get(
                RelationType(rel) if isinstance(rel, str) else rel,
                rel
            )
            mechanism = f"{src} {rel_phrase} {tgt}"
        
        # Build items list
        items = ", ".join(key_info["subjects"][:5]) if key_info["subjects"] else "none found"
        
        # Build steps
        steps = "; ".join(key_info["inferences"][:3]) if key_info["inferences"] else "unknown"
        
        # Fill template
        filled = template.format(
            subject=subject or "this",
            definition=definition or "not found in knowledge base",
            relation=mechanism,
            object=key_info["objects"][0] if key_info["objects"] else "unknown",
            mechanism=mechanism or definition,
            steps=steps,
            items=items,
            topic=subject,
            explanation=definition or mechanism,
            query=query,
            diff1="has certain properties",
            diff2="has different properties",
        )
        
        return filled
    
    def _extract_subject_from_query(self, query: str) -> str:
        """Extract main subject from query."""
        # Remove question words
        cleaned = query.lower()
        for word in ["what", "how", "is", "are", "does", "do", "the", "a", "an", "?"]:
            cleaned = cleaned.replace(word, "")
        
        # Get first remaining significant word
        words = [w.strip() for w in cleaned.split() if w.strip()]
        return words[0] if words else "this"
    
    def _polish_output(self, text: str) -> str:
        """Polish the generated text."""
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Ensure ends with period
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Remove double spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove repeated punctuation
        text = re.sub(r'\.+', '.', text)
        
        return text.strip()
    
    def _calculate_confidence(self, context: Any, key_info: Dict) -> float:
        """Calculate confidence based on available evidence."""
        confidence = 0.5  # Base
        
        # More facts = more confidence
        fact_count = len(key_info["facts"])
        confidence += min(0.2, fact_count * 0.05)
        
        # More inferences = more confidence
        inf_count = len(key_info["inferences"])
        confidence += min(0.15, inf_count * 0.05)
        
        # Context confidence
        ctx_conf = getattr(context, 'confidence', 0.5)
        confidence = (confidence + ctx_conf) / 2
        
        # Penalty for contradictions
        cont_count = len(getattr(context, 'contradictions', []))
        confidence -= cont_count * 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def learn_pattern(self, text: str, category: str) -> None:
        """
        Learn a new pattern from example text.
        
        This uses co-occurrence analysis, NOT neural learning.
        """
        # Extract pattern (simplified)
        words = text.split()
        if len(words) >= 3:
            pattern = f"{{subject}} {' '.join(words[1:-1])} {{object}}"
            self._learned_templates.append(pattern)
            self._phrase_patterns[category].append(pattern)
    
    def __repr__(self) -> str:
        return f"SOMAVerbalizer(templates={len(self.TEMPLATES)}, learned={len(self._learned_templates)})"

