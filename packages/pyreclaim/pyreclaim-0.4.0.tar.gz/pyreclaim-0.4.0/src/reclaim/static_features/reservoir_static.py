import pandas as pd
from shapely.geometry import Point, Polygon
import numpy as np

# Import utils
from reclaim.static_features.utils.flow_length import find_actual_flow_path
from reclaim.static_features.utils.area_perimeter import calculate_length_area_meters
from reclaim.static_features.utils.aec_shape import concavity_index, mean_curvature, mean_slope


def reservoir_based_static_features(
    obc: float = None,
    hgt: float = None,
    mrb: str = None,
    lat: float = None,
    lon: float = None,
    by: int = None,
    reservoir_polygon: Polygon = None,
    inlet_point: Point = None,
    resolution: float = None,
    aec_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Compute reservoir-based features for RECLAIM input dataset.
    
    Parameters
    ----------
    obc : float, optional
        Original Built Capacity (MCM), original design capacity of the reservoir.
    hgt : float, optional
        Dam height (meters).
    mrb : str, optional
        Major river basin name.
    lat : float, optional
        Latitude of dam location (degrees).
    lon : float, optional
        Longitude of dam location (degrees).
    by : int, optional
        Build year of the reservoir.
    reservoir_polygon : shapely.geometry.Polygon, optional
        Reservoir polygon geometry used to compute area and perimeter.
    dam_point : shapely.geometry.Point, optional
        Location of the dam.
    inlet_point : shapely.geometry.Point, optional
        Reservoir inlet location (if not provided, estimated internally).
    resolution : float, optional
        Spatial resolution used in flow length calculations.
    aec_df : pd.DataFrame, optional
        Area-Elevation Curve dataframe with columns ['area', 'elevation'].
    
    Returns
    -------
    pd.DataFrame
        A single-row DataFrame with the following columns:
        - OBC: Original Built Capacity (MCM)
        - HGT: Dam Height (m)
        - MRB: Major River Basin
        - LAT: Latitude (deg)
        - LON: Longitude (deg)
        - BY: Build Year
        - RA: Reservoir Area (sq km)
        - RP: Reservoir Perimeter (km)
        - FL: Flow Length (km)
        - AECS: AEC Mean Slope (km2/m)
        - AECC: AEC Mean Curvature (km2/m2)
        - AECI: AEC Concavity Index (DL)
    """

    features = {
        "OBC": obc,
        "HGT": hgt,
        "MRB": mrb,
        "LAT": lat,
        "LON": lon,
        "BY": by,
        "RA": None,
        "RP": None,
        "FL": None,
        "AECS": None,
        "AECC": None,
        "AECI": None,
    }

    # Area and Perimeter
    if reservoir_polygon is not None:
        features["RP"], features["RA"] = calculate_length_area_meters(reservoir_polygon, area=True)
        features["RA"] = features["RA"] / 1e6  # m2 → km2
        features["RP"] = features["RP"] / 1e3  # m → km

    # Flow Length
    dam_point = Point(lon, lat)
    if dam_point is not None and reservoir_polygon is not None:
        _, _, features["FL"], _ = (
            find_actual_flow_path(dam_point, reservoir_polygon, inlet_point, resolution) 
        )  
        if features["FL"]: 
            features["FL"] = calculate_length_area_meters(features["FL"], area=False) / 1e3  # m → km
        else:
            features["FL"] = np.nan

    # AEC metrics
    if aec_df is not None:
        features["AECS"] = mean_slope(aec_df)
        features["AECC"] = mean_curvature(aec_df)
        features["AECI"] = concavity_index(aec_df)

    return pd.DataFrame([features])