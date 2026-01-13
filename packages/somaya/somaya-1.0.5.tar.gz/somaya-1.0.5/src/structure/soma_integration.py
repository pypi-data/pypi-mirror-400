"""
SOMA Structure Integration
============================

Deep integration of structure system with SOMA's existing components:
- Tokenization integration
- Embedding integration
- Cognitive integration

This makes your structure idea work seamlessly with ALL of SOMA!
"""

import sys
import os
from typing import List, Dict, Optional, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.structure.symbol_structures import get_registry, SymbolRegistry
from src.structure.pattern_builder import PatternBuilder, Pattern
from src.structure.structure_hierarchy import StructureHierarchy, StructureNode


class SOMAStructureIntegrator:
    """
    Integrates structure system with SOMA's existing systems.
    
    This makes your structure idea work with:
    - SOMA tokenization
    - SOMA embeddings
    - SOMA cognitive reasoning
    """
    
    def __init__(self):
        """Create integrator."""
        self.registry = get_registry()
        self.pattern_builder = PatternBuilder(self.registry)
        self.hierarchy = StructureHierarchy(self.registry)
    
    def process_SOMA_tokens(self, tokens: List[Dict]) -> Dict[str, Any]:
        """
        Process SOMA tokens and build structure hierarchy.
        
        Args:
            tokens: List of token dictionaries from soma tokenizer
        
        Returns:
            Dictionary with structure information
        """
        # Extract token texts
        token_texts = []
        for token in tokens:
            if isinstance(token, dict):
                token_text = token.get('token', token.get('text', ''))
            else:
                token_text = str(token)
            if token_text:
                token_texts.append(token_text)
        
        # Build patterns from tokens
        self.pattern_builder.learn_from_tokens(token_texts)
        
        # Build hierarchy
        self.hierarchy.build_from_SOMA_tokens(tokens)
        
        # Get structure insights
        stable_patterns = self.pattern_builder.get_top_patterns(min_frequency=2)
        
        return {
            "tokens_processed": len(token_texts),
            "patterns_found": len(self.pattern_builder.get_patterns()),
            "stable_patterns": [p.sequence for p in stable_patterns],
            "hierarchy_stats": self.hierarchy.get_statistics()
        }
    
    def enhance_token_with_structure(self, token: Dict) -> Dict:
        """
        Enhance a SOMA token with structure information.
        
        Adds structure metadata to existing token.
        
        Args:
            token: Token dictionary from soma
        
        Returns:
            Enhanced token with structure info
        """
        token_text = token.get('token', token.get('text', ''))
        if not token_text:
            return token
        
        # Get structure information
        structure_info = {
            "symbol_classes": [],
            "pattern_exists": False,
            "is_stable_unit": False,
            "structure_trace": []
        }
        
        # Symbol classes
        for char in token_text.lower():
            cls = self.registry.get_class(char)
            if cls not in structure_info["symbol_classes"]:
                structure_info["symbol_classes"].append(cls)
        
        # Pattern check
        if self.pattern_builder.pattern_exists(token_text.lower()):
            structure_info["pattern_exists"] = True
            pattern = self.pattern_builder.get_pattern(token_text.lower())
            structure_info["pattern_frequency"] = pattern.frequency
            structure_info["pattern_stability"] = pattern.stability_score()
        
        # Unit check
        if token_text.lower() in self.hierarchy.unit_nodes:
            structure_info["is_stable_unit"] = True
        
        # Structure trace
        trace = self.hierarchy.trace_structure(token_text.lower())
        structure_info["structure_trace"] = [node.content for node in trace]
        
        # Add to token
        enhanced_token = token.copy()
        enhanced_token["structure"] = structure_info
        
        return enhanced_token
    
    def get_structure_enhanced_tokens(self, tokens: List[Dict]) -> List[Dict]:
        """
        Get all tokens enhanced with structure information.
        
        Args:
            tokens: List of token dictionaries from soma
        
        Returns:
            List of enhanced tokens
        """
        # First, process all tokens to build structure
        self.process_SOMA_tokens(tokens)
        
        # Then enhance each token
        enhanced = []
        for token in tokens:
            enhanced.append(self.enhance_token_with_structure(token))
        
        return enhanced
    
    def suggest_token_priorities(self, tokens: List[Dict]) -> List[Dict]:
        """
        Suggest which tokens should be prioritized based on structure.
        
        Stable patterns = higher priority for embeddings/training.
        
        Args:
            tokens: List of token dictionaries
        
        Returns:
            List of tokens with priority scores
        """
        # Process tokens
        self.process_SOMA_tokens(tokens)
        
        # Score tokens by structure stability
        scored_tokens = []
        for token in tokens:
            token_text = token.get('token', token.get('text', ''))
            if not token_text:
                continue
            
            score = 0.0
            
            # Pattern stability
            if self.pattern_builder.pattern_exists(token_text.lower()):
                pattern = self.pattern_builder.get_pattern(token_text.lower())
                score += pattern.stability_score() * 0.5
            
            # Unit status
            if token_text.lower() in self.hierarchy.unit_nodes:
                score += 0.3
            
            # Frequency
            if token_text.lower() in self.hierarchy.pattern_nodes:
                node = self.hierarchy.pattern_nodes[token_text.lower()]
                score += min(0.2, node.frequency / 10.0)
            
            scored_token = token.copy()
            scored_token["structure_priority"] = score
            scored_tokens.append(scored_token)
        
        # Sort by priority
        scored_tokens.sort(key=lambda t: t.get("structure_priority", 0), reverse=True)
        
        return scored_tokens
    
    def explain_token_structure(self, token_text: str) -> str:
        """
        Explain the structure of a token (human-readable).
        
        Args:
            token_text: Token to explain
        
        Returns:
            Human-readable explanation
        """
        return self.hierarchy.explain_structure(token_text.lower())


