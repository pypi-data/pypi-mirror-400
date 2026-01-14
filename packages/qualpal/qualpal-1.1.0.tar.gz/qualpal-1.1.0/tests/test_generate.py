"""Tests for Qualpal.generate() method.

Phase 2.3: Integration
Tests the integration of Python Qualpal class with C++ algorithm.
"""

from __future__ import annotations

import pytest

from qualpal import Color, Palette, Qualpal


class TestGenerateBasic:
    """Test basic generate() functionality."""

    def test_generate_returns_palette(self):
        """Test that generate() returns a Palette object."""
        qp = Qualpal()
        result = qp.generate(3)

        assert isinstance(result, Palette)

    def test_generate_correct_count(self):
        """Test that generate() returns correct number of colors."""
        qp = Qualpal()
        n = 5
        result = qp.generate(n)

        assert len(result) == n

    def test_generate_returns_color_objects(self):
        """Test that generate() returns Palette with Color objects."""
        qp = Qualpal()
        result = qp.generate(3)

        for color in result:
            assert isinstance(color, Color)

    def test_generate_distinct_colors(self):
        """Test that generated colors are distinct."""
        qp = Qualpal()
        result = qp.generate(5)

        # Convert to hex for comparison
        hex_colors = [c.hex() for c in result]
        assert len(hex_colors) == len(set(hex_colors))


class TestGenerateDifferentSizes:
    """Test generate() with different palette sizes."""

    @pytest.mark.parametrize("n", [1, 2, 5, 10, 20])
    def test_generate_various_sizes(self, n):
        """Test generating palettes of various sizes."""
        qp = Qualpal()
        result = qp.generate(n)

        assert isinstance(result, Palette)
        assert len(result) == n

    def test_generate_single_color(self):
        """Test generating a palette with just one color."""
        qp = Qualpal()
        result = qp.generate(1)

        assert len(result) == 1
        assert isinstance(result[0], Color)

    def test_generate_large_palette(self):
        """Test generating a larger palette."""
        qp = Qualpal()
        result = qp.generate(50)

        assert len(result) == 50


class TestGenerateWithColorspace:
    """Test generate() with custom colorspace."""

    def test_generate_with_restricted_hue(self):
        """Test generation with restricted hue range."""
        qp = Qualpal(colorspace={"h": (0, 120), "s": (0, 1), "l": (0, 1)})
        result = qp.generate(5)

        assert len(result) == 5
        assert isinstance(result, Palette)

    def test_generate_with_restricted_saturation(self):
        """Test generation with restricted saturation range."""
        qp = Qualpal(colorspace={"h": (0, 360), "s": (0.5, 1), "l": (0, 1)})
        result = qp.generate(5)

        assert len(result) == 5

    def test_generate_with_restricted_lightness(self):
        """Test generation with restricted lightness range."""
        qp = Qualpal(colorspace={"h": (0, 360), "s": (0, 1), "l": (0.3, 0.7)})
        result = qp.generate(5)

        assert len(result) == 5

    def test_generate_with_narrow_colorspace(self):
        """Test generation with very narrow colorspace."""
        qp = Qualpal(colorspace={"h": (0, 60), "s": (0.4, 0.6), "l": (0.4, 0.6)})
        result = qp.generate(3)

        assert len(result) == 3

    def test_generate_with_lchab_colorspace(self):
        """Test generation with LCHab colorspace."""
        qp = Qualpal(
            colorspace={"h": (0, 360), "c": (0, 1), "l": (0, 1)}, space="lchab"
        )
        result = qp.generate(5)

        assert len(result) == 5
        assert isinstance(result, Palette)


class TestGenerateWithColors:
    """Test generate() with colors input mode."""

    def test_generate_from_colors_list(self):
        """Test generating palette from list of colors."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
        qp = Qualpal(colors=colors)
        result = qp.generate(2)

        assert isinstance(result, Palette)
        assert len(result) == 2

    def test_generate_selects_from_colors(self):
        """Test that generate selects colors from the input list."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff"]
        qp = Qualpal(colors=colors)
        result = qp.generate(3)

        # All generated colors should be from the input list
        result_hex = [c.hex() for c in result]
        for hex_color in result_hex:
            assert hex_color in colors

    def test_generate_all_colors_from_list(self):
        """Test generating all colors from the list."""
        colors = ["#ff0000", "#00ff00", "#0000ff"]
        qp = Qualpal(colors=colors)
        result = qp.generate(3)

        assert len(result) == 3

    def test_generate_fewer_than_available_colors(self):
        """Test generating fewer colors than provided."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
        qp = Qualpal(colors=colors)
        result = qp.generate(3)

        assert len(result) == 3
        # Should select the most distinct subset
        assert isinstance(result, Palette)

    def test_generate_single_from_many_colors(self):
        """Test selecting single color from many."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
        qp = Qualpal(colors=colors)
        result = qp.generate(1)

        assert len(result) == 1
        assert result[0].hex() in colors


