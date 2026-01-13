# Quaternary Plots

A Python library for creating beautiful quaternary (tetrahedral) compositional plots using Plotly.

## Installation

```bash
pip install quaternary-plots
```

## Quick Start

```python
import quaternary as quat
import numpy as np

# Create empty tetrahedron
fig = quat.tetrahedron(labels=['CaCO3', 'MgCO3', 'Na2CO3', 'K2CO3'])

# Add data points
compositions = np.array([
    [25, 25, 25, 25],  # Centroid
    [50, 30, 10, 10],  # Ca-rich
])
fig = quat.add_points(fig, compositions, name='Samples', color='red')

fig.show()
```

## Features

- 🎯 Plot quaternary compositional diagrams
- 📊 Add points, lines, surfaces, and volumes
- 🔄 Convert between barycentric and Cartesian coordinates
- 🎨 Fully customizable colors, sizes, and styles
- 📱 Interactive 3D visualization

## Documentation

See [examples/basic_usage.py](examples/basic_usage.py) for more examples.

## License

GPL-3.0
