from typing import Callable, Dict, Optional

from PIL import Image

from lambdawaker.draw.color.HSLuvColor import HSLuvColor, ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.shapes_grid.paint import paint_shapes_grid, paint_random_shapes_grid
from lambdawaker.draw.shapes.simple_shapes import circle


def create_shapes_grid(width: int = 800, height: int = 800, radius: float = 15,
                       draw_function: Callable = circle, draw_parameters: Optional[Dict] = None,
                       separation: float = 10, angle: float = 0, thickness: float = 2,
                       color: ColorUnion = HSLuvColor(0, 0, 0, 255),
                       outline: ColorUnion = None
                       ) -> Image.Image:
    """Create an RGBA image and draw a grid of shapes.

    Args:
        width (int): Image width in pixels.
        height (int): Image height in pixels.
        radius (float): Base radius for shapes.
        draw_function (callable): Shape drawing function from `simple_shapes`.
        draw_parameters (dict | None): Extra keyword args for the shape function.
        separation (float): Extra spacing added between shapes.
        angle (float): Rotation angle for the grid.
        thickness (float): Outline thickness in pixels.
        color (ColorUnion): Fill color as an RGBA tuple or HSLuvColor.
        outline (ColorUnion): Outline color as an RGBA tuple or HSLuvColor.

    Returns:
        PIL.Image.Image: The generated image.
    """
    color = to_hsluv_color(color)
    outline = to_hsluv_color(outline)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    paint_shapes_grid(
        image=img,
        size=(width, height),
        radius=radius,
        draw_function=draw_function,
        draw_parameters=draw_parameters,
        separation=separation,
        angle=angle,
        thickness=thickness,
        color=color,
        outline=outline,
    )
    return img


def create_random_shapes_grid(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw a random grid of shapes on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random shapes grid.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_shapes_grid(img, size=(width, height))
    return img


def vis():
    img = create_random_shapes_grid()
    img.show()


if __name__ == '__main__':
    vis()
