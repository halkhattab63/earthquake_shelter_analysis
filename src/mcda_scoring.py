


import geopandas as gpd
import pandas as pd
import numpy as np
import logging
import json
import os

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def load_weights(json_path="data/shelters_with_criteria.json"):
    """Load AHP weights and directions from JSON file."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Weights file not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if all(isinstance(v, (int, float)) for v in data.values()):
            # Assume all positive if only weights given
            return {k: {"weight": v, "direction": "positive"} for k, v in data.items()}
        return data

def min_max_normalize(series):
    """Apply Min-Max normalization to a Pandas Series."""
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

def compute_scores(gdf, weights):
    """
    Compute weighted scores for each site using normalized criteria columns.

    Args:
        gdf (GeoDataFrame): Input GeoDataFrame with normalized criteria.
        weights (dict): Dict with weights and directions.

    Returns:
        GeoDataFrame with additional weighted columns and a final 'score' column.
    """
    weighted_cols = []

    for criterion, config in weights.items():
        norm_col = f"{criterion}_norm"
        weighted_col = f"{criterion}_w"

        if norm_col not in gdf.columns:
            raise KeyError(f"Missing normalized column: {norm_col}")

        weight = float(config["weight"])
        gdf[weighted_col] = gdf[norm_col] * weight
        weighted_cols.append(weighted_col)

    gdf["score"] = gdf[weighted_cols].sum(axis=1)
    return gdf

def normalize_and_score(input_path, output_path, weights_json):
    """
    Normalize input data using AHP weights, compute MCDA scores, and save output.

    Args:
        input_path (str): Path to GeoJSON/GPKG file.
        output_path (str): Where to save the scored data.
        weights_json (str): Path to AHP weights file.
    """
    logging.info(f"🔍 Loading input: {input_path}")
    gdf = gpd.read_file(input_path)
    weights = load_weights(weights_json)

    # Normalize each criterion
    for criterion, config in weights.items():
        if criterion not in gdf.columns:
            raise KeyError(f"Column '{criterion}' not found in input data.")

        series = gdf[criterion]
        if not pd.api.types.is_numeric_dtype(series):
            raise TypeError(f"Column '{criterion}' must be numeric.")

        norm_col = f"{criterion}_norm"
        normalized = min_max_normalize(series)

        if config.get("direction", "positive") == "negative":
            normalized = 1 - normalized

        gdf[norm_col] = normalized

    # Compute weighted scores
    scored_gdf = compute_scores(gdf.copy(), weights)

    # Determine driver format
    driver = "GeoJSON" if output_path.lower().endswith(".geojson") else "GPKG"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save to file
    scored_gdf.to_file(output_path, driver=driver)

    logging.info(f"💾 Scored data saved to: {output_path}")
    logging.info(f"🏆 Max score: {scored_gdf['score'].max():.4f}")
    logging.info(f"📉 Min score: {scored_gdf['score'].min():.4f}")

    return scored_gdf
