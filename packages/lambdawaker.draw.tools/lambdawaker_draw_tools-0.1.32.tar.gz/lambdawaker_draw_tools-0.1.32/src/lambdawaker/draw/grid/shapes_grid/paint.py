import math
from typing import Callable, Dict, Optional, Tuple, Union

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.shapes_grid.parameters import generate_random_shapes_grid_parameters
from lambdawaker.draw.shapes.simple_shapes import circle
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_shapes_grid(
        image: Image.Image,
        size: Optional[Tuple[int, int]] = None,
        radius: float = 15,
        draw_function: Optional[Callable] = None,
        draw_parameters: Optional[Dict] = None,
        separation: float = 0,
        angle: float = 0,
        thickness: float = 2,
        color: ColorUnion = (0, 0, 0, 255),
        outline: ColorUnion = (0, 0, 0, 255)
) -> None:
    """Draw a staggered grid of shapes into an existing image."""
    color = to_hsluv_color(color)
    outline = to_hsluv_color(outline)

    draw_function = draw_function if draw_function is not None else circle
    draw_parameters = draw_parameters if draw_parameters is not None else {}

    if size is None:
        size = image.size

    width, height = size

    draw = aggdraw.Draw(image)
    brush = aggdraw.Brush(color.to_rgba())
    pen = aggdraw.Pen(outline.to_rgba(), thickness)

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
                draw_function(draw, (rot_x, rot_y), radius, angle, pen, brush, **draw_parameters)

    draw.flush()


def paint_random_shapes_grid(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        outline: Optional[ColorUnion] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        radius: Union[float, Default, Random] = Default,
        draw_function: Union[Callable, Default, Random] = Default,
        draw_parameters: Union[Dict, Default, Random] = Default,
        separation: Union[float, Default, Random] = Default,
        angle: Union[float, Default, Random] = Default,
        thickness: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "size": size,
        "radius": radius,
        "draw_function": draw_function,
        "draw_parameters": draw_parameters,
        "separation": separation,
        "angle": angle,
        "thickness": thickness,
        "color": color,
        "outline": outline,
    })

    parameters = generate_random_shapes_grid_parameters(img, primary_color, color, outline, size)

    parameters = parameters | passed_values
    paint_shapes_grid(img, **parameters)
