# src/path_finder.py
from shapely.geometry import Point
import networkx as nx
import numpy as np

def find_nearest_node(graph, point):
    """ابحث عن أقرب عقدة للطريق من نقطة معينة."""
    return min(graph.nodes, key=lambda node: Point(node).distance(point))

def get_shortest_path(graph, origin: Point, target: Point):
    u = find_nearest_node(graph, origin)
    v = find_nearest_node(graph, target)
    return nx.shortest_path(graph, source=u, target=v, weight="weight")
