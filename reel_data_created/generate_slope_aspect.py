import os
import numpy as np
import rasterio
from rasterio import windows
from rasterio.enums import Resampling
from rasterio.plot import show
import matplotlib.pyplot as plt

import sys
sys.stdout.reconfigure(encoding='utf-8')
# 📁 Giriş ve çıkış dosyaları
input_path = "data/raw/N38E039_dem.tif"
slope_path = "data/processed/slope.tif"
aspect_path = "data/processed/aspect.tif"
os.makedirs("data/processed", exist_ok=True)

# ✅ Yardımcı fonksiyonlar: Slope ve Aspect hesaplama
def calculate_slope_aspect(dem, transform):
    x, y = np.gradient(dem, transform[0], transform[4])

    # slope in radians → sonra ° veya %'ye çevrilebilir
    slope_rad = np.arctan(np.sqrt(x**2 + y**2))
    slope_deg = np.degrees(slope_rad)        # derece cinsinden
    slope_percent = np.tan(slope_rad) * 100  # yüzde cinsinden

    # Aspect hesaplama (derece cinsinden)
    aspect = np.degrees(np.arctan2(-x, y))
    aspect = np.where(aspect < 0, 90.0 - aspect, 360.0 - aspect + 90.0)
    aspect = np.where(dem == np.nan, np.nan, aspect)  # nodata maskesi

    return slope_deg, aspect

# ✅ Raster verisini oku ve analiz et
print("🗺️ DEM verisi okunuyor...")
with rasterio.open(input_path) as src:
    dem = src.read(1).astype("float32")
    dem[dem == src.nodata] = np.nan
    transform = src.transform
    profile = src.profile

    print("🧮 Slope ve aspect hesaplanıyor...")
    slope, aspect = calculate_slope_aspect(dem, transform)

    # 📤 Slope kaydet (° cinsinden)
    profile.update(dtype='float32', count=1, compress='lzw')
    with rasterio.open(slope_path, 'w', **profile) as dst:
        dst.write(slope, 1)
    print(f"✅ slope.tif kaydedildi: {slope_path}")

    # 📤 Aspect kaydet (°)
    with rasterio.open(aspect_path, 'w', **profile) as dst:
        dst.write(aspect, 1)
    print(f"✅ aspect.tif kaydedildi: {aspect_path}")

# ✅ Görselleştirme
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.imshow(slope, cmap="terrain")
plt.title("Eğim Haritası (Slope °)")
plt.colorbar(label="Eğim (derece)")

plt.subplot(1, 2, 2)
plt.imshow(aspect, cmap="twilight")
plt.title("Yön Haritası (Aspect °)")
plt.colorbar(label="Yön (0–360°)")

plt.tight_layout()
plt.show()
