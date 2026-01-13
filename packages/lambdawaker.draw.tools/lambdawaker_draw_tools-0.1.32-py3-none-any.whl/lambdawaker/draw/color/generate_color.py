import random

from lambdawaker.draw.color.HSLuvColor import HSLuvColor


def generate_hsluv_text_contrasting_color() -> HSLuvColor:
    """
    Generates a random HSLuv color that is likely to have good contrast with text.

    The generated color has a random hue (0-360), and saturation and lightness
    constrained to the range [30, 60]. This range is chosen to avoid extremely
    light or dark colors, providing a balanced background for text.

    Returns:
        HSLuvColor: A new HSLuvColor instance with the tag "CONTRASTING".
    """
    hue = random.randint(0, 360)
    saturation = random.randint(30, 60)
    lightness = random.randint(30, 60)

    return HSLuvColor(hue, saturation, lightness, tag="CONTRASTING")
