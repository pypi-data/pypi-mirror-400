import math
from typing import Tuple

import aggdraw

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color


def rotating_polygons(draw: aggdraw.Draw, center: Tuple[float, float], sides: int = 6, num_polygons: int = 10,
                      spacing: float = 20, rotation_step: float = 10,
                      color: ColorUnion = (0, 0, 0, 255), thickness: float = 2) -> None:
    """
    Draws concentric rotating polygons using aggdraw.

    :param draw: aggdraw.Draw object
    :param center: (x, y) tuple for the center of polygons
    :param sides: Number of sides for the polygons (3=triangle, 4=square, etc.)
    :param num_polygons: Total number of nested polygons
    :param spacing: Pixel distance between each consecutive polygon
    :param rotation_step: Degrees of rotation to add per nested layer
    :param color: RGBA tuple for the outline or HSLuvColor
    :param thickness: Line width
    """
    color = to_hsluv_color(color)

    pen = aggdraw.Pen(color.to_rgba(), thickness)
    cx, cy = center

    for i in range(1, num_polygons + 1):

        radius = i * spacing

        angle_offset = math.radians(i * rotation_step)

        points = []
        for s in range(sides):
            angle = (2 * math.pi * s / sides) + angle_offset
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append(x)
            points.append(y)

        draw.polygon(points, pen)
