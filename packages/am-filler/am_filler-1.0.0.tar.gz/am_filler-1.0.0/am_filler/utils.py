"""
AM_filler Utility Functions
Helper functions for column type detection, logging, and other utilities.
"""

import logging
import re
from typing import Literal

import pandas as pd
import numpy as np


# Column type constants
COLUMN_TYPE_NUMERIC = "numeric"
COLUMN_TYPE_CATEGORICAL = "categorical"
COLUMN_TYPE_TEXT = "text"

ColumnType = Literal["numeric", "categorical", "text"]


def configure_logger(name: str = "am_filler", level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger for AM_filler.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(level)
    return logger


def is_text_column(series: pd.Series, word_threshold: int = 3) -> bool:
    """
    Detect if a column contains sentence-like text.
    
    A column is considered text if:
    - It's of object/string dtype
    - Average word count per entry is >= word_threshold
    - Contains punctuation typical of sentences
    
    Args:
        series: Pandas Series to analyze
        word_threshold: Minimum average words to classify as text
    
    Returns:
        True if column appears to contain text/sentences
    """
    if series.dtype not in [object, "string"]:
        return False
    
    # Get non-null values
    non_null = series.dropna()
    if len(non_null) == 0:
        return False
    
    # Convert to string and calculate word counts
    str_values = non_null.astype(str)
    word_counts = str_values.apply(lambda x: len(x.split()))
    avg_words = word_counts.mean()
    
    # Check for sentence-like characteristics
    has_punctuation = str_values.apply(
        lambda x: bool(re.search(r'[.!?,;:]', x))
    ).mean() > 0.3
    
    return avg_words >= word_threshold or has_punctuation


def detect_column_type(series: pd.Series) -> ColumnType:
    """
    Automatically detect the type of a column.
    
    Classification logic:
    1. Numeric types (int, float) -> "numeric"
    2. Text columns (sentence-like) -> "text"
    3. Everything else (object, category) -> "categorical"
    
    Args:
        series: Pandas Series to classify
    
    Returns:
        Column type: "numeric", "categorical", or "text"
    """
    # Check for numeric types
    if pd.api.types.is_numeric_dtype(series):
        return COLUMN_TYPE_NUMERIC
    
    # Check for text/sentence columns
    if is_text_column(series):
        return COLUMN_TYPE_TEXT
    
    # Default to categorical
    return COLUMN_TYPE_CATEGORICAL


def get_missing_summary(df_original: pd.DataFrame, df_filled: pd.DataFrame) -> dict:
    """
    Generate a summary of missing values filled.
    
    Args:
        df_original: Original DataFrame with missing values
        df_filled: DataFrame after imputation
    
    Returns:
        Dictionary with column-wise missing value counts
    """
    summary = {}
    
    for col in df_original.columns:
        original_missing = df_original[col].isna().sum()
        filled_missing = df_filled[col].isna().sum()
        
        if original_missing > 0:
            summary[col] = {
                "original_missing": int(original_missing),
                "remaining_missing": int(filled_missing),
                "filled": int(original_missing - filled_missing)
            }
    
    return summary
