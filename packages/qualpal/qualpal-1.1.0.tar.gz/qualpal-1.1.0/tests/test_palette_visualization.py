"""Tests for Palette.show() visualization method.

Phase 5.2: Matplotlib Integration
Tests the show() method for palette visualization.
"""

from __future__ import annotations

import pytest

from qualpal import Palette

# Check if matplotlib is available
try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


@pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
class TestPaletteShow:
    """Test Palette.show() method with matplotlib."""

    def test_show_returns_figure(self):
        """Test that show() returns a matplotlib Figure."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        fig = pal.show()
        plt.close(fig)

        assert isinstance(fig, mpl.figure.Figure)

    def test_show_without_labels(self):
        """Test show() without labels."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        fig = pal.show()
        plt.close(fig)

        assert fig is not None

    def test_show_with_hex_labels(self):
        """Test show() with hex code labels."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        fig = pal.show(labels=True)
        plt.close(fig)

        assert fig is not None

    def test_show_with_custom_labels(self):
        """Test show() with custom labels."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        fig = pal.show(labels=["Red", "Green", "Blue"])
        plt.close(fig)

        assert fig is not None

    def test_show_single_color(self):
        """Test show() with single color."""
        pal = Palette(["#ff0000"])

        fig = pal.show()
        plt.close(fig)

        assert fig is not None

    def test_show_many_colors(self):
        """Test show() with many colors."""
        colors = [f"#{i:02x}0000" for i in range(10)]
        pal = Palette(colors)

        fig = pal.show()
        plt.close(fig)

        assert fig is not None

    def test_show_wrong_number_of_labels_raises_error(self):
        """Test that wrong number of labels raises ValueError."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        with pytest.raises(ValueError, match="Number of labels"):
            fig = pal.show(labels=["Red", "Green"])  # Only 2 labels for 3 colors
            plt.close(fig)

    def test_figure_can_be_saved(self):
        """Test that returned figure can be saved."""
        import tempfile

        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])
        fig = pal.show()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            fig.savefig(f.name)
            plt.close(fig)
            # File should exist
            import os

            assert os.path.exists(f.name)
            os.unlink(f.name)

    def test_show_labels_none_vs_false(self):
        """Test that labels=None and labels=False behave the same."""
        pal = Palette(["#ff0000", "#00ff00"])

        fig1 = pal.show(labels=None)
        fig2 = pal.show(labels=False)
        plt.close(fig1)
        plt.close(fig2)

        # Both should work (not raise errors)
        assert fig1 is not None
        assert fig2 is not None


@pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
class TestPaletteShowIntegration:
    """Integration tests for palette visualization."""

    def test_show_after_generation(self):
        """Test show() after palette generation."""
        from qualpal import Qualpal

        qp = Qualpal()
        pal = qp.generate(5)

        fig = pal.show()
        plt.close(fig)

        assert fig is not None

    def test_show_with_analysis(self):
        """Test combining visualization with analysis."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        # Analyze
        min_dist = pal.min_distance()

        # Visualize
        fig = pal.show(labels=True)
        plt.close(fig)

        assert min_dist > 0
        assert fig is not None

    def test_show_multiple_times(self):
        """Test that show() can be called multiple times."""
        pal = Palette(["#ff0000", "#00ff00"])

        fig1 = pal.show()
        fig2 = pal.show(labels=True)
        fig3 = pal.show(labels=["A", "B"])

        plt.close(fig1)
        plt.close(fig2)
        plt.close(fig3)

        assert all(fig is not None for fig in [fig1, fig2, fig3])


class TestPaletteShowWithoutMatplotlib:
    """Test behavior when matplotlib is not available."""

    def test_import_error_when_matplotlib_missing(self, monkeypatch):
        """Test that ImportError is raised when matplotlib is missing."""
        # Mock matplotlib import to fail
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if "matplotlib" in name:
                msg = "No module named 'matplotlib'"
                raise ImportError(msg)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        with pytest.raises(ImportError, match="matplotlib is required"):
            pal.show()


@pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
class TestPaletteShowEdgeCases:
    """Test edge cases for palette visualization."""

    def test_show_empty_palette(self):
        """Test show() with empty palette."""
        pal = Palette([])

        fig = pal.show()
        plt.close(fig)

        # Should not crash
        assert fig is not None

    def test_show_with_empty_custom_labels(self):
        """Test show() with empty custom labels list."""
        pal = Palette([])

        fig = pal.show(labels=[])
        plt.close(fig)

        assert fig is not None

    def test_show_preserves_color_order(self):
        """Test that show() preserves color order."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
        pal = Palette(colors)

        fig = pal.show()

        # Check that figure was created (order is visual, hard to test programmatically)
        assert fig is not None
        plt.close(fig)


@pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed")
class TestPaletteShowUseCases:
    """Test practical use cases for palette visualization."""

    def test_show_for_presentation(self):
        """Test visualization for presentation/documentation."""
        from qualpal import Qualpal

        qp = Qualpal()
        pal = qp.generate(6)

        # Create labeled visualization
        fig = pal.show(labels=True)

        # Should be ready to display or save
        assert fig is not None
        plt.close(fig)

    def test_show_with_custom_workflow_labels(self):
        """Test visualization with workflow-specific labels."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff", "#ffff00"])

        labels = ["Primary", "Success", "Info", "Warning"]
        fig = pal.show(labels=labels)

        assert fig is not None
        plt.close(fig)

    def test_figure_customization(self):
        """Test that returned figure can be further customized."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        fig = pal.show()

        # Add title to figure
        fig.suptitle("My Color Palette")

        assert fig is not None
        plt.close(fig)
