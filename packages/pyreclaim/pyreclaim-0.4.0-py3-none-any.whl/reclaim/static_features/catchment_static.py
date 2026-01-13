import pandas as pd

from reclaim.static_features.utils.catchment_agreggate import compute_catchment_aggregate

def catchment_based_static_features(
    ca: float,
    dca: float,
    catchment_geometry,
    glc_share_path: str,
    hwsd2_path: str,
    hilda_veg_freq_path: str,
    terrain_path: str,
) -> pd.DataFrame:
    """
    Compute catchment-based features for a reservoir.

    Parameters
    ----------
    ca : float
        Catchment Area (sq km).
    dca : float
        Differential Catchment Area (sq km).
    catchment_geometry : shapely.geometry.Polygon or GeoSeries
        Catchment polygon.
    glc_share_path : str
        Path to the GLC-Share NetCDF file (land cover fractions).
    hwsd2_path : str
        Path to the HWSD2 NetCDF file (soil composition).
    hilda_veg_freq_path : str
        Path to the HILDA vegetation frequency NetCDF file.
    terrain_path : str
        Path to the terrain NetCDF file (DEM derivatives).

    Returns
    -------
    pd.DataFrame
        A single-row DataFrame with abbreviations as columns:
        - CA, DCA, LCAS, LCC, LCG, LCT, LCS, LCHV, LCM, LCSV,
        LCBS, LCSG, LCWB, DLC, COAR, SAND, SILT, CLAY, BULK,
        ELEV, SLOP, CURV, ASP, HILL, VGF, VLF
        
    """

    features = {"CA": ca, "DCA": dca}

    # ---- Land cover (GLC-Share)
    glc_dict = {
        "artificial_surfaces": "mean",
        "cropland": "mean",
        "grassland": "mean",
        "tree_covered": "mean",
        "shrubs_covered": "mean",
        "aquatic_herbaceous": "mean",
        "mangroves": "mean",
        "sparse_vegetation": "mean",
        "bare_soil": "mean",
        "snow_glaciers": "mean",
        "waterbodies": "mean",
        "dominant_class": "mode",
    }
    glc_df = compute_catchment_aggregate(
        netcdf_path=glc_share_path,
        catchment_geometry=catchment_geometry,
        function_type=glc_dict,
    )

    # ---- Soil composition (HWSD2)
    hwsd_df = compute_catchment_aggregate(
        netcdf_path=hwsd2_path,
        catchment_geometry=catchment_geometry,
        function_type="mean",
    )

    # ---- HILDA vegetation frequency
    hilda_df = compute_catchment_aggregate(
        netcdf_path=hilda_veg_freq_path,
        catchment_geometry=catchment_geometry,
        function_type="mean",
    )

    # ---- Terrain
    terrain_df = compute_catchment_aggregate(
        netcdf_path=terrain_path,
        catchment_geometry=catchment_geometry,
        function_type="mean",
    )

    # Merge everything
    merged = pd.concat([glc_df, hwsd_df, hilda_df, terrain_df], axis=1)
    features.update(merged.to_dict(orient="records")[0])

    # ---- Rename columns to abbreviations
    rename_dict = {
        # Land cover
        "artificial_surfaces_mean": "LCAS",
        "cropland_mean": "LCC",
        "grassland_mean": "LCG",
        "tree_covered_mean": "LCT",
        "shrubs_covered_mean": "LCS",
        "aquatic_herbaceous_mean": "LCHV",
        "mangroves_mean": "LCM",
        "sparse_vegetation_mean": "LCSV",
        "bare_soil_mean": "LCBS",
        "snow_glaciers_mean": "LCSG",
        "waterbodies_mean": "LCWB",
        "dominant_class_mode": "DLC",
        # Soil
        "COARSE_mean": "COAR",
        "SAND_mean": "SAND",
        "SILT_mean": "SILT",
        "CLAY_mean": "CLAY",
        "BULK_mean": "BULK",
        # Terrain
        "elevation_mean": "ELEV",
        "slope_mean": "SLOP",
        "curvature_mean": "CURV",
        "aspect_mean": "ASP",
        "hillshade_mean": "HILL",
        # HILDA (optional, not mapped to abbreviations yet)
        "vegetation_gain_frequency_mean": "VGF",
        "vegetation_loss_frequency_mean": "VLF",
    }

    # Apply renaming
    features_df = pd.DataFrame([features]).rename(columns=rename_dict)

    return features_df