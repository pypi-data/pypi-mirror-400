from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.concentric_polygons.paint import paint_concentric_polygons, paint_random_concentric_polygons


def create_concentric_polygons(
        width: int = 800,
        height: int = 800,
        sides: int = 6,
        rotation_step: float = 5,
        spacing: float = 15,
        color: ColorUnion = (0, 0, 0, 255),
        stroke_color: ColorUnion = None,
        thickness: float = 2,
        bg_color: ColorUnion = (0, 0, 0, 0)) -> Image:
    """
    Create an RGBA image and draw concentric polygons on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        sides (int): Number of sides for the polygons (e.g., 6 for hexagons).
        rotation_step (float): Degrees of rotation added per nested layer.
        spacing (float): Pixel distance between consecutive polygons.
        color (ColorUnion): RGBA tuple for the outline color or HSLuvColor.
        stroke_color (ColorUnion): RGBA tuple for the outline color or HSLuvColor.
        thickness (float): Stroke thickness of polygon edges in pixels.
        bg_color (ColorUnion): Background color for the created image (RGBA; default transparent).

    Returns:
        PIL.Image.Image: The generated image containing the concentric polygons.
    """
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())

    paint_concentric_polygons(
        image=img,
        size=(width, height),
        sides=sides,
        rotation_step=rotation_step,
        spacing=spacing,
        color=color,
        stroke_color=stroke_color,
        thickness=thickness
    )

    return img


def create_random_concentric_polygons(
        width: int = 800,
        height: int = 800,
) -> Image:
    """
    Create an RGBA image and draw random concentric polygons on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random concentric polygons.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_concentric_polygons(img, size=(width, height))
    return img


def vis():
    img = create_random_concentric_polygons()
    img.show()


if __name__ == '__main__':
    vis()
