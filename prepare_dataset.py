import os
import logging
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from src import config, load_data

# إعداد اللوج
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
PROJECTED_CRS = "EPSG:32637"  # UTM Zone 37N - مناسب للمنطقة الشرقية من تركيا

def calculate_distance_to_nearest(source_gdf, target_gdf, label):
    """
    حساب أقرب مسافة من كل نقطة في source_gdf إلى أقرب مكان في target_gdf
    """
    target_gdf = target_gdf.to_crs(PROJECTED_CRS)
    source_gdf = source_gdf.to_crs(PROJECTED_CRS)
    source_gdf[label] = source_gdf.geometry.apply(lambda x: target_gdf.distance(x).min())
    return source_gdf.to_crs("EPSG:4326")

def categorize_landuse(gdf, landuse_gdf):
    """
    تصنيف استخدام الأرض ومنح نقاط لكل نوع
    """
    landuse_gdf = landuse_gdf.to_crs(gdf.crs)

    def get_score(point):
        for _, row in landuse_gdf.iterrows():
            if row.geometry.contains(point):
                land_type = str(row.get("landuse", "")).lower()
                if "park" in land_type:
                    return 0.9
                elif "residential" in land_type:
                    return 0.5
                elif "industrial" in land_type:
                    return 0.3
                else:
                    return 0.2
        return 0.1  # default low score for undefined areas

    gdf["LandUse_Score"] = gdf.geometry.apply(get_score)
    return gdf

def match_population_density(gdf, pop_gdf):
    """
    ربط نقاط الملاجئ بالكثافة السكانية القريبة
    """
    if not all(pop_gdf.geometry.type == "Point"):
        raise ValueError("❌ ملف الكثافة السكانية يجب أن يحتوي فقط على هندسة من النوع Point.")

    gdf_proj = gdf.to_crs(PROJECTED_CRS)
    pop_proj = pop_gdf.to_crs(PROJECTED_CRS)

    joined = gpd.sjoin_nearest(gdf_proj, pop_proj, how="left", distance_col="pop_dist")
    joined = joined.reset_index(drop=True)
    gdf_proj = gdf_proj.reset_index(drop=True)

    if "population_density" in joined.columns:
        gdf_proj["Population_Density"] = joined["population_density"].fillna(joined["population_density"].mean())
    elif "population_estimate" in joined.columns:
        gdf_proj["Population_Density"] = joined["population_estimate"].fillna(joined["population_estimate"].mean())
    else:
        logging.warning("⚠️ لا يوجد عمود population_density أو population_estimate.")
        gdf_proj["Population_Density"] = 0

    return gdf_proj.to_crs("EPSG:4326")

def main():
    logging.info("📍 تحميل نقاط الملاجئ...")
    shelters = gpd.read_file("data/geo/shelters.geojson")

    logging.info("🚗 تحميل شبكة الطرق...")
    roads = gpd.read_file("data/geo/roads.geojson")
    shelters = calculate_distance_to_nearest(shelters, roads, "Distance_to_Roads")

    logging.info("🌍 تحميل خطوط الصدع...")
    faults = gpd.read_file("data/processed/fault_lines_elazig.geojson")
    shelters = calculate_distance_to_nearest(shelters, faults, "Distance_to_Faults")

    logging.info("👥 تحميل الكثافة السكانية...")
    population = gpd.read_file("data/processed/population.geojson")
    shelters = match_population_density(shelters, population)

    logging.info("🌱 تحميل استخدامات الأراضي...")
    landuse = gpd.read_file("data/processed/landuse.geojson")
    shelters = categorize_landuse(shelters, landuse)

    output_path = config.SHELTER_INPUT
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shelters.to_file(output_path, driver="GeoJSON")
    logging.info(f"✅ تم حفظ بيانات الملاجئ المعززة: {output_path}")

if __name__ == "__main__":
    main()