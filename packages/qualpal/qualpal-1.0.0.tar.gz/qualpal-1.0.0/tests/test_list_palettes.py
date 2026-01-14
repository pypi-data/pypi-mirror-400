"""Tests for list_palettes() function.

Phase 4.2: Named Palettes
Tests the list_palettes functionality.
"""

from __future__ import annotations

from qualpal import Qualpal, list_palettes


class TestListPalettes:
    """Test list_palettes() function."""

    def test_list_palettes_returns_dict(self):
        """Test that list_palettes returns a dict."""
        result = list_palettes()

        assert isinstance(result, dict)

    def test_list_palettes_has_packages(self):
        """Test that list_palettes returns known packages."""
        result = list_palettes()

        # Should have at least ColorBrewer
        assert "ColorBrewer" in result
        assert len(result) > 0

    def test_list_palettes_has_palette_lists(self):
        """Test that each package has a list of palettes."""
        result = list_palettes()

        for _package, palettes in result.items():
            assert isinstance(palettes, list)
            assert len(palettes) > 0
            assert all(isinstance(p, str) for p in palettes)

    def test_colorbrewer_has_expected_palettes(self):
        """Test that ColorBrewer has some expected palettes."""
        result = list_palettes()

        assert "ColorBrewer" in result
        cb_palettes = result["ColorBrewer"]

        # Check for some known ColorBrewer palettes
        assert "Set1" in cb_palettes or "Set2" in cb_palettes or "Set3" in cb_palettes

    def test_pokemon_package_exists(self):
        """Test that Pokemon package exists."""
        result = list_palettes()

        assert "Pokemon" in result
        assert len(result["Pokemon"]) > 0

    def test_palette_names_are_strings(self):
        """Test that all palette names are strings."""
        result = list_palettes()

        for _package, palettes in result.items():
            for palette in palettes:
                assert isinstance(palette, str)
                assert len(palette) > 0


class TestListPalettesIntegration:
    """Integration tests for list_palettes with Qualpal."""

    def test_can_use_listed_palette_with_qualpal(self):
        """Test that listed palettes can be used with Qualpal."""
        palettes = list_palettes()

        # Pick the first palette from ColorBrewer
        if "ColorBrewer" in palettes and len(palettes["ColorBrewer"]) > 0:
            palette_name = f"ColorBrewer:{palettes['ColorBrewer'][0]}"

            qp = Qualpal(palette=palette_name)
            result = qp.generate(3)

            assert len(result) == 3

    def test_all_colorbrewer_palettes_work(self):
        """Test that all ColorBrewer palettes can be loaded."""
        palettes = list_palettes()

        if "ColorBrewer" in palettes:
            # Test first 3 palettes
            for palette_name in palettes["ColorBrewer"][:3]:
                full_name = f"ColorBrewer:{palette_name}"
                qp = Qualpal(palette=full_name)
                result = qp.generate(2)
                assert len(result) == 2

    def test_pokemon_palette_works(self):
        """Test that a Pokemon palette can be loaded."""
        palettes = list_palettes()

        if "Pokemon" in palettes and "Charizard" in palettes["Pokemon"]:
            qp = Qualpal(palette="Pokemon:Charizard")
            result = qp.generate(3)
            assert len(result) == 3


class TestListPalettesConsistency:
    """Test consistency of list_palettes output."""

    def test_list_palettes_is_deterministic(self):
        """Test that list_palettes returns same results."""
        result1 = list_palettes()
        result2 = list_palettes()

        assert result1.keys() == result2.keys()
        for package in result1:
            assert sorted(result1[package]) == sorted(result2[package])

    def test_palette_count(self):
        """Test that we have a reasonable number of palettes."""
        result = list_palettes()

        total_palettes = sum(len(palettes) for palettes in result.values())

        # Should have at least 50 palettes total
        assert total_palettes >= 50

        # Should have multiple packages
        assert len(result) >= 3


class TestListPalettesDocumentation:
    """Test that list_palettes follows documented behavior."""

    def test_format_matches_qualpal_usage(self):
        """Test that palette names work with 'package:palette' format."""
        palettes = list_palettes()

        # Test format with first available palette
        for package, palette_list in palettes.items():
            if len(palette_list) > 0:
                palette_name = f"{package}:{palette_list[0]}"

                # Should not raise an error
                qp = Qualpal(palette=palette_name)
                result = qp.generate(1)
                assert len(result) == 1
                break
