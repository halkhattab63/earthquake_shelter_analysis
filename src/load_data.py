import os
import logging
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Define the path to raw data
RAW_DIR = "data/raw"

def check_file_exists(path):
    """Check if a file exists, raise an error if not found."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found: {path}")

def load_shelter_points(filename="shelters.geojson"):
    """
    Load shelter points from a GeoJSON file.
    Returns:
        GeoDataFrame: Shelter locations.
    """
    path = os.path.join(RAW_DIR, filename)
    check_file_exists(path)
    logging.info(f"Loading shelters from: {path}")
    return gpd.read_file(path)

def load_gathering_points(filename="gathering_points.geojson"):
    """
    Load gathering points from a GeoJSON file.
    Returns:
        GeoDataFrame: Gathering point locations.
    """
    path = os.path.join(RAW_DIR, filename)
    check_file_exists(path)
    logging.info(f"Loading gathering points from: {path}")
    return gpd.read_file(path)

def load_roads(filename="roads.geojson"):
    """
    Load road network from a GeoJSON file.
    Returns:
        GeoDataFrame: Road geometries.
    """
    path = os.path.join(RAW_DIR, filename)
    check_file_exists(path)
    logging.info(f"Loading roads from: {path}")
    return gpd.read_file(path)

def load_fault_lines(filename="fault_lines.geojson"):
    """
    Load fault lines from a GeoJSON file.
    Returns:
        GeoDataFrame: Fault line geometries.
    """
    path = os.path.join(RAW_DIR, filename)
    check_file_exists(path)
    logging.info(f"Loading fault lines from: {path}")
    return gpd.read_file(path)

def load_population_density(filename="population.csv"):
    """
    Load population density from a CSV file.
    Returns:
        DataFrame: Population statistics.
    """
    path = os.path.join(RAW_DIR, filename)
    check_file_exists(path)
    logging.info(f"Loading population density from: {path}")
    return pd.read_csv(path)

def load_land_use(filename="landuse.geojson"):
    """
    Load land use data from a GeoJSON file.
    Returns:
        GeoDataFrame: Land use classification.
    """
    path = os.path.join(RAW_DIR, filename)
    check_file_exists(path)
    logging.info(f"Loading land use from: {path}")
    return gpd.read_file(path)

def load_rivers(filename="rivers.geojson"):
    """
    Load river and waterway data from a GeoJSON file.
    Returns:
        GeoDataFrame: River geometries.
    """
    path = os.path.join(RAW_DIR, filename)
    check_file_exists(path)
    logging.info(f"Loading rivers from: {path}")
    return gpd.read_file(path)

def load_dem(filename="dem.tif"):
    """
    Load path to Digital Elevation Model (DEM) raster file.
    Returns:
        str: File path to the DEM raster.
    """
    path = os.path.join(RAW_DIR, filename)
    check_file_exists(path)
    logging.info(f"DEM file path: {path}")
    return path  # Will be read using rasterio externally
