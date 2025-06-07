import os
import osmnx as ox
import geopandas as gpd
import pandas as pd
import sys

from shapely.geometry import Point

sys.stdout.reconfigure(encoding='utf-8')

# 📍 المدينة المستهدفة
place = "Elazığ, Turkey"
os.makedirs("data/processed", exist_ok=True)

# 🏷️ أنواع استخدامات الأراضي التي سنطلبها
tags = {
    "landuse": True,  # يجلب جميع الأنواع
    "leisure": True,
    "amenity": True,
    "military": True,
    "natural": True
}

print("🔽 جلب بيانات استخدامات الأراضي من OpenStreetMap...")
gdf = ox.features_from_place(place, tags=tags)

# ✅ فقط مناطق (Polygon/MultiPolygon)
gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

# ✅ تحويل إلى CRS متري لحساب المساحة
gdf_proj = gdf.to_crs(epsg=3857)
gdf["area_m2"] = gdf_proj.area

# ✅ حساب Centroid وتحويله لـ EPSG:4326
centroids = gdf_proj.centroid.to_crs(epsg=4326)
gdf["lon"] = centroids.x
gdf["lat"] = centroids.y

# ✅ تصنيف نوع الأرض تلقائيًا بناءً على الأعمدة
def classify_landuse(row):
    for col in ["landuse", "leisure", "amenity", "natural", "military"]:
        val = row.get(col)
        if pd.notna(val):
            return f"{col}:{val}"
    return "unknown"

gdf["landuse_type"] = gdf.apply(classify_landuse, axis=1)

# ✅ إعطاء درجة خطر تقديرية لكل نوع
def hazard_score(landuse_type):
    if "residential" in landuse_type:
        return 2  # مأهولة - متوسط خطر
    elif "industrial" in landuse_type:
        return 3  # بنية صلبة وخطر ثانوي
    elif "commercial" in landuse_type:
        return 2
    elif "park" in landuse_type or "grass" in landuse_type:
        return 1  # مناسبة للملاجئ
    elif "military" in landuse_type or "cemetery" in landuse_type:
        return 4  # غير مناسبة
    else:
        return 3  # تصنيف احترازي

gdf["hazard_score"] = gdf["landuse_type"].apply(hazard_score)

# ✅ تقييم صلاحية المنطقة كمأوى
gdf["shelter_candidate"] = gdf["area_m2"].apply(lambda a: a > 1000)

# ✅ الأعمدة النهائية
cols = ["landuse_type", "area_m2", "lat", "lon", "hazard_score", "shelter_candidate", "geometry"]
final_gdf = gdf[cols].copy()

# ✅ حفظ النتائج
geojson_path = "data/processed/landuse.geojson"
csv_path = "data/processed/landuse_summary.csv"
final_gdf.to_file(geojson_path, driver="GeoJSON")
final_gdf.drop(columns="geometry").to_csv(csv_path, index=False)

print(f"✅ تم حفظ {geojson_path} و {csv_path}")
print(f"📌 إجمالي السجلات: {len(final_gdf)}")
print(final_gdf.head())
