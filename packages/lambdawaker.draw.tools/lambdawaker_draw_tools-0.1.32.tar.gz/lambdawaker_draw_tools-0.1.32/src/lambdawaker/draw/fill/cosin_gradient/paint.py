from typing import Tuple, Union, Optional

import numpy as np
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.fill.cosin_gradient.parameters import generate_random_cosine_gradient_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_cosine_gradient(
        image: Image.Image,
        right_corner: Tuple[int, int] = (0, 0),
        size: Optional[Tuple[int, int]] = None,
        start_color: ColorUnion = (0, 0, 0, 255),
        end_color: ColorUnion = (255, 255, 255, 255),
        angle: float = 0,
        wavelength: float = 100.0,
) -> None:
    """
    Draws a cosine wave gradient onto an existing PIL image at a specific location.
    The gradient oscillates between start_color and end_color.
    """

    start_rgba = to_hsluv_color(start_color).to_rgba()
    end_rgba = to_hsluv_color(end_color).to_rgba()

    width, height = size if size is not None else image.size
    mode = image.mode

    y, x = np.ogrid[:height, :width]
    rad = np.deg2rad(angle)
    cos_a, sin_a = np.cos(rad), np.sin(rad)

    projection = x * cos_a + y * sin_a

    wave = 0.5 * (np.cos(2 * np.pi * projection / wavelength) + 1)
    mask = wave[..., np.newaxis]

    channels = 4 if mode == "RGBA" else 3
    start_c = np.array(start_rgba[:channels])
    end_c = np.array(end_rgba[:channels])

    gradient_array = (start_c + mask * (end_c - start_c)).astype(np.uint8)

    gradient_patch = Image.fromarray(gradient_array, mode=mode)

    image.paste(gradient_patch, right_corner, mask=gradient_patch if mode == "RGBA" else None)


def paint_random_cosine_gradient(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        right_corner: Union[Tuple[int, int], Default, Random] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        start_color: Optional[ColorUnion] = None,
        end_color: Optional[ColorUnion] = None,
        angle: Optional[float] = None,
        wavelength: Optional[float] = None
) -> None:
    passed_values = clean_passed_parameters({
        "right_corner": right_corner,
        "size": size,
        "start_color": start_color,
        "end_color": end_color,
        "angle": angle,
        "wavelength": wavelength,
    })

    parameters = generate_random_cosine_gradient_parameters(
        img, primary_color, right_corner, size
    )

    parameters = parameters | passed_values
    paint_cosine_gradient(img, **parameters)
