import random
from typing import Tuple, Union, Iterator

import hsluv

from lambdawaker.draw.color.generate_from_color import compute_random_shade_color, compute_complementary_color, \
    compute_triadic_colors, compute_analogous_colors, compute_equidistant_variants, compute_harmonious_color
from lambdawaker.draw.color.utils import clamp_hue, clamp, hsla_string_to_hsl_tuple, get_from_tuple


class HSLuvColor:
    """
    Represents a color in the HSLuv color space with support for range constraints and basic manipulation.
    """

    def __init__(self, hue: float, saturation: float, lightness: float, alpha: float = 1.0,
                 h_range: Tuple[float, float] = (0, 360),
                 s_range: Tuple[float, float] = (0, 100),
                 l_range: Tuple[float, float] = (0, 100),
                 a_range: Tuple[float, float] = (0, 1), tag: str = "") -> None:
        """
        Initialize HSLuv with value constraints.

        Args:
            hue (float): The hue value (0-360).
            saturation (float): The saturation value (0-100).
            lightness (float): The lightness value (0-100). If the value is outside the range, it will be clamped.
            h_range (tuple): Min and max allowed values for hue.
            s_range (tuple): Min and max allowed values for saturation.
            l_range (tuple): Min and max allowed values for lightness.
            alpha (float): The alpha (opacity) value (0.0-1.0).
            tag (str): An optional tag or label for the color.
        """
        self.h_range = (h_range[0] % 360, h_range[1] % 360)
        self.s_range = s_range
        self.l_range = l_range
        self.a_range = a_range

        self.hue = clamp_hue(hue, self.h_range)
        self.saturation = clamp(saturation, s_range)
        self.lightness = clamp(lightness, l_range)
        self.alpha = clamp(alpha, (0.0, 1.0))
        self.tag = tag

    def add_hue(self, amount: float, tag: str = "ADD HUE") -> 'HSLuvColor':
        """
        Returns a new HSLuvColor with the hue adjusted by the given amount.
        """

        hue = clamp_hue(self.hue + amount, self.h_range)
        return HSLuvColor(hue, saturation=self.saturation, lightness=self.lightness,
                          alpha=self.alpha, h_range=self.h_range, s_range=self.s_range,
                          l_range=self.l_range, a_range=self.a_range, tag=tag)

    def add_saturation(self, amount: float, tag: str = "ADD SATURATION") -> 'HSLuvColor':
        """
        Returns a new HSLuvColor with the saturation adjusted by the given amount.
        """
        saturation = clamp(self.saturation + amount, self.s_range)
        return HSLuvColor(self.hue, saturation=saturation, lightness=self.lightness, alpha=self.alpha,
                          h_range=self.h_range, s_range=self.s_range, l_range=self.l_range, a_range=self.a_range,
                          tag=tag)

    def add_lightness(self, amount: float, tag: str = "ADD LIGHTNESS") -> 'HSLuvColor':
        """
        Returns a new HSLuvColor with the lightness adjusted by the given amount.
        """
        lightness = clamp(self.lightness + amount, self.l_range)
        return HSLuvColor(self.hue, saturation=self.saturation, lightness=lightness, alpha=self.alpha,
                          h_range=self.h_range, s_range=self.s_range, l_range=self.l_range, a_range=self.a_range,
                          tag=tag)

    def add_alpha(self, amount: float, tag: str = "ADD ALPHA") -> 'HSLuvColor':
        """
        Returns a new HSLuvColor with the alpha adjusted by the given amount.
        """
        alpha = clamp(self.alpha + amount, self.a_range)
        return HSLuvColor(self.hue, saturation=self.saturation, lightness=self.lightness, alpha=alpha,
                          h_range=self.h_range, s_range=self.s_range, l_range=self.l_range, a_range=self.a_range,
                          tag=tag)

    def __sub__(self, other: Union[
        str, Tuple[float, float, float], Tuple[float, float, float, float], 'HSLuvColor']) -> 'HSLuvColor':
        """
        Allows hsluv - "50H" syntax.
        Returns a new instance to keep with Python's immutable __sub__ convention,
        or modifies self if you prefer in-place.
        """
        corrected = other
        if isinstance(other, str):
            try:
                corrected = hsla_string_to_hsl_tuple(other)
            except (ValueError, IndexError):
                raise ValueError(f"Invalid format: {other}. Use format like '50H'.")

        corrected = -corrected[0], -corrected[1], -corrected[2], - get_from_tuple(corrected, 3, 1)
        return self.__add__(corrected)

    def __add__(self, other: Union[
        str, Tuple[float, float, float], Tuple[float, float, float, float], 'HSLuvColor']) -> 'HSLuvColor':
        """Allows hsluv + "50H" syntax.
        Returns a new instance to keep with Python's immutable __add__ convention, or modifies self if you prefer
        in-place.
        If `other` is a tuple, it should have 4 floats (H, S, L, A).
        """
        corrected = other
        if isinstance(other, str):
            try:
                corrected = hsla_string_to_hsl_tuple(other)
            except (ValueError, IndexError):
                raise ValueError(f"Invalid format: {corrected}. Use format like '50H'.")

        if isinstance(corrected, (tuple, list, HSLuvColor)):
            new_h, new_s, new_l, new_a = self.hue, self.saturation, self.lightness, self.alpha
            new_h += corrected[0]
            new_s += corrected[1]
            new_l += corrected[2]
            if len(corrected) > 3:
                new_a += corrected[3]
        else:
            raise NotImplemented

        return HSLuvColor(new_h, new_s, new_l, new_a, self.h_range, self.s_range, self.l_range, self.a_range)

    def __getitem__(self, index: Union[int, slice]) -> Union[float, Tuple[float, ...]]:
        """Allows access via color[0], color[1], color[2], color[3] or slicing."""

        components = (self.hue, self.saturation, self.lightness, self.alpha)

        if isinstance(index, slice):
            start, stop, step = index.indices(len(components))
            return tuple(components[i] for i in range(start, stop, step))

        if isinstance(index, int):
            try:
                return components[index]
            except IndexError:
                raise IndexError(
                    f"Index {index} out of bounds. Use 0 (H), 1 (S), 2 (L), 3 (a)."
                ) from None

        raise TypeError(f"Invalid argument type: {type(index).__name__}")

    def __iter__(self) -> Iterator[float]:
        """Allows unpacking: h, s, l = color_instance"""
        yield self.hue
        yield self.saturation
        yield self.lightness
        yield self.alpha

    def __len__(self) -> int:
        return 3

    def to_rgba(self) -> tuple[int, int, int, int]:
        """
        Converts the HSLuv color to an RGB tuple with values in the range [0, 255].
        """
        r, g, b = hsluv.hsluv_to_rgb((self.hue, self.saturation, self.lightness))
        return int(r * 255), int(g * 255), int(b * 255), int(self.alpha * 255)

    def to_css_rgba(self) -> str:
        r, g, b = self.to_rgb()
        a = self.alpha
        return f'rgba({r},{g},{b},{a:02f})'

    def to_rgb(self):
        r, g, b = hsluv.hsluv_to_rgb((self.hue, self.saturation, self.lightness))
        return int(r * 255), int(g * 255), int(b * 255)

    def to_rgb_hex(self) -> str:
        """
        Converts the HSLuv color to an RGBA hexadecimal string (e.g., "#RRGGBBAA").
        """
        r, g, b = self.to_rgb()
        return f'#{r:02x}{g:02x}{b:02x}'

    def to_rgba_hex(self) -> str:
        """
        Converts the HSLuv color to an RGBA hexadecimal string (e.g., "#RRGGBBAA").
        """
        r, g, b, a = self.to_rgba()
        return f'#{r:02x}{g:02x}{b:02x}{a:02x}'

    def __repr__(self) -> str:
        return f"HSLuv(H={self.hue:.1f}, S={self.saturation:.1f}, L={self.lightness:.1f}, A={self.alpha:.1f})"

    def random_shade(self, lightness_limit: int = 30, min_distance: int = 10) -> 'HSLuvColor':
        """Generates a random shade of this color."""
        return compute_random_shade_color(self, lightness_limit=lightness_limit, min_distance=min_distance)

    def complementary_color(self) -> 'HSLuvColor':
        """
        Returns the complementary color.

        The complementary color is found by rotating the hue by 180 degrees.
        """
        return compute_complementary_color(self)

    def harmonious_color(self, hue_offset: int = 90, lightness_offset: int = 15,
                         saturation_offset: int = 15) -> 'HSLuvColor':
        """
        Generates a harmonious color based on the current color.

        Args:
            hue_offset (int): The maximum offset for the hue component.
            lightness_offset (int): The maximum offset for the lightness component.
            saturation_offset (int): The maximum offset for the saturation component.

        Returns:
            HSLuvColor: A new HSLuvColor object representing the harmonious color.
        """
        return compute_harmonious_color(
            self,
            hue_offset=hue_offset,
            lightness_offset=lightness_offset,
            saturation_offset=saturation_offset
        )

    def split_complementary_colors(self, angle: float = 30.0) -> Tuple['HSLuvColor', 'HSLuvColor']:
        """
        Returns a tuple of two HSLuvColor objects representing the split complementary colors.
        """

    def close_color(self, hue_offset: int = 25, lightness_offset: int = 8,
                    saturation_offset: int = 5) -> 'HSLuvColor':
        return compute_harmonious_color(
            self,
            hue_offset=hue_offset,
            lightness_offset=lightness_offset,
            saturation_offset=saturation_offset
        )

    def triadic_colors(self, factor: float = 1 / 3) -> Tuple['HSLuvColor', 'HSLuvColor']:
        """
        Returns a tuple of two HSLuvColor objects representing the triadic color variants.

        Triadic colors are three colors evenly spaced around the color wheel.
        """
        return compute_triadic_colors(self, factor=factor)

    def analogous_colors(self, factor: float = 1 / 8) -> Tuple['HSLuvColor', 'HSLuvColor']:
        """
        Returns a tuple of two HSLuvColor objects representing the analogous color variants.

        Analogous colors are groups of three colors that are next to each other on the color wheel,
        and a tertiary.
        """
        return compute_analogous_colors(self, factor=factor)

    def analogous_color(self, factor: float = 1 / 8) -> Tuple['HSLuvColor', 'HSLuvColor']:
        """
        Returns a tuple of two HSLuvColor objects representing the analogous color variants.

        Analogous colors are groups of three colors that are next to each other on the color wheel,
        and a tertiary.
        """
        return compute_analogous_colors(self, factor=factor)

    def equidistant_variants(self, factor: float) -> Tuple['HSLuvColor', 'HSLuvColor']:
        """
        Returns two color variants equidistant from this color's hue.

        Args:
            factor (float): The factor by which to offset the hue in both directions.

        Returns:
            Tuple['HSLuvColor', 'HSLuvColor']: A tuple containing two HSLuvColor objects.
        """
        return compute_equidistant_variants(self, factor=factor)


ColorUnion = Union[str, Tuple[float, float, float], Tuple[float, float, float, float], HSLuvColor, None]


def to_hsluv_color(color: ColorUnion) -> HSLuvColor:
    """
    Converts various color representations into an HSLuvColor object.

    Args:
        color (ColorUnion): The color to convert. Can be a string (e.g., "50H"),
                            a tuple (H, S, L) or (H, S, L, A), or an existing HSLuvColor object.

    Returns:
        HSLuvColor: The converted HSLuvColor object.
    """
    if isinstance(color, HSLuvColor):
        return color
    elif isinstance(color, str):
        return HSLuvColor(*hsla_string_to_hsl_tuple(color))
    elif isinstance(color, (tuple, list)):
        return HSLuvColor(*color)
    elif color is None:
        return HSLuvColor(0, 0, 0, 0)
    else:
        raise TypeError(f"Unsupported color type: {type(color)}")


def random_alpha(low: float = 0, high: float = 1) -> Tuple[float, float, float, float]:
    """Generates a random alpha value."""
    return 0, 0, 0, random.uniform(low, high)
