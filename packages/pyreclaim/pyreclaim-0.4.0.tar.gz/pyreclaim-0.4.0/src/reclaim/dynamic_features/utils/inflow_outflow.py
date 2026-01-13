import pandas as pd
import numpy as np

SECONDS_PER_DAY = 24 * 3600
DAYS_PER_YEAR = 365.25
SECONDS_PER_YEAR = SECONDS_PER_DAY * DAYS_PER_YEAR

def mean_annual_flow_m3_per_s(ts: pd.Series) -> float:
    """
    Computes the mean annual flow in m³/s from a time series of daily flow in m³/day.

    Parameters
    ----------
    ts : pd.Series
        Time series of daily flow values in m³/day, indexed by datetime.

    Returns
    -------
    float
        Mean annual flow in m³/s.
    """
    if ts.empty:
        return float('nan')

    annual_totals = ts.groupby(ts.index.year).sum()
    mean_annual = annual_totals.mean()
    return mean_annual / SECONDS_PER_YEAR


def mean_annual_flow_std_m3_per_s(ts: pd.Series) -> float:
    """
    Computes the mean annual standard deviation of daily flow (in m³/s).

    Parameters
    ----------
    ts : pd.Series
        Time series of daily flow values in m³/day, indexed by datetime.

    Returns
    -------
    float
        Mean annual standard deviation of flow in m³/s.
    """
    if ts.empty:
        return float('nan')

    annual_std = ts.groupby(ts.index.year).std()
    annual_std_m3_per_s = annual_std / SECONDS_PER_DAY
    return annual_std_m3_per_s.mean()


def max_annual_flow_m3_per_s(ts: pd.Series) -> float:
    """
    Computes the maximum annual flow in m³/s from daily flow series.

    Parameters
    ----------
    ts : pd.Series
        Time series of daily flow values in m³/day, indexed by datetime.

    Returns
    -------
    float
        Maximum annual flow in m³/s.
    """
    if ts.empty:
        return float('nan')

    annual_totals = ts.groupby(ts.index.year).sum()
    max_annual = annual_totals.max()
    return max_annual / SECONDS_PER_YEAR


def mean_annual_flow_variability(ts: pd.Series) -> float:
    """
    Computes the mean annual variability (coefficient of variation) of daily flow.

    CV = std / mean within each year

    Parameters
    ----------
    ts : pd.Series
        Time series of daily flow values in m³/day, indexed by datetime.

    Returns
    -------
    float
        Mean coefficient of variation across all years (unitless).
    """
    if ts.empty:
        return float('nan')

    annual_stats = ts.groupby(ts.index.year).agg(['mean', 'std'])
    annual_stats['cv'] = annual_stats['std'] / annual_stats['mean']
    return annual_stats['cv'].mean()