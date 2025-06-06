import numpy as np
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def normalize_matrix(matrix):
    """
    Normalize a pairwise comparison matrix by column-wise division.

    Args:
        matrix (np.ndarray): Raw pairwise comparison matrix.

    Returns:
        np.ndarray: Normalized matrix.
    """
    column_sum = matrix.sum(axis=0)
    return matrix / column_sum

def calculate_weights(normalized_matrix):
    """
    Calculate AHP weights as the average of rows.

    Args:
        normalized_matrix (np.ndarray): Normalized comparison matrix.

    Returns:
        np.ndarray: Array of weights.
    """
    return normalized_matrix.mean(axis=1)

def calculate_consistency_ratio(matrix, weights):
    """
    Calculate the consistency ratio (CR) of an AHP matrix.

    Args:
        matrix (np.ndarray): Raw comparison matrix.
        weights (np.ndarray): Computed weights.

    Returns:
        float: Consistency Ratio (CR).
    """
    n = matrix.shape[0]
    ri_values = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
                 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    weighted_sum = matrix @ weights
    lambda_max = (weighted_sum / weights).mean()
    ci = (lambda_max - n) / (n - 1)
    ri = ri_values.get(n, 1.49)
    cr = ci / ri if ri != 0 else 0
    return round(cr, 3)

def ahp_from_matrix(matrix, criteria_names):
    """
    Perform full AHP calculation from a comparison matrix.

    Args:
        matrix (np.ndarray): Pairwise comparison matrix.
        criteria_names (list): Names of the criteria.

    Returns:
        dict: Dictionary of criteria weights.
    """
    logging.info("Starting AHP calculation...")
    normalized = normalize_matrix(matrix)
    weights = calculate_weights(normalized)
    cr = calculate_consistency_ratio(matrix, weights)

    if cr > 0.1:
        logging.warning(f"❗ High consistency ratio detected: CR = {cr} (> 0.1)")
    else:
        logging.info(f"✔ Consistency ratio is acceptable: CR = {cr}")

    weights_dict = dict(zip(criteria_names, weights.round(4)))
    return weights_dict

def save_weights_to_json(weights_dict, output_path="data/criteria_weights.json"):
    """
    Save AHP weights to a JSON file.

    Args:
        weights_dict (dict): Criteria and their weights.
        output_path (str): Output path for the JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(weights_dict, f, indent=4)
    logging.info(f"✔ Weights saved to {output_path}")



# import sys


# sys.stdout.reconfigure(encoding='utf-8')


# import numpy as np
# import json
# import logging
# from pathlib import Path

# # إعدادات اللوج
# logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# def normalize_matrix(matrix):
#     """تطبيع مصفوفة المقارنة الزوجية."""
#     column_sum = matrix.sum(axis=0)
#     return matrix / column_sum

# def calculate_weights(normalized_matrix):
#     """حساب الأوزان كمتوسط للصفوف."""
#     return normalized_matrix.mean(axis=1)

# def calculate_consistency_ratio(matrix, weights):
#     """حساب نسبة الاتساق (CR) لمصفوفة AHP."""
#     n = matrix.shape[0]
#     ri_values = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
#                  6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
#     weighted_sum = matrix @ weights
#     lambda_max = (weighted_sum / weights).mean()
#     ci = (lambda_max - n) / (n - 1)
#     ri = ri_values.get(n, 1.49)
#     cr = ci / ri if ri != 0 else 0
#     return round(cr, 3)

# def ahp_from_matrix(matrix, criteria_names):
#     """تنفيذ حساب AHP كامل من مصفوفة المقارنة."""
#     logging.info("بدء حساب AHP...")
#     normalized = normalize_matrix(matrix)
#     weights = calculate_weights(normalized)
#     cr = calculate_consistency_ratio(matrix, weights)

#     if cr > 0.1:
#         logging.warning(f"❗ تم اكتشاف نسبة اتساق عالية: CR = {cr} (> 0.1)")
#     else:
#         logging.info(f"✔ نسبة الاتساق مقبولة: CR = {cr}")

#     weights_dict = dict(zip(criteria_names, weights.round(4)))
#     return weights_dict

# def save_weights_to_json(weights_dict, output_path="data/processed/shelters_with_criteria.json"):
#     """حفظ أوزان AHP في ملف JSON."""
#     output_path = Path(output_path)
#     output_path.parent.mkdir(parents=True, exist_ok=True)
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(weights_dict, f, indent=4)
#     logging.info(f"✔ تم حفظ الأوزان في {output_path}")
