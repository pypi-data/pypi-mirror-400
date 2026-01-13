"""
Unit Tests: Atlas 14 Multi-Duration Support

Tests multi-duration support (6h, 12h, 24h, 96h) for Atlas14Storm module.

Test Categories:
1. Duration validation (supported vs unsupported)
2. Depth conservation for all durations
3. 48-hour gap handling
4. Regional availability

Usage:
    pytest tests/test_atlas14_multiduration.py -v
"""

import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

# Add parent directory to path for development
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from hms_commander import Atlas14Storm


class TestSupportedDurations:
    """Test that supported durations constant is correct."""

    def test_supported_durations_constant(self):
        """Verify SUPPORTED_DURATIONS constant exists and has correct values."""
        assert hasattr(Atlas14Storm, 'SUPPORTED_DURATIONS')
        assert Atlas14Storm.SUPPORTED_DURATIONS == [6, 12, 24, 96]

    def test_48_hour_not_supported(self):
        """Verify 48-hour is not in supported durations."""
        assert 48 not in Atlas14Storm.SUPPORTED_DURATIONS


class TestMultiDurationGeneration:
    """Test hyetograph generation for all supported durations."""

    @pytest.mark.parametrize("duration", [6, 12, 24, 96])
    def test_multiduration_depth_conservation(self, duration):
        """Test that all supported durations conserve depth exactly."""
        total_depth = 10.0

        hyeto = Atlas14Storm.generate_hyetograph(
            total_depth_inches=total_depth,
            state="tx",
            region=3,
            duration_hours=duration,
            aep_percent=1.0,
            quartile="All Cases"
        )

        # Verify depth conservation (< 10^-6 inches)
        error = abs(hyeto['cumulative_depth'].iloc[-1] - total_depth)
        assert error < 1e-6, f"Depth conservation failed for {duration}h: error={error}"

    @pytest.mark.parametrize("duration,expected_steps", [
        (6, 13),   # 0-6h at 0.5h increments
        (12, 25),  # 0-12h at 0.5h increments
        (24, 49),  # 0-24h at 0.5h increments
        (96, 97),  # 0-96h at 1h increments (NOAA uses coarser for longer durations)
    ])
    def test_multiduration_step_count(self, duration, expected_steps):
        """Test that step count matches NOAA published time resolution."""
        hyeto = Atlas14Storm.generate_hyetograph(
            total_depth_inches=10.0,
            state="tx",
            region=3,
            duration_hours=duration,
            aep_percent=1.0
        )

        # NOAA uses different time resolutions:
        # - 6h, 12h, 24h: 0.5h increments
        # - 96h: 1h increments (coarser for longer durations)
        assert len(hyeto) == expected_steps, \
            f"Expected {expected_steps} steps for {duration}h, got {len(hyeto)}"

    @pytest.mark.parametrize("duration", [6, 12, 24, 96])
    def test_multiduration_non_negative(self, duration):
        """Test that all incremental values are non-negative."""
        hyeto = Atlas14Storm.generate_hyetograph(
            total_depth_inches=10.0,
            state="tx",
            region=3,
            duration_hours=duration,
            aep_percent=1.0
        )

        assert np.all(hyeto['incremental_depth'] >= 0), f"Negative values found in {duration}h hyetograph"


class Test48HourGap:
    """Test 48-hour duration handling."""

    def test_48hour_raises_valueerror(self):
        """Test that 48-hour duration raises ValueError with helpful message."""
        with pytest.raises(ValueError, match="48-hour duration is not available"):
            Atlas14Storm.generate_hyetograph(
                total_depth_inches=10.0,
                state="tx",
                region=3,
                duration_hours=48,
                aep_percent=1.0
            )

    def test_48hour_error_mentions_frequencystorm(self):
        """Test that 48-hour error message mentions FrequencyStorm as alternative."""
        try:
            Atlas14Storm.generate_hyetograph(
                total_depth_inches=10.0,
                state="tx",
                region=3,
                duration_hours=48,
                aep_percent=1.0
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            error_msg = str(e)
            assert "FrequencyStorm" in error_msg, \
                "Error message should mention FrequencyStorm as alternative"
            assert "2880" in error_msg, \
                "Error message should mention 2880 (48 hours in minutes)"


class TestUnsupportedDurations:
    """Test handling of unsupported durations."""

    @pytest.mark.parametrize("duration", [1, 3, 18, 36, 72, 120])
    def test_unsupported_duration_raises_valueerror(self, duration):
        """Test that unsupported durations raise ValueError."""
        with pytest.raises(ValueError):
            Atlas14Storm.generate_hyetograph(
                total_depth_inches=10.0,
                state="tx",
                region=3,
                duration_hours=duration,
                aep_percent=1.0
            )


class TestDepthConservation:
    """Test depth conservation with various input values."""

    @pytest.mark.parametrize("depth", [1.0, 5.0, 10.0, 17.9, 25.0, 50.0])
    def test_depth_conservation_various_values(self, depth):
        """Test depth conservation with various input depths."""
        hyeto = Atlas14Storm.generate_hyetograph(
            total_depth_inches=depth,
            state="tx",
            region=3,
            duration_hours=24,
            aep_percent=1.0
        )

        error = abs(hyeto['cumulative_depth'].iloc[-1] - depth)
        assert error < 1e-6, f"Depth conservation failed for {depth}: error={error}"


class TestCaching:
    """Test that caching works correctly for different durations."""

    def test_cache_key_includes_duration(self):
        """Test that cache keys are unique per duration."""
        # Generate for two different durations
        hyeto_6h = Atlas14Storm.generate_hyetograph(
            total_depth_inches=10.0,
            state="tx",
            region=3,
            duration_hours=6,
            aep_percent=1.0
        )

        hyeto_24h = Atlas14Storm.generate_hyetograph(
            total_depth_inches=10.0,
            state="tx",
            region=3,
            duration_hours=24,
            aep_percent=1.0
        )

        # Should have different lengths (different durations)
        assert len(hyeto_6h) != len(hyeto_24h), \
            "Different durations should produce different step counts"

        # Check cache has both entries
        cache = Atlas14Storm._temporal_cache
        assert "tx_3_6h" in cache, "6h cache entry missing"
        assert "tx_3_24h" in cache, "24h cache entry missing"


class TestDurationValidation:
    """Test the internal duration validation method."""

    def test_validate_duration_passes_for_supported(self):
        """Test that validation passes for supported durations."""
        for duration in Atlas14Storm.SUPPORTED_DURATIONS:
            # Should not raise
            Atlas14Storm._validate_duration(duration)

    def test_validate_duration_fails_for_48(self):
        """Test that validation fails for 48-hour with specific message."""
        with pytest.raises(ValueError, match="48-hour duration is not available"):
            Atlas14Storm._validate_duration(48)

    def test_validate_duration_fails_for_unsupported(self):
        """Test that validation fails for other unsupported durations."""
        for duration in [1, 3, 18, 36, 72, 120]:
            with pytest.raises(ValueError, match="is not supported"):
                Atlas14Storm._validate_duration(duration)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
