import math
from typing import Tuple, Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.waves.parallel_sin.parameters import generate_random_sine_waves_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_sine_waves(
        image: Image.Image,
        area_size: Optional[Tuple[int, int]] = None,
        spacing: int = 30,
        thickness: float = 2,
        amplitude: float = 40,
        frequency: float = 0.01,
        angle: float = 45,
        color: ColorUnion = (0, 0, 0, 255),
) -> None:
    """
    Draw a set of parallel sine waves at a given rotation into a context.
    """
    color = to_hsluv_color(color)

    if area_size is None:
        area_size = image.size

    draw = aggdraw.Draw(image)
    width, height = area_size
    pen = aggdraw.Pen(color.to_rgba(), thickness)

    rad = math.radians(angle)
    cx, cy = width / 2.0, height / 2.0

    diagonal = int(math.sqrt(width ** 2 + height ** 2))

    for d in range(-diagonal, diagonal + int(spacing), int(spacing)):
        pts = []

        for x_virtual in range(-diagonal, diagonal + 1, 2):
            y_virtual = amplitude * math.sin(frequency * x_virtual) + d

            nx = x_virtual * math.cos(rad) - y_virtual * math.sin(rad) + cx
            ny = x_virtual * math.sin(rad) + y_virtual * math.cos(rad) + cy

            pts.extend([nx, ny])

        if len(pts) > 3:
            draw.line(pts, pen)

    draw.flush()


def paint_random_sine_waves(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        area_size: Union[Tuple[int, int], Default, Random] = Default,
        spacing: Union[int, Default, Random] = Default,
        thickness: Union[float, Default, Random] = Default,
        amplitude: Union[float, Default, Random] = Default,
        frequency: Union[float, Default, Random] = Default,
        angle: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "area_size": area_size,
        "spacing": spacing,
        "thickness": thickness,
        "amplitude": amplitude,
        "frequency": frequency,
        "angle": angle,
        "color": color,
    })

    parameters = generate_random_sine_waves_parameters(img, primary_color, color, area_size)

    parameters = parameters | passed_values
    paint_sine_waves(img, **parameters)
