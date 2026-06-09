from manim import *
from typing import Dict, List, Tuple, Optional
import numpy as np


class GraphNode(VGroup):
    def __init__(self, label: str, radius: float = 0.3, color=GREEN, font_size: int = 24, **kwargs):
        super().__init__(**kwargs)
        self.label_text = label
        self.radius = radius
        self.default_color = color
        
        self.circle = Circle(radius=radius, color=color)
        self.label = Text(label, font_size=font_size)
        self.add(self.circle, self.label)
    
    def anim_highlight(self, color=YELLOW):
        return self.circle.animate.set_fill(color, opacity=0.8)
    
    def anim_unhighlight(self):
        return self.circle.animate.set_fill(self.default_color, opacity=0.3)
    
    def anim_set_color(self, color):
        return self.circle.animate.set_fill(color, opacity=0.8)


class DijkstraGraph(VGroup):
    def __init__(self, vertices: List[str], edges: List[Tuple[str, str, float]], 
                 radius: float = 2.5, arrow_size: float = 0.3, **kwargs):
        super().__init__(**kwargs)
        self.vertices = vertices
        self.edges = edges
        self.radius = radius
        self.arrow_size = arrow_size
        self.nodes: Dict[str, GraphNode] = {}
        self.edge_objects: Dict[Tuple[str, str], VGroup] = {}
        
        self._create_graph()
    
    def _create_graph(self):
        n = len(self.vertices)
        for i, vertex in enumerate(self.vertices):
            angle = i * 2 * PI / n - PI / 2
            pos = self.radius * np.array([np.cos(angle), np.sin(angle), 0])
            node = GraphNode(vertex, radius=0.4)
            node.move_to(pos)
            self.nodes[vertex] = node
            self.add(node)
        
        for start, end, weight in self.edges:
            self._create_edge(start, end, weight)
    
    def _create_edge(self, start: str, end: str, weight: float):
        start_node = self.nodes[start]
        end_node = self.nodes[end]
        
        start_pos = start_node.get_center()
        end_pos = end_node.get_center()
        
        direction = end_pos - start_pos
        distance = np.linalg.norm(direction)
        
        if distance > 0:
            unit_dir = direction / distance
            edge_start = start_pos + unit_dir * 0.4
            edge_end = end_pos - unit_dir * 0.4
        else:
            edge_start = start_pos
            edge_end = end_pos
        
        line = Line(edge_start, edge_end, color=WHITE, stroke_width=2)
        
        # 计算权重数字的位置（在箭头起始端）
        start_offset = 0.3  # 距离起始端的偏移量
        weight_pos = edge_start + unit_dir * start_offset
        
        # 创建数字文本
        weight_text = Text(str(int(weight)), font_size=14, color=WHITE)
        weight_text.move_to(weight_pos)
        
        # 为数字添加方框背景
        weight_bg = SurroundingRectangle(weight_text, color=BLACK, fill_opacity=1, buff=0.05)
        weight_bg.move_to(weight_pos)

        # 创建统一大小的箭头（固定大小）
        arrow = Arrow(edge_start, edge_end, color=WHITE, stroke_width=2, buff=0.15, tip_length=0.2)

        # 按顺序添加：先线，再箭头，再数字组（确保数字在最上层不被覆盖）
        edge_group = VGroup(line, arrow, weight_bg, weight_text)
        self.edge_objects[(start, end)] = edge_group
        self.add(edge_group)
    
    def get_node(self, vertex: str) -> GraphNode:
        return self.nodes[vertex]
    
    def get_edge(self, start: str, end: str) -> Optional[VGroup]:
        return self.edge_objects.get((start, end))
    
    def highlight_edge(self, start: str, end: str, color=YELLOW):
        edge = self.get_edge(start, end)
        if edge:
            return [edge[0].animate.set_color(color), edge[1].animate.set_color(color)]
        return []
    
    def unhighlight_edge(self, start: str, end: str):
        edge = self.get_edge(start, end)
        if edge:
            return [edge[0].animate.set_color(WHITE), edge[1].animate.set_color(WHITE)]
        return []


class DijkstraTable:
    def __init__(self, vertices: List[str], start_vertex: str = "A"):
        self.vertices = vertices
        self.start_vertex = start_vertex
        self.distances = {v: float('infinity') for v in vertices}
        self.distances[start_vertex] = 0
        self.visited = set()
        self.previous = {}
    
    def get_unvisited_vertices(self):
        return [v for v in self.vertices if v not in self.visited]
    
    def get_current_min(self):
        unvisited = self.get_unvisited_vertices()
        if not unvisited:
            return None, float('infinity')
        
        min_vertex = min(unvisited, key=lambda v: self.distances[v])
        return min_vertex, self.distances[min_vertex]
    
    def update_distance(self, vertex: str, new_distance: float, previous_vertex: str):
        if new_distance < self.distances[vertex]:
            self.distances[vertex] = new_distance
            self.previous[vertex] = previous_vertex
            return True
        return False
    
    def mark_visited(self, vertex: str):
        self.visited.add(vertex)


