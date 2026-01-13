import pandas as pd
import numpy as np

from scipy.stats import skew, kurtosis

def annual_mean(ts: pd.Series) -> float:
    """
    Calculates the mean of annual means from a time series.
    The annual mean is computed for each year using daily values.

    Parameters
    ----------
    ts : pd.Series
        Time series of daily values, indexed by datetime.

    Returns
    -------
    float
        Mean of the annual mean values across all years.
    """
    if ts.empty:
        return float('nan')

    # Group by year and calculate mean surface area for each year
    annual_means = ts.groupby(ts.index.year).mean()

    # Return the mean of these annual means
    return annual_means.mean()

def annual_std(ts: pd.Series) -> float:
    """
    Calculates the mean annual standard deviation from a time series.
    Standard deviation is computed for each year using daily values.

    Parameters
    ----------
    ts : pd.Series
        Time series of daily values, indexed by datetime.

    Returns
    -------
    float
        Mean standard deviation across all years.
    """
    if ts.empty:
        return float('nan')

    # Group by year and compute standard deviation for each year
    annual_std_values = ts.groupby(ts.index.year).std()

    # Return the mean standard deviation across years
    return annual_std_values.mean()

# Skewness
def skewness(ts: pd.Series) -> float:
    """
    Calculates skewness of the given time series.

    Parameters
    ----------
    ts : pd.Series
        Time series, indexed by datetime.

    Returns
    -------
    float
        Skewness of the time series (unitless).
    """
    if ts.empty:
        return float('nan')
    return skew(ts.dropna())

# Kurtosis
def kurtosis_val(ts: pd.Series) -> float:
    """
    Calculates kurtosis of the given time series.

    Parameters
    ----------
    ts : pd.Series
        Time series, indexed by datetime.

    Returns
    -------
    float
        Kurtosis of the time series (excess kurtosis, unitless).
    """
    if ts.empty:
        return float('nan')
    return kurtosis(ts.dropna(), fisher=True)

# COV
def coefficient_of_variation(ts: pd.Series) -> float:
    """
    Calculates coefficient of variation (CV) of the given time series.

    Parameters
    ----------
    ts : pd.Series
        Time series, indexed by datetime.

    Returns
    -------
    float
        Coefficient of variation (std/mean, unitless).
    """
    if ts.empty:
        return float('nan')
    mean_val = ts.mean()
    if mean_val == 0:
        return float('nan')
    return ts.std() / mean_val



def max_days_above_90th(ts: pd.Series) -> float:
    """
    Calculates the maximum number of days per year where the daily values 
    exceed the 90th percentile threshold (computed over the entire time series).

    Parameters
    ----------
    ts : pd.Series
        Time series of daily values, indexed by datetime.

    Returns
    -------
    float
        Maximum count of days above the 90th percentile across years.
    """
    if ts.empty:
        return float('nan')

    # Compute global 90th percentile threshold
    threshold = np.nanpercentile(ts, 90)

    # Boolean series: True if value > threshold
    above_threshold = ts > threshold

    # Count per year
    annual_counts = above_threshold.groupby(ts.index.year).sum()

    # Return maximum count across years
    return float(annual_counts.max()) if not annual_counts.empty else float('nan')

def max_annual_persistence(timeseries, threshold=1/np.e, min_periods=30):
    """
    Compute the persistence (decorrelation time) of high values in a time series annually.
    
    Parameters
    ----------
    timeseries : pd.Series
        A datetime-indexed series of daily values.
    threshold : float, optional
        Autocorrelation cutoff (default=1/e ~ 0.367).
    min_periods : int, optional
        Minimum number of days required in a year to compute autocorrelation.
    
    Returns
    -------
    int
        Maximum persistence (days) across all years.
    """
    
    results = {}
    
    # group by year
    for year, group in timeseries.groupby(timeseries.index.year):
        if len(group) < min_periods:
            continue
        
        # normalize (remove mean, divide std)
        x = (group - group.mean()) / group.std()
        n = len(x)
        
        # compute autocorrelation using np.correlate
        acf = np.correlate(x, x, mode='full') / n
        acf = acf[n-1:] / acf[n-1]  # keep positive lags, normalize at lag 0 = 1
        
        # find first lag where acf < threshold
        persistence = np.argmax(acf < threshold)
        if persistence == 0:  # if acf never drops below threshold
            persistence = len(acf) - 1
        
        results[year] = persistence
    
    if not results:
        return float('nan')
    
    return max(results.values())