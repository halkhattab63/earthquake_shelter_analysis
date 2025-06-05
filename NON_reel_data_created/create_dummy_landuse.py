# create_dummy_landuse.py
import geopandas as gpd
from shapely.geometry import Polygon
import os

landuse = gpd.GeoDataFrame({
    "type": ["residential", "industrial", "park"],
    "score": [0.9, 0.3, 0.8],
    "geometry": [
        Polygon([(39.221, 38.673), (39.224, 38.673), (39.224, 38.676), (39.221, 38.676)]),
        Polygon([(39.225, 38.670), (39.228, 38.670), (39.228, 38.673), (39.225, 38.673)]),
        Polygon([(39.219, 38.675), (39.222, 38.675), (39.222, 38.678), (39.219, 38.678)])
    ]
}, crs="EPSG:4326")

os.makedirs("data/raw", exist_ok=True)
landuse.to_file("data/raw/landuse.geojson", driver="GeoJSON")

print(" landuse.geojson created successfully.")
