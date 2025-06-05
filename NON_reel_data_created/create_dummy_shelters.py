import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os

# بيانات تجريبية لـ 3 ملاجئ
shelters = gpd.GeoDataFrame({
    "id": [1, 2, 3],
    "name": ["Shelter A", "Shelter B", "Shelter C"],
    "geometry": [
        Point(39.222, 38.674),
        Point(39.225, 38.676),
        Point(39.227, 38.672),
    ]
}, crs="EPSG:4326")

# حفظ الملف داخل data/raw
os.makedirs("data/raw", exist_ok=True)
shelters.to_file("data/raw/shelters.geojson", driver="GeoJSON")

print(" shelters.geojson created successfully.")
