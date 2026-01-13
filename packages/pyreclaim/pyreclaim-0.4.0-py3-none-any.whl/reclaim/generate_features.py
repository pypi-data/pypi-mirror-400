### Wrappers to compute all static, dynamic, and derived features for RECLAIM input dataset.

from typing import Dict, List
import pandas as pd

# Import from your package structure
from reclaim.static_features.reservoir_static import reservoir_based_static_features
from reclaim.static_features.catchment_static import catchment_based_static_features
from reclaim.dynamic_features.reservoir_dynamic import reservoir_based_dynamic_features
from reclaim.dynamic_features.catchment_dynamic import catchment_based_dynamic_features
from reclaim.derived_features.feature_engineering_and_transformation import engineer_and_transform_features


def create_features_per_row(
    idx: int,
    observation_period: List[int],
    reservoir_static_params: dict,
    catchment_static_params: dict,
    reservoir_dynamic_info: dict = None,
    catchment_dynamic_info: dict = None,
) -> pd.DataFrame:
    """
    Compute all static, dynamic, and derived features for a single reservoir observation.

    Parameters
    ----------
    idx : int
        Index of the reservoir sedimentation observation (for tracking/logging purposes).
    
    observation_period : list of int
        Two-element list [OSY, OEY] for observation start year and end year.
        
    reservoir_static_params : dict
        Parameters for reservoir_based_static_features(). Expected keys:
            - obc : float, Original Built Capacity (MCM)
            - hgt : float, Dam Height (m)
            - mrb : str, Major River Basin, optional
            - lat : float, Latitude (deg)
            - lon : float, Longitude (deg)
            - by : int, Build Year
            - reservoir_polygon : shapely.geometry.Polygon
            - inlet_point : shapely.geometry.Point, optional
            - resolution : float, optional
            - aec_df : pd.DataFrame with columns ['area', 'elevation']

    catchment_static_params : dict
        Parameters for catchment_based_static_features(). Expected keys:
            - ca : float, Catchment Area (sq km)
            - dca : float, Differential Catchment Area (sq km)
            - catchment_geometry : shapely.geometry.Polygon or GeoSeries
            - glc_share_path : str, path to GLC-Share NetCDF (land cover)
            - hwsd2_path : str, path to HWSD2 NetCDF (soils)
            - hilda_veg_freq_path : str, path to HILDA vegetation NetCDF
            - terrain_path : str, path to terrain/DEM derivatives NetCDF

    reservoir_dynamic_info : dict, optional
        variable_info dict for reservoir time series. Required keys (case-sensitive):
            - "inflow":       {"path": str, "time_column": str, "data_column": str}
            - "outflow":      {"path": str, "time_column": str, "data_column": str}
            - "evaporation":  {"path": str, "time_column": str, "data_column": str}
            - "surface_area": {"path": str, "time_column": str, "data_column": str}
            - "nssc":         {"path": str, "time_column": str, "data_column": str}
            - "nssc2":        {"path": str, "time_column": str, "data_column": str}

    catchment_dynamic_info : dict, optional
        variable_info dict for catchment time series. Required keys (case-sensitive):
            - "precip": {"path": str, "time_column": str, "data_column": str}
            - "tmin":   {"path": str, "time_column": str, "data_column": str}
            - "tmax":   {"path": str, "time_column": str, "data_column": str}
            - "wind":   {"path": str, "time_column": str, "data_column": str}

    Returns
    -------
    pd.DataFrame
        Single-row DataFrame with all features:
        - Reservoir static
        - Catchment static
        - Reservoir dynamic
        - Catchment dynamic
        - Derived/log-transformed
    """
    
    # --- Observevation period features ---
    osy, oey = observation_period
    df_obs_period = pd.DataFrame({
        "idx": [idx],
        "OSY": [osy],
        "OEY": [oey]
    })

    # --- Static features ---
    df_res_static = reservoir_based_static_features(**reservoir_static_params)
    df_catch_static = catchment_based_static_features(**catchment_static_params)

    # --- Dynamic features ---
    df_res_dyn = pd.DataFrame()
    df_catch_dyn = pd.DataFrame()

    if reservoir_dynamic_info is not None and observation_period is not None:
        df_res_dyn = reservoir_based_dynamic_features(reservoir_dynamic_info, observation_period)

    if catchment_dynamic_info is not None and observation_period is not None:
        df_catch_dyn = catchment_based_dynamic_features(catchment_dynamic_info, observation_period)
    
    # --- Combine all static + dynamic ---
    df_combined = pd.concat([df_obs_period, df_res_static, df_catch_static, df_res_dyn, df_catch_dyn], axis=1)

    # --- Engineer + log-transform features ---
    df_final = engineer_and_transform_features(df_combined)

    return df_final


def create_features_multi(
    reservoirs_input: List[Dict]
) -> pd.DataFrame:
    """
    Compute features for multiple reservoirs using structured input.

    Parameters
    ----------
    reservoirs_input : list of dict
        Each element should be a dictionary with the following keys:
        
        - `idx` : int
            Index of the reservoir sedimentation observation.
        - `observation_period` : list of int
            Two-element list `[OSY, OEY]` specifying the observation period.
        - `reservoir_static_params` : dict
            Parameters for `reservoir_based_static_features()`.
        - `catchment_static_params` : dict
            Parameters for `catchment_based_static_features()`.
        - `reservoir_dynamic_info` : dict
            Parameters for `reservoir_based_dynamic_features()`.
        - `catchment_dynamic_info` : dict
            Parameters for `catchment_based_dynamic_features()`.
        

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with one row per reservoir observation.
    """

    all_rows = []
    for idx, reservoir_info in enumerate(reservoirs_input):
        df_row = create_features_per_row(
            idx=reservoir_info.get("idx"),
            observation_period=reservoir_info.get("observation_period"),
            reservoir_static_params=reservoir_info.get("reservoir_static_params", {}),
            catchment_static_params=reservoir_info.get("catchment_static_params", {}),
            reservoir_dynamic_info=reservoir_info.get("reservoir_dynamic_info", None),
            catchment_dynamic_info=reservoir_info.get("catchment_dynamic_info", None),
        )
        all_rows.append(df_row)

    df_all = pd.concat(all_rows, axis=0).reset_index(drop=True)
    return df_all