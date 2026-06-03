from manim import *
from manim_slides import Slide
from src import AVLTree


class slides(Slide):
    def construct(self):
        # self.construct_intro()
        # self.construct_BinaryTree()
        self.construct_AVLTree()

    def construct_intro(self):
        title = Text("数据结构与算法-课程作业讲解", font_size=40)
        self.play(Write(title))
        self.wait(0.5)
        self.next_slide()
        self.play(FadeOut(title))

        title = Text("目录", font_size=40).to_edge(UP+LEFT)
        menu = Text(
        """
            二叉树遍历与还原
            AVL 树插入、旋转与平衡维护
            最小堆构建与删除
        """,
            font_size=30
        ).to_edge(UP+LEFT).shift(DOWN)
        self.play(Write(title))
        self.play(Write(menu))
        self.wait(2)
        self.next_slide(auto_next=True)
        self.play(*[FadeOut(title), FadeOut(menu)])

    def construct_BinaryTree(self):
        title = Text("二叉树遍历与还原", font_size=40)
        self.play(Write(title))
        self.wait(0.5)
        self.next_slide()

        self.play(FadeOut(title))

        # 这里可以添加二叉树遍历与还原的动画展示
        # 由于篇幅限制，这里暂不实现，后续可以根据需要补充

    def _insertion_group_count(self, node, tree) -> int:
        """Return number of animation groups produced by BST.insert()."""
        if node is tree.root and node.left is None and node.right is None:
            return 1  # root creation only
        return 3  # Create(node), Create(edge), Layout

    def construct_AVLTree(self):
        title = Text("AVL 树插入、旋转与平衡维护", font_size=40)
        self.play(Write(title))
        self.wait(0.5)
        self.next_slide()

        self.play(FadeOut(title))

        tree = AVLTree(root_position=UP * 2)
        values = [30, 20, 40, 10, 25, 22, 50, 60, 55]

        # 首先展示列表
        list_text = Text("插入序列: [" + ", ".join(map(str, values)) + "]", font_size=24).to_edge(UP+LEFT)
        self.play(Write(list_text))
        self.wait(1)
        self.next_slide()

        info = Text("", font_size=24).to_edge(UP+RIGHT)
        self.add(info)

        for i, val in enumerate(values):
            info.become(Text(f"步骤 {i+1}: 插入 {val}", font_size=24).to_edge(UP+RIGHT))

            node, groups = tree.insert(val)
            if not groups:
                continue

            n_ins = self._insertion_group_count(node, tree)
            insert_groups = groups[:n_ins]
            rotate_groups = groups[n_ins:]

            # -- 插入动画 --
            for group in insert_groups:
                self.play(*group, run_time=0.8)
                self.wait(0.2)

            # -- 旋转前暂停，供讲解 --
            if tree.rotation_desc:
                all_nodes = set()
                for lst in tree.rotation_highlights:
                    all_nodes.update(lst)

                # -- 旋转前高亮相关节点 --
                self.play(*[n.anim_highlight() for n in all_nodes], run_time=0.3)

                #-- 旋转前显示说明文本 --
                lines = "\n".join(tree.rotation_desc)
                desc_text = Text(lines, font_size=22, color=YELLOW, line_spacing=1.2)
                desc_text.to_edge(DOWN, buff=0.3)
                self.play(Write(desc_text), run_time=0.5)

                # -- 旋转动画 --
                for group in rotate_groups:
                    self.next_slide()
                    self.play(*group, run_time=0.8)
                    self.wait(0.2)

                # -- 旋转后取消高亮和说明 --
                self.play(*[n.anim_unhighlight() for n in all_nodes], run_time=0.3)
                self.play(FadeOut(desc_text))

            else:
                for group in rotate_groups:
                    self.play(*group, run_time=0.8)
                    self.wait(0.2)

            self.wait(0.3)
            self.next_slide()

        info.become(Text("构建完成!", font_size=24, color=GREEN).to_edge(UP+RIGHT))
        self.wait(2)
        self.next_slide(auto_next=True)
