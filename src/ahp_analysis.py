import numpy as np
import json
import logging
import pandas as pd

import sys
sys.stdout.reconfigure(encoding='utf-8')

# إعداد السجل
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

RI_VALUES = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
}


def validate_matrix(matrix):
    """
    Validate AHP pairwise comparison matrix for:
    - Square shape
    - Diagonal of 1s
    - Reciprocal symmetry
    """
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("❌ Matrix must be square.")
    
    if not np.allclose(np.diag(matrix), 1.0):
        raise ValueError("❌ Diagonal elements must all be 1.")

    if not np.allclose(matrix, 1 / matrix.T, rtol=1e-3):
        raise ValueError("❌ Matrix must be reciprocal (a_ij = 1 / a_ji).")

    logging.info("✅ Matrix passed validation.")


def normalize_matrix(matrix):
    column_sum = matrix.sum(axis=0)
    return matrix / column_sum


def calculate_weights(normalized_matrix):
    return normalized_matrix.mean(axis=1)


def calculate_consistency_ratio(matrix, weights):
    n = matrix.shape[0]
    weighted_sum = matrix @ weights
    lambda_max = (weighted_sum / weights).mean()
    ci = (lambda_max - n) / (n - 1)
    ri = RI_VALUES.get(n, 1.49)
    cr = ci / ri if ri != 0 else 0
    return round(lambda_max, 4), round(ci, 4), round(cr, 4)


def ahp_from_matrix(matrix, criteria_names):
    logging.info("📊 Starting AHP calculation...")

    validate_matrix(matrix)
    normalized = normalize_matrix(matrix)
    weights = calculate_weights(normalized)
    lambda_max, ci, cr = calculate_consistency_ratio(matrix, weights)

    if cr > 0.1:
        logging.warning(f"❗ High Consistency Ratio: CR = {cr} (> 0.1)")
    else:
        logging.info(f"✔ Acceptable Consistency Ratio: CR = {cr}")

    result = {
        "criteria": criteria_names,
        "weights": weights.round(4).tolist(),
        "λ_max": lambda_max,
        "CI": ci,
        "CR": cr
    }

    return result


def save_ahp_result(result, json_path="data/criteria_weights.json", csv_path="data/criteria_weights.csv"):
    """
    Save AHP result as:
    - JSON (with structure compatible with MCDA)
    - CSV (for inspection)
    """
    # Reformat for MCDA
    structured_weights = {
        criterion: {
            "weight": round(weight, 4),
            "direction": "positive"  # يمكن تعديلها لاحقًا إذا لزم الأمر
        }
        for criterion, weight in zip(result["criteria"], result["weights"])
    }

    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured_weights, f, indent=4, ensure_ascii=False)

    # Save CSV
    df = pd.DataFrame({
        "Criterion": result["criteria"],
        "Weight": result["weights"]
    })
    df["λ_max"] = result["λ_max"]
    df["CI"] = result["CI"]
    df["CR"] = result["CR"]
    df.to_csv(csv_path, index=False)

    logging.info(f"✔ Saved AHP result to {json_path} and {csv_path}")


# ✅ مثال للاستخدام المباشر
if __name__ == "__main__":
    criteria = ["Distance_to_Roads", "Distance_to_Faults", "Population_Density", "LandUse_Score", "estimated_capacity"]

    pairwise_matrix = np.array([
        [1,     3,     5,     7,     1/3],
        [1/3,   1,     3,     5,     1/5],
        [1/5,   1/3,   1,     3,     1/7],
        [1/7,   1/5,   1/3,   1,     1/9],
        [3,     5,     7,     9,     1]
    ])

    result = ahp_from_matrix(pairwise_matrix, criteria)
    save_ahp_result(result)
