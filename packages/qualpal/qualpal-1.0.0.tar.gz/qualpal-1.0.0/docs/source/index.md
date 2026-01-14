# Qualpal

```{toctree}
:maxdepth: 2
:hidden:
:caption: Contents

Home<self>
tutorial
api
changelog
```

## Automatically Generate Qualitative Color Palettes

Qualpal automatically generates qualitative color palettes with distinct, perceptually uniform colors. It's perfect for:

- Data visualization
- Categorical plots
- Accessible color schemes
- Color vision deficiency (CVD) safe palettes

## Installation

```bash
pip install qualpal        # Core functionality
pip install qualpal[viz]   # With matplotlib visualization
```

## Quick Start

```python
from qualpal import Qualpal

# Generate a palette with 6 distinct colors
qp = Qualpal()
palette = qp.generate(6)

# Display colors
print(palette.hex())
# ['#f68ec8', '#233604', '#15045a', '#13cbf6', '#ebf919', '#e84123']

# Export for web development
css = palette.to_css(prefix="theme")
# ['--theme-1: #f68ec8;', '--theme-2: #233604;', ...]
```

## Key Features

### 🎨 **Color Operations**

```python
from qualpal import Color

# Create and convert colors
color = Color("#ff0000")
print(color.rgb())      # (1.0, 0.0, 0.0)
print(color.hsl())      # (0.0, 1.0, 0.5)
print(color.lab())      # (53.24, 80.09, 67.20)

# Measure perceptual distance
red = Color("#ff0000")
orange = Color("#ff6600")
distance = red.distance(orange)  # 33.42
```

### 🎯 **Smart Palette Generation**

```python
# Customize color space
qp = Qualpal(
    colorspace={
        'h': (20, 300),    # Hue range
        's': (0.3, 0.7),   # Saturation range
        'l': (0.7, 0.9)    # Lightness range
    }
)
pastel_palette = qp.generate(5)

# Optimize for backgrounds
qp_dark = Qualpal(background="#1a1a1a")
dark_palette = qp_dark.generate(4)
```

### ♿ **Accessibility First**

```python
# Simulate color vision deficiency
red = Color("#ff0000")
protan = red.simulate_cvd("protan", severity=1.0)

# Generate CVD-aware palettes
qp_accessible = Qualpal(cvd={'deutan': 0.7})
accessible_palette = qp_accessible.generate(6)
```

### 📊 **Palette Analysis**

```python
# Analyze palette quality
min_dist = palette.min_distance()  # Minimum pairwise distance
matrix = palette.distance_matrix()  # Full distance matrix
```

### 📤 **Export Formats**

```python
# CSS custom properties
css = palette.to_css(prefix="brand")
# ['--brand-1: #f68ec8;', ...]

# JSON
json_str = palette.to_json()
# '["#f68ec8", "#233604", ...]'

# Matplotlib visualization
fig = palette.show(labels=True)
fig.savefig("palette.png")
```

### 📓 **Jupyter Integration**

Rich HTML display automatically shows color swatches in notebooks:

```python
color  # Shows: [swatch] #ff0000
palette  # Shows: [swatch1] [swatch2] [swatch3]
```

## Learn More

- **[Tutorial](tutorial.md)** - Comprehensive guide with examples
- **[API Reference](api.md)** - Complete API documentation
- **[Changelog](changelog.md)** - Version history

## References

Based on the qualpal algorithm:

- Larsson, J. (2024). qualpal: Automatic Generation of Qualitative Color Palettes. 
  *Journal of Open Source Software*, 9(102), 8936. 
  [https://doi.org/10.21105/joss.08936](https://doi.org/10.21105/joss.08936)

## License

MIT License - see [LICENSE](https://github.com/jolars/qualpal-py/blob/main/LICENSE)

## Installation

**Requirements:**
- Python 3.9+
- C++ compiler (for building the extension)
- CMake 3.15+

```bash
# Install from source
git clone https://github.com/jolars/qualpal-py.git
cd qualpal-py
uv pip install -e .
```

## Development Status

See [ROADMAP.md](https://github.com/jolars/qualpal-py/blob/main/ROADMAP.md) for current implementation status.

**Completed:**
- ✅ Phase 1.1: Color class (pure Python)

**In Progress:**
- 🚧 Phase 1.2: Color space conversions
- 🚧 Phase 1.3: Palette class
- 🚧 Phase 2: Core generation algorithm

## Architecture

This package uses a **Python-first architecture**:
- **Python layer**: API, data structures, validation
- **C++ layer**: Performance-critical algorithms only

## References

Based on the qualpal C++ library: https://github.com/jolars/qualpal

