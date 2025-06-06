
import os
import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 📍 Hedef şehir: Elazığ
place = "Elazığ, Turkey"

# 📂 Klasör oluştur
os.makedirs("data/geo", exist_ok=True)

# 🏙️ Şehir alanlarını çek (residential, commercial, industrial vs.)
tags = {
    "landuse": ["residential", "commercial", "industrial"]
}

print("🔽 OSM'den yerleşim alanları indiriliyor...")
gdf = ox.features_from_place(place, tags=tags)

# 🧼 Sadece Polygon geometrilerini al
gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

# 📏 Alan hesaplamak için EPSG:3857'e çevir
gdf_proj = gdf.to_crs(epsg=3857)
gdf["area_m2"] = gdf_proj.area

# 🧮 Yoğunluk tahmini (kişi/km²)
density_mapping = {
    "residential": 10000,
    "commercial": 3000,
    "industrial": 1000
}

# 🧠 Tahmini yoğunlukları ata
def estimate_density(row):
    return density_mapping.get(row.get("landuse"), 0)

gdf["population_density"] = gdf.apply(estimate_density, axis=1)

# 🧮 Nüfus = Yoğunluk * Alan (km² cinsine çevir)
gdf["population_estimate"] = (gdf["population_density"] * gdf["area_m2"]) / 1_000_000

# 📍 Temsilci nokta (centroid) - EPSG:3857'de hesapla, EPSG:4326'a çevir
centroids_proj = gdf_proj.centroid
centroids = gpd.GeoSeries(centroids_proj, crs=3857).to_crs(epsg=4326)

# Yeni geometri olarak centroid'leri kullan
gdf["geometry"] = centroids
gdf = gdf.set_geometry("geometry")
gdf.set_crs(epsg=4326, inplace=True)

# 🎯 Son kolonları filtrele
final_gdf = gdf[["landuse", "area_m2", "population_density", "population_estimate", "geometry"]].copy()

# 💾 GeoJSON olarak kaydet
output_path = "data/geo/population.geojson"
final_gdf.to_file(output_path, driver="GeoJSON")

print(f"✅ population.geojson başarıyla kaydedildi. Kayıt sayısı: {len(final_gdf)}")
print(final_gdf.head())
