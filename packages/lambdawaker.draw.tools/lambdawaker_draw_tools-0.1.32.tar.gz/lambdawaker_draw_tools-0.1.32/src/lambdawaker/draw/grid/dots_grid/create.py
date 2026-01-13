from PIL import Image

from lambdawaker.draw.color.HSLuvColor import HSLuvColor, ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.dots_grid.paint import paint_dots_grid, paint_random_dots_grid


def create_dots_grid(width: int = 800, height: int = 800, radius: float = 5,
                     separation: float = 10, angle: float = 0,
                     color: ColorUnion = HSLuvColor(0, 0, 0, 255),
                     ) -> Image.Image:
    """Create an RGBA image and draw a grid of dots.

    Args:
        width (int): Image width in pixels.
        height (int): Image height in pixels.
        radius (float): Radius of the dots.
        separation (float): Extra spacing added between dots.
        angle (float): Rotation angle for the grid.
        color (ColorUnion): Fill color as an RGBA tuple or HSLuvColor.

    Returns:
        PIL.Image.Image: The generated image.
    """
    color = to_hsluv_color(color)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    paint_dots_grid(
        image=img,
        size=(width, height),
        radius=radius,
        separation=separation,
        angle=angle,
        color=color,
    )
    return img


def create_random_dots_grid(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw a random grid of dots on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random dots grid.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_dots_grid(img, size=(width, height))
    return img


def vis():
    img = create_random_dots_grid()
    img.show()


if __name__ == '__main__':
    vis()
