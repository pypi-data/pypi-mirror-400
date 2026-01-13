"""
AM_filler - Automatic Missing Value Filler

A Python library that automatically fills missing values in datasets
using intelligent strategies based on column type detection.

Example:
    >>> from am_filler import AMFiller
    >>> df_clean = AMFiller().fit_transform(df)
"""

__version__ = "1.0.0"
__author__ = "AM_filler Team"

from .core import AMFiller
from .utils import detect_column_type, configure_logger
from .numeric import fill_numeric, detect_skewness, detect_outliers
from .categorical import fill_categorical
from .text import fill_text

__all__ = [
    "AMFiller",
    "detect_column_type",
    "configure_logger",
    "fill_numeric",
    "detect_skewness",
    "detect_outliers",
    "fill_categorical",
    "fill_text",
]
