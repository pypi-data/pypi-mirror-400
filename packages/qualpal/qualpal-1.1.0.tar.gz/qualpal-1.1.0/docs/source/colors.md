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

# Colors

Qualpal features a full-fledged color class for working with colors,
measuring perceptual distances, and simulating color vision deficiencies.

## Basic Color Operations

Let's start by working with individual colors:

```{code-cell} ipython3
from qualpal import Color, Palette

# Create a color from hex
red = Color("#ff0000")

print(f"Hex: {red.hex()}")
print(f"RGB: {red.rgb()}")
print(f"RGB (0-255): {red.rgb255()}")
print(f"HSL: {red.hsl()}")

red
```

As you can see, the `Color` class supports multiple color formats and
provides easy conversion between them. It also has a rich HTML
representation for Jupyter notebooks.

### Creating Colors from Different Formats

Colors can be created from various formats:

```{code-cell} ipython3
# From RGB (0-1 range)
green = Color.from_rgb(0.0, 1.0, 0.0)

# From HSL
blue_hsl = Color.from_hsl(240, 1.0, 0.5)

Palette([red, green, blue_hsl])
```

And as you can see above, these colors can be combined into a
`Palette` for easy visualization.

## Color Distance

A key feature of Qualpal is measuring perceptual color differences,
which is used in the palette generation algorithm. You can compute
the distance between two colors like this:

```{code-cell} ipython3
color1 = Color("#ff0000")
color2 = Color("#ff6600")

color1.distance(color2)
```

## Color Vision Deficiency (CVD) Simulation

We also expose methods to simulate how colors appear to individuals
with different types of color vision deficiencies:

```{code-cell} ipython3
original = Color("#ff0000")

# Simulate different types of CVD
protan = original.simulate_cvd("protan", severity=1.0)
deutan = original.simulate_cvd("deutan", severity=1.0)
tritan = original.simulate_cvd("tritan", severity=1.0)

Palette([original, protan, deutan, tritan])
```

For more details, see the [API documentation](api.md).
