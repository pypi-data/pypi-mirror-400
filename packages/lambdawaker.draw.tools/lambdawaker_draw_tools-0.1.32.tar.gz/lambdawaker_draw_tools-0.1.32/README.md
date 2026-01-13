lambda-draw-tools

Drawing utilities for generating geometric patterns, grids, and wave-based line art using Pillow and aggdraw.

Install

```
pip install lambda-draw-tools
```

Quick start

Hexagon grid

```python
from lambdawaker.draw.grid.hexagon_grid import create_hexagon_grid

img = create_hexagon_grid(
    width=600,
    height=600,
    hexagon_size=40,
    thickness=2,
    angle=0,
    color="#4B0082",
    bg_color=(255, 255, 255, 0),
)
img.show()
```

Angled parallel lines

```python
from lambdawaker.draw.waves.parallel_lines import create_parallel_lines

img = create_parallel_lines(
    width=800,
    height=600,
    spacing=24,
    thickness=2,
    angle=35,
    color="midnightblue",
    bg_color=(255, 255, 255, 0),
)
img.show()
```

Project Structure

The project is organized into several packages under `lambdawaker.draw`, each serving a specific purpose:

- **`lambdawaker.draw.grid`**: Contains functions to generate grid-based patterns.
  - `shapes_grid.py`: Creates grids of arbitrary shapes (circles, squares, etc.).
  - `hexagon_grid.py`: Generates hexagonal tiling grids.
  - `traingles_grid.py`: Generates equilateral triangle tiling grids.
  - `concentric_polygins.py`: Draws concentric polygons.
  - `simple_shapes.py`: Helper functions for drawing basic shapes like circles, squares, triangles, polygons, and stars.

- **`lambdawaker.draw.waves`**: Provides tools for drawing wave-like patterns.
  - `parallel_lines.py`: Draws parallel lines at a specified angle.
  - `parallel_sin.py`: Draws parallel sine waves.
  - `square_wave.py`: Draws parallel square waves.
  - `parallel_sawtooth.py`: Draws parallel sawtooth waves.

- **`lambdawaker.draw.header`**: Utilities for creating image headers with decorative bottom edges.
  - `sin_header.py`: Header with a sine-wave bottom edge.
  - `curved_header.py`: Header with a curved bottom edge.
  - `square_header.py`: Simple rectangular header.

- **`lambdawaker.draw.color`**: Color manipulation and generation tools.
  - `HSLuvColor.py`: A class for handling colors in the HSLuv color space.
  - `generate_color.py`: Functions for generating random colors.
  - `generate_from_color.py`: Functions for generating color palettes (complementary, triadic, etc.) from a base color.
  - `visualization.py`: Tools for visualizing color palettes.
  - `utils.py`: Utility functions for color math and parsing.

- **`lambdawaker.draw.shapes`**:
  - `concentric.py`: Contains `rotating_polygons` for drawing concentric rotating polygons.

Requirements

- Python 3.8+
- Pillow >= 9.0
- aggdraw >= 1.3.16.post1

Notes

- On some platforms, `aggdraw` may require build tools if a prebuilt wheel isn’t available.
- The library exposes convenience creators like `create_hexagon_grid` and `create_parallel_lines`, as well as lower-level `draw_*` functions that render into an existing `aggdraw.Draw` context.
