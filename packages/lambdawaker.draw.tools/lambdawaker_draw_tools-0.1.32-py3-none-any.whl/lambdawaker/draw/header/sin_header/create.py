import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.header.sin_header.paint import draw_sine_header, paint_random_sin_header


def create_sine_header(
        width: int = 800,
        height: int = 400,
        header_height: int = 100,
        amplitude: float = 20,
        frequency: float = 2,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an image and render a sine-wave header on top.

    Args:
        width (int): Image width.
        height (int): Image height.
        header_height (int): Vertical position of the wave baseline.
        amplitude (float): Wave amplitude in pixels.
        frequency (float): Number of full waves across the width.
        color (ColorUnion): Fill color for the header (RGBA tuple or HSLuvColor).
        bg_color (ColorUnion): Background color (RGBA tuple or HSLuvColor).

    Returns:
        PIL.Image.Image: The generated image.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())
    draw = aggdraw.Draw(img)
    draw_sine_header(
        draw=draw,
        height=header_height,
        amplitude=amplitude,
        frequency=frequency,
        color=color,
    )
    draw.flush()
    return img


def create_random_sine_header(
        width: int = 800,
        height: int = 400,
) -> Image.Image:
    """
    Create an RGBA image and draw a random sine wave header on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random sine header.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_sin_header(img)
    return img


def vis():
    img = create_random_sine_header()
    img.show()


if __name__ == '__main__':
    vis()
