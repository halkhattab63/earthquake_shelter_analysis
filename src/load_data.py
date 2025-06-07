import os
import logging
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# === Directory Configuration ===
RAW_DIR = "data/raw"
SUPPORTED_EXTENSIONS = [".geojson", ".csv", ".tif"]

# === CRS Configuration ===
DEFAULT_CRS = "EPSG:4326"  # WGS 84

# === Utility ===

def _full_path(filename: str) -> str:
    """Generate full path for a file in raw data directory."""
    path = os.path.join(RAW_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found: {path}")
    return path

def _load_vector_data(filename: str, crs: str = DEFAULT_CRS) -> gpd.GeoDataFrame:
    """Generic loader for vector GeoJSON data."""
    path = _full_path(filename)
    logging.info(f"📍 Loading vector data from: {path}")
    gdf = gpd.read_file(path)
    if gdf.crs and gdf.crs.to_string() != crs:
        gdf = gdf.to_crs(crs)
    return gdf

def _load_csv(filename: str) -> pd.DataFrame:
    """Generic CSV loader."""
    path = _full_path(filename)
    logging.info(f"📊 Loading CSV from: {path}")
    return pd.read_csv(path)

# === Data Loaders ===

def load_shelter_points() -> gpd.GeoDataFrame:
    return _load_vector_data("shelters_from_osm.geojson")

def load_gathering_points() -> gpd.GeoDataFrame:
    return _load_vector_data("gathering_points.geojson")

def load_roads() -> gpd.GeoDataFrame:
    return _load_vector_data("roads.geojson")

def load_fault_lines() -> gpd.GeoDataFrame:
    return _load_vector_data("fault_lines.geojson")

def load_population_density() -> pd.DataFrame:
    return _load_csv("population.csv")

def load_land_use() -> gpd.GeoDataFrame:
    return _load_vector_data("landuse.geojson")

def load_rivers() -> gpd.GeoDataFrame:
    return _load_vector_data("rivers.geojson")

def load_dem_path() -> str:
    """Return DEM raster path (to be read externally via rasterio)."""
    path = _full_path("dem.tif")
    logging.info(f"🗺️ DEM path resolved: {path}")
    return path
