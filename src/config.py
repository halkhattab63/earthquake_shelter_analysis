import os

# === Main Directories ===
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "..", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "..", "outputs")
MAPS_DIR = os.path.join(OUTPUTS_DIR, "maps")
REPORTS_DIR = os.path.join(OUTPUTS_DIR, "reports")
WEIGHTS_PATH = os.path.join(DATA_DIR, "criteria_weights.json")

# === MCDA Criteria ===
CRITERIA = [
    "Distance_to_Roads",
    "Distance_to_Faults",
    "Slope",
    "Population_Density",
    "LandUse_Score"
]

# === Map Settings ===
DEFAULT_MAP_CENTER = [38.6740, 39.2230]  # Example: Elazığ, Turkey
DEFAULT_ZOOM = 12

# === File Names ===
SHELTER_INPUT = os.path.join(PROCESSED_DIR, "shelters_with_criteria.geojson")
SCORED_OUTPUT = os.path.join(OUTPUTS_DIR, "results.geojson")


ROADS_PATH = os.path.join(RAW_DIR, "roads.geojson")  # أو اسم الملف الصحيح لديك
DEM_PATH = os.path.join(RAW_DIR, "dem.tif")
POPULATION_PATH = os.path.join(RAW_DIR, "population.tif")
HOSPITALS_PATH = os.path.join(RAW_DIR, "hospitals.geojson")
FAULT_LINES_PATH = os.path.join(RAW_DIR, "fault_lines.geojson")

