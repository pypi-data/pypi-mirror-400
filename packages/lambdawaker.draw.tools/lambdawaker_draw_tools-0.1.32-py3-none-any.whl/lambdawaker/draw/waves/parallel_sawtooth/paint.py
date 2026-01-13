import math
from typing import Tuple, Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.waves.parallel_sawtooth.parameters import generate_random_sawtooth_wave_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_angled_sawtooth_waves(
        image: Image.Image,
        area_size: Optional[Tuple[int, int]] = None,
        spacing: int = 50,
        thickness: float = 2,
        amplitude: float = 25,
        wavelength: float = 80,
        angle: float = 0,
        color: ColorUnion = (0, 0, 0, 255),
) -> None:
    """
    Draw a set of parallel sawtooth waves at a given rotation into a context.
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

    step = max(1, int(round(wavelength / 2.0)))

    for d in range(-diagonal, diagonal + int(spacing), int(spacing)):
        pts = []

        for x_virtual in range(-diagonal - step, diagonal + step + 1, step):
            is_peak = ((x_virtual // step) % 2) == 0
            y_virtual = d + (amplitude if is_peak else -amplitude)

            nx = x_virtual * math.cos(rad) - y_virtual * math.sin(rad) + cx
            ny = x_virtual * math.sin(rad) + y_virtual * math.cos(rad) + cy

            pts.extend([nx, ny])

        if len(pts) > 3:
            draw.line(pts, pen)

    draw.flush()


def paint_random_sawtooth_waves(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        area_size: Union[Tuple[int, int], Default, Random] = Default,
        spacing: Union[int, Default, Random] = Default,
        thickness: Union[float, Default, Random] = Default,
        amplitude: Union[float, Default, Random] = Default,
        wavelength: Union[float, Default, Random] = Default,
        angle: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "area_size": area_size,
        "spacing": spacing,
        "thickness": thickness,
        "amplitude": amplitude,
        "wavelength": wavelength,
        "angle": angle,
        "color": color,
    })

    parameters = generate_random_sawtooth_wave_parameters(img, primary_color, color, area_size)

    parameters = parameters | passed_values
    paint_angled_sawtooth_waves(img, **parameters)
