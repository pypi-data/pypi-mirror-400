from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.waves.parallel_sin.paint import paint_sine_waves, paint_random_sine_waves


def create_sine_waves(
        width: int = 800,
        height: int = 800,
        spacing: int = 30,
        thickness: float = 2,
        amplitude: float = 40,
        frequency: float = 0.01,
        angle: float = 45,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an RGBA image and draw rotated parallel sine waves on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        spacing (int): Distance between adjacent sine baselines in pixels.
        thickness (float): Stroke thickness of the sine curves in pixels.
        amplitude (float): Peak amplitude of each sine wave in pixels.
        frequency (float): Frequency factor for the sine function; larger
            values create more oscillations per pixel along the wave.
        angle (float): Rotation angle in degrees; positive values rotate
            counterclockwise around the image center.
        color (ColorUnion): Stroke color as an RGBA tuple or HSLuvColor.
        bg_color (ColorUnion): Background color for the created image as RGBA or HSLuvColor;
            default is fully transparent black `(0, 0, 0, 0)`.

    Returns:
        PIL.Image.Image: The generated image containing the angled sine waves.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())

    paint_sine_waves(
        image=img,
        area_size=(width, height),
        spacing=spacing,
        thickness=thickness,
        amplitude=amplitude,
        frequency=frequency,
        angle=angle,
        color=color,
    )
    return img


def create_random_sine_waves(
        width: int = 800,
        height: int = 800,
) -> Image.Image:
    """
    Create an RGBA image and draw random parallel sine waves on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.

    Returns:
        PIL.Image.Image: The generated image containing the random sine waves.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    paint_random_sine_waves(img, area_size=(width, height))
    return img


def vis():
    img = create_random_sine_waves()
    img.show()


if __name__ == '__main__':
    vis()
