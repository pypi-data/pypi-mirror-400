"""
Test suite for categorical.py module
Tests for: fill_categorical, fill_categorical_random
"""

import pytest
import pandas as pd
import numpy as np

from am_filler.categorical import fill_categorical, fill_categorical_random


class TestFillCategorical:
    """Tests for fill_categorical function."""
    
    def test_fills_missing_with_mode(self):
        """Should fill missing values with the mode."""
        series = pd.Series(["a", "a", "a", "b", "c", np.nan, np.nan])
        filled, strategy, value = fill_categorical(series)
        
        assert filled.isna().sum() == 0
        assert strategy == "mode"
        assert value == "a"  # Most frequent value
    
    def test_preserves_original_values(self):
        """Should preserve non-missing values."""
        series = pd.Series(["x", "y", "z", np.nan])
        filled, strategy, value = fill_categorical(series)
        
        assert filled.iloc[0] == "x"
        assert filled.iloc[1] == "y"
        assert filled.iloc[2] == "z"
    
    def test_no_missing_returns_none_strategy(self):
        """Should return 'none' strategy when no missing values."""
        series = pd.Series(["a", "b", "c", "a"])
        filled, strategy, value = fill_categorical(series)
        
        assert strategy == "none"
        assert value is None
    
    def test_all_missing_returns_skipped(self):
        """Should return 'skipped' when all values are missing."""
        series = pd.Series([np.nan, np.nan, np.nan])
        filled, strategy, value = fill_categorical(series)
        
        assert "skipped" in strategy
        assert value is None
    
    def test_single_unique_value(self):
        """Should handle series with single unique value."""
        series = pd.Series(["only_one", "only_one", np.nan])
        filled, strategy, value = fill_categorical(series)
        
        assert filled.isna().sum() == 0
        assert value == "only_one"
    
    def test_multiple_modes_uses_first(self):
        """When multiple modes exist, should use first one."""
        series = pd.Series(["a", "a", "b", "b", np.nan])
        filled, strategy, value = fill_categorical(series)
        
        assert filled.isna().sum() == 0
        assert value in ["a", "b"]  # Either is valid
    
    def test_handles_numeric_categories(self):
        """Should handle numeric categorical values."""
        series = pd.Series([1, 1, 2, 2, 2, np.nan])
        filled, strategy, value = fill_categorical(series)
        
        assert filled.isna().sum() == 0
        assert value == 2
    
    def test_handles_mixed_types(self):
        """Should handle mixed types in categories."""
        series = pd.Series(["cat", "cat", "dog", np.nan])
        filled, strategy, value = fill_categorical(series)
        
        assert filled.isna().sum() == 0
        assert value == "cat"
    
    def test_empty_series(self):
        """Should handle empty series gracefully."""
        series = pd.Series([], dtype=object)
        filled, strategy, value = fill_categorical(series)
        
        assert len(filled) == 0


class TestFillCategoricalRandom:
    """Tests for fill_categorical_random function."""
    
    def test_fills_all_missing(self):
        """Should fill all missing values."""
        series = pd.Series(["a", "b", "c", np.nan, np.nan, np.nan])
        filled, strategy = fill_categorical_random(series)
        
        assert filled.isna().sum() == 0
    
    def test_uses_existing_values(self):
        """Filled values should be from existing values only."""
        series = pd.Series(["x", "y", "z", np.nan, np.nan])
        filled, strategy = fill_categorical_random(series)
        
        existing = {"x", "y", "z"}
        for val in filled:
            assert val in existing
    
    def test_strategy_name(self):
        """Should return correct strategy name."""
        series = pd.Series(["a", np.nan])
        filled, strategy = fill_categorical_random(series)
        
        assert "random" in strategy
    
    def test_no_missing_returns_none(self):
        """Should return 'none' when no missing values."""
        series = pd.Series(["a", "b", "c"])
        filled, strategy = fill_categorical_random(series)
        
        assert strategy == "none"
    
    def test_all_missing_returns_skipped(self):
        """Should return 'skipped' when all missing."""
        series = pd.Series([np.nan, np.nan])
        filled, strategy = fill_categorical_random(series)
        
        assert "skipped" in strategy
    
    def test_preserves_non_missing(self):
        """Should preserve original non-missing values."""
        series = pd.Series(["original", np.nan, "keep"])
        filled, strategy = fill_categorical_random(series)
        
        assert filled.iloc[0] == "original"
        assert filled.iloc[2] == "keep"
    
    def test_fills_each_missing_separately(self):
        """Each missing value should be filled independently."""
        np.random.seed(42)
        series = pd.Series(["a", "b", "c", "d", "e"] + [np.nan] * 100)
        filled, strategy = fill_categorical_random(series)
        
        # With 100 missing values, should have variety
        filled_values = filled[5:].unique()
        assert len(filled_values) >= 2  # Should have some variety


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
