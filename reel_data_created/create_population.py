import os
import osmnx as ox
import geopandas as gpd
import pandas as pd
import sys
from shapely.geometry import Point

sys.stdout.reconfigure(encoding='utf-8')

# 📍 Hedef şehir
place = "Elazığ, Turkey"
os.makedirs("data/processed", exist_ok=True)

# 🏷️ OSM etiketleri
tags = {
    "landuse": ["residential", "commercial", "industrial"]
}

print("🔽 OSM'den yerleşim alanları indiriliyor...")
gdf = ox.features_from_place(place, tags=tags)

# ✅ Sadece Polygon/MultiPolygon geometrileri
gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

# ✅ EPSG:3857'e dönüştürerek alan hesapla
gdf_proj = gdf.to_crs(epsg=3857)
gdf["area_m2"] = gdf_proj.area

# ✅ Nüfus yoğunluğu haritası (kişi/km2) — referansa dayalı tahminler
density_mapping = {
    "residential": 9500,
    "commercial": 3000,
    "industrial": 1200
}

# ✅ Yoğunluk ata
gdf["population_density"] = gdf["landuse"].map(density_mapping).fillna(0)

# ✅ Tahmini nüfus (yoğunluk × alan)
gdf["population_estimate"] = (gdf["population_density"] * gdf["area_m2"]) / 1_000_000  # km² bazında

# ✅ Risk sınıfı (örnek: yoğunluk > 7500 → yüksek risk)
def risk_class(density):
    if density >= 8000:
        return "yüksek"
    elif density >= 4000:
        return "orta"
    elif density > 0:
        return "düşük"
    else:
        return "boş"

gdf["density_level"] = gdf["population_density"].apply(risk_class)

# ✅ EPSG:4326 ile centroid hesapla
centroids_proj = gdf_proj.centroid
gdf["lon"] = centroids_proj.to_crs(epsg=4326).x
gdf["lat"] = centroids_proj.to_crs(epsg=4326).y

# ✅ Centroid'i yeni geometri olarak ata
gdf["geometry"] = centroids_proj.to_crs(epsg=4326)
gdf.set_crs(epsg=4326, inplace=True)

# ✅ Son kolonlar
cols = ["landuse", "area_m2", "population_density", "population_estimate", "density_level", "lat", "lon", "geometry"]
final_gdf = gdf[cols].copy()

# ✅ Dosyaları kaydet
geojson_path = "data/processed/population.geojson"
csv_path = "data/processed/population_summary.csv"
final_gdf.to_file(geojson_path, driver="GeoJSON")
final_gdf.drop(columns="geometry").to_csv(csv_path, index=False)

print(f"✅ Kaydedildi:\n - {geojson_path}\n - {csv_path}")
print(f"📌 Toplam kayıt: {len(final_gdf)}")
print(final_gdf.head())
