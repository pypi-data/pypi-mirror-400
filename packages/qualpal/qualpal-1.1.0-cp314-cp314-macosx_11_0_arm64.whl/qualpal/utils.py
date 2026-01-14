"""Utility functions for qualpal."""

from __future__ import annotations

import _qualpal

from qualpal.palette import Palette


def list_palettes() -> dict[str, list[str]]:
    """List all available named color palettes.

    Returns
    -------
    dict[str, list[str]]
        Dictionary mapping package names to lists of palette names.
        Use these names with the format "package:palette" when creating
        a Qualpal object.

    Examples
    --------
    >>> from qualpal import list_palettes
    >>> palettes = list_palettes()
    >>> print(palettes.keys())
    dict_keys(['ColorBrewer', 'Pokemon', 'Ochre', ...])
    >>> print(palettes['ColorBrewer'][:3])
    ['Accent', 'Blues', 'BrBG']

    >>> # Use with Qualpal
    >>> from qualpal import Qualpal
    >>> qp = Qualpal(palette='ColorBrewer:Set2')
    >>> pal = qp.generate(5)
    """
    return _qualpal.list_palettes()


def get_palette(name: str) -> Palette:
    """Get a specific named color palette.

    Parameters
    ----------
    name : str
        Palette name in format "package:palette" (e.g., "ColorBrewer:Set2").
        Use `list_palettes()` to see available options.

    Returns
    -------
    Palette
        A Palette object containing all colors from the named palette.

    Raises
    ------
    ValueError
        If palette name is not in "package:palette" format.
    RuntimeError
        If palette name is not found or cannot be loaded.

    Examples
    --------
    >>> from qualpal import get_palette
    >>> palette = get_palette("ColorBrewer:Set2")
    >>> len(palette)
    8
    >>> palette[0].hex()
    '#66c2a5'

    >>> # Display the palette
    >>> palette.show()  # doctest: +SKIP
    """
    if ":" not in name:
        msg = f"Palette name must be in format 'package:palette', got: {name}"
        raise ValueError(msg)

    hex_colors = _qualpal.get_palette(name)
    return Palette(hex_colors)
