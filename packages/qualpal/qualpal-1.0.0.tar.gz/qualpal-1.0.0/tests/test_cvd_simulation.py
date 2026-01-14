"""Tests for Color.simulate_cvd() method.

Phase 4.1: CVD Simulation
Tests the color vision deficiency simulation functionality.
"""

from __future__ import annotations

import pytest

from qualpal import Color


class TestCVDSimulationBasic:
    """Test basic CVD simulation functionality."""

    def test_simulate_cvd_returns_color(self):
        """Test that simulate_cvd returns a Color object."""
        color = Color("#ff0000")

        result = color.simulate_cvd("protan")

        assert isinstance(result, Color)

    def test_simulate_cvd_severity_zero_unchanged(self):
        """Test that severity=0 returns unchanged color."""
        color = Color("#ff0000")

        result = color.simulate_cvd("protan", severity=0.0)

        # Should be very close to original
        assert result.hex() == color.hex()

    def test_simulate_cvd_returns_new_color(self):
        """Test that simulate_cvd returns a new Color object (immutability)."""
        color = Color("#ff0000")

        result = color.simulate_cvd("protan", severity=1.0)

        # Original should be unchanged
        assert color.hex() == "#ff0000"
        # Result should be different
        assert result.hex() != "#ff0000"

    def test_simulate_cvd_different_severities(self):
        """Test that different severities produce different results."""
        color = Color("#ff0000")

        mild = color.simulate_cvd("protan", severity=0.3)
        moderate = color.simulate_cvd("protan", severity=0.6)
        severe = color.simulate_cvd("protan", severity=1.0)

        # All should be different
        assert mild.hex() != moderate.hex()
        assert moderate.hex() != severe.hex()
        assert mild.hex() != severe.hex()


class TestCVDTypes:
    """Test different CVD types."""

    def test_protan_simulation(self):
        """Test protanomaly/protanopia simulation."""
        red = Color("#ff0000")

        result = red.simulate_cvd("protan", severity=1.0)

        assert isinstance(result, Color)
        # Red should look darker/different to protan
        assert result.hex() != red.hex()

    def test_deutan_simulation(self):
        """Test deuteranomaly/deuteranopia simulation."""
        green = Color("#00ff00")

        result = green.simulate_cvd("deutan", severity=1.0)

        assert isinstance(result, Color)
        # Green should look different to deutan
        assert result.hex() != green.hex()

    def test_tritan_simulation(self):
        """Test tritanomaly/tritanopia simulation."""
        blue = Color("#0000ff")

        result = blue.simulate_cvd("tritan", severity=1.0)

        assert isinstance(result, Color)
        # Blue should look different to tritan
        assert result.hex() != blue.hex()

    def test_all_cvd_types_work(self):
        """Test that all three CVD types work."""
        color = Color("#ff8800")  # Orange

        protan = color.simulate_cvd("protan")
        deutan = color.simulate_cvd("deutan")
        tritan = color.simulate_cvd("tritan")

        # All should produce valid colors
        assert isinstance(protan, Color)
        assert isinstance(deutan, Color)
        assert isinstance(tritan, Color)

        # All should be different from each other
        assert protan.hex() != deutan.hex()
        assert deutan.hex() != tritan.hex()
        assert protan.hex() != tritan.hex()


class TestCVDSeverityLevels:
    """Test different severity levels."""

    @pytest.mark.parametrize("severity", [0.0, 0.25, 0.5, 0.75, 1.0])
    def test_various_severities(self, severity):
        """Test simulation with various severity levels."""
        color = Color("#ff0000")

        result = color.simulate_cvd("protan", severity=severity)

        assert isinstance(result, Color)

    def test_mild_severity(self):
        """Test mild CVD (severity=0.25)."""
        color = Color("#ff0000")

        result = color.simulate_cvd("protan", severity=0.25)

        # Should be close to original but not identical
        assert result.hex() != color.hex()

    def test_moderate_severity(self):
        """Test moderate CVD (severity=0.5)."""
        color = Color("#ff0000")

        result = color.simulate_cvd("deutan", severity=0.5)

        assert isinstance(result, Color)

    def test_complete_severity(self):
        """Test complete CVD (severity=1.0)."""
        color = Color("#ff0000")

        result = color.simulate_cvd("tritan", severity=1.0)

        assert isinstance(result, Color)


