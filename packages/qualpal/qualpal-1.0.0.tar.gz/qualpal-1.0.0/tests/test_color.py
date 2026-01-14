"""Tests for Color class."""

from __future__ import annotations

import pytest

from qualpal import Color


class TestColorConstruction:
    """Test Color object construction."""

    def test_from_hex(self):
        """Test creating Color from hex string."""
        color = Color("#ff0000")
        assert color.hex() == "#ff0000"

    def test_from_hex_lowercase(self):
        """Test hex string normalization."""
        color = Color("#FF0000")
        # Should normalize to lowercase
        assert color.hex().lower() == "#ff0000"

    def test_invalid_hex_raises(self):
        """Test that invalid hex strings raise errors."""
        with pytest.raises((ValueError, RuntimeError)):
            Color("invalid")

    def test_invalid_hex_format_raises(self):
        """Test that wrong format raises errors."""
        with pytest.raises((ValueError, RuntimeError)):
            Color("#gggggg")


class TestColorConversions:
    """Test Color conversion methods."""

    def test_hex(self):
        """Test hex() method."""
        color = Color("#ff0000")
        assert isinstance(color.hex(), str)
        assert color.hex().startswith("#")
        assert len(color.hex()) == 7

    def test_rgb(self):
        """Test rgb() method returns tuple."""
        color = Color("#ff0000")
        rgb = color.rgb()
        assert isinstance(rgb, tuple)
        assert len(rgb) == 3
        # Red channel should be 1.0 or close to it
        assert rgb[0] == pytest.approx(1.0, abs=0.01)
        assert rgb[1] == pytest.approx(0.0, abs=0.01)
        assert rgb[2] == pytest.approx(0.0, abs=0.01)

    def test_rgb255(self):
        """Test rgb255() method returns 0-255 integers."""
        color = Color("#ff0000")
        rgb255 = color.rgb255()
        assert isinstance(rgb255, tuple)
        assert len(rgb255) == 3
        assert rgb255[0] == 255
        assert rgb255[1] == 0
        assert rgb255[2] == 0


class TestColorRepresentation:
    """Test Color string representations."""

    def test_str(self):
        """Test str() returns hex."""
        color = Color("#ff0000")
        assert str(color) == "#ff0000" or str(color).lower() == "#ff0000"

    def test_repr(self):
        """Test repr() format."""
        color = Color("#ff0000")
        repr_str = repr(color)
        assert "Color" in repr_str
        assert "#" in repr_str


class TestColorEquality:
    """Test Color equality operations."""

    def test_equality_same_color(self):
        """Test two Colors with same hex are equal."""
        color1 = Color("#ff0000")
        color2 = Color("#ff0000")
        assert color1 == color2

    def test_equality_different_colors(self):
        """Test two Colors with different hex are not equal."""
        color1 = Color("#ff0000")
        color2 = Color("#00ff00")
        assert color1 != color2

    def test_equality_with_hex_string(self):
        """Test Color can compare with hex string."""
        color = Color("#ff0000")
        assert color == "#ff0000"

    def test_inequality_with_hex_string(self):
        """Test Color inequality with hex string."""
        color = Color("#ff0000")
        assert color != "#00ff00"


class TestColorRoundtrip:
    """Test round-trip conversions."""

    def test_common_colors(self):
        """Test common web colors."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffffff", "#000000"]
        for hex_color in colors:
            color = Color(hex_color)
            # Should round-trip back to same hex (case-insensitive)
            assert color.hex().lower() == hex_color.lower()


class TestColorSpaceConversions:
    """Test color space conversion methods."""

    def test_hsl_red(self):
        """Test HSL conversion for red."""
        color = Color("#ff0000")
        h, s, l = color.hsl()
        # Red: h=0, s=1, l=0.5
        assert h == pytest.approx(0.0, abs=1e-3)
        assert s == pytest.approx(1.0, abs=1e-3)
        assert l == pytest.approx(0.5, abs=1e-3)

    def test_hsl_green(self):
        """Test HSL conversion for green."""
        color = Color("#00ff00")
        h, s, l = color.hsl()
        # Green: h=120, s=1, l=0.5
        assert h == pytest.approx(120.0, abs=1e-3)
        assert s == pytest.approx(1.0, abs=1e-3)
        assert l == pytest.approx(0.5, abs=1e-3)

    def test_hsl_blue(self):
        """Test HSL conversion for blue."""
        color = Color("#0000ff")
        h, s, l = color.hsl()
        # Blue: h=240, s=1, l=0.5
        assert h == pytest.approx(240.0, abs=1e-3)
        assert s == pytest.approx(1.0, abs=1e-3)
        assert l == pytest.approx(0.5, abs=1e-3)

    def test_hsl_gray(self):
        """Test HSL conversion for gray."""
        color = Color("#808080")
        h, s, l = color.hsl()
        assert h == pytest.approx(0.0, abs=1e-3)
        assert s == pytest.approx(0.0, abs=1e-3)
        assert l == pytest.approx(0.5, abs=0.02)

    def test_from_hsl(self):
        """Test creating Color from HSL."""
        # Create red from HSL
        color = Color.from_hsl(0, 1.0, 0.5)
        r, g, b = color.rgb()
        assert r == pytest.approx(1.0, abs=1e-3)
        assert g == pytest.approx(0.0, abs=1e-3)
        assert b == pytest.approx(0.0, abs=1e-3)

    def test_hsl_roundtrip(self):
        """Test HSL round-trip conversion."""
        original = Color("#ff6347")  # Tomato
        h, s, l = original.hsl()
        roundtrip = Color.from_hsl(h, s, l)
        # Should be very close
        r1, g1, b1 = original.rgb()
        r2, g2, b2 = roundtrip.rgb()
        assert r1 == pytest.approx(r2, abs=0.01)
        assert g1 == pytest.approx(g2, abs=0.01)
        assert b1 == pytest.approx(b2, abs=0.01)

    def test_xyz_conversion(self):
        """Test XYZ conversion."""
        color = Color("#ff0000")
        x, y, z = color.xyz()
        # Values should be reasonable
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)
        assert 0.0 <= x <= 1.0
        assert 0.0 <= y <= 1.0
        assert 0.0 <= z <= 1.0

    def test_lab_conversion(self):
        """Test Lab conversion."""
        color = Color("#ff0000")
        l, a, b = color.lab()
        # L should be in [0, 100]
        assert 0.0 <= l <= 100.0
        # a, b in [-128, 127]
        assert -128.0 <= a <= 127.0
        assert -128.0 <= b <= 127.0
        # Red should have positive a (red axis)
        assert a > 0

    def test_lch_conversion(self):
        """Test LCH conversion."""
        color = Color("#ff0000")
        l, c, h = color.lch()
        # L should be in [0, 100]
        assert 0.0 <= l <= 100.0
        # C (chroma) should be non-negative
        assert c >= 0.0
        # H (hue) should be in [0, 360)
        assert 0.0 <= h < 360.0
