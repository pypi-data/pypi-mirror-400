import numpy as np
import pandas as pd

def mean_slope(df: pd.DataFrame) -> float:
    """
    Computes the mean slope (dA/dz) of reservoir bathymetry
    from area–elevation data.
    """
    if not {'elevation', 'area'}.issubset(df.columns):
        raise ValueError("DataFrame must have columns: 'elevation', 'area'")
    if df.empty:
        return float('nan')

    # Sort and drop duplicate elevations (keep mean area if duplicates exist)
    df = df.groupby("elevation", as_index=False)["area"].mean()
    df = df.sort_values("elevation").reset_index(drop=True)

    # Compute slope (Δarea/Δelevation)
    dz = np.diff(df['elevation'])
    da = np.diff(df['area'])

    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        slopes = np.where(dz != 0, da / dz, np.nan)

    return float(np.nanmean(slopes))


def mean_curvature(df: pd.DataFrame) -> float:
    """
    Computes the mean curvature (d²A/dz²) of reservoir bathymetry
    from area–elevation data.
    """
    if not {'elevation', 'area'}.issubset(df.columns):
        raise ValueError("DataFrame must have columns: 'elevation', 'area'")
    if df.empty:
        return float('nan')

    # Sort and drop duplicate elevations (keep mean area if duplicates exist)
    df = df.groupby("elevation", as_index=False)["area"].mean()
    df = df.sort_values("elevation").reset_index(drop=True)

    dz = np.diff(df['elevation'])
    da = np.diff(df['area'])

    # First derivative
    with np.errstate(divide='ignore', invalid='ignore'):
        slopes = np.where(dz != 0, da / dz, np.nan)

    # Second derivative (curvature)
    dz2 = np.diff(df['elevation'][:-1])
    dslopes = np.diff(slopes)
    with np.errstate(divide='ignore', invalid='ignore'):
        curvature = np.where(dz2 != 0, dslopes / dz2, np.nan)

    return float(np.nanmean(curvature))

def concavity_index(df: pd.DataFrame) -> float:
    """
    Computes the concavity index from a reservoir's area-elevation curve.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns 'area' (km²) and 'elevation' (m).

    Returns
    -------
    float
        Concavity index (ratio of actual curve to straight line). 
        Returns np.nan if invalid.
    """
    if not {'area', 'elevation'}.issubset(df.columns):
        raise ValueError("DataFrame must have columns: 'area' and 'elevation'")
    if df.empty:
        return np.nan

    # Convert to numpy and filter invalid values
    area = df['area'].to_numpy(dtype=float)
    elevation = df['elevation'].to_numpy(dtype=float)
    
    mask = (~np.isnan(area)) & (~np.isnan(elevation)) & (~np.isinf(area)) & (~np.isinf(elevation))
    area = area[mask]
    elevation = elevation[mask]

    if len(area) < 2:
        return np.nan

    # Normalize to 0–1
    area_norm = (area - area.min()) / (area.max() - area.min())
    elev_norm = (elevation - elevation.min()) / (elevation.max() - elevation.min())

    # Straight line between first and last point
    line = np.linspace(0, 1, len(area_norm))

    # Area under actual curve vs line
    auc_curve = np.trapezoid(elev_norm, area_norm)
    auc_line = np.trapezoid(line, area_norm)

    concavity = auc_curve / auc_line if auc_line > 0 else np.nan
    return concavity