# import geopandas as gpd
# import pandas as pd
# from shapely.geometry import Point
# import os

# # بيانات تجريبية لـ 3 ملاجئ
# shelters = gpd.GeoDataFrame({
#     "id": [1, 2, 3],
#     "name": ["Shelter A", "Shelter B", "Shelter C"],
#     "geometry": [
#         Point(39.222, 38.674),
#         Point(39.225, 38.676),
#         Point(39.227, 38.672),
#     ]
# }, crs="EPSG:4326")

# # حفظ الملف داخل data/raw
# os.makedirs("data/raw", exist_ok=True)
# shelters.to_file("data/raw/shelters.geojson", driver="GeoJSON")

# print(" shelters.geojson created successfully.")



import rasterio
from rasterio.transform import from_origin
import numpy as np
import os
import gzip
import sys
sys.stdout.reconfigure(encoding='utf-8')



# 📂 إعداد المسارات
hgt_path = "data/raw/N38E039.hgt"
tif_path = "data/raw/dem_elazig.tif"

# 🧩 قراءة ملف .hgt (إذا gzip، افتحه باستخدام gzip.open)
with open(hgt_path, "rb") as f:
    data = np.fromfile(f, np.dtype('>i2'), 1201*1201).reshape((1201, 1201))

# 🌍 إعداد geotransform
transform = from_origin(39.0, 39.0, 1/1200.0, 1/1200.0)  # زاوية شمال-غرب، حجم بكسل

# 📝 كتابة إلى GeoTIFF
with rasterio.open(
    tif_path, 'w',
    driver='GTiff',
    height=data.shape[0],
    width=data.shape[1],
    count=1,
    dtype='int16',
    crs='EPSG:4326',
    transform=transform
) as dst:
    dst.write(data, 1)

print("✅ dem_elazig.tif تمت معالجته وكتابته بنجاح.")
