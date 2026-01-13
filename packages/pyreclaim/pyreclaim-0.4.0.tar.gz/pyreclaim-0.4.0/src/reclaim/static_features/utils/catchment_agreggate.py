import pandas as pd
import numpy as np
import xarray as xr
import rioxarray
import geopandas as gpd
import regionmask
from collections import Counter
from shapely.geometry import Polygon


def compute_catchment_aggregate(
    netcdf_path,
    catchment_geometry,
    function_type="mean"  # Can be 'mean', 'mode', 'std', 'percent' or dict
) -> pd.DataFrame:
    """
    Compute catchment-based features by aggregating raster variables in a NetCDF file
    for a single catchment geometry.

    Parameters
    ----------
    netcdf_path : str or Path
        Path to the NetCDF file containing raster variables.

    catchment_geometry : shapely.geometry.Polygon or GeoSeries
        Catchment geometry (single polygon).

    function_type : str or dict, default="mean"
        Either a string ('mean', 'mode', 'std', 'percent') to apply to all variables,
        or a dictionary specifying function(s) per variable. Example::

            {
                "precip": "mean",
                "slope": ["mean", "std"],
                "landcover": {"type": "percent"}
            }

    Returns
    -------
    pd.DataFrame
        A single-row DataFrame with catchment-level features.
    """

    # Open dataset
    ds = xr.open_dataset(netcdf_path, chunks={'x': 200, 'y': 200})
    ds = ds.rio.write_crs("EPSG:4326")

    # Rename coords if needed
    if 'lon' in ds.dims and 'lat' in ds.dims:
        ds = ds.rename({'lon': 'x', 'lat': 'y'})

    variables = list(ds.data_vars)

    # Build function dict
    if isinstance(function_type, str):
        apply_func = {var: function_type for var in variables}
    elif isinstance(function_type, dict):
        apply_func = function_type
    else:
        raise ValueError("function_type must be a string or a dictionary.")

    # Order check
    y_order = "descending" if ds.y[0] > ds.y[-1] else "ascending"
    x_order = "descending" if ds.x[0] > ds.x[-1] else "ascending"

    # Get catchment bounds
    minx, miny, maxx, maxy = catchment_geometry.bounds
    if y_order == "descending":
        y_slice = slice(maxy, miny)
    else:
        y_slice = slice(miny, maxy)
    if x_order == "descending":
        x_slice = slice(maxx, minx)
    else:
        x_slice = slice(minx, maxx)

    # Subset dataset
    subset_ds = ds.sel(x=x_slice, y=y_slice)

    # Create mask
    catchment_gdf = gpd.GeoDataFrame({"geometry": [catchment_geometry]}, crs="EPSG:4326")
    mask_from_geopandas = regionmask.mask_geopandas(catchment_gdf, subset_ds.x, subset_ds.y)
    catchment_mask = mask_from_geopandas == 0

    if mask_from_geopandas.notnull().sum().sum().item() == 0:
        raise ValueError("Catchment mask is empty — geometry may not overlap the raster.")

    results = {}

    # Loop over variables
    for var in apply_func.keys():
        data = subset_ds[var]
        masked = data.where(catchment_mask).compute()
        arr = masked.where(~masked.isnull(), drop=True)

        # Skip if empty
        if arr.size == 0:
            continue

        func_list = apply_func[var]
        if not isinstance(func_list, list):
            func_list = [func_list]  # wrap into list

        for func_info in func_list:
            if isinstance(func_info, str):
                func = func_info
                threshold = None
                threshold_direction = None
            elif isinstance(func_info, dict):
                func = func_info.get("type")
                threshold = func_info.get("threshold", None)
                threshold_direction = func_info.get("direction", "greater")
            else:
                raise ValueError(f"Invalid function format for variable {var}")

            if func == "mean":
                results[f"{var}_mean"] = float(arr.mean().item())

            elif func == "mode":
                vals = arr.values.flatten()
                results[f"{var}_mode"] = Counter(vals).most_common(1)[0][0]

            elif func == "std":
                results[f"{var}_std"] = float(arr.std().item())

            elif func == "percent":
                vals = arr.values.flatten()
                total = len(vals)
                class_counts = Counter(vals)
                for cls, count in class_counts.items():
                    results[f"{var}_percent_{int(cls)}"] = (count / total) * 100

            elif func == "threshold_percent":
                if threshold is None:
                    raise ValueError(f"Threshold not provided for variable '{var}'")
                vals = arr.values.flatten()
                valid = vals[~np.isnan(vals)]
                if threshold_direction == "greater":
                    percent = (valid > threshold).sum() / len(valid) * 100
                    results[f"{var}_percent_above_{threshold}"] = percent
                else:
                    percent = (valid < threshold).sum() / len(valid) * 100
                    results[f"{var}_percent_below_{threshold}"] = percent

            else:
                raise ValueError(f"Unknown function type '{func}' for variable '{var}'")

    return pd.DataFrame([results])