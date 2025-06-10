import folium
import geopandas as gpd
import branca.colormap as cm
import logging
import os

# إعداد سجل التشغيل
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def create_colormap(min_score, max_score):
    """Create color map from red (bad) to green (good)."""
    return cm.linear.RdYlGn_09.scale(min_score, max_score).to_step(n=10)


def add_geojson_layer(fmap, gdf, name, style_function):
    """Add a vector layer with tooltip."""
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
    additional_layers=None,
    show_labels=False,
):
    """Visualize shelters with MCDA score and relevant infrastructure on an interactive map."""

    # Load shelters
    if gdf is None:
        logging.info("📍 Loading shelters...")
        if not os.path.exists(shelter_path):
            raise FileNotFoundError(f"❌ Shelter file not found: {shelter_path}")
        gdf = gpd.read_file(shelter_path)
    else:
        logging.info("📍 Using GeoDataFrame from memory...")

    if "score" not in gdf.columns:
        raise ValueError("GeoDataFrame must include a 'score' column.")

    # Reproject if needed
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Map center
    center = gdf.unary_union.centroid
    fmap = folium.Map(location=[center.y, center.x], zoom_start=12, tiles="CartoDB positron")

    # Color scale
    min_score = gdf["score"].min()
    max_score = gdf["score"].max()
    colormap = create_colormap(min_score, max_score)

    # Add shelters as circles
    logging.info("🖍️ Drawing shelter points...")
    for _, row in gdf.iterrows():
        score = row["score"]
        coords = row.geometry.centroid

        popup_info = f"""
        <b>🏕️ Shelter Info</b><br>
        📊 Score: <b>{round(score, 3)}</b><br>
        🛣️ Distance to Roads: {round(row.get('Distance_to_Roads', 0), 2)} m<br>
        🌋 Distance to Faults: {round(row.get('Distance_to_Faults', 0), 2)} m<br>
        👥 Population Density: {round(row.get('Population_Density', 0), 2)}<br>
        🏞️ Land Use Score: {round(row.get('LandUse_Score', 0), 2)}<br>
        """
        if "Slope" in row:
            popup_info += f"⛰️ Slope: {round(row.get('Slope', 0), 2)}<br>"

        folium.CircleMarker(
            location=[coords.y, coords.x],
            radius=6 + 3 * ((score - min_score) / (max_score - min_score + 1e-6)),  # dynamic radius
            color="black",
            weight=0.5,
            fill=True,
            fill_color=colormap(score),
            fill_opacity=0.9,
            popup=folium.Popup(popup_info, max_width=300)
        ).add_to(fmap)

        if show_labels:
            folium.Marker(
                location=[coords.y, coords.x],
                icon=folium.DivIcon(html=f"<div style='font-size:10px;'>{round(score,2)}</div>")
            ).add_to(fmap)

    logging.info(f"✅ Total shelters plotted: {len(gdf)}")

    # Fault lines
    if os.path.exists(faults_path):
        logging.info("🌋 Adding fault lines...")
        faults = gpd.read_file(faults_path)
        add_geojson_layer(
            fmap, faults, "Fault Lines",
            style_function=lambda _: {"color": "red", "weight": 2, "opacity": 0.7}
        )

    # Roads
    if os.path.exists(roads_path):
        logging.info("🛣️ Adding roads...")
        roads = gpd.read_file(roads_path)
        add_geojson_layer(
            fmap, roads, "Roads",
            style_function=lambda _: {"color": "blue", "weight": 1.5, "opacity": 0.5}
        )

    # Additional layers
    if additional_layers:
        for layer_path, config in additional_layers.items():
            if os.path.exists(layer_path):
                name = config.get("name", os.path.basename(layer_path))
                style_fn = config.get("style_function", lambda _: {"color": "gray", "weight": 1})
                layer_data = gpd.read_file(layer_path)
                add_geojson_layer(fmap, layer_data, name, style_fn)
            else:
                logging.warning(f"⚠️ Layer not found: {layer_path}")

    # Legend and controls
    colormap.caption = "Shelter Suitability Score"
    fmap.add_child(colormap)
    folium.LayerControl().add_to(fmap)

    # Save map
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fmap.save(output_path)
    logging.info(f"🗺️ Map saved to: {output_path}")


# def show_path_on_map(path_coords, output_path="outputs/maps/evacuation_path.html"):
#     fmap = folium.Map(location=path_coords[0][::-1], zoom_start=13, tiles="CartoDB positron")
    
#     folium.PolyLine(
#         locations=[(y, x) for x, y in path_coords],  # (lat, lon)
#         color="blue",
#         weight=4,
#         opacity=0.8,
#         tooltip="Evacuation Route"
#     ).add_to(fmap)

#     folium.Marker(
#         location=path_coords[0][::-1],
#         icon=folium.Icon(color="green", icon="user"),
#         tooltip="Start Point"
#     ).add_to(fmap)

#     folium.Marker(
#         location=path_coords[-1][::-1],
#         icon=folium.Icon(color="red", icon="info-sign"),
#         tooltip="Shelter"
#     ).add_to(fmap)

#     fmap.save(output_path)
#     print(f"✅ Evacuation path map saved to: {output_path}")
