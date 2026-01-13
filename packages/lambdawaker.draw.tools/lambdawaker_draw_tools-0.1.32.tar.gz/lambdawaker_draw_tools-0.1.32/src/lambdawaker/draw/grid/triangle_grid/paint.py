import math
from typing import Tuple, Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.triangle_grid.parameters import generate_random_triangle_grid_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_triangle_grid(
        image: Image.Image,
        area_size: Optional[Tuple[int, int]] = None,
        size: float = 50,
        thickness: float = 2.0,
        angle: float = 0,
        color: ColorUnion = (0, 0, 0, 255),
) -> None:
    """
    Draw a tiling of equilateral triangles across a given area into an existing image.
    """
    color = to_hsluv_color(color)

    if area_size is None:
        area_size = image.size

    draw = aggdraw.Draw(image)
    width, height = area_size
    pen = aggdraw.Pen(color.to_rgba(), thickness)

    cx, cy = width / 2.0, height / 2.0
    rad = math.radians(angle)

    tri_height = (math.sqrt(3.0) / 2.0) * size
    horiz_dist = size / 2.0
    vert_dist = tri_height

    diagonal = int(math.sqrt(width ** 2 + height ** 2))

    def rot(px: float, py: float):
        nx = px * math.cos(rad) - py * math.sin(rad) + cx
        ny = px * math.sin(rad) + py * math.cos(rad) + cy
        return nx, ny

    col_range = int(diagonal // max(1.0, horiz_dist)) + 4
    row_range = int(diagonal // max(1.0, vert_dist)) + 4

    for row in range(-row_range, row_range + 1):
        for col in range(-col_range, col_range + 1):
            x_base = col * horiz_dist
            y_base = row * vert_dist

            is_up = ((row + col) % 2) == 0

            if is_up:
                verts = [
                    (x_base, y_base),
                    (x_base - size / 2.0, y_base + tri_height),
                    (x_base + size / 2.0, y_base + tri_height),
                ]
            else:
                verts = [
                    (x_base, y_base + tri_height),
                    (x_base - size / 2.0, y_base),
                    (x_base + size / 2.0, y_base),
                ]

            verts.append(verts[0])

            path = []
            for px, py in verts:
                path.extend(rot(px, py))

            draw.line(path, pen)

    draw.flush()


def paint_random_triangle_grid(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        area_size: Union[Tuple[int, int], Default, Random] = Default,
        size: Union[float, Default, Random] = Default,
        thickness: Union[float, Default, Random] = Default,
        angle: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "area_size": area_size,
        "size": size,
        "thickness": thickness,
        "angle": angle,
        "color": color,
    })

    parameters = generate_random_triangle_grid_parameters(img, primary_color, color, area_size)

    parameters = parameters | passed_values
    paint_triangle_grid(img, **parameters)
