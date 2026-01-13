import math
from typing import Tuple, Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.waves.parallel_lines.parameters import generate_random_parallel_lines_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_parallel_lines(
        image: Image.Image,
        area_size: Optional[Tuple[int, int]] = None,
        spacing: int = 20,
        thickness: float = 2,
        angle: float = 45,
        color: ColorUnion = (0, 0, 0, 255),
) -> None:
    """
    Draw a set of equally spaced, parallel lines at a given angle into an existing image.
    """
    color = to_hsluv_color(color)

    if area_size is None:
        area_size = image.size

    draw = aggdraw.Draw(image)
    width, height = area_size
    pen = aggdraw.Pen(color.to_rgba(), thickness)

    radians = math.radians(angle)

    diagonal = int(math.sqrt(width ** 2 + height ** 2))

    for d in range(-diagonal, diagonal * 2, int(spacing)):
        x0 = d * math.cos(radians + math.pi / 2) - diagonal * math.cos(radians)
        y0 = d * math.sin(radians + math.pi / 2) - diagonal * math.sin(radians)
        x1 = d * math.cos(radians + math.pi / 2) + diagonal * math.cos(radians)
        y1 = d * math.sin(radians + math.pi / 2) + diagonal * math.sin(radians)

        draw.line((x0, y0, x1, y1), pen)

    draw.flush()


def paint_random_parallel_lines(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        area_size: Union[Tuple[int, int], Default, Random] = Default,
        spacing: Union[int, Default, Random] = Default,
        thickness: Union[float, Default, Random] = Default,
        angle: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "area_size": area_size,
        "spacing": spacing,
        "thickness": thickness,
        "angle": angle,
        "color": color,
    })

    parameters = generate_random_parallel_lines_parameters(img, primary_color, color, area_size)

    parameters = parameters | passed_values
    paint_parallel_lines(img, **parameters)
