import math
from typing import Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.header.sin_header.parameters import generate_random_sin_header_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def draw_sine_header(draw: aggdraw.Draw, height: int = 100, amplitude: float = 20, frequency: float = 2, color: ColorUnion = (0, 0, 0, 255)) -> None:
    """
    Creates a header with a sine-wave bottom edge.
    """
    color = to_hsluv_color(color)
    width, _ = draw.size
    brush = aggdraw.Brush(color.to_rgba())
    path = aggdraw.Path()

    path.moveto(0, 0)
    path.lineto(width, 0)

    end_y = height + amplitude * math.sin(2 * math.pi * frequency)
    path.lineto(width, end_y)

    steps = 100
    for i in range(steps, -1, -1):
        x = (i / steps) * width

        y = height + amplitude * math.sin(2 * math.pi * frequency * (i / steps))
        path.lineto(x, y)

    path.close()

    draw.path(path, brush)
    draw.flush()


def paint_random_sin_header(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        height: Union[int, Default, Random] = Default,
        amplitude: Union[float, Default, Random] = Default,
        frequency: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "height": height,
        "amplitude": amplitude,
        "frequency": frequency,
        "color": color,
    })

    parameters = generate_random_sin_header_parameters(img, primary_color, color)

    parameters = parameters | passed_values

    draw = aggdraw.Draw(img)
    draw_sine_header(draw, **parameters)
