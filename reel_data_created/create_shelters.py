# import os
# import sys
# import osmnx as ox
# import geopandas as gpd
# import pandas as pd
# from shapely.geometry import Point
# from shapely.geometry import Polygon

# sys.stdout.reconfigure(encoding='utf-8')

# # 📍 Hedef konum
# place = "Elazığ, Turkey"

# # 📁 Çıktı klasörü
# os.makedirs("data/geo", exist_ok=True)

# # 📥 OSM veri filtreleri
# tags = {
#     "emergency": "shelter",
#     "amenity": "shelter",
#     "leisure": "park",
#     "landuse": "grass"
# }

# print("🔽 OSM'den barınak ve yeşil alan verisi indiriliyor...")
# gdf = ox.features_from_place(place, tags=tags)

# # 🧹 Geometri filtresi
# gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

# # 📏 Alan hesaplama için projeksiyon
# gdf_proj = gdf.to_crs(epsg=3857)
# gdf["area_m2"] = gdf_proj.area

# # ⚠️ Alanı çok küçük olanları filtrele
# gdf = gdf[gdf["area_m2"] >= 500]

# # 📍 Merkez koordinat
# centroids = gdf_proj.centroid.to_crs(epsg=4326)
# gdf["lon"] = centroids.x
# gdf["lat"] = centroids.y
# gdf["centroid"] = [Point(xy) for xy in zip(gdf["lon"], gdf["lat"])]

# # 🧠 Kategorize etme
# def classify_shelter(row):
#     if pd.notna(row.get("emergency")) or pd.notna(row.get("amenity")):
#         return "formal_shelter"
#     elif pd.notna(row.get("leisure")):
#         return "public_park"
#     elif pd.notna(row.get("landuse")):
#         return "grass_field"
#     else:
#         return "undefined"

# gdf["shelter_type"] = gdf.apply(classify_shelter, axis=1)

# # ❌ Grass field barınaklarını çıkar
# gdf = gdf[gdf["shelter_type"] != "grass_field"]

# # 🧮 Kapasite tahmini (1 kişi = 3.5 m²)
# gdf["estimated_capacity"] = (gdf["area_m2"] / 3.5).astype(int)

# # 🔢 Uniq shelter isimleri üret
# def generate_unique_name(row, idx):
#     prefix = "Shelter" if row["shelter_type"] == "formal_shelter" else "Park"
#     return f"{prefix}_{idx:03d}"

# gdf = gdf.reset_index(drop=True)
# gdf["name"] = [generate_unique_name(row, idx + 1) for idx, row in gdf.iterrows()]

# # 🧭 CRS dönüşümü
# gdf.set_geometry("geometry", inplace=True)
# gdf.set_crs(epsg=4326, inplace=True)

# # 🧠 Nüfus katmanıyla ilişkilendirme (buffer + spatial join)
# pop_path = "data/processed/population.geojson"
# if os.path.exists(pop_path):
#     print("🔄 population.geojson bulundu, nüfus yoğunluğu eşleştiriliyor...")
#     pop_gdf = gpd.read_file(pop_path).to_crs(epsg=3857)
#     shelters_buffered = gdf.to_crs(epsg=3857).copy()
#     shelters_buffered["geometry"] = shelters_buffered.geometry.buffer(100)  # 100m çevresel etki
#     joined = gpd.sjoin(shelters_buffered, pop_gdf, how="left", predicate="intersects")

#     gdf["nearby_population_density"] = joined["population_density"].fillna(0)
#     gdf["nearby_population_estimate"] = joined["population_estimate"].fillna(0)
# else:
#     print("⚠️ population.geojson bulunamadı, nüfus yoğunluğu eklenmedi.")
#     gdf["nearby_population_density"] = 0
#     gdf["nearby_population_estimate"] = 0

# # 📊 Nihai kolonlar
# final_cols = [
#     "name", "shelter_type", "area_m2", "estimated_capacity",
#     "lat", "lon", "geometry", "centroid",
#     "nearby_population_density", "nearby_population_estimate"
# ]
# gdf_final = gdf[final_cols].copy()

# # 💾 Kaydet
# output_path = "data/geo/shelters.geojson"
# gdf_final.to_file(output_path, driver="GeoJSON")

