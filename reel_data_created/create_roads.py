

import os
import sys
import osmnx as ox
import geopandas as gpd

# 🖥️ UTF-8 destekli çıktı
sys.stdout.reconfigure(encoding='utf-8')

# 📍 Hedef şehir
place_name = "Elazığ, Turkey"

# 🔍 Yol türü filtreleri (OSM'deki highway etiketine göre)
road_types = ["primary", "secondary", "tertiary", "residential"]

print("🔽 OpenStreetMap üzerinden yol verisi indiriliyor...")
gdf = ox.features_from_place(place_name, tags={"highway": True})

# 🛣️ Sadece yol türlerine göre filtreleme (daha az gürültü)
gdf = gdf[gdf["highway"].isin(road_types)]

# ❗ Sadece LineString/MultiLineString geometrilerini al
gdf = gdf[gdf.geometry.type.isin(["LineString", "MultiLineString"])]

# 📏 Uzunluk hesaplamak için metrik sistem (EPSG:3857)
gdf_proj = gdf.to_crs(epsg=3857)
gdf["length_m"] = gdf_proj.geometry.length

# 🧹 Sadece belirli sütunları al (daha sade veri)
columns = ["highway", "name", "geometry", "length_m"]
existing = [col for col in columns if col in gdf.columns]
roads_gdf = gdf[existing].copy()

# Kaydet
os.makedirs("data/raw", exist_ok=True)
output_path = "data/raw/roads.geojson"
roads_gdf.to_file(output_path, driver="GeoJSON")

# Bilgilendirme
print(f"✅ Yol verisi kaydedildi: {output_path}")
print(f"🛣️ Toplam yol kaydı: {len(roads_gdf)}")
print(roads_gdf.head())
