
import requests
import os
import gzip
import shutil
import sys
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.transform import from_origin

sys.stdout.reconfigure(encoding='utf-8')

# 📍 SRTM veri kaynağı – Elazığ için
url = "https://s3.amazonaws.com/elevation-tiles-prod/skadi/N38/N38E039.hgt.gz"
tile_name = "N38E039"
compressed_file = f"{tile_name}.hgt.gz"
hgt_file = f"{tile_name}.hgt"
tif_file = f"{tile_name}.tif"

# 📂 Dosya yolları
output_dir = "data/raw"
os.makedirs(output_dir, exist_ok=True)

gz_path = os.path.join(output_dir, compressed_file)
hgt_path = os.path.join(output_dir, hgt_file)
tif_path = os.path.join(output_dir, tif_file)

# ✅ Adım 1: İndir
if not os.path.exists(gz_path):
    print("🔽 SRTM verisi indiriliyor...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(gz_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"✅ İndirme tamamlandı: {gz_path}")
    else:
        print(f"❌ İndirme başarısız. Kod: {response.status_code}")
        sys.exit()
else:
    print("📁 Dosya zaten mevcut, tekrar indirme yapılmadı.")

# ✅ Adım 2: Aç (gzip → .hgt)
if not os.path.exists(hgt_path):
    print("📦 GZip dosyası açılıyor...")
    with gzip.open(gz_path, 'rb') as f_in, open(hgt_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"✅ Açma tamamlandı: {hgt_path}")
else:
    print("📂 .hgt dosyası zaten mevcut.")

# ✅ Adım 3: Raster olarak oku ve GeoTIFF’e çevir
print("🗺️ Raster verisi yükleniyor...")
with rasterio.open(
    hgt_path,
    'r',
    driver='SRTMHGT',
) as src:
    data = src.read(1)
    transform = src.transform

    # GeoTIFF olarak yaz
    with rasterio.open(
        tif_path,
        'w',
        driver='GTiff',
        height=src.height,
        width=src.width,
        count=1,
        dtype=data.dtype,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(data, 1)

    print(f"✅ GeoTIFF olarak kaydedildi: {tif_path}")
    print(f"📏 Boyut: {src.width}x{src.height}, CRS: {src.crs}")

# ✅ Adım 4: Görselleştir
plt.figure(figsize=(8, 6))
plt.imshow(data, cmap='terrain')
plt.colorbar(label="Yükseklik (metre)")
plt.title("Elazığ Yükseklik Verisi (SRTM)")
plt.tight_layout()
plt.show()








