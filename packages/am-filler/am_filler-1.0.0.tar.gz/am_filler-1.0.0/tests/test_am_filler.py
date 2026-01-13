"""
AM_filler Unit Tests

Comprehensive tests for all imputation modules.
"""

import pytest
import pandas as pd
import numpy as np
from scipy import stats

# Import AM_filler components
from am_filler import AMFiller, detect_column_type
from am_filler.numeric import fill_numeric, detect_skewness, detect_outliers
from am_filler.categorical import fill_categorical
from am_filler.text import fill_text
from am_filler.utils import is_text_column


class TestColumnTypeDetection:
    """Tests for automatic column type detection."""
    
    def test_numeric_int_detection(self):
        series = pd.Series([1, 2, 3, 4, 5])
        assert detect_column_type(series) == "numeric"
    
    def test_numeric_float_detection(self):
        series = pd.Series([1.1, 2.2, 3.3, None, 5.5])
        assert detect_column_type(series) == "numeric"
    
    def test_categorical_detection(self):
        series = pd.Series(["a", "b", "c", "a", "b"])
        assert detect_column_type(series) == "categorical"
    
    def test_text_detection(self):
        series = pd.Series([
            "This is a long sentence with many words.",
            "Another sentence here with punctuation!",
            "Yet another descriptive piece of text.",
        ])
        assert detect_column_type(series) == "text"


class TestNumericImputation:
    """Tests for numeric missing value imputation."""
    
    def test_skewness_detection_normal(self):
        # Normal distribution should not be skewed
        np.random.seed(42)
        normal_data = pd.Series(np.random.normal(0, 1, 100))
        assert detect_skewness(normal_data) == False
    
    def test_skewness_detection_skewed(self):
        # Exponential distribution is skewed
        np.random.seed(42)
        skewed_data = pd.Series(np.random.exponential(1, 100))
        assert detect_skewness(skewed_data) == True
    
    def test_outlier_detection_with_outliers(self):
        series = pd.Series([1, 2, 3, 4, 5, 100, 200])  # 100 and 200 are outliers
        assert detect_outliers(series) == True
    
    def test_outlier_detection_no_outliers(self):
        series = pd.Series([1, 2, 3, 4, 5, 6, 7])
        assert detect_outliers(series) == False
    
    def test_fill_numeric_uses_mean_for_normal(self):
        np.random.seed(42)
        data = np.random.normal(50, 5, 100)
        data[0] = np.nan
        series = pd.Series(data)
        
        filled, strategy, value = fill_numeric(series)
        
        assert filled.isna().sum() == 0
        assert "mean" in strategy
    
    def test_fill_numeric_uses_median_for_skewed(self):
        np.random.seed(42)
        data = list(np.random.exponential(10, 50)) + [np.nan]
        series = pd.Series(data)
        
        filled, strategy, value = fill_numeric(series)
        
        assert filled.isna().sum() == 0
        assert "median" in strategy


class TestCategoricalImputation:
    """Tests for categorical missing value imputation."""
    
    def test_fill_categorical_uses_mode(self):
        series = pd.Series(["a", "a", "a", "b", "c", np.nan])
        
        filled, strategy, value = fill_categorical(series)
        
        assert filled.isna().sum() == 0
        assert strategy == "mode"
        assert value == "a"  # Most common value
    
    def test_fill_categorical_all_missing(self):
        series = pd.Series([np.nan, np.nan, np.nan])
        
        filled, strategy, value = fill_categorical(series)
        
        assert "skipped" in strategy
    
    def test_fill_categorical_no_missing(self):
        series = pd.Series(["a", "b", "c"])
        
        filled, strategy, value = fill_categorical(series)
        
        assert strategy == "none"


class TestTextImputation:
    """Tests for text missing value imputation."""
    
    def test_is_text_column_true(self):
        series = pd.Series([
            "This is a complete sentence with many words.",
            "Another descriptive text entry here.",
            "More text content for testing purposes.",
        ])
        assert is_text_column(series) == True
    
    def test_is_text_column_false(self):
        series = pd.Series(["a", "b", "c"])
        assert is_text_column(series) == False
    
    def test_fill_text_fills_missing(self):
        series = pd.Series(["Hello world.", np.nan, "Goodbye world."])
        
        filled, strategy, sample = fill_text(series)
        
        assert filled.isna().sum() == 0
        assert "predefined" in strategy
    
    def test_fill_text_no_missing(self):
        series = pd.Series(["Hello.", "World.", "Test."])
        
        filled, strategy, sample = fill_text(series)
        
        assert strategy == "none"


class TestAMFillerIntegration:
    """Integration tests for the main AMFiller class."""
    
    def test_fit_transform_basic(self):
        df = pd.DataFrame({
            "num": [1.0, 2.0, np.nan, 4.0],
            "cat": ["a", np.nan, "a", "b"],
        })
        
        filler = AMFiller(verbose=False)
        result = filler.fit_transform(df)
        
        assert result.isna().sum().sum() == 0
    
    def test_fit_transform_preserves_non_missing(self):
        df = pd.DataFrame({
            "num": [1.0, 2.0, np.nan, 4.0],
        })
        
        filler = AMFiller(verbose=False)
        result = filler.fit_transform(df)
        
        assert result.loc[0, "num"] == 1.0
        assert result.loc[1, "num"] == 2.0
        assert result.loc[3, "num"] == 4.0
    
    def test_fit_then_transform(self):
        df = pd.DataFrame({
            "num": [1.0, np.nan, 3.0],
        })
        
        filler = AMFiller(verbose=False)
        filler.fit(df)
        result = filler.transform(df)
        
        assert result.isna().sum().sum() == 0
    
    def test_transform_without_fit_raises(self):
        df = pd.DataFrame({"num": [1.0, np.nan]})
        filler = AMFiller(verbose=False)
        
        with pytest.raises(ValueError):
            filler.transform(df)
    
    def test_get_strategies(self):
        df = pd.DataFrame({
            "num": [1.0, 2.0, np.nan],
            "cat": ["a", "b", np.nan],
        })
        
        filler = AMFiller(verbose=False)
        filler.fit(df)
        strategies = filler.get_strategies()
        
        assert "num" in strategies
        assert "cat" in strategies
        assert strategies["num"]["type"] == "numeric"
        assert strategies["cat"]["type"] == "categorical"
    
    def test_mixed_dataframe(self):
        df = pd.DataFrame({
            "age": [25, 30, np.nan, 35],
            "city": ["NYC", np.nan, "LA", "NYC"],
            "bio": [
                "Software engineer with experience.",
                np.nan,
                "Data scientist passionate about AI.",
                "Product manager.",
            ],
        })
        
        filler = AMFiller(verbose=False)
        result = filler.fit_transform(df)
        
        assert result.isna().sum().sum() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
