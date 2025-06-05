import os
import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 📍 تحديد المنطقة المستهدفة: Elazığ، تركيا
place = "Elazığ, Turkey"

# 📂 إنشاء مجلد لحفظ البيانات
os.makedirs("data/raw", exist_ok=True)

# 🏙️ تحديد الفلاتر لجلب أنواع استخدامات الأراضي المختلفة
tags = {
    "landuse": ["residential", "industrial", "commercial", "park", "forest", "grass", "meadow"]
}

print("🔽 جلب بيانات استخدامات الأراضي من OpenStreetMap...")
# 🗺️ جلب البيانات من OSM باستخدام الفلاتر المحددة
gdf = ox.features_from_place(place, tags=tags)

# 🧼 تصفية البيانات للاحتفاظ فقط بالهندسة من نوع Polygon أو MultiPolygon
gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

# 📏 تحويل CRS إلى EPSG:3857 لحساب المساحة بدقة
gdf_proj = gdf.to_crs(epsg=3857)
gdf["area_m2"] = gdf_proj.area

# 📍 حساب المركز الهندسي (centroid) لكل مضلع
centroids_proj = gdf_proj.centroid
centroids = gpd.GeoSeries(centroids_proj, crs=3857).to_crs(epsg=4326)

# 🧭 استخراج الإحداثيات الجغرافية للمركز الهندسي
gdf["lat"] = centroids.y
gdf["lon"] = centroids.x

# 🧠 تعيين تصنيف يدوي لكل نوع من استخدامات الأراضي
def classify_landuse(row):
    lu = row.get("landuse", "")
    if lu == "residential":
        return "residential"
    elif lu == "industrial":
        return "industrial"
    elif lu == "commercial":
        return "commercial"
    elif lu == "park":
        return "park"
    elif lu == "forest":
        return "forest"
    elif lu == "grass":
        return "grass"
    elif lu == "meadow":
        return "meadow"
    else:
        return "other"

gdf["landuse_type"] = gdf.apply(classify_landuse, axis=1)

# 🎯 تحديد الأعمدة المطلوبة
final_gdf = gdf[["landuse", "landuse_type", "area_m2", "lat", "lon", "geometry"]].copy()

# 💾 حفظ البيانات بصيغة GeoJSON
output_path = "data/raw/landuse.geojson"
final_gdf.to_file(output_path, driver="GeoJSON")

print(f"✅ تم حفظ ملف landuse.geojson بنجاح. عدد السجلات: {len(final_gdf)}")
print(final_gdf.head())
