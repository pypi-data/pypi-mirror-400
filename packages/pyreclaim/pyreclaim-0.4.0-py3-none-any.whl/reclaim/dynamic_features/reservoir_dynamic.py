import os
import pandas as pd
import numpy as np
from typing import Dict, Sequence, Union, Callable

from reclaim.dynamic_features.utils.statistical_metrics import (
    annual_mean,
    annual_std,
    skewness,
    kurtosis_val,
    coefficient_of_variation,
    max_days_above_90th,
    max_annual_persistence
)
from reclaim.dynamic_features.utils.inflow_outflow import (
    mean_annual_flow_m3_per_s,
    mean_annual_flow_std_m3_per_s,
    max_annual_flow_m3_per_s,
    mean_annual_flow_variability
)
from reclaim.dynamic_features.utils.ts_aggregate import compute_ts_aggregate

def reservoir_based_dynamic_features(
    variable_info: Dict[str, Dict[str, str]],
    observation_period: Sequence[int],
) -> pd.DataFrame:
    """
    Compute dynamic reservoir features for a single reservoir using inflow, outflow,
    surface area, evaporation, and sediment-related time series.

    Required time series keys (case-sensitive):

    - ``inflow``:       Daily inflow in m³/day
    - ``outflow``:      Daily outflow in m³/day
    - ``evaporation``:  Daily evaporation in mm/day
    - ``surface_area``: Reservoir surface area in km²
    - ``nssc``:         Normalized suspended sediment concentration variant 1 (red/green) (dimensionless)
    - ``nssc2``:        Normalized suspended sediment concentration variant 2 (near-infrared/red) (dimensionless)

    Parameters
    ----------
    variable_info : dict
        Dictionary of input series metadata.
        Each key corresponds to a variable (``inflow``, ``outflow``, ``evaporation``, ``surface_area``, ``nssc``, ``nssc2``).
        Each value is a dict with the following structure::

            {
                "path": str,          # Path to the CSV file
                "time_column": str,   # Name of the datetime column
                "data_column": str    # Name of the variable column
            }

        Example::

            {
                "inflow": {"path": "data/inflow.csv", "time_column": "date", "data_column": "inflow (m3/d)"},
                "outflow": {"path": "data/outflow.csv", "time_column": "date", "data_column": "outflow (m3/d)"}
            }

    observation_period : sequence[int]
        Two-element sequence [OSY, OEY] specifying the observation period to clip the series.

    Returns
    -------
    pd.DataFrame
        A one-row DataFrame containing the computed reservoir dynamic features.
        Missing variables in ``variable_info`` will result in NaN values for their features.

    Notes
    -----
    - All inflow/outflow metrics are converted to m³/s internally.
    - Surface area statistics are reported both for full record and clipped period.
    - NSSC statistics are dimensionless.
    - If a variable is missing in ``variable_info``, its corresponding features are NaN.
    """

    # Define which features depend on which variable
    variable_features = {
        "inflow": {
            "MAI": mean_annual_flow_m3_per_s,
            "PAI": max_annual_flow_m3_per_s,
            "I_cv": mean_annual_flow_variability,
            "I_std": mean_annual_flow_std_m3_per_s,
            "I_above_90": max_days_above_90th,
            "I_max_persis": max_annual_persistence,
        },
        "outflow": {
            "MAO": mean_annual_flow_m3_per_s,
            "O_std": mean_annual_flow_std_m3_per_s,
            "O_cv": mean_annual_flow_variability,
        },
        "evaporation": {
            "E_mean": annual_mean,
            "E_std": annual_std,
        },
        "surface_area": {
            "SA_mean": annual_mean,
            "SA_std": annual_std,
            "SA_cv": coefficient_of_variation,
            "SA_skew": skewness,
            "SA_kurt": kurtosis_val,
            "SA_mean_clip": annual_mean,
            "SA_above_90": max_days_above_90th,
        },
        "nssc": {
            "NSSC1_mean": annual_mean,
            "NSSC1_std": annual_std,
            "NSSC1_cv": coefficient_of_variation,
            "NSSC1_skew": skewness,
            "NSSC1_kurt": kurtosis_val,
        },
        "nssc2": {
            "NSSC2_mean": annual_mean,
            "NSSC2_above_90": max_days_above_90th,
            "NSSC2_max_persis": max_annual_persistence,
        },
    }

    results = {}

    # Loop through required variables
    for var, feat_dict in variable_features.items():
        if var not in variable_info:
            # Fill with NaN if variable not provided
            for feat in feat_dict.keys():
                results[feat] = np.nan
            continue

        path = variable_info[var]["path"]
        time_col = variable_info[var]["time_column"]
        data_col = variable_info[var]["data_column"]

        # Some features require clipping, others use full record
        for feat, func in feat_dict.items():
            if var == "surface_area" and feat in ["SA_mean", "SA_std", "SA_cv", "SA_skew", "SA_kurt"]:
                obs_period = None  # full record
            else:
                obs_period = observation_period

            try:
                df_feat = compute_ts_aggregate(
                    path, time_col, data_col, func, feat, obs_period
                )
                results[feat] = df_feat.iloc[0, 0]  # single value
            except Exception as e:
                print(f"Failed to compute {feat} due to error: {e}. Setting as NaN.")
                results[feat] = np.nan

    return pd.DataFrame([results])