"""
Test suite for numeric.py module
Tests for: detect_skewness, detect_outliers, determine_numeric_strategy, fill_numeric
"""

import pytest
import pandas as pd
import numpy as np
from scipy import stats

from am_filler.numeric import (
    detect_skewness,
    detect_outliers,
    determine_numeric_strategy,
    fill_numeric,
)


class TestDetectSkewness:
    """Tests for detect_skewness function."""
    
    def test_normal_distribution_not_skewed(self):
        """Normal distribution should not be detected as skewed."""
        np.random.seed(42)
        data = pd.Series(np.random.normal(100, 10, 200))
        assert detect_skewness(data) == False
    
    def test_exponential_distribution_is_skewed(self):
        """Exponential distribution should be detected as skewed."""
        np.random.seed(42)
        data = pd.Series(np.random.exponential(5, 200))
        assert detect_skewness(data) == True
    
    def test_right_skewed_data(self):
        """Right-skewed data should be detected."""
        data = pd.Series([1, 1, 1, 2, 2, 3, 3, 4, 5, 100])
        assert detect_skewness(data) == True
    
    def test_left_skewed_data(self):
        """Left-skewed data should be detected."""
        data = pd.Series([1, 95, 96, 97, 97, 98, 98, 99, 99, 100])
        assert detect_skewness(data) == True
    
    def test_too_few_values_returns_false(self):
        """Less than 3 values should return False."""
        data = pd.Series([1, 2])
        assert detect_skewness(data) == False
    
    def test_handles_nan_values(self):
        """Should handle NaN values correctly."""
        np.random.seed(42)
        data = pd.Series([np.nan] + list(np.random.normal(50, 5, 100)))
        result = detect_skewness(data)
        assert isinstance(result, bool)
    
    def test_custom_threshold(self):
        """Custom threshold should work."""
        data = pd.Series([1, 2, 2, 3, 3, 3, 4, 4, 5])  # Slightly skewed
        # With high threshold, should not be skewed
        assert detect_skewness(data, threshold=2.0) == False


class TestDetectOutliers:
    """Tests for detect_outliers function."""
    
    def test_data_with_obvious_outliers(self):
        """Data with obvious outliers should be detected."""
        data = pd.Series([10, 11, 12, 13, 14, 15, 100, 200, 300])
        assert detect_outliers(data) == True
    
    def test_data_without_outliers(self):
        """Data without outliers should return False."""
        data = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
        assert detect_outliers(data) == False
    
    def test_uniform_data(self):
        """Uniform data should have no outliers."""
        np.random.seed(42)
        data = pd.Series(np.random.uniform(0, 100, 50))
        # Uniform data typically has no outliers
        assert detect_outliers(data) == False
    
    def test_too_few_values_returns_false(self):
        """Less than 4 values should return False."""
        data = pd.Series([1, 100, 1000])
        assert detect_outliers(data) == False
    
    def test_handles_nan_values(self):
        """Should handle NaN values correctly."""
        data = pd.Series([np.nan, 10, 11, 12, 13, 14, 15, np.nan])
        result = detect_outliers(data)
        assert isinstance(result, bool)
    
    def test_custom_iqr_multiplier(self):
        """Custom IQR multiplier should work."""
        data = pd.Series([10, 11, 12, 13, 14, 15, 30])
        # With higher multiplier, fewer outliers detected
        assert detect_outliers(data, iqr_multiplier=6.0) == False


class TestDetermineNumericStrategy:
    """Tests for determine_numeric_strategy function."""
    
    def test_normal_data_uses_mean(self):
        """Normal data should use mean strategy."""
        np.random.seed(42)
        data = pd.Series(np.random.normal(50, 5, 100))
        strategy, reason = determine_numeric_strategy(data)
        assert strategy == "mean"
        assert "normal" in reason
    
    def test_skewed_data_uses_median(self):
        """Skewed data should use median strategy."""
        np.random.seed(42)
        data = pd.Series(np.random.exponential(10, 100))
        strategy, reason = determine_numeric_strategy(data)
        assert strategy == "median"
    
    def test_data_with_outliers_uses_median(self):
        """Data with outliers should use median strategy."""
        data = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 500, 600, 700])
        strategy, reason = determine_numeric_strategy(data)
        assert strategy == "median"
        assert "outlier" in reason
    
    def test_skewed_with_outliers(self):
        """Data that is both skewed and has outliers."""
        data = pd.Series([1, 1, 1, 2, 2, 3, 5, 10, 50, 100, 1000])
        strategy, reason = determine_numeric_strategy(data)
        assert strategy == "median"


class TestFillNumeric:
    """Tests for fill_numeric function."""
    
    def test_fills_missing_values(self):
        """Should fill all missing values."""
        data = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0, np.nan])
        filled, strategy, value = fill_numeric(data)
        assert filled.isna().sum() == 0
    
    def test_preserves_original_values(self):
        """Should preserve non-missing values."""
        data = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        filled, strategy, value = fill_numeric(data)
        assert filled.iloc[0] == 1.0
        assert filled.iloc[1] == 2.0
        assert filled.iloc[3] == 4.0
        assert filled.iloc[4] == 5.0
    
    def test_returns_correct_strategy_mean(self):
        """Should return mean strategy for normal data."""
        np.random.seed(42)
        data = list(np.random.normal(50, 5, 50))
        data[0] = np.nan
        series = pd.Series(data)
        filled, strategy, value = fill_numeric(series)
        assert "mean" in strategy
    
    def test_returns_correct_strategy_median(self):
        """Should return median strategy for skewed data."""
        np.random.seed(42)
        data = list(np.random.exponential(10, 50))
        data[0] = np.nan
        series = pd.Series(data)
        filled, strategy, value = fill_numeric(series)
        assert "median" in strategy
    
    def test_no_missing_values_returns_none_strategy(self):
        """Should return 'none' strategy when no missing values."""
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        filled, strategy, value = fill_numeric(data)
        assert strategy == "none"
        assert np.isnan(value)
    
    def test_returns_correct_fill_value(self):
        """Should return the actual fill value used."""
        data = pd.Series([10.0, 20.0, np.nan, 40.0])  # Mean = 23.33
        filled, strategy, value = fill_numeric(data)
        assert isinstance(value, (int, float))
        assert not np.isnan(value)
    
    def test_single_missing_value(self):
        """Should handle single missing value correctly."""
        data = pd.Series([10.0, 20.0, 30.0, np.nan])
        filled, strategy, value = fill_numeric(data)
        assert filled.isna().sum() == 0
    
    def test_all_nan_except_one(self):
        """Should handle mostly NaN data."""
        data = pd.Series([np.nan, np.nan, np.nan, 100.0])
        filled, strategy, value = fill_numeric(data)
        # Should fill with the only available value
        assert filled.isna().sum() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
