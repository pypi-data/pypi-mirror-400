"""Palette class."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, overload

import _qualpal

from qualpal.color import Color

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class Palette:
    """A collection of colors that behaves like a list.

    Palette objects are immutable.
    """

    def __init__(self, colors: Sequence[Color | str]) -> None:
        """Create a Palette from a list of colors.

        Parameters
        ----------
        colors : Sequence[Color | str]
            Sequence of Color objects or hex strings

        Raises
        ------
        ValueError
            If any color is invalid
        """
        self._colors: list[Color] = []
        for c in colors:
            if isinstance(c, Color):
                self._colors.append(c)
            elif isinstance(c, str):
                self._colors.append(Color(c))
            else:
                msg = f"Invalid color type: {type(c)}"
                raise TypeError(msg)

    def __len__(self) -> int:
        """Return the number of colors in the palette."""
        return len(self._colors)

    @overload
    def __getitem__(self, index: int) -> Color: ...

    @overload
    def __getitem__(self, index: slice) -> Palette: ...

    def __getitem__(self, index: int | slice) -> Color | Palette:
        """Get color(s) by index or slice.

        Parameters
        ----------
        index : int | slice
            Index or slice object

        Returns
        -------
        Color | Palette
            Single Color if index is int, new Palette if index is slice
        """
        if isinstance(index, slice):
            return Palette(self._colors[index])
        return self._colors[index]

    def __iter__(self) -> Iterator[Color]:
        """Iterate over colors in the palette."""
        return iter(self._colors)

    def __contains__(self, item: object) -> bool:
        """Check if a color is in the palette.

        Parameters
        ----------
        item : object
            Color object or hex string to check

        Returns
        -------
        bool
            True if color is in palette, False otherwise
        """
        if isinstance(item, Color):
            return item in self._colors
        if isinstance(item, str):
            try:
                color = Color(item)
                return color in self._colors
            except ValueError:
                return False
        return False

    def hex(self) -> list[str]:
        """Get list of hex color strings.

        Returns
        -------
        list[str]
            List of hex strings in format #rrggbb (lowercase)
        """
        return [c.hex() for c in self._colors]

    def rgb(self) -> list[tuple[float, float, float]]:
        """Get RGB values as list of tuples.

        Returns
        -------
        list[tuple[float, float, float]]
            List of RGB tuples in range [0.0, 1.0]
        """
        return [c.rgb() for c in self._colors]

    def to_css(self, prefix: str = "color") -> list[str]:
        """Export palette as CSS custom properties (CSS variables).

        Parameters
        ----------
        prefix : str
            Prefix for CSS variable names (default: 'color')

        Returns
        -------
        list[str]
            List of CSS custom property declarations

        Examples
        --------
        >>> from qualpal import Palette
        >>> pal = Palette(['#ff0000', '#00ff00', '#0000ff'])
        >>> pal.to_css()
        ['--color-1: #ff0000;', '--color-2: #00ff00;', '--color-3: #0000ff;']
        >>> pal.to_css(prefix='theme')
        ['--theme-1: #ff0000;', '--theme-2: #00ff00;', '--theme-3: #0000ff;']
        """
        return [
            f"--{prefix}-{i}: {color.hex()};" for i, color in enumerate(self._colors, 1)
        ]

    def to_json(self) -> str:
        """Export palette as JSON array of hex colors.

        Returns
        -------
        str
            JSON string containing array of hex color strings

        Examples
        --------
        >>> from qualpal import Palette
        >>> pal = Palette(['#ff0000', '#00ff00', '#0000ff'])
        >>> pal.to_json()
        '["#ff0000", "#00ff00", "#0000ff"]'
        """
        return json.dumps(self.hex())

    def show(
        self, labels: bool | list[str] | None = None
    ) -> object:  # Returns Figure if matplotlib available
        """Display palette as color swatches (requires matplotlib).

        Parameters
        ----------
        labels : bool | list[str] | None
            - None (default): No labels
            - True: Show hex codes as labels
            - list[str]: Custom labels for each color

        Returns
        -------
        matplotlib.figure.Figure
            Matplotlib Figure object that can be saved or further customized

        Raises
        ------
        ImportError
            If matplotlib is not installed

        Examples
        --------
        >>> from qualpal import Palette
        >>> pal = Palette(['#ff0000', '#00ff00', '#0000ff'])
        >>> fig = pal.show()  # Display swatches
        >>> fig = pal.show(labels=True)  # With hex codes
        >>> fig = pal.show(labels=['Red', 'Green', 'Blue'])  # Custom labels
        >>> fig.savefig('palette.png')  # Save to file
        """
        try:
            import matplotlib.pyplot as plt  # noqa: PLC0415
            from matplotlib.patches import Rectangle  # noqa: PLC0415
        except ImportError as e:
            msg = (
                "matplotlib is required for palette visualization. "
                "Install it with: pip install matplotlib"
            )
            raise ImportError(msg) from e

        # Validate labels
        if isinstance(labels, list) and len(labels) != len(self._colors):
            msg = f"Number of labels ({len(labels)}) must match number of colors ({len(self._colors)})"
            raise ValueError(msg)

        # Create figure
        n_colors = len(self._colors)

        # Handle empty palette
        if n_colors == 0:
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.text(
                0.5,
                0.5,
                "Empty palette",
                ha="center",
                va="center",
                fontsize=12,
                color="gray",
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            plt.tight_layout()
            return fig

        fig, ax = plt.subplots(figsize=(n_colors * 1.5, 2))

        # Draw color swatches
        for i, color in enumerate(self._colors):
            ax.add_patch(
                Rectangle(
                    (i, 0), 1, 1, facecolor=color.hex(), edgecolor="black", linewidth=1
                )
            )

        # Set axis properties
        ax.set_xlim(0, n_colors)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")

        # Add labels if requested
        if labels is True:
            # Use hex codes as labels
            for i, color in enumerate(self._colors):
                ax.text(
                    i + 0.5,
                    -0.15,
                    color.hex(),
                    ha="center",
                    va="top",
                    fontsize=9,
                    family="monospace",
                )
        elif isinstance(labels, list):
            # Use custom labels
            for i, label in enumerate(labels):
                ax.text(
                    i + 0.5,
                    -0.15,
                    label,
                    ha="center",
                    va="top",
                    fontsize=10,
                )

        plt.tight_layout()
        return fig

    def distance_matrix(self, metric: str = "ciede2000") -> list[list[float]]:
        """Calculate pairwise distance matrix for all colors in the palette.

        Parameters
        ----------
        metric : str
            Distance metric to use. Options:
            - 'ciede2000' (default): CIEDE2000 metric
            - 'din99d': DIN99d metric
            - 'cie76': CIE76 (Euclidean distance in Lab space)

        Returns
        -------
        list[list[float]]
            Symmetric distance matrix where element [i][j] is the distance
            between colors i and j. Diagonal elements are 0.0.

        Examples
        --------
        >>> from qualpal import Palette
        >>> pal = Palette(['#ff0000', '#00ff00', '#0000ff'])
        >>> matrix = pal.distance_matrix()
        >>> len(matrix)
        3
        >>> matrix[0][0]  # Distance to self
        0.0
        """
        # Get hex colors
        hex_colors = [c.hex() for c in self._colors]

        # Call C++ function (returns flat array)
        flat_matrix = _qualpal.color_distance_matrix_cpp(hex_colors, metric)

        # Convert to 2D list
        n = len(self._colors)
        matrix = []
        for i in range(n):
            row = flat_matrix[i * n : (i + 1) * n]
            matrix.append(row)

        return matrix

    def min_distance(self, metric: str = "ciede2000") -> float:
        """Get the minimum pairwise distance between any two colors.

        Parameters
        ----------
        metric : str
            Distance metric to use (default: 'ciede2000')

        Returns
        -------
        float
            Minimum distance between any pair of distinct colors

        Examples
        --------
        >>> from qualpal import Palette
        >>> pal = Palette(['#ff0000', '#00ff00', '#0000ff'])
        >>> min_dist = pal.min_distance()
        >>> min_dist > 0
        True
        """
        if len(self._colors) < 2:
            msg = "Need at least 2 colors to compute minimum distance"
            raise ValueError(msg)

        matrix = self.distance_matrix(metric)

        # Find minimum non-zero distance
        min_dist = float("inf")
        for i in range(len(matrix)):
            for j in range(i + 1, len(matrix)):  # Only upper triangle
                dist = matrix[i][j]
                if dist > 0 and dist < min_dist:
                    min_dist = dist

        return min_dist

    def min_distances(self, metric: str = "ciede2000") -> list[float]:
        """Get minimum distance for each color to its nearest neighbor.

        Parameters
        ----------
        metric : str
            Distance metric to use (default: 'ciede2000')

        Returns
        -------
        list[float]
            List where element i is the minimum distance from color i
            to any other color in the palette

        Examples
        --------
        >>> from qualpal import Palette
        >>> pal = Palette(['#ff0000', '#00ff00', '#0000ff'])
        >>> min_dists = pal.min_distances()
        >>> len(min_dists)
        3
        >>> all(d > 0 for d in min_dists)
        True
        """
        if len(self._colors) < 2:
            msg = "Need at least 2 colors to compute minimum distances"
            raise ValueError(msg)

        matrix = self.distance_matrix(metric)

        # For each color, find its minimum distance to any other color
        min_dists = []
        for i in range(len(matrix)):
            min_dist = float("inf")
            for j in range(len(matrix)):
                if i != j and matrix[i][j] < min_dist:
                    min_dist = matrix[i][j]
            min_dists.append(min_dist)

        return min_dists

    def __str__(self) -> str:
        """String representation showing hex colors."""
        hex_list = ", ".join(f"'{c.hex()}'" for c in self._colors)
        return f"Palette([{hex_list}])"

    def __repr__(self) -> str:
        """Developer representation."""
        return self.__str__()

    def _repr_html_(self) -> str:
        """Return HTML representation for Jupyter/IPython.

        Returns
        -------
        str
            HTML string with colored swatches in a row
        """
        if not self._colors:
            return '<div style="font-style: italic; color: #888;">Empty palette</div>'

        swatches = []
        for color in self._colors:
            swatches.append(
                f'<div style="display: inline-block; text-align: center; margin: 4px;">'
                f'<div style="width: 60px; height: 60px; background-color: {color.hex()}; '
                f'border: 1px solid #333; border-radius: 4px; margin-bottom: 4px;"></div>'
                f'<div style="font-family: monospace; font-size: 11px;">{color.hex()}</div>'
                f"</div>"
            )

        return (
            f'<div style="display: flex; flex-wrap: wrap; gap: 4px; '
            f'padding: 8px; background: #f5f5f5; border-radius: 4px;">'
            f"{''.join(swatches)}"
            f"</div>"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another Palette."""
        if not isinstance(other, Palette):
            return NotImplemented

        return self._colors == other._colors

    def __ne__(self, other: object) -> bool:
        """Check inequality."""
        result = self.__eq__(other)

        if result is NotImplemented:
            return result

        return not result

    def __hash__(self) -> int:
        """Return hash of the palette.

        Since Palette is immutable, it can be hashed.
        """
        return hash(tuple(self._colors))