class TestCVDParameterValidation:
    """Test parameter validation."""

    def test_invalid_cvd_type_raises_error(self):
        """Test that invalid CVD type raises ValueError."""
        color = Color("#ff0000")

        with pytest.raises(ValueError, match="cvd_type must be one of"):
            color.simulate_cvd("invalid_type")

    def test_severity_too_low_raises_error(self):
        """Test that severity < 0 raises ValueError."""
        color = Color("#ff0000")

        with pytest.raises(ValueError, match="severity must be in range"):
            color.simulate_cvd("protan", severity=-0.1)

    def test_severity_too_high_raises_error(self):
        """Test that severity > 1 raises ValueError."""
        color = Color("#ff0000")

        with pytest.raises(ValueError, match="severity must be in range"):
            color.simulate_cvd("protan", severity=1.5)

    def test_severity_not_number_raises_error(self):
        """Test that non-numeric severity raises TypeError."""
        color = Color("#ff0000")

        with pytest.raises(TypeError, match="severity must be a number"):
            color.simulate_cvd("protan", severity="high")  # type: ignore[arg-type]


class TestCVDWithDifferentColors:
    """Test CVD simulation with various colors."""

    def test_cvd_on_primary_colors(self):
        """Test CVD simulation on primary colors."""
        colors = [
            Color("#ff0000"),  # Red
            Color("#00ff00"),  # Green
            Color("#0000ff"),  # Blue
        ]

        for color in colors:
            result = color.simulate_cvd("protan", severity=1.0)
            assert isinstance(result, Color)

    def test_cvd_on_grayscale(self):
        """Test CVD simulation on grayscale colors."""
        colors = [
            Color("#000000"),  # Black
            Color("#808080"),  # Gray
            Color("#ffffff"),  # White
        ]

        for color in colors:
            result = color.simulate_cvd("deutan", severity=1.0)
            assert isinstance(result, Color)
            # Grayscale should remain relatively unchanged
            # (CVD mainly affects color perception, not brightness)

    def test_cvd_on_pastel_colors(self):
        """Test CVD simulation on pastel colors."""
        pastel = Color("#ffd1dc")  # Pastel pink

        result = pastel.simulate_cvd("tritan", severity=0.7)

        assert isinstance(result, Color)


class TestCVDDefaultParameters:
    """Test default parameter values."""

    def test_default_severity_is_one(self):
        """Test that default severity is 1.0."""
        color = Color("#ff0000")

        default = color.simulate_cvd("protan")
        explicit = color.simulate_cvd("protan", severity=1.0)

        assert default.hex() == explicit.hex()


class TestCVDIntegration:
    """Integration tests for CVD simulation."""

    def test_cvd_then_distance(self):
        """Test using CVD simulation with distance calculation."""
        original = Color("#ff0000")
        simulated = original.simulate_cvd("protan", severity=1.0)

        distance = original.distance(simulated)

        # Distance should be positive
        assert distance > 0

    def test_cvd_workflow(self):
        """Test complete CVD workflow."""
        # Create color
        color = Color("#ff8844")

        # Simulate for different types
        protan = color.simulate_cvd("protan", severity=0.8)
        deutan = color.simulate_cvd("deutan", severity=0.8)

        # Compare distances
        dist_protan = color.distance(protan)
        dist_deutan = color.distance(deutan)

        assert dist_protan > 0
        assert dist_deutan > 0

    def test_chain_simulations(self):
        """Test that CVD simulations can be chained."""
        color = Color("#ff0000")

        # Simulate protan then deutan
        result = color.simulate_cvd("protan", 0.5).simulate_cvd("deutan", 0.5)

        assert isinstance(result, Color)
        assert result.hex() != color.hex()
