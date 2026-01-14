"""Tests for Palette analysis methods.

Phase 3.2: Palette Analysis
Tests the distance matrix and analysis functionality.
"""

from __future__ import annotations

import pytest

from qualpal import Palette


class TestPaletteDistanceMatrix:
    """Test Palette.distance_matrix() method."""

    def test_distance_matrix_returns_list(self):
        """Test that distance_matrix returns a list of lists."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        matrix = pal.distance_matrix()

        assert isinstance(matrix, list)
        assert all(isinstance(row, list) for row in matrix)

    def test_distance_matrix_correct_shape(self):
        """Test that distance matrix has correct shape (n x n)."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
        pal = Palette(colors)

        matrix = pal.distance_matrix()

        assert len(matrix) == 4
        assert all(len(row) == 4 for row in matrix)

    def test_distance_matrix_diagonal_is_zero(self):
        """Test that diagonal elements (self-distance) are zero."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        matrix = pal.distance_matrix()

        for i in range(len(matrix)):
            assert matrix[i][i] == 0.0

    def test_distance_matrix_is_symmetric(self):
        """Test that distance matrix is symmetric."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        matrix = pal.distance_matrix()

        for i in range(len(matrix)):
            for j in range(len(matrix)):
                assert matrix[i][j] == matrix[j][i]

    def test_distance_matrix_all_positive(self):
        """Test that all off-diagonal distances are positive."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        matrix = pal.distance_matrix()

        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if i != j:
                    assert matrix[i][j] > 0

    def test_distance_matrix_different_metrics(self):
        """Test distance matrix with different metrics."""
        pal = Palette(["#ff0000", "#00ff00"])

        matrix_ciede = pal.distance_matrix(metric="ciede2000")
        matrix_din = pal.distance_matrix(metric="din99d")
        matrix_cie = pal.distance_matrix(metric="cie76")

        # All should be different
        assert matrix_ciede[0][1] != matrix_din[0][1]
        assert matrix_ciede[0][1] != matrix_cie[0][1]

    def test_distance_matrix_single_color(self):
        """Test distance matrix with single color."""
        pal = Palette(["#ff0000"])

        matrix = pal.distance_matrix()

        assert len(matrix) == 1
        assert matrix[0][0] == 0.0


class TestPaletteMinDistance:
    """Test Palette.min_distance() method."""

    def test_min_distance_returns_float(self):
        """Test that min_distance returns a float."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.min_distance()

        assert isinstance(result, float)

    def test_min_distance_is_positive(self):
        """Test that min_distance is positive."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.min_distance()

        assert result > 0

    def test_min_distance_finds_minimum(self):
        """Test that min_distance finds the actual minimum."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        min_dist = pal.min_distance()
        matrix = pal.distance_matrix()

        # Manual minimum (excluding diagonal)
        manual_min = float("inf")
        for i in range(len(matrix)):
            for j in range(i + 1, len(matrix)):
                manual_min = min(manual_min, matrix[i][j])

        assert min_dist == manual_min

    def test_min_distance_similar_colors(self):
        """Test min_distance with very similar colors."""
        pal = Palette(["#ff0000", "#ff0001"])  # Almost identical

        min_dist = pal.min_distance()

        assert min_dist < 1.0  # Should be very small

    def test_min_distance_distinct_colors(self):
        """Test min_distance with very distinct colors."""
        pal = Palette(["#000000", "#ffffff"])  # Black and white

        min_dist = pal.min_distance()

        assert min_dist > 50  # Should be large

    def test_min_distance_with_one_color_raises_error(self):
        """Test that min_distance with 1 color raises ValueError."""
        pal = Palette(["#ff0000"])

        with pytest.raises(ValueError, match="Need at least 2 colors"):
            pal.min_distance()

    def test_min_distance_different_metrics(self):
        """Test min_distance with different metrics."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        min_ciede = pal.min_distance(metric="ciede2000")
        min_din = pal.min_distance(metric="din99d")
        min_cie = pal.min_distance(metric="cie76")

        # All should be positive
        assert min_ciede > 0
        assert min_din > 0
        assert min_cie > 0


class TestPaletteMinDistances:
    """Test Palette.min_distances() method."""

    def test_min_distances_returns_list(self):
        """Test that min_distances returns a list."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.min_distances()

        assert isinstance(result, list)

    def test_min_distances_correct_length(self):
        """Test that min_distances returns correct number of values."""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
        pal = Palette(colors)

        result = pal.min_distances()

        assert len(result) == 4

    def test_min_distances_all_positive(self):
        """Test that all min_distances are positive."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        result = pal.min_distances()

        assert all(d > 0 for d in result)

    def test_min_distances_finds_nearest_neighbors(self):
        """Test that min_distances finds correct nearest neighbors."""
        # Red, slightly different red, green
        pal = Palette(["#ff0000", "#ff0001", "#00ff00"])

        min_dists = pal.min_distances()

        # First two should have smallest distances (they're neighbors)
        assert min_dists[0] < 1.0  # Red's nearest is almost-red
        assert min_dists[1] < 1.0  # Almost-red's nearest is red

    def test_min_distances_with_one_color_raises_error(self):
        """Test that min_distances with 1 color raises ValueError."""
        pal = Palette(["#ff0000"])

        with pytest.raises(ValueError, match="Need at least 2 colors"):
            pal.min_distances()

    def test_min_distances_different_metrics(self):
        """Test min_distances with different metrics."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        dists_ciede = pal.min_distances(metric="ciede2000")
        dists_din = pal.min_distances(metric="din99d")
        dists_cie = pal.min_distances(metric="cie76")

        assert len(dists_ciede) == 3
        assert len(dists_din) == 3
        assert len(dists_cie) == 3


