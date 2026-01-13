from typing import Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.header.curved_header.parameters import generate_random_curved_header_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def draw_curved_header(draw: aggdraw.Draw, height: int = 100, curve_depth: float = 50, color: ColorUnion = (0, 0, 0, 255)) -> None:
    """
    Creates a header with a curved bottom edge using aggdraw.path()
    """
    color = to_hsluv_color(color)
    width, _ = draw.size
    brush = aggdraw.Brush(color.to_rgba())

    path = aggdraw.Path()
    path.moveto(0, 0)
    path.lineto(width, 0)
    path.lineto(width, height)

    path.curveto(width * 0.75, height + curve_depth, width * 0.25, height + curve_depth, 0, height)
    path.close()

    draw.path(path, brush)

    draw.flush()


def paint_random_curved_header(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        height: Union[int, Default, Random] = Default,
        curve_depth: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "height": height,
        "curve_depth": curve_depth,
        "color": color,
    })

    parameters = generate_random_curved_header_parameters(primary_color, color)

    parameters = parameters | passed_values

    draw = aggdraw.Draw(img)
    draw_curved_header(draw, **parameters)
