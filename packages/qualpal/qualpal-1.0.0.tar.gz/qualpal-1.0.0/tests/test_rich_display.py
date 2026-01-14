"""Tests for rich display (Jupyter/IPython) functionality.

Phase 6.1: Rich Display
Tests the _repr_html_() methods for Color and Palette.
"""

from __future__ import annotations

from qualpal import Color, Palette


class TestColorRichDisplay:
    """Test Color._repr_html_() method."""

    def test_repr_html_exists(self):
        """Test that _repr_html_() method exists."""
        color = Color("#ff0000")

        assert hasattr(color, "_repr_html_")
        assert callable(color._repr_html_)

    def test_repr_html_returns_string(self):
        """Test that _repr_html_() returns a string."""
        color = Color("#ff0000")

        html = color._repr_html_()

        assert isinstance(html, str)

    def test_repr_html_contains_hex(self):
        """Test that HTML contains the hex color code."""
        color = Color("#ff0000")

        html = color._repr_html_()

        assert "#ff0000" in html

    def test_repr_html_contains_color_style(self):
        """Test that HTML contains inline style with background color."""
        color = Color("#00ff00")

        html = color._repr_html_()

        assert "background-color" in html
        assert "#00ff00" in html

    def test_repr_html_is_valid_html(self):
        """Test that returned HTML has basic structure."""
        color = Color("#0000ff")

        html = color._repr_html_()

        # Should have div tags
        assert "<div" in html
        assert "</div>" in html

    def test_repr_html_different_colors(self):
        """Test that different colors produce different HTML."""
        red = Color("#ff0000")
        green = Color("#00ff00")

        html_red = red._repr_html_()
        html_green = green._repr_html_()

        assert html_red != html_green
        assert "#ff0000" in html_red
        assert "#00ff00" in html_green


class TestPaletteRichDisplay:
    """Test Palette._repr_html_() method."""

    def test_repr_html_exists(self):
        """Test that _repr_html_() method exists."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        assert hasattr(pal, "_repr_html_")
        assert callable(pal._repr_html_)

    def test_repr_html_returns_string(self):
        """Test that _repr_html_() returns a string."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        html = pal._repr_html_()

        assert isinstance(html, str)

    def test_repr_html_contains_all_colors(self):
        """Test that HTML contains all colors in the palette."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        html = pal._repr_html_()

        assert "#ff0000" in html
        assert "#00ff00" in html
        assert "#0000ff" in html

    def test_repr_html_empty_palette(self):
        """Test HTML representation of empty palette."""
        pal = Palette([])

        html = pal._repr_html_()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_repr_html_single_color(self):
        """Test HTML representation of palette with single color."""
        pal = Palette(["#ff0000"])

        html = pal._repr_html_()

        assert "#ff0000" in html

    def test_repr_html_many_colors(self):
        """Test HTML representation with many colors."""
        colors = [f"#{i:02x}0000" for i in range(10)]
        pal = Palette(colors)

        html = pal._repr_html_()

        # Should contain all colors
        for color in colors:
            assert color in html

    def test_repr_html_is_valid_html(self):
        """Test that returned HTML has basic structure."""
        pal = Palette(["#ff0000", "#00ff00"])

        html = pal._repr_html_()

        # Should have div tags
        assert "<div" in html
        assert "</div>" in html

    def test_repr_html_has_multiple_swatches(self):
        """Test that HTML has multiple color swatches."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        html = pal._repr_html_()

        # Should have multiple background-color styles
        assert html.count("background-color") >= 3


class TestRichDisplayIntegration:
    """Integration tests for rich display."""

    def test_color_from_palette_has_repr_html(self):
        """Test that colors from palette have _repr_html_()."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        color = pal[0]

        assert hasattr(color, "_repr_html_")
        html = color._repr_html_()
        assert "#ff0000" in html

    def test_palette_after_generation_has_repr_html(self):
        """Test that generated palette has _repr_html_()."""
        from qualpal import Qualpal

        qp = Qualpal()
        pal = qp.generate(3)

        html = pal._repr_html_()
        assert isinstance(html, str)
        assert len(html) > 0

    def test_str_and_repr_still_work(self):
        """Test that str() and repr() still work as expected."""
        color = Color("#ff0000")
        pal = Palette(["#ff0000", "#00ff00"])

        # Color
        assert str(color) == "#ff0000"
        assert "Color" in repr(color)

        # Palette
        assert "Palette" in str(pal)
        assert "Palette" in repr(pal)


class TestRichDisplayHTMLStructure:
    """Test HTML structure details."""

    def test_color_html_has_swatch_and_code(self):
        """Test that color HTML has both swatch and hex code."""
        color = Color("#ff0000")

        html = color._repr_html_()

        # Should have styled div for swatch
        assert "width:" in html or "height:" in html
        # Should have code tag or text with hex
        assert "#ff0000" in html

    def test_palette_html_has_proper_layout(self):
        """Test that palette HTML has flex layout."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        html = pal._repr_html_()

        # Should use flex or inline layout
        assert "display:" in html.lower()

    def test_empty_palette_html_has_message(self):
        """Test that empty palette shows appropriate message."""
        pal = Palette([])

        html = pal._repr_html_()

        # Should indicate it's empty
        assert "empty" in html.lower() or "palette" in html.lower()


class TestRichDisplayConsistency:
    """Test consistency of rich display."""

    def test_repr_html_deterministic(self):
        """Test that _repr_html_() is deterministic."""
        color = Color("#ff0000")

        html1 = color._repr_html_()
        html2 = color._repr_html_()

        assert html1 == html2

    def test_palette_repr_html_deterministic(self):
        """Test that palette _repr_html_() is deterministic."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        html1 = pal._repr_html_()
        html2 = pal._repr_html_()

        assert html1 == html2

    def test_same_colors_same_html(self):
        """Test that same colors produce same HTML."""
        color1 = Color("#ff0000")
        color2 = Color("#ff0000")

        assert color1._repr_html_() == color2._repr_html_()


class TestRichDisplayEdgeCases:
    """Test edge cases for rich display."""

    def test_color_with_uppercase_hex(self):
        """Test rich display with uppercase hex (should be normalized)."""
        color = Color("#FF0000")

        html = color._repr_html_()

        # Should be lowercase in output
        assert "#ff0000" in html

    def test_palette_order_preserved_in_html(self):
        """Test that color order is preserved in HTML."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        html = pal._repr_html_()

        # Red should appear before green, green before blue in HTML
        red_pos = html.find("#ff0000")
        green_pos = html.find("#00ff00")
        blue_pos = html.find("#0000ff")

        assert red_pos < green_pos < blue_pos
