"""
Test suite for text.py module
Tests for: get_text_templates, fill_text, fill_text_from_existing
"""

import pytest
import pandas as pd
import numpy as np

from am_filler.text import (
    get_text_templates,
    fill_text,
    fill_text_from_existing,
    DEFAULT_TEXT_TEMPLATES,
    PRODUCT_DESCRIPTIONS,
    REVIEW_TEMPLATES,
    NOTES_TEMPLATES,
)


class TestGetTextTemplates:
    """Tests for get_text_templates function."""
    
    def test_default_templates_for_unknown_column(self):
        """Should return default templates for unknown column names."""
        templates = get_text_templates("random_column")
        assert templates == DEFAULT_TEXT_TEMPLATES
    
    def test_product_templates_for_description_column(self):
        """Should return product templates for description columns."""
        for col_name in ["description", "desc", "product_description", "DESCRIPTION"]:
            templates = get_text_templates(col_name)
            assert templates == PRODUCT_DESCRIPTIONS
    
    def test_review_templates_for_review_column(self):
        """Should return review templates for review/feedback columns."""
        for col_name in ["review", "feedback", "comment", "user_review"]:
            templates = get_text_templates(col_name)
            assert templates == REVIEW_TEMPLATES
    
    def test_notes_templates_for_notes_column(self):
        """Should return notes templates for notes/remark columns."""
        for col_name in ["note", "remark", "observation", "notes"]:
            templates = get_text_templates(col_name)
            assert templates == NOTES_TEMPLATES
    
    def test_empty_column_name(self):
        """Should return default templates for empty column name."""
        templates = get_text_templates("")
        assert templates == DEFAULT_TEXT_TEMPLATES
    
    def test_case_insensitive(self):
        """Column name matching should be case insensitive."""
        templates_lower = get_text_templates("description")
        templates_upper = get_text_templates("DESCRIPTION")
        templates_mixed = get_text_templates("DeScRiPtIoN")
        
        assert templates_lower == templates_upper == templates_mixed


class TestFillText:
    """Tests for fill_text function."""
    
    def test_fills_all_missing_values(self):
        """Should fill all missing values."""
        series = pd.Series(["Hello.", np.nan, "World.", np.nan, np.nan])
        filled, strategy, sample = fill_text(series)
        
        assert filled.isna().sum() == 0
    
    def test_preserves_original_values(self):
        """Should preserve non-missing values."""
        series = pd.Series(["Original text.", np.nan, "Another text."])
        filled, strategy, sample = fill_text(series)
        
        assert filled.iloc[0] == "Original text."
        assert filled.iloc[2] == "Another text."
    
    def test_strategy_mentions_predefined(self):
        """Should indicate predefined sentences in strategy."""
        series = pd.Series([np.nan])
        filled, strategy, sample = fill_text(series)
        
        assert "predefined" in strategy
    
    def test_no_missing_returns_none_strategy(self):
        """Should return 'none' strategy when no missing values."""
        series = pd.Series(["A", "B", "C"])
        filled, strategy, sample = fill_text(series)
        
        assert strategy == "none"
        assert sample == ""
    
    def test_returns_sample_fill_value(self):
        """Should return a sample of what was filled."""
        series = pd.Series([np.nan, np.nan])
        filled, strategy, sample = fill_text(series)
        
        assert isinstance(sample, str)
        assert len(sample) > 0
    
    def test_uses_product_templates_for_description(self):
        """Should use product templates for description column."""
        series = pd.Series([np.nan])
        filled, strategy, sample = fill_text(series, column_name="product_description")
        
        assert sample in PRODUCT_DESCRIPTIONS
    
    def test_uses_review_templates_for_review(self):
        """Should use review templates for review column."""
        series = pd.Series([np.nan])
        filled, strategy, sample = fill_text(series, column_name="customer_review")
        
        assert sample in REVIEW_TEMPLATES
    
    def test_uses_notes_templates_for_notes(self):
        """Should use notes templates for notes column."""
        series = pd.Series([np.nan])
        filled, strategy, sample = fill_text(series, column_name="user_notes")
        
        assert sample in NOTES_TEMPLATES
    
    def test_filled_values_are_strings(self):
        """All filled values should be strings."""
        series = pd.Series([np.nan, np.nan, np.nan])
        filled, strategy, sample = fill_text(series)
        
        for val in filled:
            assert isinstance(val, str)
    
    def test_single_missing_value(self):
        """Should handle single missing value."""
        series = pd.Series(["Hello.", np.nan, "World."])
        filled, strategy, sample = fill_text(series)
        
        assert filled.isna().sum() == 0
        assert filled.iloc[0] == "Hello."
        assert filled.iloc[2] == "World."


class TestFillTextFromExisting:
    """Tests for fill_text_from_existing function."""
    
    def test_fills_all_missing(self):
        """Should fill all missing values."""
        series = pd.Series(["Existing text.", "Another one.", np.nan, np.nan])
        filled, strategy = fill_text_from_existing(series)
        
        assert filled.isna().sum() == 0
    
    def test_uses_existing_values(self):
        """Filled values should come from existing values."""
        existing = ["Text A", "Text B", "Text C"]
        series = pd.Series(existing + [np.nan, np.nan])
        filled, strategy = fill_text_from_existing(series)
        
        for val in filled[3:]:
            assert val in existing
    
    def test_strategy_name(self):
        """Should return correct strategy name."""
        series = pd.Series(["Something.", np.nan])
        filled, strategy = fill_text_from_existing(series)
        
        assert "random" in strategy or "existing" in strategy
    
    def test_no_missing_returns_none(self):
        """Should return 'none' when no missing values."""
        series = pd.Series(["A", "B", "C"])
        filled, strategy = fill_text_from_existing(series)
        
        assert strategy == "none"
    
    def test_all_missing_falls_back_to_templates(self):
        """Should fall back to templates when all values missing."""
        series = pd.Series([np.nan, np.nan])
        filled, strategy = fill_text_from_existing(series)
        
        assert filled.isna().sum() == 0
        assert "predefined" in strategy or "no existing" in strategy
    
    def test_preserves_non_missing(self):
        """Should preserve original non-missing values."""
        series = pd.Series(["Keep this.", np.nan, "And this."])
        filled, strategy = fill_text_from_existing(series)
        
        assert filled.iloc[0] == "Keep this."
        assert filled.iloc[2] == "And this."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
