# colorswan

**colorswan** is a precision color conversion library for Python, focused on converting sRGB to the perceptual color spaces **Oklab** and **Oklch**.

It provides accurate conversions using standard white points and matrices, suitable for color science, data visualization, and web design applications.

## Installation

```bash
pip install colorswan
```

## Usage

### Basic Conversion (Hex to Oklab/Oklch)

```python
from colorswan import OkColor

converter = OkColor()

# Convert from Hex (returns Oklab object by default)
result = converter.convert("#FF0000") 
print(result.L) 
# 0.6279...

# Request Oklch explicitly
oklch = converter.convert("#FF0000", return_type="oklch")
print(oklch.h)
# 29.23...

# Request both (legacy behavior)
all_results = converter.convert("#FF0000", return_type="all")
print(all_results['oklab'].L)
```

### Tuple Input

You can also pass RGB tuples (0-255).

```python
# Convert from RGB Tuple
white = converter.convert((255, 255, 255))
print(white.L)
# 1.0
```

### Using Constants

The library exposes standard color matrices and white points.

```python
from colorswan import constants

print(constants.WHITE_POINT_D65)
# (0.95047, 1.0, 1.08883)
```

## Features
- **Accurate**: Implements the official Oklab matrices (sRGB -> Linear -> XYZ -> LMS -> Oklab).
- **Zero Dependencies**: Pure Python implementation.
- **Easy to Use**: Simple API for common color tasks.

## License
MIT
