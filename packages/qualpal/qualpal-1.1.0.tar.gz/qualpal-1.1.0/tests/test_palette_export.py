"""Tests for Palette export methods.

Phase 5.1: Export Formats
Tests the to_css() and to_json() methods.
"""

from __future__ import annotations

import json

from qualpal import Palette, Qualpal


class TestPaletteToCss:
    """Test Palette.to_css() method."""

    def test_to_css_returns_list(self):
        """Test that to_css returns a list."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.to_css()

        assert isinstance(result, list)

    def test_to_css_correct_count(self):
        """Test that to_css returns correct number of declarations."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.to_css()

        assert len(result) == 3

    def test_to_css_format(self):
        """Test that to_css returns properly formatted CSS."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.to_css()

        assert result[0] == "--color-1: #ff0000;"
        assert result[1] == "--color-2: #00ff00;"
        assert result[2] == "--color-3: #0000ff;"

    def test_to_css_default_prefix(self):
        """Test that default prefix is 'color'."""
        pal = Palette(["#ff0000"])

        result = pal.to_css()

        assert result[0].startswith("--color-")

    def test_to_css_custom_prefix(self):
        """Test to_css with custom prefix."""
        pal = Palette(["#ff0000", "#00ff00"])

        result = pal.to_css(prefix="theme")

        assert result[0] == "--theme-1: #ff0000;"
        assert result[1] == "--theme-2: #00ff00;"

    def test_to_css_single_color(self):
        """Test to_css with single color."""
        pal = Palette(["#ff0000"])

        result = pal.to_css()

        assert len(result) == 1
        assert result[0] == "--color-1: #ff0000;"

    def test_to_css_many_colors(self):
        """Test to_css with many colors."""
        colors = [f"#{i:02x}0000" for i in range(10)]
        pal = Palette(colors)

        result = pal.to_css()

        assert len(result) == 10
        assert result[9].startswith("--color-10:")

    def test_to_css_numbering_starts_at_one(self):
        """Test that CSS variable numbering starts at 1."""
        pal = Palette(["#ff0000", "#00ff00"])

        result = pal.to_css()

        assert "--color-1:" in result[0]
        assert "--color-2:" in result[1]
        # Should not have --color-0
        assert not any("--color-0:" in r for r in result)


class TestPaletteToJson:
    """Test Palette.to_json() method."""

    def test_to_json_returns_string(self):
        """Test that to_json returns a string."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.to_json()

        assert isinstance(result, str)

    def test_to_json_valid_json(self):
        """Test that to_json returns valid JSON."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.to_json()

        # Should be parseable as JSON
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_to_json_correct_values(self):
        """Test that to_json contains correct hex values."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.to_json()
        parsed = json.loads(result)

        assert parsed == ["#ff0000", "#00ff00", "#0000ff"]

    def test_to_json_single_color(self):
        """Test to_json with single color."""
        pal = Palette(["#ff0000"])

        result = pal.to_json()
        parsed = json.loads(result)

        assert parsed == ["#ff0000"]

    def test_to_json_preserves_order(self):
        """Test that to_json preserves color order."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
        pal = Palette(colors)

        result = pal.to_json()
        parsed = json.loads(result)

        assert parsed == colors

    def test_to_json_empty_palette(self):
        """Test to_json with empty palette."""
        pal = Palette([])

        result = pal.to_json()
        parsed = json.loads(result)

        assert parsed == []


class TestExportFormatsIntegration:
    """Integration tests for export formats."""

    def test_css_and_json_consistent(self):
        """Test that CSS and JSON exports are consistent."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        css = pal.to_css()
        json_str = pal.to_json()
        json_data = json.loads(json_str)

        # Same number of colors
        assert len(css) == len(json_data)

        # CSS contains all hex values
        for hex_color in json_data:
            assert any(hex_color in declaration for declaration in css)

    def test_export_after_generation(self):
        """Test exporting after palette generation."""
        qp = Qualpal()
        pal = qp.generate(5)

        css = pal.to_css()
        json_str = pal.to_json()

        assert len(css) == 5
        assert len(json.loads(json_str)) == 5

    def test_export_different_prefixes(self):
        """Test CSS export with various prefixes."""
        pal = Palette(["#ff0000", "#00ff00"])

        prefixes = ["theme", "brand", "ui", "primary"]
        for prefix in prefixes:
            result = pal.to_css(prefix=prefix)
            assert result[0].startswith(f"--{prefix}-")


class TestExportEdgeCases:
    """Test edge cases in export methods."""

    def test_to_css_with_uppercase_hex(self):
        """Test to_css with uppercase hex colors (should be normalized)."""
        pal = Palette(["#FF0000", "#00FF00"])

        result = pal.to_css()

        # Should be lowercase in output
        assert "#ff0000" in result[0]
        assert "#00ff00" in result[1]

    def test_to_json_with_uppercase_hex(self):
        """Test to_json with uppercase hex colors (should be normalized)."""
        pal = Palette(["#FF0000", "#00FF00"])

        result = pal.to_json()
        parsed = json.loads(result)

        # Should be lowercase
        assert parsed == ["#ff0000", "#00ff00"]

    def test_to_css_special_characters_in_prefix(self):
        """Test to_css with prefix containing valid CSS characters."""
        pal = Palette(["#ff0000"])

        result = pal.to_css(prefix="my-theme")

        assert result[0] == "--my-theme-1: #ff0000;"


class TestExportUseCases:
    """Test practical use cases for export methods."""

    def test_css_for_web_development(self):
        """Test CSS export for web development use case."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        css = pal.to_css(prefix="brand")

        # Should be ready to paste into CSS
        css_block = ":root {\n  " + "\n  ".join(css) + "\n}"

        assert "--brand-1: #ff0000;" in css_block
        assert "--brand-2: #00ff00;" in css_block
        assert "--brand-3: #0000ff;" in css_block

    def test_json_for_api_response(self):
        """Test JSON export for API response use case."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        json_str = pal.to_json()

        # Should be valid JSON that can be sent in API
        response = {"palette": json.loads(json_str)}
        assert len(response["palette"]) == 3

    def test_json_for_config_file(self):
        """Test JSON export for configuration file use case."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff", "#ffff00"])

        config = {"theme": {"colors": json.loads(pal.to_json())}}

        assert len(config["theme"]["colors"]) == 4
        assert "#ff0000" in config["theme"]["colors"]
