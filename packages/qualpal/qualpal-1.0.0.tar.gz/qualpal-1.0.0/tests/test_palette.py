"""Tests for Palette class."""

from __future__ import annotations

import unittest

import pytest

from qualpal import Color, Palette


class TestPaletteCreation(unittest.TestCase):
    """Tests for Palette creation."""

    def test_from_colors(self):
        """Test creating Palette from Color objects."""
        colors = [Color("#ff0000"), Color("#00ff00"), Color("#0000ff")]
        palette = Palette(colors)

        assert len(palette) == 3
        assert palette[0] == Color("#ff0000")

    def test_from_hex_strings(self):
        """Test creating Palette from hex strings."""
        palette = Palette(["#ff0000", "#00ff00", "#0000ff"])

        assert len(palette) == 3
        assert palette[0] == "#ff0000"

    def test_from_mixed(self):
        """Test creating Palette from mixed Color and hex."""
        palette = Palette([Color("#ff0000"), "#00ff00", Color("#0000ff")])

        assert len(palette) == 3
        assert palette[1] == "#00ff00"

    def test_empty_palette(self):
        """Test creating empty Palette."""
        palette = Palette([])

        assert len(palette) == 0

    def test_invalid_color(self):
        """Test that invalid colors raise ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            Palette(["#ff0000", "invalid", "#0000ff"])

    def test_invalid_type(self):
        """Test that invalid types raise TypeError."""
        with pytest.raises(TypeError):
            Palette([123, 456, 789])  # type: ignore[list-item]


class TestPaletteIndexing(unittest.TestCase):
    """Tests for Palette indexing and slicing."""

    def setUp(self):
        """Create a test palette."""
        self.palette = Palette(["#ff0000", "#00ff00", "#0000ff", "#ffff00"])

    def test_len(self):
        """Test __len__."""
        assert len(self.palette) == 4

    def test_getitem_positive_index(self):
        """Test getting by positive index."""
        color = self.palette[0]

        assert isinstance(color, Color)
        assert color == "#ff0000"

    def test_getitem_negative_index(self):
        """Test getting by negative index."""
        color = self.palette[-1]

        assert color == "#ffff00"

    def test_getitem_out_of_range(self):
        """Test that out of range index raises IndexError."""
        with pytest.raises(IndexError):
            _ = self.palette[10]

    def test_slice_returns_palette(self):
        """Test that slicing returns a new Palette."""
        sub = self.palette[0:2]

        assert isinstance(sub, Palette)
        assert len(sub) == 2

    def test_slice_content(self):
        """Test slice contains correct colors."""
        sub = self.palette[1:3]

        assert sub[0] == "#00ff00"
        assert sub[1] == "#0000ff"

    def test_slice_step(self):
        """Test slicing with step."""
        sub = self.palette[::2]

        assert len(sub) == 2
        assert sub[0] == "#ff0000"
        assert sub[1] == "#0000ff"

    def test_slice_negative(self):
        """Test negative slicing."""
        sub = self.palette[-2:]

        assert len(sub) == 2
        assert sub[0] == "#0000ff"


class TestPaletteIteration(unittest.TestCase):
    """Tests for Palette iteration."""

    def test_iter(self):
        """Test iterating over palette."""
        palette = Palette(["#ff0000", "#00ff00", "#0000ff"])
        colors = list(palette)

        assert len(colors) == 3
        assert isinstance(colors[0], Color)

    def test_for_loop(self):
        """Test using palette in for loop."""
        palette = Palette(["#ff0000", "#00ff00", "#0000ff"])
        hex_values = [c.hex() for c in palette]

        assert hex_values == ["#ff0000", "#00ff00", "#0000ff"]


class TestPaletteContains(unittest.TestCase):
    """Tests for Palette membership testing."""

    def setUp(self):
        """Create a test palette."""
        self.palette = Palette(["#ff0000", "#00ff00", "#0000ff"])

    def test_contains_color(self):
        """Test contains with Color object."""
        assert Color("#ff0000") in self.palette
        assert Color("#ffffff") not in self.palette

    def test_contains_hex_string(self):
        """Test contains with hex string."""
        assert "#ff0000" in self.palette
        assert "#ffffff" not in self.palette

    def test_contains_case_insensitive(self):
        """Test contains is case-insensitive."""
        assert "#FF0000" in self.palette
        assert "#Ff0000" in self.palette

    def test_contains_invalid_string(self):
        """Test contains with invalid hex string."""
        assert "invalid" not in self.palette

    def test_contains_other_type(self):
        """Test contains with other types."""
        assert 123 not in self.palette
        assert None not in self.palette


class TestPaletteConversions(unittest.TestCase):
    """Tests for Palette conversion methods."""

    def setUp(self):
        """Create a test palette."""
        self.palette = Palette(["#ff0000", "#00ff00", "#0000ff"])

    def test_hex(self):
        """Test hex() method."""
        hex_list = self.palette.hex()

        assert hex_list == ["#ff0000", "#00ff00", "#0000ff"]
        assert isinstance(hex_list, list)

    def test_rgb(self):
        """Test rgb() method."""
        rgb_list = self.palette.rgb()

        assert len(rgb_list) == 3
        assert isinstance(rgb_list, list)
        assert isinstance(rgb_list[0], tuple)
        assert rgb_list[0] == (1.0, 0.0, 0.0)
        assert rgb_list[1] == (0.0, 1.0, 0.0)
        assert rgb_list[2] == (0.0, 0.0, 1.0)


class TestPaletteRepresentation(unittest.TestCase):
    """Tests for Palette string representation."""

    def test_str(self):
        """Test __str__."""
        palette = Palette(["#ff0000", "#00ff00", "#0000ff"])
        s = str(palette)

        assert "Palette" in s
        assert "#ff0000" in s
        assert "#00ff00" in s
        assert "#0000ff" in s

    def test_repr(self):
        """Test __repr__."""
        palette = Palette(["#ff0000", "#00ff00"])
        r = repr(palette)

        assert r == "Palette(['#ff0000', '#00ff00'])"

    def test_empty_repr(self):
        """Test __repr__ of empty palette."""
        palette = Palette([])

        assert repr(palette) == "Palette([])"


class TestPaletteEquality(unittest.TestCase):
    """Tests for Palette equality."""

    def test_equal_palettes(self):
        """Test equality of identical palettes."""
        p1 = Palette(["#ff0000", "#00ff00", "#0000ff"])
        p2 = Palette(["#ff0000", "#00ff00", "#0000ff"])

        assert p1 == p2

    def test_equal_mixed_construction(self):
        """Test equality with different construction methods."""
        p1 = Palette([Color("#ff0000"), Color("#00ff00")])
        p2 = Palette(["#ff0000", "#00ff00"])

        assert p1 == p2

    def test_not_equal_different_colors(self):
        """Test inequality with different colors."""
        p1 = Palette(["#ff0000", "#00ff00"])
        p2 = Palette(["#ff0000", "#0000ff"])

        assert p1 != p2

    def test_not_equal_different_length(self):
        """Test inequality with different lengths."""
        p1 = Palette(["#ff0000", "#00ff00"])
        p2 = Palette(["#ff0000"])

        assert p1 != p2

    def test_not_equal_different_order(self):
        """Test inequality with different order."""
        p1 = Palette(["#ff0000", "#00ff00"])
        p2 = Palette(["#00ff00", "#ff0000"])

        assert p1 != p2

    def test_not_equal_other_type(self):
        """Test inequality with non-Palette type."""
        palette = Palette(["#ff0000"])

        assert palette != "#ff0000"
        assert palette != ["#ff0000"]


if __name__ == "__main__":
    unittest.main()
