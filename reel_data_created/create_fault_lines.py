import os
import geopandas as gpd
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 📍 Kaynak: Global Plate Boundaries (PB2002)
URL = "https://github.com/fraxen/tectonicplates/raw/master/GeoJSON/PB2002_boundaries.json"
SAVE_PATH = "data/processed/fault_lines_elazig.geojson"
os.makedirs("data/processed", exist_ok=True)

# 📌 Elazığ Bounding Box (yaklaşık)
bbox_elazig = {
    "minx": 39.0,
    "maxx": 39.5,
    "miny": 38.5,
    "maxy": 39.0
}

print("🔽 Fay hattı verisi indiriliyor ve işleniyor...")

# ✅ 1. Veri oku ve EPSG:4326'e çevir
gdf = gpd.read_file(URL)
gdf = gdf.to_crs(epsg=4326)

# ✅ 2. Sadece çizgi (LineString/MultiLineString) türünü filtrele
gdf = gdf[gdf.geometry.type.isin(["LineString", "MultiLineString"])]

# ✅ 3. Elazığ bölgesi ile sınırla
gdf_elazig = gdf.cx[bbox_elazig["minx"]:bbox_elazig["maxx"], bbox_elazig["miny"]:bbox_elazig["maxy"]]

# ✅ 4. Uzunluk (metre) hesapla
gdf_elazig = gdf_elazig.to_crs(epsg=3857)  # metrik projeksiyon
gdf_elazig["length_m"] = gdf_elazig.geometry.length
gdf_elazig = gdf_elazig.to_crs(epsg=4326)  # tekrar coğrafi

# ✅ 5. Tür bilgisi (isteğe bağlı: convergent, transform, vb.)
def classify_fault(name):
    if "Transform" in name:
        return "transform"
    elif "Convergent" in name or "Subduction" in name:
        return "convergent"
    elif "Divergent" in name:
        return "divergent"
    else:
        return "unknown"

if "Name" in gdf_elazig.columns:
    gdf_elazig["fault_type"] = gdf_elazig["Name"].apply(classify_fault)
else:
    gdf_elazig["fault_type"] = "unknown"

# ✅ 6. Son sütunları seç
keep_cols = ["fault_type", "length_m", "geometry"]
final_gdf = gdf_elazig[keep_cols].copy()

# ✅ 7. Kaydet
final_gdf.to_file(SAVE_PATH, driver="GeoJSON")
print(f"✅ Fay verisi kaydedildi: {SAVE_PATH}")
print(f"📌 Elazığ'da bulunan fay hattı sayısı: {len(final_gdf)}")
print(final_gdf.head())
