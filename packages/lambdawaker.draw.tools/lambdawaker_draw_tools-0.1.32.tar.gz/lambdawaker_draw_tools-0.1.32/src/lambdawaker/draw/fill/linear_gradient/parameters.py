import random
from typing import Tuple, Union, Dict, Any

from PIL.Image import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.random.values import DefaultValue, Default, Random


def generate_random_linear_gradient_parameters(
        img: Image,
        primary_color: Union[ColorUnion, Random] = Random,
        right_corner: Union[Tuple[int, int], Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default
) -> Dict[str, Any]:
    """
    Generates random parameters for a linear gradient.

    Args:
        img (Image): The image for which the gradient parameters are being generated.
        primary_color (Union[ColorUnion, Random], optional): The primary color for the gradient.
            If Random, a contrasting color will be generated. Defaults to Random.
        right_corner (Union[Tuple[int, int], Default, Random], optional): The right corner of the gradient.
            If Default, it defaults to (0, 0). If Random, a random point with no margin is chosen.
            Defaults to Default.
        size (Union[Tuple[int, int], Default, Random], optional): The size of the gradient.
            If Default, it defaults to the image size. If Random, a random point with no margin is chosen.
            Defaults to Default.

    Returns:
        Dict[str, Any]: A dictionary containing the generated gradient parameters, including:
            - "right_corner": The top-left corner of the gradient.
            - "size": The size of the gradient.
            - "angle": The angle of the gradient in degrees (0-360).
            - "start_color": The starting HSLuv color of the gradient.
            - "end_color": The ending HSLuv color of the gradient, harmonized with the start color.
    """
    if primary_color == Random:
        primary_color = generate_hsluv_text_contrasting_color()
    else:
        primary_color = to_hsluv_color(primary_color)

    color = primary_color.close_color()

    if right_corner == Default:
        right_corner = DefaultValue((0, 0))

    if size == Default:
        size = DefaultValue(lambda: img.size)

    return {
        "right_corner": get_random_point_with_margin(img.size, default=right_corner, margin=0),
        "size": get_random_point_with_margin(img.size, default=size, margin=0),
        "angle": random.uniform(0, 360),
        "start_color": color,
        "end_color": color.harmonious_color(),
    }
