import random
from typing import Tuple, Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.random.values import DefaultValue, Default, Random


def generate_random_sine_waves_parameters(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Union[ColorUnion, Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default
) -> Dict[str, Any]:
    """
    Generates random parameters for parallel sine waves.

    Args:
        img (Image.Image): The image for which the parameters are being generated.
        primary_color (Union[ColorUnion, Random], optional): The primary color used to derive other colors if they are not specified.
            If `Random`, a random contrasting color is generated. Defaults to `Random`.
        color (Union[ColorUnion, Default, Random], optional): The color of the waves.
            If `Default`, a color derived from `primary_color` is used.
            If `Random`, a random contrasting color is generated.
            Defaults to `Default`.
        size (Union[Tuple[int, int], Default, Random], optional): The size of the area.
            If Default, it defaults to the image size. If Random, a random point with no margin is chosen.
            Defaults to Default.

    Returns:
        Dict[str, Any]: A dictionary containing the generated parameters, including:
            - "area_size": The size of the area.
            - "spacing": The distance between wave baselines.
            - "thickness": The thickness of the waves.
            - "amplitude": The peak amplitude of the waves.
            - "frequency": The frequency of the waves.
            - "angle": The rotation angle of the waves in degrees (0-360).
            - "color": The color of the waves (HSLuv).
    """
    if primary_color == Random:
        primary_color = generate_hsluv_text_contrasting_color()
    else:
        primary_color = to_hsluv_color(primary_color)

    if color == Default:
        color = primary_color.close_color()
    elif color == Random:
        color = generate_hsluv_text_contrasting_color()

    if size == Default:
        size = DefaultValue(lambda: img.size)

    thickness = random.uniform(1, 3)

    return {
        "area_size": get_random_point_with_margin(img.size, default=size, margin=0),
        "spacing": thickness * random.uniform(1.4, 8),
        "thickness": thickness,
        "amplitude": random.uniform(10, 100),
        "frequency": random.uniform(0.005, 0.05),
        "angle": random.uniform(0, 360),
        "color": color,
    }
