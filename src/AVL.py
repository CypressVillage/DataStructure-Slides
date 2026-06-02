from manim import *
from typing import Optional, List, Tuple

from .BST import BinaryTree, TreeNode


class AVLTree(BinaryTree):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # ─── AVL 内部 ───────────────────────────────────────

    def _get_height(self, node: Optional[TreeNode]) -> int:
        return node._tree_height if node else 0

    def _update_height(self, node: TreeNode):
        node._tree_height = 1 + max(self._get_height(node.left), self._get_height(node.right))

    def _balance_factor(self, node: TreeNode) -> int:
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, z: TreeNode):
        y = z.left
        t2 = y.right

        y.right = z
        z.left = t2
        y.parent = z.parent
        z.parent = y
        if t2:
            t2.parent = z

        if y.parent:
            if y.parent.left is z:
                y.parent.left = y
            else:
                y.parent.right = y
        else:
            self.root = y

        self._update_height(z)
        self._update_height(y)

    def _rotate_left(self, z: TreeNode):
        y = z.right
        t2 = y.left

        y.left = z
        z.right = t2
        y.parent = z.parent
        z.parent = y
        if t2:
            t2.parent = z

        if y.parent:
            if y.parent.left is z:
                y.parent.left = y
            else:
                y.parent.right = y
        else:
            self.root = y

        self._update_height(z)
        self._update_height(y)

    def _rotation_anims(self, anchor_point=None) -> List[Animation]:
        targets = self._compute_layout(root_anchor=False)
        if anchor_point is None:
            anchor_point = self.root.get_center()
        offset = anchor_point - targets[self.root]
        for n in targets:
            targets[n] += offset

        old_edge_to_child = {}
        for n in self._preorder_nodes():
            if n.edge_to_parent:
                old_edge_to_child[n.edge_to_parent] = n
        old_edges = list(old_edge_to_child.keys())

        for n in self._preorder_nodes():
            if n.edge_to_parent:
                self.remove(n.edge_to_parent)
                n.edge_to_parent = None

        unassigned = old_edges.copy()
        children_with_parent = [n for n in self._preorder_nodes() if n.parent]
        for n in children_with_parent:
            if n.edge_to_parent is not None:
                continue
            for line in unassigned:
                if old_edge_to_child[line] is n:
                    unassigned.remove(line)
                    n.edge_to_parent = line
                    self.add(line)
                    break
        for n in children_with_parent:
            if n.edge_to_parent is None and unassigned:
                line = unassigned.pop(0)
                n.edge_to_parent = line
                self.add(line)

        edge_anims = [FadeOut(line) for line in unassigned]
        for n in self._preorder_nodes():
            if n.parent and n.edge_to_parent is None:
                self._connect_edge(n.parent, n)
                ppos = targets[n.parent]
                cpos = targets[n]
                a, b = self._edge_endpoints(ppos, cpos, self.node_radius)
                n.edge_to_parent.put_start_and_end_on(a, b)
                edge_anims.append(Create(n.edge_to_parent))

        return edge_anims + self._layout_anims(targets)

    # ─── AVL 重平衡 ─────────────────────────────────────

    def _rebalance(self, node: TreeNode) -> List[List[Animation]]:
        groups = []
        current = node
        while current:
            self._update_height(current)
            bf = self._balance_factor(current)
            did_rotate = False

            if bf > 1:
                anchor = self.root.get_center()
                if self._balance_factor(current.left) < 0:
                    self._rotate_left(current.left)
                    groups.append(self._rotation_anims(anchor_point=anchor))
                    did_rotate = True
                self._rotate_right(current)
                groups.append(self._rotation_anims(anchor_point=anchor))
                did_rotate = True
            elif bf < -1:
                anchor = self.root.get_center()
                if self._balance_factor(current.right) > 0:
                    self._rotate_right(current.right)
                    groups.append(self._rotation_anims(anchor_point=anchor))
                    did_rotate = True
                self._rotate_left(current)
                groups.append(self._rotation_anims(anchor_point=anchor))
                did_rotate = True

            if did_rotate:
                if current.parent:
                    current = current.parent
                continue

            current = current.parent

        return groups

    # ─── AVL 插入 ───────────────────────────────────────

    def insert(self, value: int) -> Tuple[Optional[TreeNode], List[List[Animation]]]:
        node, anim_groups = super().insert(value)
        # return node, anim_groups
        if node is None:
            return node, anim_groups
        if self.root is node and node.left is None and node.right is None:
            return node, anim_groups

        rebalance_groups = self._rebalance(node)
        anim_groups.extend(rebalance_groups)
        return node, anim_groups
