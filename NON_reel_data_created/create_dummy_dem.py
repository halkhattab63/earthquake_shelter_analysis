# create_dummy_dem.py
import numpy as np
import rasterio
from rasterio.transform import from_origin
import os

width = height = 100
dem_data = np.random.randint(100, 300, size=(height, width)).astype("float32")
transform = from_origin(39.20, 38.68, 0.0002, 0.0002)  # Xmin, Ymax, pixel size

os.makedirs("data/raw", exist_ok=True)
with rasterio.open(
    "data/raw/dem.tif",
    "w",
    driver="GTiff",
    height=dem_data.shape[0],
    width=dem_data.shape[1],
    count=1,
    dtype="float32",
    crs="EPSG:4326",
    transform=transform,
) as dst:
    dst.write(dem_data, 1)

print(" dem.tif created successfully.")
