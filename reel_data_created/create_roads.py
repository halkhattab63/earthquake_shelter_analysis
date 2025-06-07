import os
import sys
import osmnx as ox
import geopandas as gpd
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# 📍 Hedef şehir
place_name = "Elazığ, Turkey"
os.makedirs("data/processed", exist_ok=True)

# 🔍 Yol türü filtresi (OSM highway)
selected_road_types = ["motorway", "trunk", "primary", "secondary", "tertiary", "residential"]

print("🔽 Yol verisi indiriliyor (OpenStreetMap)...")
gdf = ox.features_from_place(place_name, tags={"highway": selected_road_types})

# 🧼 Sadece yol geometrileri
gdf = gdf[gdf.geometry.type.isin(["LineString", "MultiLineString"])]

# 🎯 EPSG:3857 ile uzunluk hesapla
gdf_proj = gdf.to_crs(epsg=3857)
gdf["length_m"] = gdf_proj.length

# 🎯 EPSG:4326 ile analiz uyumu
gdf = gdf.to_crs(epsg=4326)

# 🔢 Yol önceliği belirleme
priority_map = {
    "motorway": 1,
    "trunk": 2,
    "primary": 3,
    "secondary": 4,
    "tertiary": 5,
    "residential": 6
}
gdf["importance"] = gdf["highway"].map(priority_map).fillna(9).astype(int)

# 🎯 Kolonları seç
columns = ["name", "highway", "length_m", "importance", "geometry"]
roads_gdf = gdf[columns].copy()

# 💾 Kaydet
roads_gdf.to_file("data/processed/roads.geojson", driver="GeoJSON")
roads_gdf.drop(columns="geometry").to_csv("data/processed/roads_summary.csv", index=False)

print("✅ Yol verisi başarıyla kaydedildi:")
print(" - GeoJSON:", "data/processed/roads.geojson")
print(" - CSV:", "data/processed/roads_summary.csv")
print(f"🛣️ Toplam yol kaydı: {len(roads_gdf)}")
print(roads_gdf.head())
