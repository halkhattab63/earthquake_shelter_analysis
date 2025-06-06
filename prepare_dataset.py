# import os
# import logging
# import geopandas as gpd
# import pandas as pd
# import rasterio
# import numpy as np
# from shapely.geometry import Point
# from src import config, load_data

# # إعدادات اللوج
# logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
# PROJECTED_CRS = "EPSG:32637"  # UTM Zone 37N - مناسب للمنطقة الشرقية من تركيا

# def calculate_distance_to_nearest(source_gdf, target_gdf, label):
#     """حساب المسافة لأقرب عنصر من طبقة الهدف"""
#     target_gdf = target_gdf.to_crs(PROJECTED_CRS)
#     source_gdf = source_gdf.to_crs(PROJECTED_CRS)
#     source_gdf[label] = source_gdf.geometry.apply(lambda x: target_gdf.distance(x).min())
#     return source_gdf.to_crs("EPSG:4326")  # العودة للإسقاط الجغرافي

# def extract_raster_values(dem_path, points):
#     """استخلاص القيم من الـ DEM"""
#     with rasterio.open(dem_path) as src:
#         values = list(src.sample([(pt.x, pt.y) for pt in points]))
#     return np.nan_to_num(np.array(values).flatten())

# def categorize_landuse(gdf, landuse_gdf):
#     """إعطاء كل نقطة ملجأ درجة حسب نوع الأرض"""
#     def get_score(point):
#         for _, row in landuse_gdf.iterrows():
#             if row.geometry.contains(point):
#                 land_type = row.get("land_type", "unknown").lower()
#                 if "park" in land_type or "open" in land_type:
#                     return 0.9
#                 elif "residential" in land_type:
#                     return 0.5
#                 else:
#                     return 0.2
#         return 0.1
#     gdf["LandUse_Score"] = gdf.geometry.apply(get_score)
#     return gdf

# def match_population_density(gdf, pop_df):
#     """مطابقة الكثافة السكانية لكل ملجأ حسب أقرب نقطة سكانية"""
#     pop_gdf = gpd.GeoDataFrame(pop_df, geometry=gpd.points_from_xy(pop_df.lon, pop_df.lat), crs="EPSG:4326")
#     joined = gpd.sjoin_nearest(gdf, pop_gdf, how="left", distance_col="pop_dist")
#     col = "population_density" if "population_density" in joined.columns else "density"
#     gdf["Population_Density"] = joined[col].fillna(joined[col].mean())
#     return gdf

# def main():
#     logging.info("📍 Loading shelter points...")
#     shelters = load_data.load_shelter_points()

#     logging.info("🚗 Loading road network...")
#     roads = load_data.load_roads()
#     shelters = calculate_distance_to_nearest(shelters, roads, "Distance_to_Roads")

#     logging.info("🌍 Loading fault lines...")
#     faults = load_data.load_fault_lines()
#     shelters = calculate_distance_to_nearest(shelters, faults, "Distance_to_Faults")

#     logging.info("🟫 Loading DEM for slope...")
#     dem_path = load_data.load_dem()
#     shelters = shelters.to_crs(PROJECTED_CRS)
#     slope_values = extract_raster_values(dem_path, shelters.geometry)
#     shelters["Slope"] = slope_values
#     shelters = shelters.to_crs("EPSG:4326")  # نعود إلى CRS الأصلي

#     logging.info("👥 Loading population density...")
#     pop_df = load_data.load_population_density()
#     shelters = match_population_density(shelters, pop_df)

#     logging.info("🌱 Loading land use...")
#     landuse = load_data.load_land_use()
#     shelters = categorize_landuse(shelters, landuse)

#     # حفظ الملف النهائي
#     output_path = config.SHELTER_INPUT
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#     shelters.to_file(output_path, driver="GeoJSON")
#     logging.info(f"✅ Saved enriched shelter data to: {output_path}")

# if __name__ == "__main__":
#     main()




import os
import logging
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from src import config, load_data

# إعدادات اللوج
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
PROJECTED_CRS = "EPSG:32637"  # UTM Zone 37N - مناسب للمنطقة الشرقية من تركيا


def calculate_distance_to_nearest(source_gdf, target_gdf, label):
    target_gdf = target_gdf.to_crs(PROJECTED_CRS)
    source_gdf = source_gdf.to_crs(PROJECTED_CRS)
    source_gdf[label] = source_gdf.geometry.apply(lambda x: target_gdf.distance(x).min())
    return source_gdf.to_crs("EPSG:4326")


def categorize_landuse(gdf, landuse_gdf):
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
        return 0.1

    gdf["LandUse_Score"] = gdf.geometry.apply(get_score)
    return gdf


def match_population_density(gdf, pop_gdf):
    # تحقق من أن البيانات تحتوي على نقاط
    if not all(pop_gdf.geometry.type == "Point"):
        raise ValueError("❌ ملف الكثافة السكانية يجب أن يحتوي فقط على هندسة من النوع Point.")

    # إعادة إسقاط البيانات إلى نظام إسقاطي مناسب
    gdf_proj = gdf.to_crs(PROJECTED_CRS)
    pop_proj = pop_gdf.to_crs(PROJECTED_CRS)

    # إجراء أقرب انضمام جغرافي
    joined = gpd.sjoin_nearest(gdf_proj, pop_proj, how="left", distance_col="pop_dist")
    joined = joined.reset_index(drop=True)
    gdf_proj = gdf_proj.reset_index(drop=True)

    # تعيين قيم الكثافة
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
    shelters = gpd.read_file("data/raw/shelters_from_osm.geojson")

    logging.info("🚗 تحميل شبكة الطرق...")
    roads = gpd.read_file("data/raw/roads.geojson")
    shelters = calculate_distance_to_nearest(shelters, roads, "Distance_to_Roads")

    logging.info("🌍 تحميل خطوط الصدع...")
    faults = gpd.read_file("data/raw/fault_lines.geojson")
    shelters = calculate_distance_to_nearest(shelters, faults, "Distance_to_Faults")

    logging.info("👥 تحميل الكثافة السكانية...")
    population = gpd.read_file("data/raw/population.geojson")
    shelters = match_population_density(shelters, population)

    logging.info("🌱 تحميل استخدامات الأراضي...")
    landuse = gpd.read_file("data/raw/landuse.geojson")
    shelters = categorize_landuse(shelters, landuse)

    output_path = config.SHELTER_INPUT
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shelters.to_file(output_path, driver="GeoJSON")
    logging.info(f"✅ تم حفظ بيانات الملاجئ المعززة: {output_path}")


if __name__ == "__main__":
    main()
