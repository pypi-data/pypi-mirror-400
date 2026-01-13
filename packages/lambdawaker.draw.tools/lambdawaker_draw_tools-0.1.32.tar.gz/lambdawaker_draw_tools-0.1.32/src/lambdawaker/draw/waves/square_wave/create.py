from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.waves.square_wave.paint import paint_angled_square_waves, paint_random_square_waves


def create_angled_square_waves(
        width: int = 800,
        height: int = 800,
        spacing: int = 50,
        thickness: float = 2,
        amplitude: float = 25,
        wavelength: float = 80,
        angle: float = 0,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an RGBA image and draw rotated parallel square waves on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        spacing (int): Distance between adjacent wave baselines in pixels.
        thickness (float): Stroke thickness of the wave in pixels.
        amplitude (float): Peak vertical displacement of the square wave in pixels.
        wavelength (float): Horizontal length of one full cycle in pixels.
        angle (float): Rotation in degrees; positive values rotate
            counterclockwise around the image center.
        color (ColorUnion): Stroke color as an RGBA tuple or HSLuvColor.
        bg_color (ColorUnion): Background color for the created image as RGBA or HSLuvColor; default
            is fully transparent black `(0, 0, 0, 0)`.

    Returns:
        PIL.Image.Image: The generated image containing the angled square waves.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())

    paint_angled_square_waves(
        image=img,
        area_size=(width, height),
        spacing=spacing,
        thickness=thickness,
        amplitude=amplitude,
        wavelength=wavelength,
        angle=angle,
        color=color,
    )
    return img


def create_random_square_waves(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw random parallel square waves on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random square waves.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_square_waves(img, area_size=(width, height))
    return img


def vis():
    img = create_random_square_waves()
    img.show()


if __name__ == '__main__':
    vis()
