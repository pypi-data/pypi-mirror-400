import random
from typing import Tuple, Union, Dict, Any

from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.color.utils import get_random_point_with_margin
from lambdawaker.draw.shapes.simple_shapes import circle, square, triangle, polygon, star
from lambdawaker.random.values import DefaultValue, Default, Random


def generate_random_shapes_grid_parameters(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Union[ColorUnion, Default, Random] = Default,
        outline: Union[ColorUnion, Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default
) -> Dict[str, Any]:
    """
    Generates random parameters for a grid of shapes.

    Args:
        img (Image.Image): The image for which the grid parameters are being generated.
        primary_color (Union[ColorUnion, Random], optional): The primary color used to derive other colors if they are not specified.
            If `Random`, a random contrasting color is generated. Defaults to `Random`.
        color (Union[ColorUnion, Default, Random], optional): The fill color of the shapes.
            If `Default`, a color derived from `primary_color` is used.
            If `Random`, a random contrasting color is generated.
            Defaults to `Default`.
        outline (Union[ColorUnion, Default, Random], optional): The outline color of the shapes.
            If `Default`, a color derived from `primary_color` is used.
            If `Random`, a random contrasting color is generated.
            Defaults to `Default`.
        size (Union[Tuple[int, int], Default, Random], optional): The size of the grid area.
            If Default, it defaults to the image size. If Random, a random point with no margin is chosen.
            Defaults to Default.

    Returns:
        Dict[str, Any]: A dictionary containing the generated grid parameters, including:
            - "size": The size of the grid area.
            - "radius": The base radius for the shapes.
            - "draw_function": The function used to draw the shapes (e.g., circle, square).
            - "draw_parameters": Additional parameters for the draw function (e.g., sides, points).
            - "separation": The spacing between shapes.
            - "angle": The rotation angle of the grid in degrees (0-360).
            - "thickness": The thickness of the shape outlines.
            - "color": The fill color of the shapes (HSLuv).
            - "outline": The outline color of the shapes (HSLuv).
    """
    if primary_color == Random:
        primary_color = generate_hsluv_text_contrasting_color()
    else:
        primary_color = to_hsluv_color(primary_color)

    if color == Default:
        color = primary_color.close_color()
    elif color == Random:
        color = generate_hsluv_text_contrasting_color()

    if outline == Default:
        outline = primary_color.random_shade()
    elif outline == Random:
        outline = generate_hsluv_text_contrasting_color()

    if size == Default:
        size = DefaultValue(lambda: img.size)

    draw_function = random.choice([circle, square, triangle, polygon, star])
    draw_parameters = {}
    if draw_function == polygon:
        draw_parameters["sides"] = random.randint(3, 8)
    elif draw_function == star:
        draw_parameters["points"] = random.randint(4, 8)

    return {
        "size": get_random_point_with_margin(img.size, default=size, margin=0),
        "radius": random.uniform(10, 50),
        "draw_function": draw_function,
        "draw_parameters": draw_parameters,
        "separation": random.uniform(5, 30),
        "angle": random.uniform(0, 360),
        "thickness": random.uniform(1, 5),
        "color": color,
        "outline": outline,
    }
