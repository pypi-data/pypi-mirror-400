"""Qualpal class for generating qualitative color palettes."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import _qualpal

from qualpal.color import Color
from qualpal.palette import Palette

if TYPE_CHECKING:
    from collections.abc import Sequence


class Qualpal:
    """Generate qualitative color palettes with distinct colors.

    The Qualpal class provides a stateful builder for generating color
    palettes. You can specify colors, colorspace, or palette as input,
    and configure parameters like CVD simulation, distance metric, etc.
    """

    def __init__(
        self,
        colors: Sequence[str] | None = None,
        colorspace: dict[str, tuple[float, float]] | None = None,
        palette: str | None = None,
        space: str = "hsl",
        cvd: dict[str, float] | None = None,
        metric: str = "ciede2000",
        background: str | None = None,
        max_memory: float = 1.0,
        colorspace_size: int = 1000,
    ) -> None:
        """Initialize Qualpal object.

        Parameters
        ----------
        colors : Sequence[str] | None
            List of hex color strings to use as starting point.
            Mutually exclusive with colorspace and palette.

        colorspace : dict[str, tuple[float, float]] | None
            Colorspace specification with ranges for each dimension.
            Keys depend on 'space' parameter:
            - 'hsl': 'h', 's', 'l'
            - 'lchab': 'h', 'c', 'l'
            Each value is a (min, max) tuple.
            Mutually exclusive with colors and palette.

        palette : str | None
            Named palette in format 'source:name' (e.g., 'ColorBrewer:Set1').
            Mutually exclusive with colors and colorspace.

        space : str
            Color space to use: 'hsl' (default) or 'lchab'.

        cvd : dict[str, float] | None
            Color vision deficiency simulation. Keys: 'protan', 'deutan', 'tritan'.
            Values: 0.0 (normal) to 1.0 (complete deficiency).

        metric : str
            Color difference metric: 'ciede2000' (default), 'din99d', or 'cie76'.

        background : str | None
            Background color as hex string (e.g., '#ffffff').

        max_memory : float
            Maximum memory to use in GB (default: 1.0).

        colorspace_size : int
            Number of colors to sample from colorspace (default: 1000).

        Raises
        ------
        ValueError
            If multiple of colors/colorspace/palette are provided,
            or if any parameter has invalid values.

        TypeError
            If parameter types are incorrect.
        """
        # Validate mutual exclusivity
        provided = sum(
            [
                colors is not None,
                colorspace is not None,
                palette is not None,
            ]
        )
        if provided > 1:
            msg = "Provide only one of: colors, colorspace, or palette"
            raise ValueError(msg)

        # Set defaults if none provided
        if provided == 0:
            colorspace = {"h": (0, 360), "s": (0, 1), "l": (0, 1)}
            space = "hsl"

        # Validate palette exists
        if palette is not None and ":" not in palette:
            msg = "palette must be in format 'source:name'"
            raise ValueError(msg)
            # TODO: Check if palette exists (implementation detail)

        # Validate colorspace structure
        if colorspace is not None:
            if space == "hsl":
                required = {"h", "s", "l"}
            elif space == "lchab":
                required = {"h", "c", "l"}
            else:
                msg = f"space must be 'hsl' or 'lchab', got '{space}'"
                raise ValueError(msg)

            if not isinstance(colorspace, dict):
                msg = "colorspace must be a dict"
                raise TypeError(msg)
            if set(colorspace.keys()) != required:
                msg = f"colorspace must have keys {required}"
                raise ValueError(msg)

            for key, value in colorspace.items():
                if not isinstance(value, (tuple, list)) or len(value) != 2:
                    msg = f"colorspace['{key}'] must be a tuple/list of length 2"
                    raise TypeError(msg)
                min_val, max_val = value
                if not isinstance(min_val, (int, float)) or not isinstance(
                    max_val, (int, float)
                ):
                    msg = f"colorspace['{key}'] range must be numeric"
                    raise TypeError(msg)
                if min_val >= max_val:
                    msg = f"colorspace['{key}'] min must be < max"
                    raise ValueError(msg)

        # Store input mode
        self._colors = colors
        self._colorspace = colorspace
        self._palette = palette
        self._space = space

        # Initialize private attributes (will be set via property setters)
        self._cvd: dict[str, float] | None = None
        self._metric: str = "ciede2000"
        self._background: str | None = None
        self._max_memory: float = 1.0
        self._colorspace_size: int = 1000

        # Use setters for validation even in __init__
        self.cvd = cvd
        self.metric = metric
        self.background = background
        self.max_memory = max_memory
        self.colorspace_size = colorspace_size

    @property
    def cvd(self) -> dict[str, float] | None:
        """Get color vision deficiency simulation settings."""
        return self._cvd

    @cvd.setter
    def cvd(self, value: dict[str, float] | None) -> None:
        """Set color vision deficiency simulation settings.

        Parameters
        ----------
        value : dict[str, float] | None
            Dictionary with keys 'protan', 'deutan', or 'tritan',
            and values between 0.0 and 1.0.

        Raises
        ------
        TypeError
            If value is not a dict or values are not numeric.
        ValueError
            If keys are invalid or values are out of range.
        """
        if value is not None:
            valid_types = {"protan", "deutan", "tritan"}
            if not isinstance(value, dict):
                msg = "cvd must be a dict"
                raise TypeError(msg)
            if not set(value.keys()).issubset(valid_types):
                msg = f"cvd keys must be in {valid_types}"
                raise ValueError(msg)
            for k, v in value.items():
                if not isinstance(v, (int, float)):
                    msg = f"cvd['{k}'] must be a number"
                    raise TypeError(msg)
                if not 0.0 <= v <= 1.0:
                    msg = f"cvd['{k}'] must be between 0.0 and 1.0"
                    raise ValueError(msg)
        self._cvd = value

    @property
    def metric(self) -> str:
        """Get color difference metric."""
        return self._metric

    @metric.setter
    def metric(self, value: str) -> None:
        """Set color difference metric.

        Parameters
        ----------
        value : str
            Metric name: 'ciede2000', 'din99d', or 'cie76'.

        Raises
        ------
        ValueError
            If metric is not one of the valid options.
        """
        valid = {"ciede2000", "din99d", "cie76"}
        if value not in valid:
            msg = f"metric must be one of {valid}"
            raise ValueError(msg)
        self._metric = value

    @property
    def background(self) -> str | None:
        """Get background color."""
        return self._background

    @background.setter
    def background(self, value: str | None) -> None:
        """Set background color.

        Parameters
        ----------
        value : str | None
            Hex color string (e.g., '#ffffff') or None.

        Raises
        ------
        TypeError
            If value is not a string.
        ValueError
            If hex format is invalid.
        """
        if value is not None:
            if not isinstance(value, str):
                msg = "background must be a hex string"
                raise TypeError(msg)
            if not re.match(r"^#[0-9a-fA-F]{6}$", value):
                msg = f"Invalid hex color: {value}"
                raise ValueError(msg)
        self._background = value

    @property
    def max_memory(self) -> float:
        """Get maximum memory in GB."""
        return self._max_memory

    @max_memory.setter
    def max_memory(self, value: float) -> None:
        """Set maximum memory in GB.

        Parameters
        ----------
        value : float
            Maximum memory in GB, must be positive.

        Raises
        ------
        TypeError
            If value is not numeric.
        ValueError
            If value is not positive.
        """
        if not isinstance(value, (int, float)):
            msg = "max_memory must be a number"
            raise TypeError(msg)
        if value <= 0:
            msg = "max_memory must be positive"
            raise ValueError(msg)
        self._max_memory = float(value)

    @property
    def colorspace_size(self) -> int:
        """Get colorspace size."""
        return self._colorspace_size

    @colorspace_size.setter
    def colorspace_size(self, value: int) -> None:
        """Set colorspace size.

        Parameters
        ----------
        value : int
            Number of colors to sample from colorspace, must be positive.

        Raises
        ------
        TypeError
            If value is not an integer.
        ValueError
            If value is not positive.
        """
        if not isinstance(value, int):
            msg = "colorspace_size must be an integer"
            raise TypeError(msg)
        if value <= 0:
            msg = "colorspace_size must be positive"
            raise ValueError(msg)
        self._colorspace_size = value

    def generate(self, n: int) -> Palette:
        """Generate a color palette with n distinct colors.

        Parameters
        ----------
        n : int
            Number of colors to generate.

        Returns
        -------
        Palette
            A Palette object containing n Color objects.

        Raises
        ------
        RuntimeError
            If palette generation fails (e.g., C++ algorithm error).
        ValueError
            If n is not positive.
        TypeError
            If n is not an integer.

        Notes
        -----
        Behavior depends on input mode:

        - **colorspace mode**: Samples n colors from the continuous color space
        - **colors mode**: Selects n most distinct colors from the provided list
        - **palette mode**: Loads named palette and selects n most distinct colors
        """
        if not isinstance(n, int):
            msg = "n must be an integer"
            raise TypeError(msg)
        if n <= 0:
            msg = "n must be positive"
            raise ValueError(msg)

        # Determine input mode and call appropriate C++ function
        try:
            if self._colors is not None:
                # Colors mode: select from provided colors
                hex_colors = _qualpal.generate_palette_from_colors(
                    n=n, colors=list(self._colors)
                )
            elif self._palette is not None:
                # Palette mode: load named palette and select
                hex_colors = _qualpal.generate_palette_from_palette(
                    n=n, palette_name=self._palette
                )
            elif self._colorspace is not None:
                # Colorspace mode: sample from color space
                # Convert colorspace to C++ format
                if self._space == "hsl":
                    h_range = list(self._colorspace["h"])
                    c_range = list(self._colorspace["s"])  # saturation -> chroma
                    l_range = list(self._colorspace["l"])
                elif self._space == "lchab":
                    h_range = list(self._colorspace["h"])
                    c_range = list(self._colorspace["c"])
                    l_range = list(self._colorspace["l"])
                else:
                    msg = f"Unsupported color space: {self._space}"
                    raise RuntimeError(msg)

                hex_colors = _qualpal.generate_palette(
                    n=n, h_range=h_range, c_range=c_range, l_range=l_range
                )
            else:
                msg = "No input source available for generation"
                raise RuntimeError(msg)

        except ValueError as e:
            # Re-raise C++ validation errors with context
            msg = f"Palette generation failed: {e}"
            raise RuntimeError(msg) from e
        except Exception as e:
            # Catch any other C++ exceptions
            msg = f"Unexpected error during palette generation: {e}"
            raise RuntimeError(msg) from e

        # Convert hex strings to Color objects
        colors = [Color(hex_color) for hex_color in hex_colors]

        # Return Palette object
        return Palette(colors)
