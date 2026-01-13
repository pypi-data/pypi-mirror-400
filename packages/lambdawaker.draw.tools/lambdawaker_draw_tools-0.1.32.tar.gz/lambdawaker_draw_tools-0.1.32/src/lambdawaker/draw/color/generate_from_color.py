import random
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from lambdawaker.draw.color.HSLuvColor import HSLuvColor


def compute_random_shade_color(base_color: 'HSLuvColor', lightness_limit: int = 30,
                               min_distance: int = 10) -> 'HSLuvColor':
    """
    Computes a random shade of the given base color by modifying its lightness.

    Args:
        base_color (HSLuvColor): The starting color.
        lightness_limit (int): The maximum amount to change the lightness by (positive or negative).
        min_distance (int): The minimum absolute change in lightness to ensure the new shade is distinct.

    Returns:
        HSLuvColor: A new HSLuvColor instance representing the random shade, tagged "SHADE".
    """
    factor = random.choice([-1, 1])
    new_lightness = factor * random.randint(0, lightness_limit // 2)
    new_lightness = max(min_distance, new_lightness)
    c = base_color + (0, 0, new_lightness)
    c.tag = f"SHADE"
    return c


def compute_complementary_color(color: 'HSLuvColor') -> 'HSLuvColor':
    """
    Computes the complementary color of the given color.

    The complementary color is found by adding 180 degrees to the hue.

    Args:
        color (HSLuvColor): The base color.

    Returns:
        HSLuvColor: The complementary color, tagged "COMPLEMENTARY".
    """
    c = color + (180, 0, 0)
    c.tag = f"COMPLEMENTARY"
    return c


def compute_analogous_colors(color: 'HSLuvColor', factor: float = 1 / 8) -> Tuple['HSLuvColor', 'HSLuvColor']:
    """
    Computes two analogous colors for the given base color.

    Analogous colors are adjacent to each other on the color wheel. By default,
    this function uses a spacing factor of 1/8 (45 degrees).

    Args:
        color (HSLuvColor): The base color.
        factor (float): The fraction of the circle to space the colors by (default 1/8).

    Returns:
        Tuple[HSLuvColor, HSLuvColor]: A tuple containing the two analogous color variants.
    """
    return compute_equidistant_variants(color, factor, "ANALOGOUS")


def compute_triadic_colors(color: 'HSLuvColor', factor: float = 1 / 3) -> Tuple['HSLuvColor', 'HSLuvColor']:
    """
    Computes the two triadic colors for the given base color.

    Triadic colors are evenly spaced around the color wheel. By default, they are
    spaced by 1/3 of the circle (120 degrees).

    Args:
        color (HSLuvColor): The base color.
        factor (float): The fraction of the circle to space the colors by (default 1/3).

    Returns:
        Tuple[HSLuvColor, HSLuvColor]: A tuple containing the two triadic color variants.
    """
    return compute_equidistant_variants(color, factor, "TRIADIC")


def compute_equidistant_variants(color: 'HSLuvColor', factor: float, tag_subfix: str = "EV") -> Tuple[
    'HSLuvColor', 'HSLuvColor']:
    """
    Computes two color variants equidistant from the base color's hue.

    One variant is created by adding the offset (factor * 360) to the hue, and
    the other by subtracting it.

    Args:
        color (HSLuvColor): The base color.
        factor (float): The fraction of the full circle (360 degrees) to offset the hue.
        tag_subfix (str): A suffix to append to the tag of the generated colors.

    Returns:
        Tuple[HSLuvColor, HSLuvColor]: A tuple containing the two generated color variants.
    """
    a = color + ((factor * 360), 0, 0)
    a.tag = f"{tag_subfix} A"

    b = color - ((factor * 360), 0, 0)
    b.tag = f"{tag_subfix} B"
    return a, b


def compute_harmonious_color(base_color: 'HSLuvColor', hue_offset: int = 60,
                             lightness_offset: int = 15, saturation_offset: int = 15) -> 'HSLuvColor':
    """
    Computes a harmonious color by slightly adjusting the hue, saturation, and lightness
    of the base color. This aims to create a color that "plays nice" with the original.

    Args:
        base_color (HSLuvColor): The starting color.
        hue_offset (int): The maximum absolute amount to change the hue by (in degrees).
        lightness_offset (int): The maximum absolute amount to change the lightness by.
        saturation_offset (int): The maximum absolute amount to change the saturation by.

    Returns:
        HSLuvColor: A new HSLuvColor instance representing the harmonious color, tagged "HARMONIOUS".
    """
    c = base_color + (random.randint(-hue_offset, hue_offset),
                      random.randint(-saturation_offset, saturation_offset),
                      random.randint(-lightness_offset, lightness_offset))
    c.tag = "HARMONIOUS"
    return c
