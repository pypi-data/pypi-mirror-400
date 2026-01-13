from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion
from lambdawaker.draw.fill.linear_gradient.paint import paint_linear_gradient, paint_random_linear_gradient


def create_linear_gradient(
        width: int = 800,
        height: int = 800,
        start_color: ColorUnion = (0, 0, 0, 255),
        end_color: ColorUnion = (255, 255, 255, 255),
        angle: float = 0,
) -> Image.Image:
    """
    Create an RGBA image and draw a linear gradient on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        start_color (ColorUnion): The starting color of the gradient.
        end_color (ColorUnion): The ending color of the gradient.
        angle (float): The angle of the gradient in degrees.

    Returns:
        PIL.Image.Image: The generated image containing the gradient.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    paint_linear_gradient(
        image=img,
        right_corner=(0, 0),
        size=(width, height),
        start_color=start_color,
        end_color=end_color,
        angle=angle,
    )

    return img


def create_random_linear_gradient(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw a random linear gradient on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random gradient.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_linear_gradient(img, right_corner=(0, 0), size=(width, height))
    return img


def vis():
    img = create_random_linear_gradient()
    img.show()


if __name__ == '__main__':
    vis()
