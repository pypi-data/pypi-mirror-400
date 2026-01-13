from typing import Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.header.square_header.parameters import generate_random_square_header_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def draw_squared_header(draw: aggdraw.Draw, height: int = 100, color: ColorUnion = (0, 0, 0, 255)) -> None:
    """
    Fills the top area of the canvas to create a header section.
    """
    color = to_hsluv_color(color)

    brush = aggdraw.Brush(color.to_rgba())

    width = draw.size[0]

    draw.rectangle((0, 0, width, height), brush)

    draw.flush()


def paint_random_square_header(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        height: Union[int, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "height": height,
        "color": color,
    })

    parameters = generate_random_square_header_parameters(img, primary_color, color)

    parameters = parameters | passed_values

    draw = aggdraw.Draw(img)
    draw_squared_header(draw, **parameters)