class TestGenerateWithPalette:
    """Test generate() with named palette input mode."""

    def test_generate_from_colorbrewer_palette(self):
        """Test generating from ColorBrewer palette."""
        qp = Qualpal(palette="ColorBrewer:Set2")
        result = qp.generate(4)

        assert isinstance(result, Palette)
        assert len(result) == 4

    def test_generate_from_pokemon_palette(self):
        """Test generating from Pokemon palette."""
        qp = Qualpal(palette="Pokemon:Porygon")
        result = qp.generate(3)

        assert isinstance(result, Palette)
        assert len(result) == 3

    def test_generate_fewer_from_palette(self):
        """Test selecting fewer colors from palette."""
        qp = Qualpal(palette="ColorBrewer:Set2")
        result = qp.generate(2)

        assert len(result) == 2

    def test_generate_palette_with_configuration(self):
        """Test palette mode with additional configuration."""
        qp = Qualpal(palette="ColorBrewer:Set2")
        qp.cvd = {"protan": 0.5}
        qp.background = "#ffffff"

        result = qp.generate(4)
        assert len(result) == 4


class TestGenerateParameterValidation:
    """Test parameter validation in generate()."""

    def test_generate_n_not_int(self):
        """Test that non-integer n raises TypeError."""
        qp = Qualpal()

        with pytest.raises(TypeError, match="n must be an integer"):
            qp.generate(5.5)  # type: ignore[arg-type]

    def test_generate_n_zero(self):
        """Test that zero n raises ValueError."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="n must be positive"):
            qp.generate(0)

    def test_generate_n_negative(self):
        """Test that negative n raises ValueError."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="n must be positive"):
            qp.generate(-5)

    def test_generate_n_string(self):
        """Test that string n raises TypeError."""
        qp = Qualpal()

        with pytest.raises(TypeError, match="n must be an integer"):
            qp.generate("5")  # type: ignore[arg-type]


class TestGenerateErrorHandling:
    """Test error handling in generate()."""

    def test_generate_with_invalid_colorspace_raises_runtime_error(self):
        """Test that invalid colorspace values cause RuntimeError."""
        # Create a Qualpal with valid colorspace, then try to break it
        qp = Qualpal(colorspace={"h": (0, 360), "s": (0, 100), "l": (0, 1)})

        # This should fail because saturation > 1
        with pytest.raises(RuntimeError, match="Palette generation failed"):
            qp.generate(5)


class TestGenerateDeterminism:
    """Test determinism of generate()."""

    def test_generate_is_deterministic(self):
        """Test that generate() produces consistent results.

        The C++ algorithm is deterministic, so same inputs should
        produce same outputs.
        """
        qp = Qualpal(colorspace={"h": (0, 360), "s": (0, 1), "l": (0, 1)})

        results = []
        for _ in range(3):
            palette = qp.generate(5)
            hex_colors = tuple(c.hex() for c in palette)
            results.append(hex_colors)

        # All results should be identical
        assert len(set(results)) == 1


class TestGenerateWithConfiguration:
    """Test generate() with different configurations."""

    def test_generate_after_changing_colorspace_size(self):
        """Test that generate() works after changing colorspace_size."""
        qp = Qualpal()
        qp.colorspace_size = 500

        result = qp.generate(5)
        assert len(result) == 5

    def test_generate_after_changing_metric(self):
        """Test that generate() works after changing metric."""
        qp = Qualpal()
        qp.metric = "din99d"

        result = qp.generate(5)
        assert len(result) == 5

    def test_generate_after_changing_cvd(self):
        """Test that generate() works after changing CVD settings."""
        qp = Qualpal()
        qp.cvd = {"protan": 0.5}

        result = qp.generate(5)
        assert len(result) == 5

    def test_generate_after_changing_background(self):
        """Test that generate() works after changing background."""
        qp = Qualpal()
        qp.background = "#ffffff"

        result = qp.generate(5)
        assert len(result) == 5

    def test_generate_after_changing_max_memory(self):
        """Test that generate() works after changing max_memory."""
        qp = Qualpal()
        qp.max_memory = 2.0

        result = qp.generate(5)
        assert len(result) == 5


class TestGenerateIntegration:
    """Integration tests for generate()."""

    def test_generate_workflow(self):
        """Test complete workflow: create, configure, generate."""
        qp = Qualpal(colorspace={"h": (0, 180), "s": (0.5, 1), "l": (0.3, 0.7)})
        qp.cvd = {"protan": 0.5}
        qp.metric = "din99d"
        qp.background = "#ffffff"

        palette = qp.generate(6)

        assert isinstance(palette, Palette)
        assert len(palette) == 6
        for color in palette:
            assert isinstance(color, Color)

    def test_generate_multiple_times(self):
        """Test generating multiple palettes from same Qualpal."""
        qp = Qualpal()

        palette1 = qp.generate(3)
        palette2 = qp.generate(5)
        palette3 = qp.generate(3)

        # Different sizes
        assert len(palette1) == 3
        assert len(palette2) == 5

        # Same size should give same results (deterministic)
        assert palette1 == palette3

    def test_generate_and_access_colors(self):
        """Test generating palette and accessing individual colors."""
        qp = Qualpal()
        palette = qp.generate(5)

        # Test indexing
        first_color = palette[0]
        assert isinstance(first_color, Color)

        # Test iteration
        for color in palette:
            assert isinstance(color, Color)
            assert color.hex().startswith("#")

        # Test slicing
        subset = palette[1:3]
        assert isinstance(subset, Palette)
        assert len(subset) == 2

    def test_generate_empty_edge_case(self):
        """Test that requesting 0 colors raises ValueError."""
        qp = Qualpal()

        with pytest.raises(ValueError, match="n must be positive"):
            qp.generate(0)
