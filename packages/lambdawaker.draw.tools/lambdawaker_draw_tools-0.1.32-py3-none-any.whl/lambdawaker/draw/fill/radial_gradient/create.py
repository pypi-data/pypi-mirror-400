from typing import Tuple, Optional

from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion
from lambdawaker.draw.fill.radial_gradient.paint import paint_radial_gradient, paint_random_radial_gradient


def create_radial_gradient(
        width: int = 800,
        height: int = 800,
        start_color: ColorUnion = (255, 255, 255, 255),
        end_color: ColorUnion = (0, 0, 0, 255),
        center: Optional[Tuple[float, float]] = None,
        radius: Optional[float] = None,
) -> Image.Image:
    """
    Create an RGBA image and draw a radial gradient on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        start_color (ColorUnion): The color at the center of the gradient.
        end_color (ColorUnion): The color at the outer edge of the gradient.
        center (Optional[Tuple[float, float]]): The center point (x, y) of the gradient.
                                                Defaults to the center of the image.
        radius (Optional[float]): The radius of the gradient. Defaults to the distance
                                  from the center to the farthest corner.

    Returns:
        PIL.Image.Image: The generated image containing the radial gradient.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    paint_radial_gradient(
        image=img,
        right_corner=(0, 0),
        size=(width, height),
        start_color=start_color,
        end_color=end_color,
        center=center,
        radius=radius,
    )

    return img


def create_random_radial_gradient(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw a random radial gradient on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random radial gradient.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_radial_gradient(img, right_corner=(0, 0), size=(width, height))
    return img


def vis():
    img = create_random_radial_gradient()
    img.show()


if __name__ == '__main__':
    vis()
