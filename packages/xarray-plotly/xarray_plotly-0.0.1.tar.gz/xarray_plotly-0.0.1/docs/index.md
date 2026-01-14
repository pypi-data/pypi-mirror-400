# xarray_plotly

**Interactive Plotly Express plotting accessor for xarray**

xarray_plotly provides interactive plotting for xarray DataArray objects using Plotly Express. It automatically assigns dimensions to plot slots based on their order, making it easy to create rich, interactive visualizations with minimal code.

## Features

- **Interactive plots**: Zoom, pan, hover for values, toggle traces - all built-in
- **Automatic dimension assignment**: Dimensions fill plot slots (x, color, facet_col, etc.) by position
- **Easy customization**: Returns Plotly `Figure` objects for further modification
- **Multiple plot types**: Line, bar, area, scatter, box, and heatmap plots
- **Faceting and animation**: Built-in support for subplot grids and animated time series
- **Full IDE support**: The `xpx()` function provides complete code completion and type hints

## Quick Example

```python
import xarray as xr
import numpy as np
from xarray_plotly import xpx

# Create sample data
da = xr.DataArray(
    np.random.randn(100, 3, 2),
    dims=["time", "city", "scenario"],
    coords={
        "time": np.arange(100),
        "city": ["NYC", "LA", "Chicago"],
        "scenario": ["baseline", "warming"],
    },
    name="temperature",
)

# Create an interactive line plot
# Dimensions auto-assign: time->x, city->color, scenario->facet_col
fig = xpx(da).line()
fig.show()

# Easy customization
fig.update_layout(
    title="Temperature Projections",
    template="plotly_dark",
)
```

## Usage Styles

xarray_plotly supports two equivalent usage styles:

```python
# Function style (recommended) - full IDE code completion
from xarray_plotly import xpx
fig = xpx(da).line()

# Accessor style - works but no IDE completion
import xarray_plotly
fig = da.plotly.line()
```

The `xpx()` function is recommended as it provides full IDE code completion and type hints.

**Why no IDE completion for the accessor?** xarray accessors are registered dynamically at runtime using `register_dataarray_accessor()`. Python's static type checkers and IDEs cannot see these dynamically added attributes, so `da.plotly` appears as an unknown attribute. This limitation could only be solved by xarray itself (e.g., through a type checker plugin), if at all. The `xpx()` function provides a workaround with an explicit return type that IDEs can follow.

## Installation

```bash
pip install xarray_plotly
```

Or with uv:

```bash
uv add xarray_plotly
```

## Why xarray_plotly?

The current `.plot` accessor in xarray is built on matplotlib, which has limitations for modern data exploration:

1. **Static outputs**: Matplotlib plots are non-interactive
2. **Post-creation modification is cumbersome**: Requires understanding complex object hierarchies
3. **Multi-dimensional data**: No built-in support for faceting or animation

xarray_plotly solves these with Plotly Express, providing:

- Interactive plots with zero additional code
- Simple, predictable dimension-to-slot assignment
- Easy post-creation customization via Plotly's `Figure` API
- Modern visualization patterns (faceting, animation) built-in
