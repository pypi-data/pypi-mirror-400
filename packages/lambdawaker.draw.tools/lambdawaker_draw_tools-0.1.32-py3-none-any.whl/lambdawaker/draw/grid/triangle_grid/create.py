from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.triangle_grid.paint import paint_triangle_grid, paint_random_triangle_grid


def create_triangle_grid(
        width: int = 800,
        height: int = 800,
        size: float = 50,
        thickness: float = 2.0,
        angle: float = 0,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0)) -> Image.Image:
    """
    Create an RGBA image and draw an equilateral triangle tiling on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        size (float): Side length of each equilateral triangle in pixels.
        thickness (float): Stroke thickness of triangle edges in pixels.
        angle (float): Rotation of the entire grid in degrees; positive values
            rotate counterclockwise around the image center.
        color (ColorUnion): Stroke color as an RGBA tuple or HSLuvColor.
        bg_color (ColorUnion): Background color as an RGBA tuple or HSLuvColor. Default is fully
            transparent black `(0, 0, 0, 0)`.

    Returns:
        PIL.Image.Image: The generated image containing the triangle grid.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())

    paint_triangle_grid(
        image=img,
        area_size=(width, height),
        size=size,
        thickness=thickness,
        angle=angle,
        color=color,
    )
    return img


def create_random_triangle_grid(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw a random equilateral triangle tiling on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random triangle grid.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_triangle_grid(img, area_size=(width, height))
    return img


def vis():
    img = create_random_triangle_grid()
    img.show()


if __name__ == '__main__':
    vis()
