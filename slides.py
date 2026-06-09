from manim import *
from manim_slides import Slide
from src import AVLTree, BinaryTree
from src.Dijkstra import DijkstraGraph, DijkstraTable, create_dijkstra_history_table


class slides(Slide):
    def construct(self):
        # self.construct_intro()
        # self.construct_BinaryTree()
        # self.construct_AVLTree()
        self.construct_Dijkstra()

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

    def _make_sub_array(self, values, color=GOLD):
        texts = [Text("[", font_size=22, color=color)]
        for i, v in enumerate(values):
            texts.append(Text(str(v), font_size=22, color=color))
            if i < len(values) - 1:
                texts.append(Text(",", font_size=22, color=color))
        texts.append(Text("]", font_size=22, color=color))
        return VGroup(*texts).arrange(RIGHT, buff=0.08)

    def construct_BinaryTree(self):
        title = Text("二叉树遍历与还原", font_size=40)
        self.play(Write(title))
        self.wait(0.5)
        self.next_slide()
        self.play(FadeOut(title))

        problem = Text(
            "已知前序和中序遍历，如何还原二叉树？",
            font_size=30,
        ).to_edge(UP, buff=0.6)
        self.play(Write(problem))

        pre_label = Text("前序 (Preorder):", font_size=26, color=BLUE).to_edge(LEFT, buff=0.4).shift(UP * 1.5)
        pre_vals = Text("[ A, B, D, G, E, C, F, H, I ]", font_size=26, color=BLUE).next_to(pre_label, RIGHT)
        in_label = Text("中序 (Inorder): ", font_size=26, color=GREEN).next_to(pre_label, DOWN, buff=0.3)
        in_vals = Text("[ D, G, B, E, A, H, F, C, I ]", font_size=26, color=GREEN).next_to(in_label, RIGHT)

        self.play(Write(pre_label), Write(pre_vals))
        self.play(Write(in_label), Write(in_vals))
        self.wait(1)
        self.next_slide()

        method = Text("核心方法：前序定根，中序定子树", font_size=34, color=YELLOW)
        method.to_edge(DOWN, buff=0.5)
        self.play(Write(method))

        d1 = Text("前序遍历的第一个节点 = 树的根", font_size=24).next_to(method, UP, buff=0.3)
        d2 = Text("中序遍历中，根的左边 = 左子树，右边 = 右子树", font_size=24).next_to(d1, UP, buff=0.2)
        self.play(Write(d1))
        self.play(Write(d2))
        self.wait(1.5)
        self.next_slide()

        self.play(
            *[FadeOut(m) for m in [problem, pre_label, pre_vals, in_label, in_vals, method, d1, d2]],
        )

        # ── 可独立高亮的数组元素 ──────────────────────
        preorder = ['A', 'B', 'D', 'G', 'E', 'C', 'F', 'H', 'I']
        inorder = ['D', 'G', 'B', 'E', 'A', 'H', 'F', 'C', 'I']

        pre_texts = [Text(str(v), font_size=24, color=BLUE) for v in preorder]
        pre_all = VGroup(Text("前序: ", font_size=24, color=BLUE), *pre_texts)
        pre_all.arrange(RIGHT, buff=0.12)
        pre_all.to_corner(UL, buff=0.3)

        in_texts = [Text(str(v), font_size=28, color=GREEN) for v in inorder]
        in_all = VGroup(Text("中序: ", font_size=28, color=GREEN), *in_texts)
        in_all.arrange(RIGHT, buff=0.18)

        self.play(Write(pre_all), Write(in_all))
        self.wait(0.5)

        # 接下来让中序数组变成一行节点
        in_nodes = VGroup()
        for i, val in enumerate(inorder):
            node = VGroup()
            circle = Circle(radius=0.3, color=GREEN)
            text = Text(str(val), font_size=24).move_to(circle.get_center())
            node.add(circle, text)
            in_nodes.add(node)
        in_nodes.arrange(RIGHT, buff=0.5)
        in_nodes.move_to(DOWN * 2.0)

        # 动画替换文本为节点
        self.play(Transform(in_all, in_nodes))
        self.next_slide()

        # ── 递归构建 ─────────────────────────────────
        tree = BinaryTree(root_position=UP * 2.5)
        tree.root_position = UP * 2.5
        info = Text("", font_size=22, color=YELLOW).to_edge(DOWN, buff=0.3)
        self.add(info)

        pre_idx = [0]
        
        def build(in_s, in_e, pval, side):
            if in_s > in_e:
                return None

            root_val = preorder[pre_idx[0]]
            in_pos = inorder.index(root_val, in_s, in_e + 1)
            
            info.become(Text(
                f"前序定根 = {root_val}",
                font_size=24, color=YELLOW,
            ).to_edge(DOWN, buff=0.3))

            self.play(pre_texts[pre_idx[0]].animate.set_color(YELLOW))
            
            # 高亮中序对应的节点作为根
            root_node = in_nodes[in_pos]
            self.play(root_node[0].animate.set_color(YELLOW), root_node[1].animate.set_color(YELLOW))
            self.wait(0.2)

            # 把选中的根节点变到树的位置
            new_node = tree._make_node(root_val)
            new_node.move_to(root_node.get_center())
            self.add(new_node)
            
            if pval is None:
                tree.root = new_node
            else:
                parent = pval
                if side == "left":
                    parent.left = new_node
                else:
                    parent.right = new_node
                new_node.parent = parent
                tree._connect_edge(parent, new_node)

            # 计算这一步结束时的最终布局
            target_layout = tree._compute_layout(root_anchor=False)
            # 手动设置根节点到目标位置
            if tree.root and tree.root in target_layout:
                offset = tree.root_position - target_layout[tree.root]
                for node in target_layout:
                    target_layout[node] += offset

            # 让它从中序序列飞过去（上升到树中的位置）
            anims = [new_node.animate.move_to(target_layout[new_node])]
            
            if new_node.edge_to_parent:
                a, b = tree._edge_endpoints(target_layout[parent], target_layout[new_node], tree.node_radius)
                new_node.edge_to_parent.put_start_and_end_on(a, b)
                anims.append(Create(new_node.edge_to_parent))

            # 其他树节点布局调整
            for node, pos in target_layout.items():
                if node is not new_node:
                    anims.append(ApplyMethod(node.move_to, pos))
                    if node.edge_to_parent and node.parent:
                        ppos = target_layout[node.parent]
                        a, b = tree._edge_endpoints(ppos, pos, tree.node_radius)
                        anims.append(ApplyMethod(node.edge_to_parent.put_start_and_end_on, a, b))

            self.play(*anims, run_time=0.8)

            self.wait(0.3)
            self.next_slide()

            pre_idx[0] += 1
            
            build(in_s, in_pos - 1, new_node, "left")
            build(in_pos + 1, in_e, new_node, "right")

        build(0, len(inorder) - 1, None, None)

        info.become(Text("还原完成!", font_size=28, color=GREEN).to_edge(DOWN, buff=0.3))
        self.wait(2)
        self.next_slide(auto_next=True)
        # self.play(*[FadeOut(m) for m in [pre_all, in_all, info]])
        self.clear()

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

    def construct_Dijkstra(self):
        # title = Text("Dijkstra 最短路径算法", font_size=40)
        # self.play(Write(title))
        # self.wait(0.5)
        # self.next_slide()
        # self.play(FadeOut(title))
        
        # 定义图的数据
        vertices = ['A', 'B', 'C', 'D', 'E', 'F']
        edges = [
            ('A', 'B', 4),
            ('A', 'C', 2),
            ('A', 'D', 9),
            ('B', 'C', 1),
            ('B', 'D', 5),
            ('B', 'E', 4),
            ('B', 'F', 15),
            ('C', 'B', 1),
            ('C', 'D', 8),
            ('C', 'E', 10),
            ('C', 'F', 12),
            ('D', 'E', 2),
            ('D', 'F', 6),
            ('E', 'F', 3)
        ]
        
        # 第一步：显示表格形式的边和权重
        table_title = Text("图的边和权重", font_size=30).to_edge(UP)
        # self.play(Write(table_title))
        
        # 创建表格
        table_rows = []
        header = VGroup(
            Text("起点", font_size=22, color=BLUE),
            Text("终点", font_size=22, color=GREEN),
            Text("权重", font_size=22, color=YELLOW)
        )
        header.arrange(RIGHT, buff=0.8)
        table_rows.append(header)
        
        for start, end, weight in edges:
            row = VGroup(
                Text(start, font_size=22),
                Text(end, font_size=22),
                Text(str(weight), font_size=22)
            )
            row.arrange(RIGHT, buff=0.8)
            table_rows.append(row)
        
        edge_table = VGroup(*table_rows)
        edge_table.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        edge_table.center()
        # self.play(Create(edge_table))
        # self.wait(1)
        # self.next_slide()
        
        # 第二步：将表格转换为图形
        # self.play(FadeOut(table_title), FadeOut(edge_table))
        
        # 创建图形
        graph = DijkstraGraph(vertices, edges, radius=2.5)
        graph.center()
        self.play(Create(graph))
        self.wait(1)
        self.next_slide()
        
        # 第三步：将场景分为左右两部分，图移动到左边，表格在右边
        graph_left = graph.copy()
        graph_left.shift(LEFT * 4)  # 向左移动更多
        self.play(Transform(graph, graph_left))
        

        # 在右边创建初始表格框架（10行）
        max_table_rows = 10
        vertices_for_table = sorted(vertices)

        # 创建初始历史记录
        initial_history = [{
            'visited_set': set(),
            'distances': {v: float('infinity') for v in vertices},
            'current_vertex': None
        }]
        # 设置起点距离为0
        initial_history[0]['distances']['A'] = 0
        
        table_right = create_dijkstra_history_table(initial_history, max_rows=max_table_rows, edges=edges)
        table_right.shift(RIGHT * 3)  # 向右移动更多
        self.play(Create(table_right))
        self.wait(1)
        self.next_slide()
        
        # 第四步：开始执行Dijkstra算法
        dijkstra = DijkstraTable(vertices, 'A')
        history = initial_history.copy()  # 记录历史状态
        
        info_text = Text("", font_size=20).to_edge(DOWN, buff=0.5)
        self.add(info_text)
        
        iteration = 0
        while True:
            current_vertex, current_dist = dijkstra.get_current_min()
            if current_vertex is None or current_dist == float('infinity'):
                break
            
            iteration += 1
            
            # 更新说明文字
            info_text.become(Text(
                f"步骤 {iteration}: 从 {current_vertex} 开始探索",
                font_size=24, color=YELLOW
            ).to_edge(DOWN, buff=0.5))
            self.play(Write(info_text))
            
            # 高亮当前节点
            current_node = graph.get_node(current_vertex)
            self.play(current_node.anim_highlight(YELLOW))
            
            # 获取当前节点的所有邻居
            neighbors = []
            for start, end, weight in edges:
                if start == current_vertex and end not in dijkstra.visited:
                    neighbors.append((end, weight))
            
            # 高亮所有可能的路径（黄色）
            edge_anims = []
            for neighbor, weight in neighbors:
                edge_anims.extend(graph.highlight_edge(current_vertex, neighbor, YELLOW))
            
            if edge_anims:
                self.play(*edge_anims)
            self.wait(0.5)
            self.next_slide()
            
            # 找到最短路径并高亮（红色）
            best_neighbor = None
            best_distance = float('infinity')
            
            # 计算所有可达邻居的距离
            reachable_neighbors = {}
            for neighbor, weight in neighbors:
                new_dist = dijkstra.distances[current_vertex] + weight
                reachable_neighbors[neighbor] = new_dist
                if new_dist < best_distance:
                    best_distance = new_dist
                    best_neighbor = neighbor
            
            if best_neighbor:
                # 高亮最短路径为红色
                self.play(*graph.highlight_edge(current_vertex, best_neighbor, GREEN))

                # 取消其他路径的高亮，保留最短路径的红色高亮
                for neighbor, weight in neighbors:
                    if neighbor != best_neighbor:
                        self.play(*graph.unhighlight_edge(current_vertex, neighbor))
                
                self.next_slide()

                # 更新说明
                info_text.become(Text(
                    f"选择最短路径: {current_vertex} -> {best_neighbor} (距离 {int(best_distance)})",
                    font_size=22, color=RED
                ).to_edge(DOWN, buff=0.5))
                self.play(Write(info_text))
                
                # 更新距离
                dijkstra.update_distance(best_neighbor, best_distance, current_vertex)
                
                # 更新其他可达邻居的距离（显示可达距离而不是无穷）
                for neighbor, distance in reachable_neighbors.items():
                    if neighbor != best_neighbor:
                        # 这些是可达但不是最短的路径
                        if distance < dijkstra.distances[neighbor]:
                            dijkstra.distances[neighbor] = distance
                
                # 记录当前状态到历史
                history.append({
                    'visited_set': dijkstra.visited.copy(),
                    'distances': dijkstra.distances.copy(),
                    'current_vertex': current_vertex
                })
                
                # 重新生成表格（表格大小不变，只是填充新内容）
                new_table = create_dijkstra_history_table(history, max_rows=max_table_rows, edges=edges)
                new_table.shift(RIGHT * 3.5)
                self.play(Transform(table_right, new_table))
            else:
                # 即使没有更新距离，也要记录当前状态
                history.append({
                    'visited_set': dijkstra.visited.copy(),
                    'distances': dijkstra.distances.copy(),
                    'current_vertex': current_vertex
                })
                
                # 重新生成表格
                new_table = create_dijkstra_history_table(history, max_rows=max_table_rows, edges=edges)
                new_table.shift(RIGHT * 3.5)
                self.play(Transform(table_right, new_table))
            
            # 标记当前节点为已访问
            dijkstra.mark_visited(current_vertex)
            current_node.anim_set_color(GREEN)
            self.play(current_node.anim_set_color(GREEN))
            
            self.wait(1)
            self.next_slide()
        
        # 算法完成
        info_text.become(Text(
            "算法完成！已找到从起点 A 到所有其他顶点的最短路径",
            font_size=24, color=GREEN
        ).to_edge(DOWN, buff=0.5))
        self.play(Write(info_text))
        
        # 最终表格
        final_history = history.copy()
        final_history.append({
            'visited_set': dijkstra.visited.copy(),
            'distances': dijkstra.distances.copy(),
            'current_vertex': None
        })
        
        final_table = create_dijkstra_history_table(final_history, max_rows=max_table_rows, edges=edges)
        final_table.shift(RIGHT * 3.5)
        self.play(Transform(table_right, final_table))
        
        self.wait(3)
        self.next_slide(auto_next=True)
        self.clear()
