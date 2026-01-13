from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.hexagon_grid.paint import paint_hexagon_grid, paint_random_hexagon_grid


def create_hexagon_grid(
        width: int = 800,
        height: int = 800,
        hexagon_size: float = 20,
        thickness: float = 2.0,
        angle: float = 0,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0)) -> Image.Image:
    """
    Create an RGBA image and draw a hexagonal grid on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        hexagon_size (float): Distance from the hexagon center to a vertex
            (circumradius), in pixels.
        thickness (float): Stroke thickness of hexagon edges in pixels.
        angle (float): Rotation of the entire grid in degrees. Positive values
            rotate counterclockwise around the image center.
        color (ColorUnion): Stroke color as an RGBA tuple or HSLuvColor.
        bg_color (ColorUnion): Background color for the created image as RGBA
            (default fully transparent black `(0, 0, 0, 0)`).

    Returns:
        PIL.Image.Image: The generated image containing the hexagon grid.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())

    paint_hexagon_grid(
        image=img,
        area_size=(width, height),
        hexagon_size=hexagon_size,
        thickness=thickness,
        angle=angle,
        color=color,
    )
    return img


def create_random_hexagon_grid(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw a random hexagonal grid on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random hexagon grid.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_hexagon_grid(img, size=(width, height))
    return img


def vis():
    img = create_random_hexagon_grid()
    img.show()


if __name__ == '__main__':
    vis()