# Convenience functions for easy integration
def integrate_structure_with_SOMA_tokens(tokens: List[Dict]) -> List[Dict]:
    """
    Quick function to integrate structure system with SOMA tokens.
    
    Args:
        tokens: List of token dictionaries from soma tokenizer
    
    Returns:
        List of tokens enhanced with structure information
    """
    integrator = SOMAStructureIntegrator()
    return integrator.get_structure_enhanced_tokens(tokens)


def get_structure_priorities(tokens: List[Dict]) -> List[Dict]:
    """
    Get token priorities based on structure stability.
    
    Args:
        tokens: List of token dictionaries
    
    Returns:
        List of tokens sorted by structure priority
    """
    integrator = SOMAStructureIntegrator()
    return integrator.suggest_token_priorities(tokens)


# Test it works
if __name__ == "__main__":
    print("Testing SOMA Structure Integration...")
    print("=" * 70)
    
    integrator = SOMAStructureIntegrator()
    
    # Simulate SOMA tokens
    tokens = [
        {"token": "cat", "position": 0},
        {"token": "cat", "position": 1},
        {"token": "dog", "position": 2},
        {"token": "cat", "position": 3}
    ]
    
    print("\n1. Processing SOMA tokens...")
    result = integrator.process_SOMA_tokens(tokens)
    print(f"   Tokens processed: {result['tokens_processed']}")
    print(f"   Patterns found: {result['patterns_found']}")
    print(f"   Stable patterns: {result['stable_patterns']}")
    
    print("\n2. Enhancing tokens with structure...")
    enhanced = integrator.get_structure_enhanced_tokens(tokens)
    for token in enhanced[:2]:
        print(f"   Token: {token.get('token')}")
        if 'structure' in token:
            print(f"     Pattern exists: {token['structure']['pattern_exists']}")
            if token['structure']['pattern_exists']:
                print(f"     Frequency: {token['structure'].get('pattern_frequency', 0)}")
    
    print("\n3. Token priorities...")
    priorities = integrator.suggest_token_priorities(tokens)
    for token in priorities[:3]:
        print(f"   '{token.get('token')}': priority {token.get('structure_priority', 0):.3f}")
    
    print("\n✅ Integration works!")
