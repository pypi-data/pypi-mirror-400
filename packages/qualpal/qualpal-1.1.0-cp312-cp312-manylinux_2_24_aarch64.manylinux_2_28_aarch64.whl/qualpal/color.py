"""Color class."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import _qualpal

if TYPE_CHECKING:
    from typing_extensions import Self


class Color:
    """A color with various representations and conversions.

    Color objects are immutable.
    """

    def __init__(self, hex_color: str) -> None:
        """Create a Color from a hex string.

        Parameters
        ----------
        hex_color : str
            Hex color string in format #RRGGBB

        Raises
        ------
        ValueError
            If hex_color is not a valid hex color string
        """
        # Validate format
        if not re.match(r"^#[0-9a-fA-F]{6}$", hex_color):
            msg = f"Invalid hex color format: {hex_color}"
            raise ValueError(msg)

        self._hex = hex_color.lower()

        # Parse RGB values (0-1 range)
        r_int = int(self._hex[1:3], 16)
        g_int = int(self._hex[3:5], 16)
        b_int = int(self._hex[5:7], 16)

        self._r = r_int / 255.0
        self._g = g_int / 255.0
        self._b = b_int / 255.0

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float) -> Self:
        """Create a Color from RGB values.

        Parameters
        ----------
        r, g, b : float
            RGB values in range [0.0, 1.0]

        Returns
        -------
        Color
            New Color object
        """
        # Validate range
        if not (0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0):
            msg = "RGB values must be in range [0.0, 1.0]"
            raise ValueError(msg)

        # Convert to hex
        r_int = round(r * 255)
        g_int = round(g * 255)
        b_int = round(b * 255)

        hex_str = f"#{r_int:02x}{g_int:02x}{b_int:02x}"

        return cls(hex_str)

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float) -> Self:
        """Create a Color from HSL values.

        Parameters
        ----------
        h : float
            Hue in degrees [0.0, 360.0)
        s : float
            Saturation in range [0.0, 1.0]
        l : float
            Lightness in range [0.0, 1.0]

        Returns
        -------
        Color
            New Color object
        """
        # Convert HSL to RGB using C++ library
        r, g, b = _qualpal.hsl_to_rgb(h, s, l)
        return cls.from_rgb(r, g, b)

    def hex(self) -> str:
        """Get hex representation.

        Returns
        -------
        str
            Hex color string in format #rrggbb (lowercase)
        """
        return self._hex

    def rgb(self) -> tuple[float, float, float]:
        """Get RGB tuple in range [0.0, 1.0].

        Returns
        -------
        tuple[float, float, float]
            RGB values as (r, g, b)
        """
        return (self._r, self._g, self._b)

    def rgb255(self) -> tuple[int, int, int]:
        """Get RGB tuple in range [0, 255].

        Returns
        -------
        tuple[int, int, int]
            RGB values as (r, g, b) integers
        """
        return (
            round(self._r * 255),
            round(self._g * 255),
            round(self._b * 255),
        )

    def hsl(self) -> tuple[float, float, float]:
        """Get HSL tuple.

        Returns
        -------
        tuple[float, float, float]
            HSL values as (h, s, l) where h is in degrees [0, 360)
            and s, l are in range [0.0, 1.0]
        """
        h, s, l = _qualpal.rgb_to_hsl(self._r, self._g, self._b)
        return (h, s, l)

    def xyz(self) -> tuple[float, float, float]:
        """Get XYZ tuple.

        Returns
        -------
        tuple[float, float, float]
            XYZ values as (x, y, z)
        """
        x, y, z = _qualpal.rgb_to_xyz(self._r, self._g, self._b)
        return (x, y, z)

    def lab(self) -> tuple[float, float, float]:
        """Get Lab tuple.

        Returns
        -------
        tuple[float, float, float]
            Lab values as (l, a, b) where l is in range [0, 100]
            and a, b are in range [-128, 127]
        """
        l, a, b = _qualpal.rgb_to_lab(self._r, self._g, self._b)
        return (l, a, b)

    def lch(self) -> tuple[float, float, float]:
        """Get LCH tuple.

        Returns
        -------
        tuple[float, float, float]
            LCH values as (l, c, h) where l is in range [0, 100],
            c is chroma [0, ∞), and h is hue in degrees [0, 360)
        """
        l, c, h = _qualpal.rgb_to_lch(self._r, self._g, self._b)
        return (l, c, h)

    def distance(self, other: Color | str, metric: str = "ciede2000") -> float:
        """Calculate perceptual color difference to another color.

        Parameters
        ----------
        other : Color | str
            Another Color object or hex color string
        metric : str
            Distance metric to use. Options:
            - 'ciede2000' (default): CIEDE2000 metric
            - 'din99d': DIN99d metric
            - 'cie76': CIE76 (Euclidean distance in Lab space)

        Returns
        -------
        float
            Perceptual color difference

        Raises
        ------
        ValueError
            If metric is invalid or other color is not a valid color

        Examples
        --------
        >>> red = Color('#ff0000')
        >>> green = Color('#00ff00')
        >>> red.distance(green)
        86.61
        >>> red.distance('#00ff00', metric='din99d')
        32.77
        """
        # Convert other to Color if it's a string
        if isinstance(other, str):
            other = Color(other)

        # Call C++ function
        return _qualpal.color_difference(self._hex, other._hex, metric)

    def simulate_cvd(self, cvd_type: str, severity: float = 1.0) -> Color:
        """Simulate color vision deficiency on this color.

        Parameters
        ----------
        cvd_type : str
            Type of color vision deficiency:
            - 'protan': Protanomaly/Protanopia (red-weak/blind)
            - 'deutan': Deuteranomaly/Deuteranopia (green-weak/blind)
            - 'tritan': Tritanomaly/Tritanopia (blue-weak/blind)
        severity : float
            Severity of the deficiency in range [0, 1]:
            - 0.0: Normal vision (no change)
            - 1.0: Complete deficiency

        Returns
        -------
        Color
            New Color object showing how this color appears with CVD

        Raises
        ------
        ValueError
            If cvd_type is invalid or severity is out of range

        Examples
        --------
        >>> red = Color('#ff0000')
        >>> red_protan = red.simulate_cvd('protan', severity=1.0)
        >>> red_deutan = red.simulate_cvd('deutan', severity=0.5)
        """
        # Validate cvd_type
        valid_types = {"protan", "deutan", "tritan"}
        if cvd_type not in valid_types:
            msg = f"cvd_type must be one of {valid_types}, got '{cvd_type}'"
            raise ValueError(msg)

        # Validate severity
        if not isinstance(severity, (int, float)):
            msg = "severity must be a number"
            raise TypeError(msg)
        if not 0.0 <= severity <= 1.0:
            msg = f"severity must be in range [0, 1], got {severity}"
            raise ValueError(msg)

        # Call C++ function
        r_sim, g_sim, b_sim = _qualpal.simulate_cvd(
            self._r, self._g, self._b, cvd_type, severity
        )

        # Create new Color from simulated RGB
        return Color.from_rgb(r_sim, g_sim, b_sim)

    def __str__(self) -> str:
        """String representation (hex color)."""
        return self._hex

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Color('{self._hex}')"

    def _repr_html_(self) -> str:
        """Return HTML representation for Jupyter/IPython.

        Returns
        -------
        str
            HTML string with colored swatch and hex code
        """
        return (
            f'<div style="display: inline-flex; align-items: center; gap: 8px;">'
            f'<div style="width: 40px; height: 40px; background-color: {self._hex}; '
            f'border: 1px solid #333; border-radius: 4px;"></div>'
            f'<code style="font-family: monospace; font-size: 14px;">{self._hex}</code>'
            f"</div>"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another Color or hex string."""
        if isinstance(other, Color):
            return self._hex == other._hex

        if isinstance(other, str):
            # Normalize and compare
            try:
                other_color = Color(other)
                return self._hex == other_color._hex
            except ValueError:
                return False

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Check inequality."""
        result = self.__eq__(other)

        if result is NotImplemented:
            return result

        return not result

    def __hash__(self) -> int:
        """Hash based on hex value (for use in sets/dicts)."""
        return hash(self._hex)
