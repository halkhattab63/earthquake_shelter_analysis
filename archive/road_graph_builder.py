# src/road_graph_builder.py
import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def build_road_graph(roads_path: str) -> nx.Graph:
    gdf = gpd.read_file(roads_path)
    G = nx.Graph()

    for _, row in gdf.iterrows():
        geom = row.geometry
        if isinstance(geom, LineString):
            coords = list(geom.coords)
            for i in range(len(coords) - 1):
                u = coords[i]
                v = coords[i + 1]
                distance = LineString([u, v]).length
                G.add_edge(u, v, weight=distance)
    return G
