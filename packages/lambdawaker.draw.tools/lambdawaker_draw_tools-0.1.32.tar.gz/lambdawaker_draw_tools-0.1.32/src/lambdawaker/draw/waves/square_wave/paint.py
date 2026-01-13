import math
from typing import Tuple, Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.waves.square_wave.parameters import generate_random_square_wave_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_angled_square_waves(
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
    Draw a set of parallel square waves at a given rotation into a context.
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

    def rotate_point(px: float, py: float):
        nx = px * math.cos(rad) - py * math.sin(rad) + cx
        ny = px * math.sin(rad) + py * math.cos(rad) + cy
        return nx, ny

    for d in range(-diagonal, diagonal + int(spacing), int(spacing)):
        y_high = d + amplitude
        y_low = d - amplitude

        x = -diagonal - step
        pts = []

        is_high = True

        x = -diagonal
        pts.extend(rotate_point(x, y_high if is_high else y_low))

        while x <= diagonal + step:
            next_x = x + step
            y_curr = y_high if is_high else y_low
            y_next = y_low if is_high else y_high

            pts.extend(rotate_point(next_x, y_curr))

            pts.extend(rotate_point(next_x, y_next))

            x = next_x
            is_high = not is_high

        if len(pts) > 3:
            draw.line(pts, pen)

    draw.flush()


def paint_random_square_waves(
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

    parameters = generate_random_square_wave_parameters(img, primary_color, color, area_size)

    parameters = parameters | passed_values
    paint_angled_square_waves(img, **parameters)
