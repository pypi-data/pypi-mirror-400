import pandas as pd
import numpy as np
from typing import Dict, Sequence

from reclaim.dynamic_features.utils.rainfall import (
    mean_annual_rainfall_mm,
    mean_annual_rainy_days,
)
from reclaim.dynamic_features.utils.statistical_metrics import (
    annual_mean,
    annual_std,
    coefficient_of_variation,
    skewness,
    kurtosis_val,
)
from reclaim.dynamic_features.utils.ts_aggregate import compute_ts_aggregate


def catchment_based_dynamic_features(
    variable_info: Dict[str, Dict[str, str]],
    observation_period: Sequence[int],
) -> pd.DataFrame:
    """
    Compute dynamic catchment-based features for a single reservoir's catchment,
    using precipitation, temperature, and wind speed time series.

    Required time series keys (case-sensitive)
        - "precip":  Daily precipitation in mm
        - "tmin":    Daily minimum temperature in °C
        - "tmax":    Daily maximum temperature in °C
        - "wind":    Daily wind speed in m/s

    Parameters
    ----------
    variable_info : dict
        Dictionary of input series metadata.
        Each key corresponds to a variable (precip, tmin, tmax, wind).
        Each value is a dict with:
            {
                "path": str,
                "time_column": str,
                "data_column": str
            }

    observation_period : sequence[int]
        Two-element sequence [OSY, OEY] specifying the observation period to clip the series.

    Returns
    -------
    pd.DataFrame
        A one-row DataFrame containing the computed catchment-based features.

    Notes
    -----
    - Precipitation features are reported as mm/year (for MAR) and counts (rainy days).
    - Wind statistics include mean, std, CV, skewness, kurtosis.
    - Temperature features are simple annual means (°C).
    """
    
    variable_features = {
        "precip": {
            "MAR": mean_annual_rainfall_mm,
            "#_rain_above_10": lambda ts: mean_annual_rainy_days(ts, threshold=10.0),
            "#_rain_above_50": lambda ts: mean_annual_rainy_days(ts, threshold=50.0),
            "#_rain_above_100": lambda ts: mean_annual_rainy_days(ts, threshold=100.0),
        },
        "tmin": {
            "tmin_mean": annual_mean,
        },
        "tmax": {
            "tmax_mean": annual_mean,
        },
        "wind": {
            "wind_mean": annual_mean,
            "wind_std": annual_std,
            "wind_cv": coefficient_of_variation,
            "wind_skew": skewness,
            "wind_kurt": kurtosis_val,
        },
    }

    results = {}

    for var, feat_dict in variable_features.items():
        if var not in variable_info:
            for feat in feat_dict.keys():
                results[feat] = np.nan
            continue

        path = variable_info[var]["path"]
        time_col = variable_info[var]["time_column"]
        data_col = variable_info[var]["data_column"]

        for feat, func in feat_dict.items():
            try:
                df_feat = compute_ts_aggregate(
                    path, time_col, data_col, func, feat, observation_period
                )
                results[feat] = df_feat.iloc[0, 0]  # extract scalar
            except Exception:
                results[feat] = np.nan

    return pd.DataFrame([results])