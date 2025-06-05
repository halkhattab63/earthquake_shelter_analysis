import os
import geopandas as gpd
import pandas as pd
import pdfkit
import folium
from jinja2 import Environment, FileSystemLoader

# إعداد قالب Jinja2
env = Environment(loader=FileSystemLoader("src/templates"))

def render_report_html(record, template_name="shelter_report.html"):
    """
    Render HTML report for a single shelter using Jinja2 template.

    Args:
        record (dict): Dictionary containing shelter data.
        template_name (str): Name of the HTML template.

    Returns:
        str: Rendered HTML as string.
    """
    template = env.get_template(template_name)
    return template.render(shelter=record)

def generate_mini_map(lat, lon):
    """
    Generate mini Folium map centered at given coordinates.

    Returns:
        str: Path to saved HTML map.
    """
    fmap = folium.Map(location=[lat, lon], zoom_start=14, tiles='OpenStreetMap')
    folium.Marker([lat, lon], tooltip="Shelter").add_to(fmap)
    map_path = f"outputs/maps/mini_map_{lat}_{lon}.html"
    fmap.save(map_path)
    return map_path

def generate_reports(gdf, output_dir="outputs/reports"):
    """
    Generate individual reports for each shelter in the GeoDataFrame.

    Args:
        gdf (GeoDataFrame): Contains shelter data.
        output_dir (str): Directory to save PDF reports.
    """
    os.makedirs(output_dir, exist_ok=True)

    for _, row in gdf.iterrows():
        record = row.to_dict()
        lat, lon = row.geometry.y, row.geometry.x
        map_path = generate_mini_map(lat, lon)
        record['map_path'] = map_path

        html = render_report_html(record)
        html_file = os.path.join(output_dir, f"shelter_{int(row['id'])}.html")
        pdf_file = html_file.replace(".html", ".pdf")

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)

        pdfkit.from_file(html_file, pdf_file)
        print(f"✅ Report generated: {pdf_file}")
