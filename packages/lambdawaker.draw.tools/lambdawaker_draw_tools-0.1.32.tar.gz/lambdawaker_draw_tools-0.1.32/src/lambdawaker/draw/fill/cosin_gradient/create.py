from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion
from lambdawaker.draw.fill.cosin_gradient.paint import paint_cosine_gradient, paint_random_cosine_gradient


def create_cosine_gradient(
        width: int = 800,
        height: int = 800,
        start_color: ColorUnion = (0, 0, 0, 255),
        end_color: ColorUnion = (255, 255, 255, 255),
        angle: float = 0,
        wavelength: float = 100.0,
) -> Image.Image:
    """
    Create a new RGBA image and draw a cosine wave gradient on it.

    Args:
        width (int): Width of the output image.
        height (int): Height of the output image.
        start_color (ColorUnion): First peak color.
        end_color (ColorUnion): Second peak color.
        angle (float): Direction of the wave in degrees.
        wavelength (float): Distance in pixels for one full oscillation cycle.

    Returns:
        PIL.Image.Image: A new image containing the cosine gradient.
    """

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    paint_cosine_gradient(
        image=img,
        right_corner=(0, 0),
        size=(width, height),
        start_color=start_color,
        end_color=end_color,
        angle=angle,
        wavelength=wavelength,
    )

    return img


def create_random_cosine_gradient(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create a new RGBA image and draw a random cosine wave gradient on it.

    Args:
        width (int): Width of the output image.
        height (int): Height of the output image.

    Returns:
        PIL.Image.Image: A new image containing the random cosine gradient.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_cosine_gradient(img, right_corner=(0, 0), size=(width, height))
    return img


def vis():
    img = create_random_cosine_gradient()
    img.show()


if __name__ == '__main__':
    vis()
