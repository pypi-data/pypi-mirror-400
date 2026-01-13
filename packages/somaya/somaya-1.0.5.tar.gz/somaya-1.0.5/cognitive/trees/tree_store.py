"""
TreeStore - Manages multiple knowledge trees.

Supports:
- Multiple trees (concept tree, document tree, etc.)
- Cross-tree operations
- Persistence (JSON)
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from .tree_node import TreeNode
from .tree import Tree


class TreeStore:
    """
    Manages multiple knowledge trees.
    
    Example:
        store = TreeStore()
        
        # Create concept tree
        concepts = store.create_tree("concepts", "AI Concepts")
        concepts.add_node("ml", "Machine Learning")
        concepts.add_node("dl", "Deep Learning", parent_id="ml")
        
        # Create document tree
        docs = store.create_tree("docs", "Documentation")
        docs.add_node("ch1", "Chapter 1")
        
        # Save all
        store.save("knowledge_trees.json")
    """
    
    def __init__(self):
        """Initialize empty tree store."""
        self.trees: Dict[str, Tree] = {}
    
    def create_tree(
        self,
        tree_id: str,
        name: str,
        root_content: Optional[str] = None
    ) -> Tree:
        """
        Create a new tree.
        
        Args:
            tree_id: Unique identifier
            name: Human-readable name
            root_content: Content for root node
            
        Returns:
            The created Tree
        """
        if tree_id in self.trees:
            raise ValueError(f"Tree '{tree_id}' already exists")
        
        tree = Tree(tree_id, name, root_content)
        self.trees[tree_id] = tree
        return tree
    
    def get_tree(self, tree_id: str) -> Optional[Tree]:
        """Get a tree by ID."""
        return self.trees.get(tree_id)
    
    def delete_tree(self, tree_id: str) -> bool:
        """Delete a tree. Returns True if deleted."""
        if tree_id in self.trees:
            del self.trees[tree_id]
            return True
        return False
    
    def list_trees(self) -> List[str]:
        """List all tree IDs."""
        return list(self.trees.keys())
    
    def find_node_across_trees(
        self,
        content: str,
        exact: bool = False
    ) -> List[tuple]:
        """
        Find nodes across all trees.
        
        Returns:
            List of (tree_id, TreeNode) tuples
        """
        results = []
        for tree_id, tree in self.trees.items():
            nodes = tree.find_by_content(content, exact=exact)
            for node in nodes:
                results.append((tree_id, node))
        return results
    
    def get_node_by_path(self, tree_id: str, path: List[str]) -> Optional[TreeNode]:
        """
        Get a node by path of node IDs.
        
        Args:
            tree_id: Tree to search in
            path: List of node IDs from root to target
            
        Returns:
            The node at the path, or None
        """
        tree = self.trees.get(tree_id)
        if not tree or not path:
            return None
        
        # Verify path is valid
        current = tree.get_root()
        if not current:
            return None
        
        for node_id in path:
            if node_id == current.node_id:
                continue
            
            if node_id not in current.children_ids:
                return None
            
            current = tree.get_node(node_id)
            if not current:
                return None
        
        return current
    
    def merge_trees(
        self,
        source_tree_id: str,
        target_tree_id: str,
        target_parent_id: Optional[str] = None
    ) -> bool:
        """
        Merge source tree into target tree as a subtree.
        
        Args:
            source_tree_id: Tree to merge from
            target_tree_id: Tree to merge into
            target_parent_id: Parent node in target (defaults to root)
            
        Returns:
            True if merged successfully
        """
        source = self.trees.get(source_tree_id)
        target = self.trees.get(target_tree_id)
        
        if not source or not target:
            return False
        
        target_parent_id = target_parent_id or target.root_id
        if target_parent_id not in target.nodes:
            return False
        
        # Copy all nodes from source
        id_mapping = {}  # old_id -> new_id
        
        for node in source.traverse_bfs():
            if node.is_root():
                # Add source root as child of target parent
                new_id = f"{source_tree_id}_{node.node_id}"
                new_node = target.add_node(
                    node_id=new_id,
                    content=node.content,
                    parent_id=target_parent_id,
                    metadata=node.metadata.copy()
                )
                new_node.embedding_ref = node.embedding_ref
                new_node.graph_node_ref = node.graph_node_ref
                id_mapping[node.node_id] = new_id
            else:
                # Add as child of mapped parent
                new_id = f"{source_tree_id}_{node.node_id}"
                new_parent_id = id_mapping.get(node.parent_id)
                if new_parent_id:
                    new_node = target.add_node(
                        node_id=new_id,
                        content=node.content,
                        parent_id=new_parent_id,
                        metadata=node.metadata.copy()
                    )
                    new_node.embedding_ref = node.embedding_ref
                    new_node.graph_node_ref = node.graph_node_ref
                    id_mapping[node.node_id] = new_id
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all trees."""
        total_nodes = sum(len(tree) for tree in self.trees.values())
        
        return {
            "tree_count": len(self.trees),
            "total_nodes": total_nodes,
            "trees": {
                tree_id: tree.get_stats()
                for tree_id, tree in self.trees.items()
            }
        }
    
    def save(self, filepath: str) -> None:
        """Save all trees to JSON file."""
        data = {
            "version": "1.0",
            "trees": {
                tree_id: tree.to_dict()
                for tree_id, tree in self.trees.items()
            }
        }
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str) -> None:
        """Load trees from JSON file."""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.trees = {}
        for tree_id, tree_data in data.get("trees", {}).items():
            self.trees[tree_id] = Tree.from_dict(tree_data)
    
    def clear(self) -> None:
        """Remove all trees."""
        self.trees.clear()
    
    def __len__(self) -> int:
        return len(self.trees)
    
    def __repr__(self) -> str:
        return f"TreeStore(trees={len(self.trees)})"

