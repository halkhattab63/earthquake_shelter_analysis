

import sys
sys.stdout.reconfigure(encoding='utf-8')


import os
import logging
import numpy as np
import geopandas as gpd

from src import config
from src.load_data import load_shelter_points
from src.ahp_analysis import ahp_from_matrix, save_weights_to_json
from src.mcda_scoring import normalize_and_score
from src.map_visualizer import visualize_shelters
from src.report_generator import generate_reports

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def run_workflow():
    """
    Main workflow to process and evaluate earthquake shelter suitability.
    Steps:
        1. Load data
        2. Perform AHP analysis
        3. Normalize and score shelters
        4. Visualize results
        5. Generate reports
    """
    logging.info(" Loading enriched shelter data...")
    gdf = gpd.read_file(config.SHELTER_INPUT)

    # AHP Matrix Definition
    criteria = config.CRITERIA
    ahp_matrix = np.array([
        [1,     3,     5,     7,     5],
        [1/3,   1,     3,     5,     3],
        [1/5, 1/3,     1,     3,     2],
        [1/7, 1/5, 1/3,     1,   1/2],
        [1/5, 1/3, 1/2,     2,     1]
    ])

    # Step 1: AHP Weight Calculation
    logging.info(" Running AHP analysis...")
    weights = ahp_from_matrix(ahp_matrix, criteria)
    save_weights_to_json(weights, config.WEIGHTS_PATH)

    # Step 2: MCDA Scoring
    logging.info(" Calculating MCDA scores...")
    scored_gdf = normalize_and_score(
        input_path=config.SHELTER_INPUT,
        output_path=config.SCORED_OUTPUT,
        weights_json=config.WEIGHTS_PATH
    )

        # Step 3: Interactive Map Visualization
    logging.info("🗺️ Creating interactive suitability map...")
    visualize_shelters(
        gdf=scored_gdf,
        output_path=os.path.join(config.MAPS_DIR, "shelter_map.html"),
        additional_layers={
            config.ROADS_PATH: {
                "name": "Roads",
                "style_function": lambda x: {"color": "blue", "weight": 1.5, "opacity": 0.5}
            },
            config.FAULT_LINES_PATH: {
                "name": "Fault Lines",
                "style_function": lambda x: {"color": "red", "weight": 2, "opacity": 0.6}
            }
        }
    )


    # # Step 4: Generate Individual Reports
    # logging.info(" Generating PDF/HTML reports per shelter...")
    # generate_reports(scored_gdf, output_dir=config.REPORTS_DIR)

    # logging.info(" All steps completed successfully.")

if __name__ == "__main__":
    run_workflow()
