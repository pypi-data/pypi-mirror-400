"""Utility functions for qualpal."""

from __future__ import annotations

import _qualpal


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
    return _qualpal.list_palettes_cpp()
