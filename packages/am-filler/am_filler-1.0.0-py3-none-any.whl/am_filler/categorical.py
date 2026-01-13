"""
AM_filler Categorical Imputation Module
Handles missing value imputation for categorical columns.
"""

import random
from typing import Tuple, Any

import pandas as pd


def fill_categorical(series: pd.Series) -> Tuple[pd.Series, str, Any]:
    """
    Fill missing values in a categorical column.
    
    Strategy:
    1. Use MODE if available (most frequent value)
    2. Random choice from existing values as fallback
    
    Args:
        series: Categorical pandas Series with missing values
    
    Returns:
        Tuple of (filled_series, strategy_used, fill_value)
    """
    if series.isna().sum() == 0:
        return series.copy(), "none", None
    
    # Get non-null values
    non_null = series.dropna()
    
    if len(non_null) == 0:
        # All values are missing - cannot impute
        return series.copy(), "skipped (all missing)", None
    
    # Try to use mode
    mode_values = non_null.mode()
    
    if len(mode_values) > 0:
        fill_value = mode_values.iloc[0]
        strategy = "mode"
    else:
        # Fallback to random choice
        fill_value = random.choice(non_null.tolist())
        strategy = "random choice"
    
    filled_series = series.fillna(fill_value)
    
    return filled_series, strategy, fill_value


def fill_categorical_random(series: pd.Series) -> Tuple[pd.Series, str]:
    """
    Fill each missing value with a random choice from existing values.
    
    This is useful when you want more variety in imputed values
    rather than filling all with the same value.
    
    Args:
        series: Categorical pandas Series with missing values
    
    Returns:
        Tuple of (filled_series, strategy_used)
    """
    if series.isna().sum() == 0:
        return series.copy(), "none"
    
    non_null = series.dropna()
    
    if len(non_null) == 0:
        return series.copy(), "skipped (all missing)"
    
    # Create a copy and fill each missing value randomly
    filled_series = series.copy()
    missing_mask = series.isna()
    n_missing = missing_mask.sum()
    
    # Generate random choices for all missing values
    random_values = random.choices(non_null.tolist(), k=n_missing)
    filled_series.loc[missing_mask] = random_values
    
    return filled_series, "random choice (varied)"
