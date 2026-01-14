"""Tests for Color.distance() method.

Phase 3.1: Color Distance
Tests the color distance functionality.
"""

from __future__ import annotations

import pytest

from qualpal import Color


class TestColorDistanceBasic:
    """Test basic color distance functionality."""

    def test_distance_returns_float(self):
        """Test that distance() returns a float."""
        red = Color("#ff0000")
        green = Color("#00ff00")

        result = red.distance(green)

        assert isinstance(result, float)

    def test_distance_to_self_is_zero(self):
        """Test that distance to self is 0."""
        color = Color("#ff0000")

        result = color.distance(color)

        assert result == 0.0

    def test_distance_is_symmetric(self):
        """Test that distance(A, B) == distance(B, A)."""
        color1 = Color("#ff0000")
        color2 = Color("#00ff00")

        dist1 = color1.distance(color2)
        dist2 = color2.distance(color1)

        assert dist1 == dist2

    def test_distance_accepts_color_object(self):
        """Test that distance accepts another Color object."""
        red = Color("#ff0000")
        green = Color("#00ff00")

        result = red.distance(green)

        assert result > 0

    def test_distance_accepts_hex_string(self):
        """Test that distance accepts hex color string."""
        red = Color("#ff0000")

        result = red.distance("#00ff00")

        assert result > 0


class TestColorDistanceMetrics:
    """Test different distance metrics."""

    def test_ciede2000_metric(self):
        """Test CIEDE2000 metric (default)."""
        red = Color("#ff0000")
        green = Color("#00ff00")

        result = red.distance(green, metric="ciede2000")

        assert result > 0
        # Known approximate value for red-green distance in CIEDE2000
        assert 80 < result < 90

    def test_din99d_metric(self):
        """Test DIN99d metric."""
        red = Color("#ff0000")
        green = Color("#00ff00")

        result = red.distance(green, metric="din99d")

        assert result > 0
        # DIN99d gives different values than CIEDE2000
        assert 30 < result < 35

    def test_cie76_metric(self):
        """Test CIE76 (Lab Euclidean) metric."""
        red = Color("#ff0000")
        green = Color("#00ff00")

        result = red.distance(green, metric="cie76")

        assert result > 0
        # CIE76 typically gives larger values
        assert 165 < result < 175

    def test_default_metric_is_ciede2000(self):
        """Test that default metric is CIEDE2000."""
        color1 = Color("#ff0000")
        color2 = Color("#00ff00")

        default_dist = color1.distance(color2)
        ciede2000_dist = color1.distance(color2, metric="ciede2000")

        assert default_dist == ciede2000_dist


class TestColorDistanceVariousColors:
    """Test distance with various color pairs."""

    def test_complementary_colors(self):
        """Test distance between complementary colors."""
        red = Color("#ff0000")
        cyan = Color("#00ffff")

        dist = red.distance(cyan)

        assert dist > 50  # Should be large

    def test_similar_colors(self):
        """Test distance between similar colors."""
        red1 = Color("#ff0000")
        red2 = Color("#ff1111")

        dist = red1.distance(red2)

        assert dist < 20  # Should be small

    def test_grayscale_colors(self):
        """Test distance between grayscale colors."""
        black = Color("#000000")
        white = Color("#ffffff")

        dist = black.distance(white)

        assert dist > 50  # Should be large

    def test_identical_colors_different_case(self):
        """Test that hex case doesn't affect distance."""
        color1 = Color("#FF0000")
        color2 = Color("#ff0000")

        dist = color1.distance(color2)

        assert dist == 0.0


class TestColorDistanceErrorHandling:
    """Test error handling in distance()."""

    def test_invalid_metric_raises_error(self):
        """Test that invalid metric raises ValueError."""
        color1 = Color("#ff0000")
        color2 = Color("#00ff00")

        with pytest.raises(ValueError, match="Unknown metric"):
            color1.distance(color2, metric="invalid")

    def test_invalid_hex_string_raises_error(self):
        """Test that invalid hex string raises ValueError."""
        color = Color("#ff0000")

        with pytest.raises(ValueError, match="Invalid hex color"):
            color.distance("not-a-color")

    def test_invalid_type_raises_error(self):
        """Test that invalid type raises error."""
        color = Color("#ff0000")

        with pytest.raises((TypeError, ValueError, AttributeError)):
            color.distance(12345)  # type: ignore[arg-type]


class TestColorDistanceExamples:
    """Test distance with example color combinations."""

    def test_primary_colors(self):
        """Test distance between primary colors."""
        red = Color("#ff0000")
        green = Color("#00ff00")
        blue = Color("#0000ff")

        rg_dist = red.distance(green)
        rb_dist = red.distance(blue)
        gb_dist = green.distance(blue)

        # All should be significantly different from each other
        assert rg_dist > 50
        assert rb_dist > 50
        assert gb_dist > 50

    def test_pastel_colors(self):
        """Test distance between pastel colors."""
        pastel1 = Color("#ffd1dc")  # Pastel pink
        pastel2 = Color("#d1f0ff")  # Pastel blue

        dist = pastel1.distance(pastel2)

        # Pastel colors should have moderate distance
        assert 20 < dist < 60


class TestColorDistancePrecision:
    """Test precision and edge cases."""

    def test_distance_is_nonnegative(self):
        """Test that distance is always non-negative."""
        colors = [
            Color("#ff0000"),
            Color("#00ff00"),
            Color("#0000ff"),
            Color("#ffff00"),
            Color("#ff00ff"),
            Color("#00ffff"),
        ]

        for color1 in colors:
            for color2 in colors:
                dist = color1.distance(color2)
                assert dist >= 0

    def test_triangle_inequality(self):
        """Test that distance satisfies triangle inequality: d(A,C) <= d(A,B) + d(B,C)."""
        red = Color("#ff0000")
        yellow = Color("#ffff00")
        green = Color("#00ff00")

        rg = red.distance(green)
        ry = red.distance(yellow)
        yg = yellow.distance(green)

        # Triangle inequality
        assert rg <= ry + yg + 0.01  # Small epsilon for floating point
