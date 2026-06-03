from manim import *
from src import AVLTree, BinaryTree, TreeNode


class BSTDemo(Scene):
    def construct(self):
        title = Text("BST 构建与删除演示", font_size=36)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        tree = BinaryTree()

        for val in [5, 3, 8, 2, 4, 7, 9]:
        # for val in [5, 3, 8]:
            node, groups = tree.insert(val)
            for group in groups:
                self.play(*group, run_time=0.6)
            self.wait(0.2)

        self.wait(1)


class AVLDemo(Scene):
    def construct(self):
        title = Text("AVL 树构建过程", font_size=40)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        tree = AVLTree(root_position=UP)
        values = [10, 20, 30, 40, 50, 25]

        info = Text("", font_size=24).to_edge(UP)
        self.add(info)

        for val in values:
            info.become(Text(f"插入: {val}", font_size=24).to_edge(UP))
            node, groups = tree.insert(val)
            if not groups:
                info.become(Text(f"{val} 已存在", font_size=24).to_edge(UP))
                self.wait(0.5)
                continue

            n_ins = 3
            if node is tree.root and node.left is None and node.right is None:
                n_ins = 1
            insert_groups = groups[:n_ins]
            rotate_groups = groups[n_ins:]

            for group in insert_groups:
                self.play(*group, run_time=0.8)
                self.wait(0.2)

            if tree.rotation_desc:
                all_nodes = set()
                for lst in tree.rotation_highlights:
                    all_nodes.update(lst)
                self.play(*[n.anim_highlight() for n in all_nodes], run_time=0.3)

                lines = "\n".join(tree.rotation_desc)
                desc_text = Text(lines, font_size=22, color=YELLOW, line_spacing=1.2)
                desc_text.to_edge(DOWN, buff=0.3)
                self.play(Write(desc_text), run_time=0.5)
                self.wait(1.5)

                for group in rotate_groups:
                    self.play(*group, run_time=0.8)
                    self.wait(0.2)

                self.play(*[n.anim_unhighlight() for n in all_nodes], run_time=0.3)
                self.play(FadeOut(desc_text))
            else:
                for group in rotate_groups:
                    self.play(*group, run_time=0.8)
                    self.wait(0.2)

            self.wait(0.3)

        info.become(Text("构建完成", font_size=24, color=GREEN).to_edge(UP))
        self.wait(2)
