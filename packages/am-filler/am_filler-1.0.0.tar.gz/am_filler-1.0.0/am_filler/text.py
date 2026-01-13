"""
AM_filler Text Imputation Module
Handles missing value imputation for text/sentence columns.
"""

import random
from typing import Tuple, List

import pandas as pd


# Predefined meaningful sentences for text imputation
DEFAULT_TEXT_TEMPLATES = [
    "Information not available.",
    "No description provided.",
    "Details pending review.",
    "Content to be updated.",
    "Additional information required.",
    "Description not specified.",
    "Data entry incomplete.",
    "Information unavailable at this time.",
    "Awaiting further details.",
    "No additional comments.",
]

# Domain-specific templates
PRODUCT_DESCRIPTIONS = [
    "High-quality product with excellent features.",
    "Premium item designed for everyday use.",
    "Reliable and durable product.",
    "A versatile solution for your needs.",
    "Well-crafted item with attention to detail.",
]

REVIEW_TEMPLATES = [
    "No review submitted yet.",
    "Customer feedback pending.",
    "Review not available.",
    "Awaiting customer review.",
    "No comments from buyer.",
]

NOTES_TEMPLATES = [
    "No notes added.",
    "Additional notes pending.",
    "Notes to be updated.",
    "No additional notes.",
    "Information to be added later.",
]


def get_text_templates(column_name: str = "") -> List[str]:
    """
    Get appropriate text templates based on column name hints.
    
    Args:
        column_name: Name of the column (used for context hints)
    
    Returns:
        List of appropriate text templates
    """
    col_lower = column_name.lower()
    
    if any(word in col_lower for word in ["description", "desc", "product"]):
        return PRODUCT_DESCRIPTIONS
    elif any(word in col_lower for word in ["review", "feedback", "comment"]):
        return REVIEW_TEMPLATES
    elif any(word in col_lower for word in ["note", "remark", "observation"]):
        return NOTES_TEMPLATES
    else:
        return DEFAULT_TEXT_TEMPLATES


def fill_text(series: pd.Series, column_name: str = "") -> Tuple[pd.Series, str, str]:
    """
    Fill missing values in a text column with meaningful sentences.
    
    Args:
        series: Text pandas Series with missing values
        column_name: Name of the column for context-aware filling
    
    Returns:
        Tuple of (filled_series, strategy_used, sample_fill_value)
    """
    if series.isna().sum() == 0:
        return series.copy(), "none", ""
    
    templates = get_text_templates(column_name)
    
    # Fill each missing value with a random template
    filled_series = series.copy().astype(object)
    missing_mask = series.isna()
    n_missing = missing_mask.sum()
    
    # Generate random sentences for all missing values
    random_sentences = random.choices(templates, k=n_missing)
    filled_series.loc[missing_mask] = random_sentences
    
    strategy = f"predefined sentences ({len(templates)} templates)"
    sample = random_sentences[0] if random_sentences else ""
    
    return filled_series, strategy, sample


def fill_text_from_existing(series: pd.Series) -> Tuple[pd.Series, str]:
    """
    Fill missing text values by randomly selecting from existing values.
    
    This is an alternative strategy that maintains consistency
    with the existing data patterns.
    
    Args:
        series: Text pandas Series with missing values
    
    Returns:
        Tuple of (filled_series, strategy_used)
    """
    if series.isna().sum() == 0:
        return series.copy(), "none"
    
    non_null = series.dropna()
    
    if len(non_null) == 0:
        # Fall back to templates if no existing values
        return fill_text(series)[0], "predefined (no existing values)"
    
    filled_series = series.copy()
    missing_mask = series.isna()
    n_missing = missing_mask.sum()
    
    random_values = random.choices(non_null.tolist(), k=n_missing)
    filled_series.loc[missing_mask] = random_values
    
    return filled_series, "random from existing"




