import random
from typing import Tuple, Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.random.values import DefaultValue, Default, Random


def generate_random_concentric_polygons_parameters(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Union[ColorUnion, Default, Random] = Default,
        stroke_color: Union[ColorUnion, Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        center: Union[Tuple[int, int], Default, Random] = Random,
) -> Dict[str, Any]:
    """
    Generates a dictionary of random parameters for drawing concentric polygons.

    Args:
        img (Image.Image): The image object, used to determine canvas size.
        primary_color (Union[ColorUnion, Random], optional): The primary color used to derive other colors if they are not specified.
            If `Random`, a random contrasting color is generated. Defaults to `Random`.
        color (Union[ColorUnion, Default, Random]): The fill color for the polygons.
            - If `Default`, it defaults to (0, 0, 0, 0) (transparent black).
            - If `Random`, a random contrasting HSLuv color is generated.
            - Otherwise, it uses the provided `ColorUnion` value.
            Defaults to `Default`.
        stroke_color (Union[ColorUnion, Default, Random]): The stroke color for the polygons.
            - If `Default` and `color` is also `Default`, it defaults to a close color to the
              transparent black `color`.
            - If `Default` and `color` is not `Default`, a random contrasting HSLuv color is
              generated.
            - If `Random`, a random contrasting HSLuv color is generated.
            - Otherwise, it uses the provided `ColorUnion` value.
            Defaults to `Default`.
        size (Union[Tuple[int, int], Default, Random]): The desired size of the canvas for the
            polygons.
            - If `Default`, it uses the image's size.
            - If `Random`, a random point within the image bounds is chosen.
            - Otherwise, it uses the provided `Tuple[int, int]` value.
            Defaults to `Default`.
        center (Union[Tuple[int, int], Default, Random], optional):
            The center point for the concentric polygons. If `Random`, a random point within the image bounds is chosen. Defaults to `Random`.

    Returns:
        Dict[str, Any]: A dictionary containing various parameters for drawing concentric polygons,
                        such as canvas size, number of sides, rotation step, spacing, color, thickness, and fill opacity.
    """
    if primary_color == Random or primary_color == Default:
        primary_color = generate_hsluv_text_contrasting_color()
    else:
        primary_color = to_hsluv_color(primary_color)

    if color == Default:
        color = (0, 0, 0, 0)
    elif color is Random:
        color = primary_color.close_color()

    color = to_hsluv_color(color)

    if stroke_color == Default and color == Default:
        stroke_color = color.close_color()
    elif stroke_color == Default:
        stroke_color = primary_color.close_color()

    stroke_color = to_hsluv_color(stroke_color)

    if size == Default:
        size = DefaultValue(lambda: img.size)

    thickness = random.uniform(1, 8)

    return {
        "size": get_random_point_with_margin(img.size, default=size, margin=0),
        "center": get_random_point_with_margin(img.size, default=center, margin=0),
        "sides": random.randint(3, 8),
        "rotation_step": random.uniform(0, 15),
        "spacing": thickness * random.uniform(1.2, 8),
        "color": color,
        "stroke_color": stroke_color,
        "thickness": thickness
    }
