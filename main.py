

# src/main.py

import logging
from src.config import WEIGHTS_PATH, SHELTER_INPUT, SCORED_OUTPUT, MAPS_DIR
from src.ahp_analysis import ahp_from_matrix, save_ahp_result
from src.mcda_scoring import normalize_and_score
from src.map_visualizer import visualize_shelters

import numpy as np
import os

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# الخطوة 1: مصفوفة المقارنة الزوجية (تقوم بتعديلها حسب مشروعك)
PAIRWISE_MATRIX = np.array([
    [1,   3,   5,   7],
    [1/3, 1,   3,   5],
    [1/5, 1/3, 1,   3],
    [1/7, 1/5, 1/3, 1]
])
CRITERIA_NAMES = ["Distance_to_Roads", "Distance_to_Faults", "Population_Density", "LandUse_Score"]

def main():
    # 1. حساب الأوزان باستخدام AHP
    ahp_result = ahp_from_matrix(PAIRWISE_MATRIX, CRITERIA_NAMES)
    save_ahp_result(ahp_result, json_path=WEIGHTS_PATH)

    # 2. تطبيق MCDA لحساب الدرجات
    scored_gdf = normalize_and_score(
        input_path=SHELTER_INPUT,
        output_path=SCORED_OUTPUT,
        weights_path=WEIGHTS_PATH,
        export_csv=True
    )

    # 3. إنشاء الخريطة التفاعلية
    visualize_shelters(
        gdf=scored_gdf,
        output_path=os.path.join(MAPS_DIR, "shelter_map.html")
    )

if __name__ == "__main__":
    main()
