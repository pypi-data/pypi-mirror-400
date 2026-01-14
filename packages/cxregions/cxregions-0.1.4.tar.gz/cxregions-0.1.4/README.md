# cxregions

This package is a Python interface to the [ComplexRegions.jl](https://github.com/complexvariables/ComplexRegions.jl) Julia package, providing tools for working with complex regions defined by paths and curves. It allows users to create, manipulate, and analyze geometric shapes such as circular polygons and general polygons using Julia's computational capabilities from within Python.

## Installation

To install the `cxregions` package, you can use pip:

```bash
pip install cxregions
```

The first time you import `cxregions`, it will set up a Julia environment and install the necessary Julia packages. This may take a few minutes.

## Usage

Here is a simple example of how to use the `cxregions` package:

```python
from cxregions import Polygon, Line, Arc

# Create curves
line1 = Line(0+0j, 2+2j)
print(line1.point(0.5))  # Should print 1+1j
arc1 = Arc(-1j, 1j, -1)
p = Polygon([4, 4 + 3j, 3j, -2j, 6 - 2j, 6])
print(p.winding(5 - 1j)) # Should print 1
```

Full documentation and examples can be found in the [ComplexRegions.jl documentation](https://complexvariables.github.io/ComplexRegions.jl/stable/). Most of the Julia methods shown there are members of the corresponding Python classes.