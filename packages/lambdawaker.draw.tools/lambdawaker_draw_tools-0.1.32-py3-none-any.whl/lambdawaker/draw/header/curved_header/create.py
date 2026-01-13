import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.header.curved_header.paint import draw_curved_header, paint_random_curved_header


def create_curved_header(
        width: int = 800,
        height: int = 400,
        header_height: int = 100,
        curve_depth: float = 50,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an image and render a curved header on top.

    Args:
        width (int): Image width.
        height (int): Image height.
        header_height (int): Vertical position where the curve meets the sides.
        curve_depth (int|float): How far the curve dips below the header_height.
        color (ColorUnion): Fill color for the header as an RGBA tuple or HSLuvColor.
        bg_color (ColorUnion): Background color (RGBA or HSLuvColor).

    Returns:
        PIL.Image.Image: The generated image.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())
    draw = aggdraw.Draw(img)
    draw_curved_header(draw=draw, height=header_height, curve_depth=curve_depth, color=color)
    draw.flush()
    return img


def create_random_curved_header(
        width: int = 800,
        height: int = 400,
) -> Image.Image:
    """
    Create an RGBA image and draw a random curved header on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random curved header.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_curved_header(img)
    return img


def vis():
    img = create_random_curved_header()
    img.show()


if __name__ == '__main__':
    vis()
