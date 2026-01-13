import math
from typing import Optional, Tuple, Union

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.dots_grid.parameters import generate_random_dots_grid_parameters
from lambdawaker.draw.shapes.simple_shapes import circle
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_dots_grid(
        image: Image.Image,
        size: Optional[Tuple[int, int]] = None,
        radius: float = 2,
        separation: float = 10,
        angle: float = 0,
        color: ColorUnion = (0, 0, 0, 255),
) -> None:
    """Draw a staggered grid of dots into an existing image."""
    color = to_hsluv_color(color)

    if size is None:
        size = image.size

    width, height = size

    draw = aggdraw.Draw(image)
    brush = aggdraw.Brush(color.to_rgba())
    pen = aggdraw.Pen(color.to_rgba(), 0)

    eff_r = radius + (separation / 2)
    h_spacing = eff_r * 2
    v_spacing = eff_r * math.sqrt(3)

    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    cx, cy = width / 2, height / 2

    limit = int(max(width, height) / radius) + 10

    for row in range(-limit, limit):
        for col in range(-limit, limit):
            grid_x = col * h_spacing
            if row % 2 == 1:
                grid_x += eff_r
            grid_y = row * v_spacing

            rot_x = grid_x * cos_a - grid_y * sin_a + cx
            rot_y = grid_x * sin_a + grid_y * cos_a + cy

            buffer = radius * 2
            if -buffer < rot_x < width + buffer and -buffer < rot_y < height + buffer:
                circle(draw, (rot_x, rot_y), radius, angle, pen, brush)

    draw.flush()


def paint_random_dots_grid(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        radius: Union[float, Default, Random] = Default,
        separation: Union[float, Default, Random] = Default,
        angle: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "size": size,
        "radius": radius,
        "separation": separation,
        "angle": angle,
        "color": color,
    })

    parameters = generate_random_dots_grid_parameters(img, primary_color, color, size)

    parameters = parameters | passed_values
    paint_dots_grid(img, **parameters)
