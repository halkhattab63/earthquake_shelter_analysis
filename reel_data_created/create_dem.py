import os
import sys
import gzip
import shutil
import requests
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.enums import Resampling
from rasterio.transform import from_origin

# 🖥️ UTF-8 destekli çıktı
sys.stdout.reconfigure(encoding='utf-8')

# 📍 Elazığ için SRTM veri dosyası (1° x 1° aralığı kapsar)
TILE_NAME = "N38E039"
URL = f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/N38/{TILE_NAME}.hgt.gz"

# 📁 Klasörleri tanımla
RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

gz_path = os.path.join(RAW_DIR, f"{TILE_NAME}.hgt.gz")
hgt_path = os.path.join(RAW_DIR, f"{TILE_NAME}.hgt")
tif_path = os.path.join(RAW_DIR, f"{TILE_NAME}_dem.tif")

# ✅ Adım 1: Veri indir
if not os.path.exists(gz_path):
    print("🔽 SRTM verisi indiriliyor...")
    try:
        response = requests.get(URL, stream=True)
        response.raise_for_status()
        with open(gz_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        print("✅ İndirme tamamlandı.")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        sys.exit(1)
else:
    print("📁 Dosya zaten mevcut, tekrar indirilmedi.")

# ✅ Adım 2: GZip dosyasını çıkar
if not os.path.exists(hgt_path):
    print("📦 GZip dosyası açılıyor...")
    with gzip.open(gz_path, 'rb') as f_in, open(hgt_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    print("✅ Çıkartma tamamlandı.")
else:
    print("📂 .hgt dosyası zaten mevcut.")

# ✅ Adım 3: GeoTIFF olarak kaydet
print("🗺️ GeoTIFF oluşturuluyor...")
with rasterio.open(hgt_path, 'r', driver='SRTMHGT') as src:
    data = src.read(1).astype("float32")  # 🔁 fix: convert to float32
    data[data == -32768] = np.nan         # 🚫 handle NODATA
    transform = src.transform

    with rasterio.open(
        tif_path, 'w',
        driver='GTiff',
        height=src.height,
        width=src.width,
        count=1,
        dtype='float32',
        crs='EPSG:4326',
        transform=transform
    ) as dst:
        dst.write(data, 1)


print(f"✅ GeoTIFF kaydedildi: {tif_path}")

# ✅ Adım 4: İstatistik ve Görselleştirme
print("📊 Yükseklik verisi istatistikleri:")
print(f"   ↳ Min: {np.nanmin(data):.2f} m")
print(f"   ↳ Max: {np.nanmax(data):.2f} m")
print(f"   ↳ Mean: {np.nanmean(data):.2f} m")

plt.figure(figsize=(8, 6))
plt.imshow(data, cmap='terrain')
plt.colorbar(label="Yükseklik (m)")
plt.title("Elazığ Sayısal Yükseklik Modeli (DEM)")
plt.tight_layout()
plt.show()