def create_dijkstra_history_table(history: List[Dict], max_rows: int = 10, edges: List[Tuple[str, str, float]] = None) -> VGroup:
    """创建Dijkstra算法历史记录表格
    
    Args:
        history: 历史记录列表，每个元素包含:
            - 'visited_set': 当前已访问的顶点集
            - 'distances': 当前的距离字典
            - 'current_vertex': 当前处理的顶点(可选)
        max_rows: 表格的最大行数（包括表头）
        edges: 图的边列表，用于计算可达距离
    """
    rows = []
    
    # 确定顶点顺序和列宽
    if not history or not history[0]['distances']:
        return VGroup()
    
    vertices = sorted(history[0]['distances'].keys())
    n_vertices = len(vertices)
    
    # 设置列宽
    vertex_set_width = 2.0
    column_width = 0.8
    
    # 表头
    header_texts = ["顶点集"]
    header_texts.extend(vertices)
    
    # 创建表头背景
    header_bg_width = vertex_set_width + n_vertices * column_width + 0.3
    header_bg = Rectangle(width=header_bg_width, height=0.5, color=YELLOW, fill_color=YELLOW, fill_opacity=0.2)
    
    # 创建表头文本
    header_texts_objs = [Text(text, font_size=18, color=YELLOW) for text in header_texts]
    
    # 设置表头文本位置
    header_texts_objs[0].move_to(header_bg.get_center() + LEFT * (header_bg_width/2 - vertex_set_width/2))
    
    # 安排顶点列的表头
    for j in range(1, len(header_texts_objs)):
        cell_center_x = -vertex_set_width/2 + column_width * (j - 0.5) + 0.2
        cell_center = header_bg.get_center() + RIGHT * cell_center_x
        header_texts_objs[j].move_to(cell_center)
    
    header = VGroup(*header_texts_objs)
    rows.append(VGroup(header_bg, header))
    
    # 数据行 - 预先创建所有行的框架
    row_height = 0.4
    
    for i in range(max_rows - 1):
        # 创建行背景
        row_bg = Rectangle(width=header_bg_width, height=row_height, color=BLUE, fill_color=BLUE, fill_opacity=0.05)
        
        if i < len(history):
            record = history[i]
            visited_set = record['visited_set']
            distances = record['distances']
            current_vertex = record.get('current_vertex')
            
            row_texts = []
            
            # 当前顶点集
            if visited_set:
                visited_text = ",".join(sorted(visited_set))
            else:
                visited_text = "∅"
            row_texts.append(Text(visited_text, font_size=16, color=WHITE))
            
            # 各顶点的最短距离
            for vertex in vertices:
                dist = distances[vertex]
                
                # 检查顶点是否可达（通过已访问顶点集可以到达）
                is_reachable = False
                if dist != float('infinity'):
                    is_reachable = True
                else:
                    # 检查是否有从已访问顶点到该顶点的边
                    if edges:
                        for v in visited_set:
                            for edge_start, edge_end, weight in edges:
                                if edge_start == v and edge_end == vertex:
                                    if distances[edge_start] != float('infinity'):
                                        is_reachable = True
                                        dist = distances[edge_start] + weight
                                        break
                                if is_reachable:
                                    break
                            if is_reachable:
                                break
                
                dist_str = "∞" if not is_reachable else str(int(dist))
                
                # 高亮当前处理的顶点
                if vertex == current_vertex:
                    color = YELLOW
                elif vertex in visited_set:
                    color = GREEN
                else:
                    color = WHITE
                
                row_texts.append(Text(dist_str, font_size=18, color=color))
            
            # 创建行内容并居中对齐
            row_content = VGroup(*row_texts)
            
            # 第一列（顶点集）
            row_content[0].move_to(row_bg.get_center() + LEFT * (header_bg_width/2 - vertex_set_width/2))
            
            # 其他列（顶点距离）
            for j in range(1, len(row_content)):
                cell_center_x = -vertex_set_width/2 + column_width * (j - 0.5) + 0.2
                cell_center = row_bg.get_center() + RIGHT * cell_center_x
                row_content[j].move_to(cell_center)
            
            rows.append(VGroup(row_bg, row_content))
        else:
            # 空行，只显示背景
            rows.append(VGroup(row_bg))
    
    table = VGroup(*rows)
    table.arrange(DOWN, buff=0.0, aligned_edge=RIGHT)
    
    return table