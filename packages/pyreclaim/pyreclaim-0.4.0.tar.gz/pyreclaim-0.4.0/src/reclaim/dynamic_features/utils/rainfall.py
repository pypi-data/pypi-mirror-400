import pandas as pd

def mean_annual_rainfall_mm(ts: pd.Series) -> float:
    """
    Calculates the mean annual rainfall in mm from a time series of daily rainfall in mm.

    Parameters
    ----------
    ts : pd.Series
        Time series of daily rainfall values in mm, indexed by datetime.

    Returns
    -------
    float
        Mean annual rainfall in mm.
    """
    if ts.empty:
        return float('nan')

    # Total rainfall for each year (mm/year)
    annual_totals_mm = ts.groupby(ts.index.year).sum()

    # Return mean annual rainfall (mm/year)
    return annual_totals_mm.mean()

def mean_annual_rainy_days(ts: pd.Series, threshold: float = 100.0) -> float:
    """
    Calculates the mean annual number of days on which daily rainfall exceeds a threshold.

    Parameters
    ----------
    ts : pd.Series
        Time series of daily rainfall values in mm, indexed by datetime.
    threshold : float, optional
        Rainfall threshold in mm to define a "rainy day" (default is 10 mm).

    Returns
    -------
    float
        Mean annual number of days exceeding the threshold.
    """
    if ts.empty:
        return float('nan')

    # Count days above threshold for each year
    rainy_days_per_year = ts.groupby(ts.index.year).apply(lambda x: (x > threshold).sum())

    # Return mean number of rainy days across years
    return rainy_days_per_year.mean()