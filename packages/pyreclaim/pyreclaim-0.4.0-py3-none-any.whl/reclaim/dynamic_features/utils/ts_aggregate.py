import pandas as pd
from typing import Callable, Union, Sequence

def compute_ts_aggregate(
    ts_csv_path: str,
    time_column: str,
    value_column: str,
    feature_function: Callable,
    feature_name: str,
    observation_period: Union[Sequence[int], None] = None
) -> pd.DataFrame:
    """
    Compute an aggregate feature from a user-provided time series CSV for a single reservoir.

    Parameters
    ----------
    ts_csv_path : str
        Path to the CSV file containing the time series.
    time_column : str
        Name of the column representing dates/timestamps.
    value_column : str
        Name of the column representing the variable values.
    feature_function : Callable
        Function that takes a pd.Series (the time series) and returns a single value.
    feature_name : str
        Name of the column to store the computed feature in the returned DataFrame.
    observation_period : list or tuple of two ints, optional
        [start_year, end_year] to clip the time series. If None, no clipping is applied.

    Returns
    -------
    pd.DataFrame
        A single-row DataFrame containing the computed feature with the specified column name.
    """

    # Load the CSV
    df = pd.read_csv(ts_csv_path)
    if df.empty:
        raise ValueError(f"CSV at {ts_csv_path} is empty.")
    
    # Ensure columns exist
    if time_column not in df.columns:
        raise ValueError(f"Time column '{time_column}' not found in CSV.")
    if value_column not in df.columns:
        raise ValueError(f"Value column '{value_column}' not found in CSV.")

    # Ensure time column is datetime
    df[time_column] = pd.to_datetime(df[time_column], errors='coerce')
    if df[time_column].isna().all():
        raise ValueError(f"Time column '{time_column}' could not be converted to datetime.")

    # Set index
    ts = df.set_index(time_column)[value_column]

    # Clip to observation period if provided
    if observation_period is not None:
        start_year, end_year = observation_period
        ts = ts[(ts.index.year >= start_year) & (ts.index.year <= end_year)]

    # Remove NaNs
    ts_clean = ts.dropna()
    if ts_clean.empty:
        raise ValueError("Time series has no valid data after clipping/removing NaNs.")

    # Apply user-defined feature function
    feature_value = feature_function(ts_clean)

    # Return as single-row DataFrame with user-specified column name
    return pd.DataFrame({feature_name: [feature_value]})