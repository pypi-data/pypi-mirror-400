import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.header.square_header.paint import draw_squared_header, paint_random_square_header


def create_squared_header(
        width: int = 800,
        height: int = 400,
        header_height: int = 100,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an image and render a rectangular header on top.

    Args:
        width (int): Image width.
        height (int): Image height.
        header_height (int): Height of the filled header area from the top.
        color (ColorUnion): Fill color for the header.
        bg_color (ColorUnion): Background color (supports RGBA or HSLuvColor).

    Returns:
        PIL.Image.Image: The generated image.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())
    draw = aggdraw.Draw(img)
    draw_squared_header(draw=draw, height=header_height, color=color)
    draw.flush()
    return img


def create_square_header(
        width: int = 800,
        height: int = 400,
        header_height: int = 100,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """Alias for create_squared_header for convenience."""
    return create_squared_header(
        width=width,
        height=height,
        header_height=header_height,
        color=color,
        bg_color=bg_color,
    )


def create_random_square_header(
        width: int = 800,
        height: int = 400,
) -> Image.Image:
    """
    Create an RGBA image and draw a random square header on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random square header.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_square_header(img)
    return img


def vis():
    img = create_random_square_header()
    img.show()


if __name__ == '__main__':
    vis()
