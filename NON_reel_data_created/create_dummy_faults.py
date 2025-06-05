# create_dummy_faults.py
import geopandas as gpd
from shapely.geometry import LineString
import os

# إنشاء خطوط صدع وهمية مع بعض المعلومات المفيدة
faults_data = {
    "id": [1, 2],
    "name": ["Elazığ Fayı", "Küçük Fay"],
    "activity": ["active", "unknown"],
    "geometry": [
        LineString([(39.215, 38.669), (39.235, 38.679)]),
        LineString([(39.210, 38.660), (39.230, 38.670)])
    ]
}

# إنشاء GeoDataFrame مع نظام koordinat sistemi (WGS 84)
faults_gdf = gpd.GeoDataFrame(faults_data, crs="EPSG:4326")

# التأكد من وجود المجلد
os.makedirs("data/raw", exist_ok=True)

# حفظ البيانات بصيغة GeoJSON
faults_gdf.to_file("data/raw/fault_lines.geojson", driver="GeoJSON")

print(" fault_lines.geojson created successfully with structure.")
