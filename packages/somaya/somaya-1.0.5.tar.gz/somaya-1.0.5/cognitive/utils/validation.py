"""
Validation utilities for knowledge consistency.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..graph import GraphStore, RelationType
from ..memory import UnifiedMemory
from ..reasoning import ContradictionDetector, Contradiction


class ValidationLevel(Enum):
    """Validation strictness levels."""
    BASIC = "basic"           # Just contradictions
    STANDARD = "standard"     # Contradictions + orphans
    STRICT = "strict"         # All checks


@dataclass
class ValidationIssue:
    """A validation issue found."""
    level: str  # error, warning, info
    category: str
    description: str
    node_ids: List[int]
    suggestion: str = ""


@dataclass
class ValidationReport:
    """Full validation report."""
    issues: List[ValidationIssue]
    nodes_checked: int
    edges_checked: int
    passed: bool
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.level == "error")
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.level == "warning")
    
    def summary(self) -> str:
        """Get summary string."""
        status = "✓ PASSED" if self.passed else "✗ FAILED"
        return (
            f"Validation {status}\n"
            f"  Errors: {self.error_count}\n"
            f"  Warnings: {self.warning_count}\n"
            f"  Nodes checked: {self.nodes_checked}\n"
            f"  Edges checked: {self.edges_checked}"
        )


class KnowledgeValidator:
    """
    Validate knowledge graph consistency.
    
    Checks:
    - Contradictions
    - Orphan nodes
    - Missing required edges
    - Type consistency
    - Confidence ranges
    
    Example:
        validator = KnowledgeValidator(memory)
        
        report = validator.validate()
        
        if not report.passed:
            print(report.summary())
            for issue in report.issues:
                print(f"  - {issue.description}")
    """
    
    def __init__(self, memory: UnifiedMemory):
        """
        Initialize validator.
        
        Args:
            memory: UnifiedMemory to validate
        """
        self.memory = memory
        self.graph = memory.graph
        self.contradiction_detector = ContradictionDetector(self.graph)
    
    def validate(
        self,
        level: ValidationLevel = ValidationLevel.STANDARD
    ) -> ValidationReport:
        """
        Run validation at specified level.
        
        Args:
            level: How strict to be
            
        Returns:
            ValidationReport
        """
        issues = []
        
        # Always check contradictions
        issues.extend(self._check_contradictions())
        
        if level in [ValidationLevel.STANDARD, ValidationLevel.STRICT]:
            issues.extend(self._check_orphan_nodes())
            issues.extend(self._check_confidence_ranges())
        
        if level == ValidationLevel.STRICT:
            issues.extend(self._check_type_consistency())
            issues.extend(self._check_memory_links())
        
        # Determine pass/fail
        has_errors = any(i.level == "error" for i in issues)
        
        return ValidationReport(
            issues=issues,
            nodes_checked=self.graph.node_count,
            edges_checked=self.graph.edge_count,
            passed=not has_errors
        )
    
    def _check_contradictions(self) -> List[ValidationIssue]:
        """Check for contradictions."""
        issues = []
        
        report = self.contradiction_detector.detect_all()
        
        for cont in report.contradictions:
            issues.append(ValidationIssue(
                level="error" if cont.severity >= 0.8 else "warning",
                category="contradiction",
                description=cont.description,
                node_ids=cont.nodes,
                suggestion=cont.suggestion
            ))
        
        return issues
    
    def _check_orphan_nodes(self) -> List[ValidationIssue]:
        """Check for nodes with no edges."""
        issues = []
        
        for node in self.graph.get_all_nodes():
            if node.is_isolated:
                issues.append(ValidationIssue(
                    level="info",
                    category="orphan",
                    description=f"Node '{node.text}' has no connections",
                    node_ids=[node.node_id],
                    suggestion="Consider connecting to related concepts"
                ))
        
        return issues
    
    def _check_confidence_ranges(self) -> List[ValidationIssue]:
        """Check edge weights are in valid range."""
        issues = []
        
        for edge in self.graph.get_all_edges():
            if edge.weight < 0 or edge.weight > 1:
                issues.append(ValidationIssue(
                    level="warning",
                    category="confidence",
                    description=f"Edge {edge.edge_id} has invalid weight: {edge.weight}",
                    node_ids=[edge.source_id, edge.target_id],
                    suggestion="Weight should be between 0 and 1"
                ))
        
        return issues
    
    def _check_type_consistency(self) -> List[ValidationIssue]:
        """Check node type consistency."""
        issues = []
        
        # IS_A should typically go from specific to general types
        for edge in self.graph.get_edges_by_type(RelationType.IS_A):
            source = self.graph.get_node(edge.source_id)
            target = self.graph.get_node(edge.target_id)
            
            if source and target:
                # Entity IS_A Class is ok
                # Class IS_A Entity is suspicious
                if source.node_type == "class" and target.node_type == "entity":
                    issues.append(ValidationIssue(
                        level="warning",
                        category="type",
                        description=f"Suspicious IS_A: class '{source.text}' IS_A entity '{target.text}'",
                        node_ids=[source.node_id, target.node_id],
                        suggestion="Usually entities are subtypes of classes, not vice versa"
                    ))
        
        return issues
    
    def _check_memory_links(self) -> List[ValidationIssue]:
        """Check memory object links are valid."""
        issues = []
        
        for uid, obj in self.memory.objects.items():
            # Check graph link
            if obj.graph_node_id is not None:
                node = self.graph.get_node(obj.graph_node_id)
                if node is None:
                    issues.append(ValidationIssue(
                        level="error",
                        category="link",
                        description=f"Memory object '{uid}' references non-existent graph node {obj.graph_node_id}",
                        node_ids=[obj.graph_node_id],
                        suggestion="Recreate graph node or clear reference"
                    ))
            
            # Check tree link
            if obj.tree_id and obj.tree_node_id:
                tree = self.memory.trees.get_tree(obj.tree_id)
                if tree is None:
                    issues.append(ValidationIssue(
                        level="error",
                        category="link",
                        description=f"Memory object '{uid}' references non-existent tree '{obj.tree_id}'",
                        node_ids=[],
                        suggestion="Recreate tree or clear reference"
                    ))
                elif tree.get_node(obj.tree_node_id) is None:
                    issues.append(ValidationIssue(
                        level="error",
                        category="link",
                        description=f"Memory object '{uid}' references non-existent tree node '{obj.tree_node_id}'",
                        node_ids=[],
                        suggestion="Recreate tree node or clear reference"
                    ))
        
        return issues
    
    def quick_check(self) -> Tuple[bool, str]:
        """
        Quick pass/fail check.
        
        Returns:
            (passed, message) tuple
        """
        report = self.validate(ValidationLevel.BASIC)
        return report.passed, report.summary()

