import random
from typing import Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.random.values import Default, Random


def generate_random_curved_header_parameters(
        primary_color: Union[ColorUnion, Random] = Random,
        color: Union[ColorUnion, Default, Random] = Default,
) -> Dict[str, Any]:
    """
    Generates random parameters for a curved header.

    Args:
        img (Image.Image): The image for which the parameters are being generated.
        primary_color (Union[ColorUnion, Random], optional): The primary color used to derive other colors if they are not specified.
            If `Random`, a random contrasting color is generated. Defaults to `Random`.
        color (Union[ColorUnion, Default, Random], optional): The color of the header.
            If `Default`, a color derived from `primary_color` is used.
            If `Random`, a random contrasting color is generated.
            Defaults to `Default`.
        size (Union[Tuple[int, int], Default, Random], optional): The size of the area.
            If Default, it defaults to the image size. If Random, a random point with no margin is chosen.
            Defaults to Default.

    Returns:
        Dict[str, Any]: A dictionary containing the generated parameters, including:
            - "height": The vertical position of the curve's sides.
            - "curve_depth": How far the curve dips below the height.
            - "color": The color of the header (HSLuv).
    """
    if primary_color == Random:
        primary_color = generate_hsluv_text_contrasting_color()
    else:
        primary_color = to_hsluv_color(primary_color)

    if color == Default:
        color = primary_color.close_color()
    elif color == Random:
        color = generate_hsluv_text_contrasting_color()

    return {
        "height": random.randint(150, 200),
        "curve_depth": random.randint(10, 50),
        "color": color,
    }
