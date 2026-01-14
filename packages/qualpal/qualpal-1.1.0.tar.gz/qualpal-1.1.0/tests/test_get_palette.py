"""Tests for get_palette() function.

Tests the get_palette functionality to retrieve named palettes.
"""

from __future__ import annotations

import pytest

from qualpal import Color, Palette, get_palette, list_palettes


class TestGetPalette:
    """Test get_palette() function."""

    def test_get_palette_returns_palette_object(self):
        """Test that get_palette returns a Palette object."""
        result = get_palette("ColorBrewer:Set2")
        assert isinstance(result, Palette)

    def test_get_palette_contains_colors(self):
        """Test that returned palette contains Color objects."""
        palette = get_palette("ColorBrewer:Set2")
        assert len(palette) > 0
        assert all(isinstance(color, Color) for color in palette)

    def test_get_palette_with_known_palette(self):
        """Test retrieving a known palette returns expected colors."""
        # ColorBrewer Set2 has 8 colors
        palette = get_palette("ColorBrewer:Set2")
        assert len(palette) == 8
        # First color should be #66c2a5
        assert palette[0].hex() == "#66c2a5"

    def test_get_palette_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="must be in format"):
            get_palette("InvalidName")

    def test_get_palette_nonexistent_raises_error(self):
        """Test that non-existent palette raises error."""
        with pytest.raises(ValueError, match="Package 'NonExistent' not found"):
            get_palette("NonExistent:Palette")

    def test_get_palette_pokemon(self):
        """Test retrieving a Pokemon palette."""
        palette = get_palette("Pokemon:Charizard")
        assert len(palette) > 0
        assert all(isinstance(color, Color) for color in palette)

    def test_get_palette_different_packages(self):
        """Test that we can retrieve palettes from different packages."""
        palettes = list_palettes()

        # Test a few palettes from different packages
        if "ColorBrewer" in palettes and len(palettes["ColorBrewer"]) > 0:
            cb_palette = get_palette(f"ColorBrewer:{palettes['ColorBrewer'][0]}")
            assert len(cb_palette) > 0

        if "Pokemon" in palettes and len(palettes["Pokemon"]) > 0:
            pokemon_palette = get_palette(f"Pokemon:{palettes['Pokemon'][0]}")
            assert len(pokemon_palette) > 0


class TestGetPaletteIntegration:
    """Integration tests for get_palette with other features."""

    def test_get_palette_colors_have_valid_hex(self):
        """Test that all colors in palette have valid hex values."""
        palette = get_palette("ColorBrewer:Set2")
        for color in palette:
            hex_val = color.hex()
            assert hex_val.startswith("#")
            assert len(hex_val) == 7  # #RRGGBB format

    def test_get_palette_colors_convertible(self):
        """Test that colors can be converted to other spaces."""
        palette = get_palette("ColorBrewer:Set2")
        first_color = palette[0]

        # Should be able to convert to various color spaces
        rgb = first_color.rgb()
        assert len(rgb) == 3
        assert all(0 <= val <= 1 for val in rgb)

        hsl = first_color.hsl()
        assert len(hsl) == 3

    def test_get_palette_distance_calculation(self):
        """Test that palette distance methods work."""
        palette = get_palette("ColorBrewer:Set2")
        min_dist = palette.min_distance()
        assert min_dist > 0

        matrix = palette.distance_matrix()
        assert len(matrix) == len(palette)
        assert len(matrix[0]) == len(palette)

    def test_get_palette_export_css(self):
        """Test that palette can be exported to CSS."""
        palette = get_palette("ColorBrewer:Set2")
        css = palette.to_css(prefix="set2")
        # to_css returns a list of strings
        assert isinstance(css, list)
        assert any("--set2-1:" in line for line in css)
        assert any("#66c2a5" in line for line in css)

    def test_get_palette_export_json(self):
        """Test that palette can be exported to JSON."""
        palette = get_palette("ColorBrewer:Set2")
        json_str = palette.to_json()
        assert "#66c2a5" in json_str
        assert "[" in json_str
        assert "]" in json_str


class TestGetPaletteConsistency:
    """Test consistency of get_palette output."""

    def test_get_palette_is_deterministic(self):
        """Test that get_palette returns same results."""
        palette1 = get_palette("ColorBrewer:Set2")
        palette2 = get_palette("ColorBrewer:Set2")

        assert len(palette1) == len(palette2)
        for color1, color2 in zip(palette1, palette2):
            assert color1.hex() == color2.hex()

    def test_get_palette_different_from_generate(self):
        """Test that get_palette returns full palette, not subset."""
        from qualpal import Qualpal

        # Get the full palette
        full_palette = get_palette("ColorBrewer:Set2")

        # Generate a subset using Qualpal
        qp = Qualpal(palette="ColorBrewer:Set2")
        subset = qp.generate(3)

        # Full palette should have more colors
        assert len(full_palette) > len(subset)

        # Subset colors should be from the full palette
        subset_hexes = [color.hex() for color in subset]
        full_hexes = [color.hex() for color in full_palette]
        assert all(hex_val in full_hexes for hex_val in subset_hexes)


class TestGetPaletteDocumentation:
    """Test that get_palette follows documented behavior."""

    def test_list_palettes_compatibility(self):
        """Test that listed palettes can be retrieved."""
        palettes = list_palettes()

        # Test first palette from each package
        for package, palette_list in palettes.items():
            if len(palette_list) > 0:
                palette_name = f"{package}:{palette_list[0]}"
                palette = get_palette(palette_name)
                assert len(palette) > 0
                break  # Test at least one

    def test_get_palette_name_format_validation(self):
        """Test that name format is validated correctly."""
        # Valid format should work
        palette = get_palette("ColorBrewer:Set2")
        assert len(palette) > 0

        # Invalid formats should raise ValueError
        invalid_names = [
            "NoColon",
            "TooMany:Colons:Here",
            ":NoPackage",
            "NoPalette:",
        ]

        for name in invalid_names:
            if ":" not in name:
                with pytest.raises(ValueError, match="must be in format"):
                    get_palette(name)
