import geopandas as gpd
import pandas as pd
import numpy as np
import logging
import json
import os

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def load_weights(json_path="data/criteria_weights.json"):
    """Load AHP weights and their directions from JSON file."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ Weights file not found: {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # If only weights given, assume all directions are "positive"
        if all(isinstance(v, (int, float)) for v in data.values()):
            return {k: {"weight": v, "direction": "positive"} for k, v in data.items()}
        return data

def min_max_normalize(series: pd.Series) -> pd.Series:
    """Apply Min-Max normalization with numeric validation."""
    series = pd.to_numeric(series, errors='coerce')
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

def normalize_criteria(gdf: gpd.GeoDataFrame, weights: dict) -> gpd.GeoDataFrame:
    """Normalize all relevant criteria and handle positive/negative direction."""
    for criterion, config in weights.items():
        if criterion not in gdf.columns:
            raise KeyError(f"❌ Missing criterion column: '{criterion}'")

        # Check for numeric type
        if not pd.api.types.is_numeric_dtype(gdf[criterion]):
            raise TypeError(f"❌ Column '{criterion}' must be numeric for normalization.")

        norm_col = f"{criterion}_norm"
        gdf[norm_col] = min_max_normalize(gdf[criterion])

        # Invert if direction is negative
        if config.get("direction", "positive") == "negative":
            gdf[norm_col] = 1 - gdf[norm_col]

    return gdf

def compute_scores(gdf: gpd.GeoDataFrame, weights: dict) -> gpd.GeoDataFrame:
    """Compute MCDA weighted score for each feature."""
    score_cols = []
    for criterion, config in weights.items():
        norm_col = f"{criterion}_norm"
        weight = float(config["weight"])
        weighted_col = f"{criterion}_w"

        gdf[weighted_col] = gdf[norm_col] * weight
        score_cols.append(weighted_col)

    gdf["score"] = gdf[score_cols].sum(axis=1)
    gdf["rank"] = gdf["score"].rank(ascending=False).astype(int)

    return gdf

def normalize_and_score(input_path, output_path, weights_path="data/criteria_weights.json", export_csv=False):
    """
    Apply MCDA scoring based on AHP weights.

    Args:
        input_path (str): Path to input GeoJSON.
        output_path (str): Output GeoJSON/GPKG path.
        weights_path (str): Path to AHP weights.
        export_csv (bool): Also export to CSV if True.

    Returns:
        GeoDataFrame with scores and ranks.
    """
    logging.info(f"📥 Loading shelters from: {input_path}")
    gdf = gpd.read_file(input_path)
    weights = load_weights(weights_path)

    # Normalize and score
    gdf = normalize_criteria(gdf, weights)
    gdf = compute_scores(gdf, weights)

    # Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    driver = "GeoJSON" if output_path.endswith(".geojson") else "GPKG"
    gdf.to_file(output_path, driver=driver)

    logging.info(f"✅ Output saved to: {output_path}")
    logging.info(f"🏆 Best score: {gdf['score'].max():.4f}")
    logging.info(f"📉 Lowest score: {gdf['score'].min():.4f}")

    # Optional CSV Export
    if export_csv:
        csv_path = output_path.replace(".geojson", ".csv").replace(".gpkg", ".csv")
        gdf.drop(columns="geometry").to_csv(csv_path, index=False)
        logging.info(f"📄 CSV exported to: {csv_path}")

    return gdf
