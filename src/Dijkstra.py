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
            unit_dir = RIGHT
        
        # 对于双向连接路径做偏移处理
        has_reverse_edge = any(
            edge_start_name == end and edge_end_name == start
            for edge_start_name, edge_end_name, _ in self.edges
        )
        if has_reverse_edge:
            perpendicular = np.array([-unit_dir[1], unit_dir[0], 0])
            edge_offset = perpendicular * 0.12
            edge_start += edge_offset
            edge_end += edge_offset
        
        line = Line(edge_start, edge_end, color=WHITE, stroke_width=4)
        
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
        arrow = Arrow(edge_start, edge_end, color=WHITE, stroke_width=4, buff=0.15, tip_length=0.2)

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
            - 'previous': 当前的前驱顶点字典(可选)
            - 'current_vertex': 当前处理的顶点(可选)
        max_rows: 表格的最大行数（包括表头）
        edges: 图的边列表，用于计算可达距离
    """
    if not history or not history[0]['distances']:
        return VGroup()
    
    vertices = sorted(history[0]['distances'].keys())
    rows = []
    column_widths = [2.0] + [1.0 for _ in vertices]
    table_width = sum(column_widths)
    row_height = 0.4

    column_centers = []
    left_edge = -table_width / 2
    for width in column_widths:
        column_centers.append(left_edge + width / 2)
        left_edge += width

    header_texts = ["顶点集", *vertices]
    header = VGroup(*[
        Text(text, font_size=18, color=YELLOW).move_to(RIGHT * column_centers[i])
        for i, text in enumerate(header_texts)
    ])
    rows.append(header)
    
    for i, record in enumerate(history[:max_rows - 1], start=1):
        visited_set = record['visited_set']
        distances = record['distances']
        previous = record.get('previous', {})
        current_vertex = record.get('current_vertex')
        row_y = -i * row_height
        row_texts = []
        
        visited_text = ",".join(sorted(visited_set)) if visited_set else "∅"
        row_texts.append(Text(visited_text, font_size=16, color=WHITE))
        
        for vertex in vertices:
            dist = distances[vertex]
            is_reachable = dist != float('infinity')
            if not is_reachable and edges:
                for v in visited_set:
                    for edge_start, edge_end, weight in edges:
                        if edge_start == v and edge_end == vertex and distances[edge_start] != float('infinity'):
                            is_reachable = True
                            dist = distances[edge_start] + weight
                            break
                    if is_reachable:
                        break
            
            if is_reachable:
                predecessor = previous.get(vertex)
                dist_str = f"{int(dist)}({predecessor})" if predecessor else str(int(dist))
            else:
                dist_str = "∞"
            if vertex == current_vertex:
                color = YELLOW
            elif vertex in visited_set:
                color = GREEN
            else:
                color = WHITE
            row_texts.append(Text(dist_str, font_size=18, color=color))
        
        row = VGroup(*row_texts)
        for j, text in enumerate(row):
            text.move_to(RIGHT * column_centers[j] + DOWN * abs(row_y))
        rows.append(row)
    
    table = VGroup(*rows)
    return table
