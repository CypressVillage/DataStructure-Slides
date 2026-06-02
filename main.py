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
            for group in groups:
                self.play(*group, run_time=0.8)
                self.wait(0.2)

            self.wait(0.3)

        info.become(Text("构建完成", font_size=24, color=GREEN).to_edge(UP))
        self.wait(2)
