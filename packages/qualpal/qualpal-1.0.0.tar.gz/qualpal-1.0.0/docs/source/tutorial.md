---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Tutorial: Getting Started with Qualpal

This tutorial demonstrates the main features of qualpal for generating and working with color palettes.

## Installation

```bash
pip install qualpal        # Core functionality
pip install qualpal[viz]   # With matplotlib visualization
```

## Basic Color Operations

Let's start by working with individual colors:

```{code-cell} ipython3
from qualpal import Color

# Create a color from hex
red = Color("#ff0000")
print(f"Hex: {red.hex()}")
print(f"RGB: {red.rgb()}")
print(f"RGB (0-255): {red.rgb255()}")
print(f"HSL: {red.hsl()}")
```

### Creating Colors from Different Formats

```{code-cell} ipython3
# From RGB (0-1 range)
green = Color.from_rgb(0.0, 1.0, 0.0)

# From HSL
blue_hsl = Color.from_hsl(240, 1.0, 0.5)

# Display the colors
print(f"Green: {green.hex()}")
print(f"Blue:  {blue_hsl.hex()}")
```

### Color Distance

Measure perceptual distance between colors using the CIEDE2000 metric:

```{code-cell} ipython3
color1 = Color("#ff0000")
color2 = Color("#ff6600")

distance = color1.distance(color2)
print(f"Distance between {color1.hex()} and {color2.hex()}: {distance:.2f}")
```

## Generating Palettes

Now let's generate color palettes with distinct colors:

```{code-cell} ipython3
from qualpal import Qualpal

# Create palette generator
qp = Qualpal()

# Generate 6 distinct colors
palette = qp.generate(6)

# Display as hex codes
print("Generated palette:")
for i, color in enumerate(palette, 1):
    print(f"  {i}. {color.hex()}")
```

### Customizing the Color Space

Restrict colors to specific ranges:

```{code-cell} ipython3
# Pastel colors (low saturation, high lightness)
qp_pastel = Qualpal(
    colorspace={
        'h': (0, 360),      # Full hue range
        's': (0.3, 0.6),    # Low saturation
        'l': (0.7, 0.9)     # High lightness
    }
)

pastel_palette = qp_pastel.generate(5)
print("Pastel palette:", pastel_palette.hex())
```

```{code-cell} ipython3
# Warm colors only
qp_warm = Qualpal(
    colorspace={
        'h': (-30, 90),     # Red to yellow
        's': (0.5, 1.0),
        'l': (0.4, 0.7)
    }
)

warm_palette = qp_warm.generate(5)
print("Warm palette:", warm_palette.hex())
```

## Working with Palettes

Palettes are collections of colors with useful methods:

```{code-cell} ipython3
from qualpal import Palette

# Create palette from hex colors
pal = Palette(["#ff0000", "#00ff00", "#0000ff", "#ffff00"])

# Access colors by index
first_color = pal[0]
print(f"First color: {first_color.hex()}")

# Iterate over colors
print("\nAll colors:")
for i, color in enumerate(pal):
    print(f"  {i}: {color.hex()}")

# Get length
print(f"\nPalette size: {len(pal)}")
```

### Palette Analysis

```{code-cell} ipython3
# Minimum pairwise distance
min_dist = pal.min_distance()
print(f"Minimum distance: {min_dist:.2f}")

# Distance to each nearest neighbor
min_dists = pal.min_distances()
print(f"Distances: {[f'{d:.2f}' for d in min_dists]}")

# Full distance matrix
matrix = pal.distance_matrix()
print(f"\nDistance matrix shape: {len(matrix)}x{len(matrix[0])}")
print(f"Distance from color 0 to color 1: {matrix[0][1]:.2f}")
```

## Exporting Palettes

Export palettes in various formats:

```{code-cell} ipython3
# CSS custom properties
css = pal.to_css(prefix="brand")
print("CSS variables:")
for decl in css:
    print(f"  {decl}")
```

```{code-cell} ipython3
# JSON format
import json
json_str = pal.to_json()
print(f"JSON: {json_str}")

# Can be used in configs
config = {
    "theme": {
        "colors": json.loads(json_str)
    }
}
print(f"\nConfig: {config}")
```

## Visualization

Visualize palettes with matplotlib:

```{code-cell} ipython3
:tags: [skip-execution]

# Display color swatches
fig = pal.show()

# With hex labels
fig = pal.show(labels=True)

# With custom labels
fig = pal.show(labels=["Primary", "Success", "Info", "Warning"])

# Save to file
fig.savefig("palette.png", dpi=150, bbox_inches='tight')
```

## Color Vision Deficiency (CVD) Simulation

Simulate how colors appear to people with color vision deficiency:

```{code-cell} ipython3
original = Color("#ff0000")

# Simulate different types of CVD
protan = original.simulate_cvd("protan", severity=1.0)
deutan = original.simulate_cvd("deutan", severity=1.0)
tritan = original.simulate_cvd("tritan", severity=1.0)

print(f"Original:     {original.hex()}")
print(f"Protanopia:   {protan.hex()}")
print(f"Deuteranopia: {deutan.hex()}")
print(f"Tritanopia:   {tritan.hex()}")
```

### CVD-Aware Palette Generation

Generate palettes that remain distinguishable with CVD:

```{code-cell} ipython3
# Generate palette considering deuteranomaly
qp_cvd = Qualpal(
    cvd={'deutan': 0.7}  # 70% severity deuteranomaly
)

cvd_palette = qp_cvd.generate(5)
print("CVD-aware palette:", cvd_palette.hex())

# Verify minimum distance
print(f"Min distance: {cvd_palette.min_distance():.2f}")
```

## Advanced: Custom Background Colors

Generate palettes optimized for specific backgrounds:

```{code-cell} ipython3
# Dark background
qp_dark = Qualpal(background="#1a1a1a")
dark_palette = qp_dark.generate(4)

print("Palette for dark background:")
print(dark_palette.hex())
```

```{code-cell} ipython3
# Light background
qp_light = Qualpal(background="#ffffff")
light_palette = qp_light.generate(4)

print("Palette for light background:")
print(light_palette.hex())
```

## Complete Example: Accessible Data Visualization Palette

Let's create a complete palette suitable for accessible data visualization:

```{code-cell} ipython3
# Requirements:
# - 8 distinct colors
# - Work on white background
# - Safe for deuteranomaly (most common CVD)
# - Avoid very light or very dark colors

qp_accessible = Qualpal(
    colorspace={
        'h': (0, 360),
        's': (0.4, 0.9),
        'l': (0.3, 0.7)
    },
    background="#ffffff",
    cvd={'deutan': 0.5}
)

accessible_palette = qp_accessible.generate(8)

print("Accessible visualization palette:")
for i, color in enumerate(accessible_palette, 1):
    rgb = color.rgb255()
    print(f"  {i}. {color.hex()}  RGB{rgb}")

print(f"\nMinimum distance: {accessible_palette.min_distance():.2f}")
print("(Higher is better - minimum recommended: 30)")
```

## Summary

Key features demonstrated:

- ✅ Create and convert colors between formats (hex, RGB, HSL, LAB, LCH)
- ✅ Measure perceptual color distances
- ✅ Generate palettes with distinct colors
- ✅ Customize color space constraints
- ✅ Analyze palette quality
- ✅ Export in various formats (CSS, JSON)
- ✅ Visualize with matplotlib
- ✅ Simulate color vision deficiency
- ✅ Generate CVD-aware palettes
- ✅ Optimize for specific backgrounds

For more details, see the [API documentation](api.md).
