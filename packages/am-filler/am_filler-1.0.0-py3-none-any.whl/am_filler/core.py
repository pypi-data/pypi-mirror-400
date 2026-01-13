"""
AM_filler Core Module
Main AMFiller class that orchestrates automatic missing value imputation.
"""

import logging
from typing import Dict, Any, Optional

import pandas as pd

from .utils import (
    detect_column_type,
    configure_logger,
    get_missing_summary,
    COLUMN_TYPE_NUMERIC,
    COLUMN_TYPE_CATEGORICAL,
    COLUMN_TYPE_TEXT,
)
from .numeric import fill_numeric
from .categorical import fill_categorical
from .text import fill_text


class AMFiller:
    """
    Automatic Missing Value Filler.
    
    Automatically detects column types and applies the best imputation
    strategy for each column without requiring user configuration.
    
    Features:
        - Automatic column type detection (numeric, categorical, text)
        - Smart numeric imputation (mean vs median based on distribution)
        - Mode-based categorical imputation
        - Context-aware text imputation with meaningful sentences
        - Optional logging of imputation strategies
    
    Example:
        >>> from am_filler import AMFiller
        >>> df_clean = AMFiller().fit_transform(df)
    """
    
    def __init__(self, verbose: bool = True, log_level: int = logging.INFO):
        """
        Initialize AMFiller.
        
        Args:
            verbose: Whether to print imputation summary (default: True)
            log_level: Logging level (default: INFO)
        """
        self.verbose = verbose
        self.logger = configure_logger("am_filler", log_level)
        
        # Stores learned imputation strategies after fit()
        self._strategies: Dict[str, Dict[str, Any]] = {}
        self._is_fitted: bool = False
    
    def fit(self, df: pd.DataFrame) -> "AMFiller":
        """
        Analyze the DataFrame and determine imputation strategies.
        
        Args:
            df: Input DataFrame to analyze
        
        Returns:
            Self (for method chaining)
        """
        self._strategies = {}
        
        for col in df.columns:
            series = df[col]
            missing_count = series.isna().sum()
            
            if missing_count == 0:
                self._strategies[col] = {
                    "type": detect_column_type(series),
                    "strategy": "none",
                    "has_missing": False,
                }
                continue
            
            col_type = detect_column_type(series)
            
            self._strategies[col] = {
                "type": col_type,
                "has_missing": True,
                "missing_count": missing_count,
            }
            
            if self.verbose:
                self.logger.info(
                    f"Column '{col}': {col_type} type, {missing_count} missing values"
                )
        
        self._is_fitted = True
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply imputation strategies to fill missing values.
        
        Args:
            df: DataFrame to transform
        
        Returns:
            DataFrame with missing values filled
        """
        if not self._is_fitted:
            raise ValueError("AMFiller must be fitted before transform. Call fit() first.")
        
        df_filled = df.copy()
        imputation_log = []
        
        for col in df.columns:
            if col not in self._strategies:
                continue
            
            strategy_info = self._strategies[col]
            
            if not strategy_info.get("has_missing", False):
                continue
            
            col_type = strategy_info["type"]
            series = df_filled[col]
            
            if col_type == COLUMN_TYPE_NUMERIC:
                filled_series, strategy_desc, fill_value = fill_numeric(series)
                df_filled[col] = filled_series
                imputation_log.append({
                    "column": col,
                    "type": col_type,
                    "strategy": strategy_desc,
                    "fill_value": fill_value,
                })
                
            elif col_type == COLUMN_TYPE_CATEGORICAL:
                filled_series, strategy_desc, fill_value = fill_categorical(series)
                df_filled[col] = filled_series
                imputation_log.append({
                    "column": col,
                    "type": col_type,
                    "strategy": strategy_desc,
                    "fill_value": fill_value,
                })
                
            elif col_type == COLUMN_TYPE_TEXT:
                filled_series, strategy_desc, sample_value = fill_text(series, col)
                df_filled[col] = filled_series
                imputation_log.append({
                    "column": col,
                    "type": col_type,
                    "strategy": strategy_desc,
                    "sample_fill": sample_value,
                })
        
        # Log summary
        if self.verbose and imputation_log:
            self._print_summary(imputation_log)
        
        return df_filled
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and transform in one step - the main one-line API.
        
        Args:
            df: DataFrame with missing values
        
        Returns:
            DataFrame with missing values filled
        """
        return self.fit(df).transform(df)
    
    def get_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the learned imputation strategies.
        
        Returns:
            Dictionary of column strategies
        """
        return self._strategies.copy()
    
    def _print_summary(self, imputation_log: list) -> None:
        """Print a summary of imputation actions."""
        print("\n" + "=" * 60)
        print("AM_FILLER IMPUTATION SUMMARY")
        print("=" * 60)
        
        for entry in imputation_log:
            col = entry["column"]
            col_type = entry["type"]
            strategy = entry["strategy"]
            
            print(f"\n[Column: '{col}']")
            print(f"   Type: {col_type}")
            print(f"   Strategy: {strategy}")
            
            if "fill_value" in entry and entry["fill_value"] is not None:
                fill_val = entry["fill_value"]
                if isinstance(fill_val, float):
                    print(f"   Fill Value: {fill_val:.4f}")
                else:
                    print(f"   Fill Value: {fill_val}")
            elif "sample_fill" in entry:
                print(f"   Sample Fill: \"{entry['sample_fill']}\"")
        
        print("\n" + "=" * 60)
        print(f"[OK] Successfully filled {len(imputation_log)} column(s)")
        print("=" * 60 + "\n")
