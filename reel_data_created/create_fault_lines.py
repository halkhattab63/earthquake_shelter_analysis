import os
import geopandas as gpd
import requests
from io import BytesIO
import zipfile
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 🔧 Ayarlar
url = "https://github.com/fraxen/tectonicplates/raw/master/GeoJSON/PB2002_boundaries.json"
save_path = "data/raw/fault_lines.geojson"
bbox_elazig = {
    "minx": 39.0,
    "maxx": 39.5,
    "miny": 38.5,
    "maxy": 39.0
}

# 📁 Klasör oluştur
os.makedirs("data/raw", exist_ok=True)

print("🔽 USGS Tectonic Plates verisi indiriliyor...")
gdf = gpd.read_file(url)

# 📐 Koordinat sistemini EPSG:4326 yap
gdf = gdf.to_crs(epsg=4326)

# 📍 Elazığ çevresine göre filtrele
gdf_elazig = gdf.cx[bbox_elazig["minx"]:bbox_elazig["maxx"], bbox_elazig["miny"]:bbox_elazig["maxy"]]

# 💾 Kaydet
gdf_elazig.to_file(save_path, driver="GeoJSON")

print(f"✅ Fay verisi kaydedildi: {save_path}")
print(f"📌 Kayıt sayısı: {len(gdf_elazig)}")
