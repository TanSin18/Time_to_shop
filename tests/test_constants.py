"""Tests for constants module."""

from time_to_shop.core.constants import (
    FEATURE_COLUMNS,
    DECILE_BINS,
    DECILE_LABELS,
    FILL_VALUE_DECILE,
    FILL_VALUE_RECENCY,
)


class TestConstants:
    """Test cases for constants."""

    def test_feature_columns_length(self):
        """Test that we have the expected number of features."""
        assert len(FEATURE_COLUMNS) == 14

    def test_decile_bins_and_labels(self):
        """Test decile bins and labels are consistent."""
        # Should have 11 bins (for 10 deciles)
        assert len(DECILE_BINS) == 11
        # Should have 10 labels
        assert len(DECILE_LABELS) == 10
        # Bins should be in ascending order
        assert DECILE_BINS == sorted(DECILE_BINS)
        # First bin should be 0, last should be 1
        assert DECILE_BINS[0] == 0.0
        assert DECILE_BINS[-1] == 1.0

    def test_fill_values(self):
        """Test fill values are as expected."""
        assert FILL_VALUE_DECILE == 11
        assert FILL_VALUE_RECENCY == 366
