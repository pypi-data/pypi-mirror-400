---
file_format: mystnb
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.0
kernelspec:
  name: python3
---

# Qualpal

```{toctree}
:maxdepth: 2
:hidden:
:caption: Contents

Home<self>
getting_started
colors
api
changelog
```

## Automatically Generate Qualitative Color Palettes

Qualpal automatically generates qualitative color palettes with distinct, perceptually uniform colors.
It uses sophisticated algorithms based on perceptual color difference metrics
to ensure that the colors in the palette are easily distinguishable from each
other.

## Installation

Qualpal is on PyPi and can be installed via pip:

```bash
pip install qualpal
```

If you want visualization support (requires matplotlib), install with:

```bash
pip install qualpal[viz]
```

## Quick Start

As a quick example, here's how to generate a palette with 6 distinct colors:

```{code-cell} ipython3
from qualpal import Qualpal

# Generate a palette with 6 distinct colors
qp = Qualpal()
palette = qp.generate(6)

palette
```

## Features

- Automatic selection of color palettes using perceptual color difference metrics
- Color vision deficiency simulation for accessible palette design
- Multiple input formats: RGB values, hex strings, HSL ranges, built-in palettes
- Fast algorithms for large color spaces

## Web App

If you simply want to generate color palettes without coding or want to see
what Qualpal has to offer at a glance, check out the [Qualpal web
app](https://qualpal.cc).

## Citation

Qualpal is based on the [C++ library with the same name](https:/github.com/jolars/qualpal).
If you happen to use qualpal in your research, please cite the following paper:

> Larsson, J. (2025). Qualpal: Qualitative Color Palettes for Everyone.
> _Journal of Open Source Software_, 10(114), 8936.
> [https://doi.org/10.21105/joss.08936](https://doi.org/10.21105/joss.08936)

Here's an example BibTeX entry:

:::{note}
:class: dropdown

```bibtex
@article{
    Larsson2025,
    doi = {10.21105/joss.08936},
    url = {https://doi.org/10.21105/joss.08936},
    year = {2025},
    month = {oct},
    publisher = {The Open Journal},
    volume = {10},
    number = {114},
    pages = {8936},
    author = {Larsson, Johan},
    title = {Qualpal: Qualitative Color Palettes for Everyone},
    journal = {Journal of Open Source Software}
}
```

:::

## License

MIT License - see [LICENSE](https://github.com/jolars/qualpal-py/blob/main/LICENSE)

## Installation From Source

If you want to install the latest development version, you can install directly from the GitHub repository.

```bash
uv pip install git+https://github.com/jolars/qualpal-py
```

**Requirements:**

- Python 3.9+
- C++ compiler (for building the extension)
- CMake 3.15+

## References

Based on the qualpal C++ library: https://github.com/jolars/qualpal