# # 🧾 Özet
# print(f"✅ shelters.geojson başarıyla kaydedildi. Kayıt sayısı: {len(gdf_final)}")
# print(gdf_final.head())





import os
import sys
import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

sys.stdout.reconfigure(encoding='utf-8')

# 📍 Hedef konum
place = "Elazığ, Turkey"
os.makedirs("data/geo", exist_ok=True)

# 📥 OSM veri filtreleri
tags = {
    "emergency": "shelter",
    "amenity": "shelter",
    "leisure": "park",
    "landuse": "grass"
}

print("🔽 OSM'den barınak ve yeşil alan verisi indiriliyor...")
gdf = ox.features_from_place(place, tags=tags)
gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

# 📏 Alan hesaplama
gdf_proj = gdf.to_crs(epsg=3857)
gdf["area_m2"] = gdf_proj.area
gdf = gdf[gdf["area_m2"] >= 500]

# 📍 Merkez koordinat
centroids = gdf_proj.centroid.to_crs(epsg=4326)
gdf["lon"] = centroids.x
gdf["lat"] = centroids.y
gdf["centroid"] = [Point(xy) for xy in zip(gdf["lon"], gdf["lat"])]

# 🧠 Tür sınıflandırma
def classify_shelter(row):
    if pd.notna(row.get("emergency")) or pd.notna(row.get("amenity")):
        return "formal_shelter"
    elif pd.notna(row.get("leisure")):
        return "public_park"
    elif pd.notna(row.get("landuse")):
        return "grass_field"
    else:
        return "undefined"

gdf["shelter_type"] = gdf.apply(classify_shelter, axis=1)
gdf = gdf[gdf["shelter_type"] != "grass_field"]  # ❌ Remove grass fields

# 🧮 Kapasite (1 kişi = 3.5 m²)
gdf["estimated_capacity"] = (gdf["area_m2"] / 3.5).astype(int)

# 📛 Uniq isim üret
def generate_unique_name(row, idx):
    prefix = "Shelter" if row["shelter_type"] == "formal_shelter" else "Park"
    return f"{prefix}_{idx:03d}"

gdf = gdf.reset_index(drop=True)
gdf["name"] = [generate_unique_name(row, idx + 1) for idx, row in gdf.iterrows()]
gdf.set_crs(epsg=4326, inplace=True)

# 📊 Nüfus bilgisiyle eşleştirme
pop_path = "data/processed/population.geojson"
if os.path.exists(pop_path):
    print("🔄 population.geojson bulundu, analiz başlatılıyor...")
    pop_gdf = gpd.read_file(pop_path).to_crs(epsg=3857)
    shelters_buffered = gdf.to_crs(epsg=3857).copy()
    shelters_buffered["geometry"] = shelters_buffered.geometry.buffer(100)  # 100m etkisi
    joined = gpd.sjoin(shelters_buffered, pop_gdf, how="left", predicate="intersects")

    gdf["nearby_population_density"] = joined["population_density"].fillna(0)
    gdf["nearby_population_estimate"] = joined["population_estimate"].fillna(0)

    # ✅ Tahmini kapsama oranı
    gdf["estimated_coverage_ratio"] = gdf["estimated_capacity"] / gdf["nearby_population_estimate"].replace(0, pd.NA)
else:
    print("⚠️ population.geojson bulunamadı.")
    gdf["nearby_population_density"] = 0
    gdf["nearby_population_estimate"] = 0
    gdf["estimated_coverage_ratio"] = pd.NA

# 📤 Export
final_cols = [
    "name", "shelter_type", "area_m2", "estimated_capacity",
    "lat", "lon", "geometry", "centroid",
    "nearby_population_density", "nearby_population_estimate",
    "estimated_coverage_ratio"
]
gdf_final = gdf[final_cols].copy()
gdf_final.to_file("data/geo/shelters.geojson", driver="GeoJSON")

# 🧾 Özet
print(f"✅ shelters.geojson kaydedildi. Kayıt sayısı: {len(gdf_final)}")
print(gdf_final[["name", "estimated_capacity", "nearby_population_estimate", "estimated_coverage_ratio"]].head())
