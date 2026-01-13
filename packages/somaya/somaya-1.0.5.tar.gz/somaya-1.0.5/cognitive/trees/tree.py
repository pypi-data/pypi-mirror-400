"""
Tree - A single hierarchical tree structure.

Supports:
- Adding/removing nodes
- Tree traversal (DFS, BFS)
- Path finding (root to node)
- Subtree extraction
"""

from typing import Dict, Any, Optional, List, Iterator, Callable
from collections import deque
from .tree_node import TreeNode


class Tree:
    """
    A hierarchical tree structure for organizing knowledge.
    
    Example:
        tree = Tree("concepts", "AI Concepts")
        tree.add_node("ml", "Machine Learning")
        tree.add_node("dl", "Deep Learning", parent_id="ml")
        tree.add_node("transformers", "Transformers", parent_id="dl")
    """
    
    def __init__(self, tree_id: str, name: str, root_content: Optional[str] = None):
        """
        Initialize a tree.
        
        Args:
            tree_id: Unique identifier for this tree
            name: Human-readable name
            root_content: Content for root node (defaults to name)
        """
        self.tree_id = tree_id
        self.name = name
        self.nodes: Dict[str, TreeNode] = {}
        self.root_id: Optional[str] = None
        
        # Create root node
        root_content = root_content or name
        self._create_root(root_content)
    
    def _create_root(self, content: str) -> TreeNode:
        """Create the root node."""
        root_id = f"{self.tree_id}_root"
        root = TreeNode(
            node_id=root_id,
            content=content,
            parent_id=None,
            depth=0
        )
        self.nodes[root_id] = root
        self.root_id = root_id
        return root
    
    def get_root(self) -> Optional[TreeNode]:
        """Get the root node."""
        if self.root_id:
            return self.nodes.get(self.root_id)
        return None
    
    def add_node(
        self,
        node_id: str,
        content: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TreeNode:
        """
        Add a node to the tree.
        
        Args:
            node_id: Unique ID for the node
            content: Text content
            parent_id: Parent node ID (defaults to root)
            metadata: Additional properties
            
        Returns:
            The created TreeNode
        """
        # Default to root as parent
        if parent_id is None:
            parent_id = self.root_id
        
        # Validate parent exists
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node '{parent_id}' not found")
        
        # Calculate depth
        parent = self.nodes[parent_id]
        depth = parent.depth + 1
        
        # Create node
        node = TreeNode(
            node_id=node_id,
            content=content,
            parent_id=parent_id,
            depth=depth,
            metadata=metadata or {}
        )
        
        # Add to tree
        self.nodes[node_id] = node
        parent.add_child(node_id)
        
        return node
    
    def get_node(self, node_id: str) -> Optional[TreeNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def remove_node(self, node_id: str, recursive: bool = True) -> bool:
        """
        Remove a node from the tree.
        
        Args:
            node_id: Node to remove
            recursive: If True, remove all descendants too
            
        Returns:
            True if removed
        """
        if node_id not in self.nodes:
            return False
        
        if node_id == self.root_id:
            raise ValueError("Cannot remove root node")
        
        node = self.nodes[node_id]
        
        # Remove children first if recursive
        if recursive:
            for child_id in node.children_ids.copy():
                self.remove_node(child_id, recursive=True)
        
        # Remove from parent
        if node.parent_id and node.parent_id in self.nodes:
            self.nodes[node.parent_id].remove_child(node_id)
        
        # Remove node
        del self.nodes[node_id]
        return True
    
    def get_path_to_root(self, node_id: str) -> List[TreeNode]:
        """
        Get path from node to root (inclusive).
        
        Returns list from node up to root.
        """
        path = []
        current_id = node_id
        
        while current_id is not None:
            node = self.nodes.get(current_id)
            if node is None:
                break
            path.append(node)
            current_id = node.parent_id
        
        return path
    
    def get_path_from_root(self, node_id: str) -> List[TreeNode]:
        """Get path from root to node (inclusive)."""
        return list(reversed(self.get_path_to_root(node_id)))
    
    def get_ancestors(self, node_id: str) -> List[TreeNode]:
        """Get all ancestors (excluding the node itself)."""
        path = self.get_path_to_root(node_id)
        return path[1:] if path else []
    
    def get_descendants(self, node_id: str) -> List[TreeNode]:
        """Get all descendants (excluding the node itself)."""
        descendants = []
        
        def collect(nid: str):
            node = self.nodes.get(nid)
            if node:
                for child_id in node.children_ids:
                    child = self.nodes.get(child_id)
                    if child:
                        descendants.append(child)
                        collect(child_id)
        
        collect(node_id)
        return descendants
    
    def get_siblings(self, node_id: str) -> List[TreeNode]:
        """Get sibling nodes (same parent, excluding self)."""
        node = self.nodes.get(node_id)
        if not node or not node.parent_id:
            return []
        
        parent = self.nodes.get(node.parent_id)
        if not parent:
            return []
        
        return [
            self.nodes[cid]
            for cid in parent.children_ids
            if cid != node_id and cid in self.nodes
        ]
    
    def traverse_dfs(
        self,
        start_id: Optional[str] = None,
        pre_order: bool = True
    ) -> Iterator[TreeNode]:
        """
        Depth-first traversal.
        
        Args:
            start_id: Starting node (defaults to root)
            pre_order: If True, visit parent before children
        """
        start_id = start_id or self.root_id
        if not start_id or start_id not in self.nodes:
            return
        
        def dfs(node_id: str) -> Iterator[TreeNode]:
            node = self.nodes.get(node_id)
            if not node:
                return
            
            if pre_order:
                yield node
            
            for child_id in node.children_ids:
                yield from dfs(child_id)
            
            if not pre_order:
                yield node
        
        yield from dfs(start_id)
    
    def traverse_bfs(self, start_id: Optional[str] = None) -> Iterator[TreeNode]:
        """
        Breadth-first traversal.
        
        Args:
            start_id: Starting node (defaults to root)
        """
        start_id = start_id or self.root_id
        if not start_id or start_id not in self.nodes:
            return
        
        queue = deque([start_id])
        
        while queue:
            node_id = queue.popleft()
            node = self.nodes.get(node_id)
            if not node:
                continue
            
            yield node
            queue.extend(node.children_ids)
    
    def find_nodes(
        self,
        predicate: Callable[[TreeNode], bool]
    ) -> List[TreeNode]:
        """Find all nodes matching a predicate."""
        return [node for node in self.traverse_dfs() if predicate(node)]
    
    def find_by_content(self, content: str, exact: bool = False) -> List[TreeNode]:
        """
        Find nodes by content.
        
        Args:
            content: Text to search for
            exact: If True, exact match; else substring match
        """
        content_lower = content.lower()
        
        if exact:
            return self.find_nodes(lambda n: n.content.lower() == content_lower)
        return self.find_nodes(lambda n: content_lower in n.content.lower())
    
    def get_subtree(self, node_id: str) -> "Tree":
        """Extract a subtree rooted at the given node."""
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' not found")
        
        # Create new tree
        source_node = self.nodes[node_id]
        subtree = Tree(
            tree_id=f"{self.tree_id}_sub_{node_id}",
            name=f"Subtree of {source_node.content}",
            root_content=source_node.content
        )
        
        # Copy metadata to root
        subtree.get_root().metadata = source_node.metadata.copy()
        subtree.get_root().embedding_ref = source_node.embedding_ref
        subtree.get_root().graph_node_ref = source_node.graph_node_ref
        
        # Add descendants
        def copy_children(src_id: str, dst_parent_id: str):
            src_node = self.nodes.get(src_id)
            if not src_node:
                return
            
            for child_id in src_node.children_ids:
                child = self.nodes.get(child_id)
                if child:
                    new_node = subtree.add_node(
                        node_id=child_id,
                        content=child.content,
                        parent_id=dst_parent_id,
                        metadata=child.metadata.copy()
                    )
                    new_node.embedding_ref = child.embedding_ref
                    new_node.graph_node_ref = child.graph_node_ref
                    copy_children(child_id, child_id)
        
        copy_children(node_id, subtree.root_id)
        return subtree
    
    def get_depth(self) -> int:
        """Get maximum depth of the tree."""
        if not self.nodes:
            return 0
        return max(node.depth for node in self.nodes.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tree statistics."""
        leaf_count = sum(1 for n in self.nodes.values() if n.is_leaf())
        return {
            "tree_id": self.tree_id,
            "name": self.name,
            "node_count": len(self.nodes),
            "depth": self.get_depth(),
            "leaf_count": leaf_count,
            "branch_count": len(self.nodes) - leaf_count,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tree_id": self.tree_id,
            "name": self.name,
            "root_id": self.root_id,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tree":
        """Create from dictionary."""
        tree = object.__new__(cls)
        tree.tree_id = data["tree_id"]
        tree.name = data["name"]
        tree.root_id = data["root_id"]
        tree.nodes = {
            nid: TreeNode.from_dict(ndata)
            for nid, ndata in data["nodes"].items()
        }
        return tree
    
    def print_tree(self, node_id: Optional[str] = None, indent: str = "") -> str:
        """Get a string representation of the tree."""
        lines = []
        
        def print_node(nid: str, prefix: str, is_last: bool):
            node = self.nodes.get(nid)
            if not node:
                return
            
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{node.content}")
            
            child_prefix = prefix + ("    " if is_last else "│   ")
            children = node.children_ids
            
            for i, child_id in enumerate(children):
                print_node(child_id, child_prefix, i == len(children) - 1)
        
        start_id = node_id or self.root_id
        if start_id:
            root = self.nodes.get(start_id)
            if root:
                lines.append(root.content)
                for i, child_id in enumerate(root.children_ids):
                    print_node(child_id, "", i == len(root.children_ids) - 1)
        
        return "\n".join(lines)
    
    def __len__(self) -> int:
        return len(self.nodes)
    
    def __repr__(self) -> str:
        return f"Tree('{self.tree_id}', nodes={len(self.nodes)}, depth={self.get_depth()})"

