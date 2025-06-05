# src/__init__.py

"""
Earthquake Shelter Suitability Package
Contains:
- Data loaders
- AHP analysis
- MCDA scoring
- Map visualizations
- Report generation
"""

# Optional: expose commonly used modules directly
from .config import CRITERIA, RAW_DIR, PROCESSED_DIR, WEIGHTS_PATH
from .load_data import (
    load_shelter_points,
    load_gathering_points,
    load_roads,
    load_fault_lines,
    load_population_density,
    load_land_use,
    load_rivers,
    load_dem
)
