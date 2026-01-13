from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.waves.parallel_lines.paint import paint_parallel_lines, paint_random_parallel_lines


def create_parallel_lines(
        width: int = 800,
        height: int = 800,
        spacing: int = 20,
        thickness: float = 2,
        angle: float = 45,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an RGBA image and draw parallel angled lines on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        spacing (int): Distance between adjacent lines in pixels.
        thickness (float): Line stroke width in pixels.
        angle (float): Line orientation in degrees; 0 is horizontal, positive
            values rotate counterclockwise.
        color (ColorUnion): Stroke color as an RGBA tuple or HSLuvColor.
        bg_color (ColorUnion): Background color for the created image as RGBA or HSLuvColor;
            default is fully transparent black `(0, 0, 0, 0)`.

    Returns:
        PIL.Image.Image: The generated image containing the angled lines.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())

    paint_parallel_lines(
        image=img,
        area_size=(width, height),
        spacing=spacing,
        thickness=thickness,
        angle=angle,
        color=color,
    )
    return img


def create_random_parallel_lines(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw random parallel lines on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random parallel lines.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_parallel_lines(img, area_size=(width, height))
    return img


def vis():
    img = create_random_parallel_lines()
    img.show()


if __name__ == '__main__':
    vis()
