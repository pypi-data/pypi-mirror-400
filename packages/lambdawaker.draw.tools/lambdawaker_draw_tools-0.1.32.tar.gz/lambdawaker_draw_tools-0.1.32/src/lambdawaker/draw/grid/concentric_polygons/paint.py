import math
from typing import Tuple, Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.color.HSLuvColor import HSLuvColor
from lambdawaker.draw.grid.concentric_polygons.parameters import generate_random_concentric_polygons_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_concentric_polygons(
        image: Image.Image,
        color: ColorUnion = (0, 0, 0, 255),
        stroke_color: Optional[ColorUnion] = None,
        size: Optional[Tuple[int, int]] = None,
        center: Optional[Tuple[float, float]] = None,
        sides: int = 6,
        rotation_step: float = 5,
        spacing: float = 15,
        thickness: float = 2,
) -> None:
    """
    Draws concentric polygons onto an existing PIL image using aggdraw.

    Parameters
    ----------
    image : Image.Image
        The PIL Image object to draw on. This image is modified in place.
    color : ColorUnion, optional
        The fill color of the polygons. Can be an HSLuvColor object, a tuple (h, s, l, a) for HSLuv, or (r, g, b, a) for RGBA.
        Defaults to HSLuv black (0, 0, 0, 255).
    stroke_color : Optional[ColorUnion], optional
        The stroke color of the polygon outlines. If `None`, the `color` parameter is used for the stroke. Defaults to `None`.
    size : Optional[Tuple[int, int]], optional
        The size of the canvas (width, height). If `None`, the `image`'s size is used. Defaults to `None`.
    center : Optional[Tuple[float, float]], optional
        The center coordinates (x, y) for the concentric polygons. If `None`, the center of the `image` is used. Defaults to `None`.
    sides : int, optional
        The number of sides for each polygon. Defaults to 6.
    rotation_step : float, optional
        The angular rotation step in degrees between consecutive polygons. Defaults to 5.
    spacing : float, optional
        The radial distance between consecutive polygons. Defaults to 15.
    thickness : float, optional
        The thickness of the polygon outlines. Defaults to 2.

    Returns
    -------
    None:
        The function modifies the input `image` directly; it does not return a new image.
    """
    color: HSLuvColor = to_hsluv_color(color)
    stroke_color = to_hsluv_color(stroke_color)

    if size is None:
        size = image.size

    draw = aggdraw.Draw(image)

    if center is None:
        center = size[0] // 2, size[1] // 2

    (cx, cy) = center

    max_radius = max(*size)
    num_polygons = int(1.5 * max_radius / spacing)

    brush: aggdraw.Brush = aggdraw.Brush(color.to_rgba())
    pen: aggdraw.Pen = aggdraw.Pen(stroke_color.to_rgba(), thickness)

    for i in range(num_polygons, 0, -1):
        radius = i * spacing
        angle_offset = math.radians(i * rotation_step)

        points = []
        for s in range(sides):
            angle = (2 * math.pi * s / sides) + angle_offset
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append(x)
            points.append(y)

        draw.polygon(points, pen, brush)

    draw.flush()


def paint_random_concentric_polygons(
        img: Image.Image,
        primary_color: Union[ColorUnion, Default, Random] = Default,
        color: Union[ColorUnion, Default, Random] = Default,
        stroke_color: Union[ColorUnion, Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        sides: Union[int, Default, Random] = Random,
        rotation_step: Union[float, Default, Random] = Random,
        spacing: Union[float, Default, Random] = Random,
        thickness: Union[float, Default, Random] = Random,
) -> None:
    """
    Generates random parameters for concentric polygons and draws them onto a PIL image. Any parameter
    set to `Random` will be randomly generated. Any parameter set to `Default` will use a sensible
    default value.

    Parameters
    ----------
    img : Image.Image
        The PIL Image object to draw on. This image is modified in place.
    primary_color : Union[ColorUnion, Default, Random], optional
        The primary color used to derive other colors if they are not specified.
        If `Random` or `Default`, a random contrasting color is generated.
        Defaults to `Default`.
    color : Union[ColorUnion, Default, Random], optional
        The base color for polygons. If `Random`, a random color is generated. If `Default`, a sensible default color is used.
        Can also be a specific `ColorUnion` value. Defaults to `Default`.
    stroke_color : Union[ColorUnion, Default, Random], optional
        The stroke color for polygons. If `Random`, a random color is generated. If `Default`, a sensible default color is used.
        Can also be a specific `ColorUnion` value. Defaults to `Default`.
    size : Union[Tuple[int, int], Default, Random], optional
        The canvas size (width, height). If `Default`, the image's size is used. If `Random`, a random size is generated.
        Can also be a specific `Tuple[int, int]`. Defaults to `Default`.
    sides : Union[int, Default, Random], optional
        The number of sides for polygons. If `Random`, a random number of sides is generated. If `Default`, a sensible default is used.
        Can also be a specific `int`. Defaults to `Random`.
    rotation_step : Union[float, Default, Random], optional
        The rotation step in degrees. If `Random`, a random step is generated. If `Default`, a sensible default is used.
        Can also be a specific `float`. Defaults to `Random`.
    spacing : Union[float, Default, Random], optional
        The radial spacing between polygons. If `Random`, a random spacing is generated. If `Default`, a sensible default is used.
        Can also be a specific `float`. Defaults to `Random`.
    thickness : Union[float, Default, Random], optional
        The thickness of polygon outlines. If `Random`, a random thickness is generated. If `Default`, a sensible default is used.
        Can also be a specific `float`. Defaults to `Random`.
    """
    passed_values = clean_passed_parameters({
        "size": size,
        "sides": sides,
        "rotation_step": rotation_step,
        "spacing": spacing,
        "color": color,
        "stroke_color": stroke_color,
        "thickness": thickness,
    })

    parameters = generate_random_concentric_polygons_parameters(
        img,
        primary_color=primary_color,
        color=color,
        stroke_color=stroke_color,
        size=size
    )
    parameters = parameters | passed_values
    paint_concentric_polygons(img, **parameters)
