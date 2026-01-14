# Qualpal <picture><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/jolars/qualpal/refs/heads/main/docs/images/logo.svg" align="right" width="139"> <img alt="The logo for Qualpal, which is a painting palette with five distinct colors." src="https://raw.githubusercontent.com/jolars/qualpal/refs/heads/main/docs/images/logo-dark.svg" align="right" width="139"> </picture>

[![Tests](https://github.com/jolars/qualpal-py/actions/workflows/test.yml/badge.svg)](https://github.com/jolars/qualpal-py/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/jolars/qualpal-py/graph/badge.svg?token=VBIeMY0zJt)](https://codecov.io/github/jolars/qualpal-py)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.08936/status.svg)](https://doi.org/10.21105/joss.08936)
[![App](https://img.shields.io/badge/🌐%20%20App-qualpal.cc-blue)](https://qualpal.cc)

Automatically generate qualitative color palettes with distinct, perceptually uniform colors.

## Installation

Qualpal will soon be available on PyPI. In the meantime, you can install it directly from source,
but note that this requires a C++ compiler.

```bash
# Core functionality
pip install git+https://github.com/jolars/qualpal-py

# With visualization support
pip install git+https://github.com/jolars/qualpal-py[viz]
```

## Quick Start

```python
from qualpal import Qualpal

# Generate 6 distinct colors
qp = Qualpal()
palette = qp.generate(6)

# Display colors
print(palette.hex())
# ['#f68ec8', '#233604', '#15045a', '#13cbf6', '#ebf919', '#e84123']

# Export for CSS
css = palette.to_css(prefix="theme")
# ['--theme-1: #f68ec8;', '--theme-2: #233604;', ...]

# Visualize (requires matplotlib)
palette.show(labels=True)
```

## Key Features

- 🎨 **Smart Color Generation** - Automatically selects maximally distinct colors
- 🎯 **Customizable** - Control hue, saturation, lightness ranges
- ♿ **Accessible** - CVD (color vision deficiency) simulation and optimization
- 📊 **Analysis** - Measure perceptual distances between colors
- 📤 **Export** - CSS, JSON, and matplotlib visualization
- 📓 **Jupyter** - Rich HTML display in notebooks
- 🚀 **Fast** - C++ backend with Python interface

## Examples

### Customize Color Space

```python
# Pastel colors
qp = Qualpal(
    colorspace={
        'h': (0, 360),
        's': (0.3, 0.6),
        'l': (0.7, 0.9)
    }
)
pastels = qp.generate(5)
```

### CVD-Aware Palettes

```python
# Generate palette safe for deuteranomaly
qp = Qualpal(cvd={'deutan': 0.7})
accessible = qp.generate(6)
```

### Color Operations

```python
from qualpal import Color

# Create and convert colors
color = Color("#ff0000")
print(color.rgb())   # (1.0, 0.0, 0.0)
print(color.hsl())   # (0.0, 1.0, 0.5)
print(color.lab())   # (53.24, 80.09, 67.20)

# Measure perceptual distance
red = Color("#ff0000")
orange = Color("#ff6600")
distance = red.distance(orange)  # 33.42
```

## Documentation

The full documentation is available at <https://jolars.github.io/qualpal-py/>.

## Contributing

Contributions are welcome!

Note that the main functionality comes from the underlying C++ library,
which is developed and maintained at <https://github.com/jolars/qualpal>.
So if you want to contribute to the core algorithms, please do so there.

## License

Qualpal is licensed under the [MIT license](LICENSE)

## References

Larsson, J. (2024). qualpal: Automatic Generation of Qualitative Color Palettes. 
*Journal of Open Source Software*, 9(102), 8936. 
<https://doi.org/10.21105/joss.08936>
