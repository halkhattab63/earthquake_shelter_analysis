import geopandas as gpd
from shapely.geometry import LineString
import os

# إنشاء بيانات طرق واقعية أكثر
roads_data = {
    "id": [1, 2, 3],
    "name": ["Ana Cadde", "Yan Yol", "Çevre Yolu"],
    "type": ["primary", "secondary", "tertiary"],
    "geometry": [
        LineString([(39.220, 38.670), (39.230, 38.675)]),
        LineString([(39.218, 38.672), (39.228, 38.678)]),
        LineString([(39.225, 38.665), (39.240, 38.680)])
    ]
}

# إنشاء GeoDataFrame
roads_gdf = gpd.GeoDataFrame(roads_data, crs="EPSG:4326")

# إنشاء المجلد إذا لم يكن موجود
os.makedirs("data/raw", exist_ok=True)

# حفظ الملف بصيغة GeoJSON
roads_gdf.to_file("data/raw/roads.geojson", driver="GeoJSON")

print(" roads.geojson created successfully with proper structure.")
