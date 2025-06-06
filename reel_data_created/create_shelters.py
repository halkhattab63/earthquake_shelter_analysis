
import os
import sys
import osmnx as ox
import geopandas as gpd

import pandas as pd
from shapely.geometry import Polygon, MultiPolygon

# 🖥️ دعم UTF-8 للطباعة في الطرفية
sys.stdout.reconfigure(encoding='utf-8')

# 📍 المنطقة المستهدفة
place_name = "Elazığ, Turkey"

# 🏷️ فلاتر OpenStreetMap
tags = {
    "leisure": "park",
    "landuse": "grass",
    "emergency": "shelter",
    "amenity": "shelter"
}

print("🔽 OpenStreetMap verisi indiriliyor...")

# 📥 جلب البيانات
gdf = ox.features_from_place(place_name, tags=tags)

# ❗ تصفية لـ Polygon و MultiPolygon فقط
gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

# 🗺️ التحويل إلى إسقاط متري لحساب المساحة
gdf_proj = gdf.to_crs(epsg=3857)
gdf["area_m2"] = gdf_proj.geometry.area

# 🧹 إزالة المناطق الصغيرة (< 300 m²)
gdf = gdf[gdf["area_m2"] >= 300]

# 🔄 العودة إلى EPSG:4326
gdf = gdf.to_crs(epsg=4326)

# ➕ حساب Centroid بصيغة WKT
gdf["centroid_wkt"] = gdf_proj.centroid.to_crs(epsg=4326).to_wkt()

# 🏷️ تحديد نوع المأوى يدويًا
def classify_shelter(row):
    if pd.notna(row.get("emergency")) or pd.notna(row.get("amenity")):
        return "emergency"
    elif pd.notna(row.get("leisure")):
        return "park"
    elif pd.notna(row.get("landuse")):
        return "grass_area"
    else:
        return "unknown"

gdf["shelter_type"] = gdf.apply(classify_shelter, axis=1)

# 🏷️ إنشاء اسم مأوى افتراضي
gdf["name"] = gdf["shelter_type"].str.title() + " Shelter"

# 🧱 الأعمدة النهائية المطلوبة
columns = ["name", "shelter_type", "leisure", "landuse", "emergency", "amenity", "geometry", "centroid_wkt", "area_m2"]
existing_cols = [col for col in columns if col in gdf.columns]
final_gdf = gdf[existing_cols].copy()

# 💾 الحفظ في ملف GeoJSON
os.makedirs("data/raw", exist_ok=True)
output_path = "data/raw/shelters_from_osm.geojson"
final_gdf.to_file(output_path, driver="GeoJSON")

# 📊 إحصائيات
print(f"✅ Veriler başarıyla kaydedildi: {output_path}")
print(f"📌 Toplam kayıt: {len(final_gdf)}")
print(final_gdf.head())
