from manim import *
from typing import Optional, List, Tuple

class TreeNode(VGroup):
    def __init__(self, value: int, 
                 radius: float = 0.35, color=BLUE,
                 font_size: int = 26, **kwargs):
        super().__init__(**kwargs)
        self.val = value
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None
        self.parent: Optional['TreeNode'] = None
        self._tree_height: int = 1
        self.edge_to_parent: Optional[Line] = None

        self.radius = radius
        self.default_color = color
        self.default_opacity = 0.5
        self.circle = Circle(
            radius=radius, color=color,
            fill_color=color, fill_opacity=self.default_opacity
        )
        self.label = Text(str(value), font_size=font_size)
        self.add(self.circle, self.label)

    def anim_highlight(self, color=YELLOW):
        return self.circle.animate.set_fill(color, opacity=0.9)

    def anim_unhighlight(self):
        return self.circle.animate.set_fill(self.default_color, opacity=self.default_opacity)


class BinaryTree(VGroup):
    def __init__(self, node_radius: float = 0.35, node_color=BLUE,
                 h_spacing: float = 0.6, v_spacing: float = 0.9,
                 edge_color=WHITE, edge_width: float = 2,
                 root_position=ORIGIN, **kwargs):
        super().__init__(**kwargs)
        self.root: Optional[TreeNode] = None
        self.node_radius = node_radius
        self.node_color = node_color
        self.h_spacing = h_spacing
        self.v_spacing = v_spacing
        self.edge_color = edge_color
        self.edge_width = edge_width
        self.root_position = root_position

    # ─── 内部工具 ───────────────────────────────────────

    def _make_node(self, value: int) -> TreeNode:
        node = TreeNode(value, radius=self.node_radius, color=self.node_color)
        self.add(node)
        return node

    @staticmethod
    def _edge_endpoints(p, c, r):
        diff = c - p
        dist = np.linalg.norm(diff)
        if dist < 1e-8:
            return p, c
        d = diff / dist
        return p + d * r, c - d * r

    def _connect_edge(self, parent: TreeNode, child: TreeNode) -> Line:
        a, b = self._edge_endpoints(parent.get_center(), child.get_center(), self.node_radius)
        line = Line(a, b, color=self.edge_color, stroke_width=self.edge_width)
        line.z_index = -1
        child.edge_to_parent = line
        self.add(line)
        return line

    def _remove_edge(self, node: TreeNode):
        if node.edge_to_parent:
            self.remove(node.edge_to_parent)
            node.edge_to_parent = None

    def _rebuild_edges(self):
        for node in self._preorder_nodes():
            self._remove_edge(node)
        for node in self._preorder_nodes():
            if node.parent:
                self._connect_edge(node.parent, node)

    def _preorder_nodes(self):
        def _walk(n):
            if n:
                yield n
                yield from _walk(n.left)
                yield from _walk(n.right)
        return _walk(self.root)

    def _collect_inorder(self, node, nodes=None):
        if nodes is None:
            nodes = []
        if node:
            self._collect_inorder(node.left, nodes)
            nodes.append(node)
            self._collect_inorder(node.right, nodes)
        return nodes

    def _compute_layout(self, root_anchor=True) -> dict:
        inorder = self._collect_inorder(self.root)
        depths = {}
        def _assign_depth(n, d):
            if n:
                _assign_depth(n.left, d + 1)
                depths[n] = d
                _assign_depth(n.right, d + 1)
        _assign_depth(self.root, 0)
        targets = {}
        for i, node in enumerate(inorder):
            targets[node] = i * self.h_spacing * RIGHT + (-depths[node]) * self.v_spacing * UP
        if root_anchor and self.root:
            offset = self.root.get_center() - targets[self.root]
            for node in list(targets):
                targets[node] += offset
        return targets

    def _layout_anims(self, targets: dict) -> List[Animation]:
        anims = []
        for node, pos in targets.items():
            anims.append(ApplyMethod(node.move_to, pos))
            if node.edge_to_parent and node.parent:
                ppos = targets[node.parent]
                a, b = self._edge_endpoints(ppos, pos, self.node_radius)
                anims.append(ApplyMethod(
                    node.edge_to_parent.put_start_and_end_on, a, b,
                ))
        return anims

    def apply_layout(self, root_anchor=True):
        targets = self._compute_layout(root_anchor=root_anchor)
        for node, pos in targets.items():
            node.move_to(pos)
        for node in self._preorder_nodes():
            if node.edge_to_parent and node.parent:
                ppos = targets[node.parent]
                a, b = self._edge_endpoints(ppos, targets[node], self.node_radius)
                node.edge_to_parent.put_start_and_end_on(a, b)

    # ─── 基本操作 ───────────────────────────────────────

    def find(self, value: int) -> Optional[TreeNode]:
        def _s(n):
            if n is None or n.val == value:
                return n
            if value < n.val:
                return _s(n.left)
            return _s(n.right)
        return _s(self.root)

    def get_node(self, value: int) -> Optional[TreeNode]:
        return self.find(value)

    def get_root(self) -> Optional[TreeNode]:
        return self.root

    def highlight_animation(self, node: TreeNode, color=YELLOW):
        return node.anim_highlight(color)

    def unhighlight_animation(self, node: TreeNode) -> Animation:
        return node.anim_unhighlight()

    # ─── 插入 ───────────────────────────────────────────

    def insert(self, value: int) -> Tuple[Optional[TreeNode], List[List[Animation]]]:
        """插入值，返回 (节点, 动画组列表)。每组动画应依次 play。"""
        node = self._make_node(value)

        if self.root is None:
            self.root = node
            node.move_to(self.root_position)
            return node, [[Create(node)]]

        curr = self.root
        while True:
            if value < curr.val:
                if curr.left is None:
                    curr.left = node
                    node.parent = curr
                    break
                curr = curr.left
            elif value > curr.val:
                if curr.right is None:
                    curr.right = node
                    node.parent = curr
                    break
                curr = curr.right
            else:
                self.remove(node)
                return curr, []

        node.move_to(node.parent.get_center() + DOWN * 2)
        self._connect_edge(node.parent, node)

        return node, [
            [Create(node)],
            [Create(node.edge_to_parent)],
            self._layout_anims(self._compute_layout()),
        ]

    # ─── 删除 ───────────────────────────────────────────

    def delete(self, value: int) -> List[List[Animation]]:
        """按值删除节点及其子树，返回动画组列表。"""
        node = self.find(value)
        if node is None:
            return []
        anim_groups = []

        def _collect(n):
            if n is None:
                return []
            return [n] + _collect(n.left) + _collect(n.right)

        to_remove = _collect(node)

        if node.parent:
            d = node.parent
            if d.left is node:
                d.left = None
            else:
                d.right = None
            self._remove_edge(node)
        elif node is self.root:
            self.root = None

        anim_groups.append([FadeOut(n) for n in to_remove] +
                           [FadeOut(n.edge_to_parent) for n in to_remove if n.edge_to_parent])

        for n in to_remove:
            if n.edge_to_parent:
                self.remove(n.edge_to_parent)
            self.remove(n)

        if self.root:
            anim_groups.append(self._layout_anims(self._compute_layout()))

        return anim_groups

    def delete_node(self, node: TreeNode) -> List[List[Animation]]:
        return self.delete(node.val)