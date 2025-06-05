# import folium
# import geopandas as gpd
# import branca.colormap as cm
# import logging

# # Logging config
# logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# def create_colormap(min_score, max_score):
#     """
#     Create a linear color map from red (low) to green (high).
#     """
#     return cm.linear.RdYlGn_09.scale(min_score, max_score).to_step(index=[min_score, (min_score+max_score)/2, max_score])

# def visualize_shelters(gdf, output_path="outputs/maps/shelter_map.html"):
#     """
#     Create a Folium map showing shelters with their suitability score.

#     Args:
#         gdf (GeoDataFrame): Must contain 'geometry' and 'score' columns.
#         output_path (str): Path to save the HTML map.
#     """
#     if "score" not in gdf.columns:
#         raise ValueError("GeoDataFrame must contain a 'score' column.")
    
#     # Create base map centered around mean location
#     center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]
#     fmap = folium.Map(location=center, zoom_start=12, tiles="cartodbpositron")
    
#     # Define color map
#     min_score = gdf["score"].min()
#     max_score = gdf["score"].max()
#     colormap = create_colormap(min_score, max_score)

#     # Add points to map
#     for _, row in gdf.iterrows():
#         score = row["score"]
#         popup = folium.Popup(f"Suitability Score: {round(score, 3)}", max_width=250)
#         folium.CircleMarker(
#             location=[row.geometry.y, row.geometry.x],
#             radius=6,
#             color=colormap(score),
#             fill=True,
#             fill_color=colormap(score),
#             fill_opacity=0.8,
#             popup=popup
#         ).add_to(fmap)

#     # Add legend
#     colormap.caption = "Shelter Suitability Score"
#     fmap.add_child(colormap)

#     # Save map
#     fmap.save(output_path)
#     logging.info(f"🗺️ Map saved to: {output_path}")

import folium
import geopandas as gpd
import branca.colormap as cm
import logging
import os

# إعداد سجل التشغيل
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def create_colormap(min_score, max_score):
    """Create a stepped color map from red to green based on score range."""
    return cm.linear.RdYlGn_09.scale(min_score, max_score).to_step(n=10)

def add_geojson_layer(fmap, gdf, name, style_function):
    """Helper to add optional GeoJSON layer to the map."""
    fields = [col for col in gdf.columns if col != "geometry"]
    folium.GeoJson(
        gdf,
        name=name,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=fields, aliases=[f"{col}:" for col in fields])
    ).add_to(fmap)

def visualize_shelters(
    gdf=None,
    shelter_path="data/processed/shelters_with_score.geojson",
    roads_path="data/raw/roads.geojson",
    faults_path="data/raw/fault_lines.geojson",
    output_path="outputs/maps/shelter_map.html",
    additional_layers=None
):
    """Generate an interactive Folium map with shelters, roads, fault lines, and optional layers."""

    # Load shelter data
    if gdf is None:
        logging.info("📍 Loading shelter data from file...")
        if not os.path.exists(shelter_path):
            raise FileNotFoundError(f"Shelter file not found: {shelter_path}")
        gdf = gpd.read_file(shelter_path)
    else:
        logging.info("📍 Using in-memory GeoDataFrame...")

    if "score" not in gdf.columns:
        raise ValueError("GeoDataFrame must contain a 'score' column.")

    # Initialize base map
    center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]
    fmap = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")

    # Color map
    min_score = gdf["score"].min()
    max_score = gdf["score"].max()
    colormap = create_colormap(min_score, max_score)

    # Add shelter points
    logging.info("🖍️ Adding shelters...")
    for _, row in gdf.iterrows():
        score = row["score"]
        popup_text = f"""
        <b>Shelter Information</b><br>
        Score: {round(score, 3)}<br>
        Distance to Roads: {round(row.get('Distance_to_Roads', 0), 2)} m<br>
        Distance to Faults: {round(row.get('Distance_to_Faults', 0), 2)} m<br>
        Slope: {round(row.get('Slope', 0), 2)}<br>
        Population Density: {round(row.get('Population_Density', 0), 2)}
        """
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=6,
            color=colormap(score),
            fill=True,
            fill_color=colormap(score),
            fill_opacity=0.85,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(fmap)

    # Add fault lines layer
    if os.path.exists(faults_path):
        logging.info("🌋 Adding fault lines...")
        faults = gpd.read_file(faults_path)
        add_geojson_layer(
            fmap, faults, "Fault Lines",
            style_function=lambda x: {"color": "red", "weight": 2, "opacity": 0.6}
        )

    # Add roads layer
    if os.path.exists(roads_path):
        logging.info("🛣️ Adding roads...")
        roads = gpd.read_file(roads_path)
        add_geojson_layer(
            fmap, roads, "Roads",
            style_function=lambda x: {"color": "blue", "weight": 1.5, "opacity": 0.5}
        )

    # Add any additional layers
    if additional_layers:
        for layer_path, layer_config in additional_layers.items():
            if os.path.exists(layer_path):
                name = layer_config.get("name", os.path.basename(layer_path))
                style_fn = layer_config.get("style_function", lambda x: {"color": "gray", "weight": 1})
                logging.info(f"➕ Adding layer: {name}")
                extra_gdf = gpd.read_file(layer_path)
                add_geojson_layer(fmap, extra_gdf, name, style_fn)
            else:
                logging.warning(f"⚠️ Layer not found: {layer_path}")

    # Add legend and controls
    colormap.caption = "Shelter Suitability Score"
    fmap.add_child(colormap)
    folium.LayerControl().add_to(fmap)

    # Save map
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fmap.save(output_path)
    logging.info(f"✅ Map saved to: {output_path}")