class TestPaletteAnalysisIntegration:
    """Integration tests for palette analysis methods."""

    def test_min_distance_consistent_with_min_distances(self):
        """Test that min_distance equals minimum of min_distances."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff", "#ffff00"])

        min_dist = pal.min_distance()
        min_dists = pal.min_distances()

        assert min_dist == min(min_dists)

    def test_analysis_workflow(self):
        """Test complete analysis workflow."""
        pal = Palette(["#ff0000", "#00ff00", "#0000ff"])

        # Get all analysis data
        matrix = pal.distance_matrix()
        min_dist = pal.min_distance()
        min_dists = pal.min_distances()

        # Verify consistency
        assert len(matrix) == 3
        assert isinstance(min_dist, float)
        assert len(min_dists) == 3
        assert min_dist == min(min_dists)

    def test_large_palette_analysis(self):
        """Test analysis with larger palette."""
        # Generate 10 distinct colors
        colors = [
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#ffff00",
            "#ff00ff",
            "#00ffff",
            "#800000",
            "#008000",
            "#000080",
            "#808080",
        ]
        pal = Palette(colors)

        matrix = pal.distance_matrix()
        min_dist = pal.min_distance()
        min_dists = pal.min_distances()

        assert len(matrix) == 10
        assert len(min_dists) == 10
        assert min_dist > 0

    def test_grayscale_palette_analysis(self):
        """Test analysis with grayscale palette."""
        pal = Palette(["#000000", "#808080", "#ffffff"])

        matrix = pal.distance_matrix()
        min_dist = pal.min_distance()

        # All distances should be positive
        assert min_dist > 0
        # Should be symmetric
        assert matrix[0][1] == matrix[1][0]


class TestPaletteAnalysisEdgeCases:
    """Test edge cases in palette analysis."""

    def test_two_color_palette(self):
        """Test analysis with minimum (2) colors."""
        pal = Palette(["#ff0000", "#00ff00"])

        matrix = pal.distance_matrix()
        min_dist = pal.min_distance()
        min_dists = pal.min_distances()

        assert len(matrix) == 2
        assert len(min_dists) == 2
        assert min_dist == matrix[0][1]
        assert min_dists[0] == matrix[0][1]
        assert min_dists[1] == matrix[1][0]

    def test_identical_colors_in_palette(self):
        """Test analysis with duplicate colors."""
        pal = Palette(["#ff0000", "#ff0000", "#00ff00"])

        matrix = pal.distance_matrix()

        # Distance between identical colors should be 0
        assert matrix[0][1] == 0.0
        assert matrix[1][0] == 0.0
