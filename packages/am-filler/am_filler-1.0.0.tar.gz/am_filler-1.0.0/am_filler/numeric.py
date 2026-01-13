"""
AM_filler Numeric Imputation Module
Handles missing value imputation for numeric columns using intelligent strategies.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Literal


def detect_skewness(series: pd.Series, threshold: float = 1.0) -> bool:
    """
    Detect if a numeric series is significantly skewed.
    
    Args:
        series: Numeric pandas Series
        threshold: Absolute skewness threshold (default: 1.0)
    
    Returns:
        True if series is skewed beyond threshold
    """
    clean_series = series.dropna()
    if len(clean_series) < 3:
        return False
    
    skew = stats.skew(clean_series)
    return bool(abs(skew) > threshold)


def detect_outliers(series: pd.Series, iqr_multiplier: float = 1.5) -> bool:
    """
    Detect if a numeric series contains significant outliers using IQR method.
    
    Args:
        series: Numeric pandas Series
        iqr_multiplier: IQR multiplier for outlier bounds (default: 1.5)
    
    Returns:
        True if outliers are detected
    """
    clean_series = series.dropna()
    if len(clean_series) < 4:
        return False
    
    q1 = clean_series.quantile(0.25)
    q3 = clean_series.quantile(0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - (iqr_multiplier * iqr)
    upper_bound = q3 + (iqr_multiplier * iqr)
    
    outliers = (clean_series < lower_bound) | (clean_series > upper_bound)
    outlier_ratio = outliers.sum() / len(clean_series)
    
    # Consider significant if more than 5% are outliers
    return bool(outlier_ratio > 0.05)


def determine_numeric_strategy(series: pd.Series) -> Tuple[Literal["mean", "median"], str]:
    """
    Determine the best imputation strategy for a numeric column.
    
    Strategy selection:
    - Use MEDIAN if column is skewed or has outliers (more robust)
    - Use MEAN if column is approximately normal
    
    Args:
        series: Numeric pandas Series
    
    Returns:
        Tuple of (strategy_name, reason)
    """
    is_skewed = detect_skewness(series)
    has_outliers = detect_outliers(series)
    
    if is_skewed and has_outliers:
        return "median", "skewed distribution with outliers"
    elif is_skewed:
        return "median", "skewed distribution"
    elif has_outliers:
        return "median", "presence of outliers"
    else:
        return "mean", "approximately normal distribution"


def fill_numeric(series: pd.Series) -> Tuple[pd.Series, str, float]:
    """
    Fill missing values in a numeric column using the best strategy.
    
    Args:
        series: Numeric pandas Series with missing values
    
    Returns:
        Tuple of (filled_series, strategy_used, fill_value)
    """
    if series.isna().sum() == 0:
        return series.copy(), "none", np.nan
    
    strategy, reason = determine_numeric_strategy(series)
    
    if strategy == "median":
        fill_value = series.median()
    else:
        fill_value = series.mean()
    
    filled_series = series.fillna(fill_value)
    strategy_desc = f"{strategy} ({reason})"
    
    return filled_series, strategy_desc, fill_value
