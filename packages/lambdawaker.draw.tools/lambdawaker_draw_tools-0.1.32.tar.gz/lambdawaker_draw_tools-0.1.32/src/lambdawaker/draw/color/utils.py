import random
import re
from typing import Tuple, Dict, Union

from lambdawaker.random.values import DefaultValue


def clamp_hue(raw_val: float, h_range: Tuple[float, float]) -> float:
    """
    Clamps a hue value to a specific range, handling circular wrapping.

    If the range covers the full circle (e.g., 0-360), the value is simply wrapped.
    Otherwise, it is clamped to the nearest bound of the specified arc.

    Args:
        raw_val (float): The input hue value.
        h_range (tuple): A tuple (min, max) defining the allowed hue range.

    Returns:
        float: The clamped hue value.
    """
    val = raw_val % 360
    h_min, h_max = h_range

    if (h_min % 360) == (h_max % 360):
        return val

    if is_inside(val, h_range):
        return val

    dist_to_min = min(abs(val - h_min), 360 - abs(val - h_min))
    dist_to_max = min(abs(val - h_max), 360 - abs(val - h_max))

    return h_min if dist_to_min < dist_to_max else h_max


def clamp(val: float, range_tuple: Tuple[float, float]) -> float:
    """
    Clamps a value to be within the specified range (inclusive).

    Args:
        val (float): The value to clamp.
        range_tuple (tuple): A tuple (min, max) defining the range.

    Returns:
        float: The clamped value.
    """
    return max(range_tuple[0], min(val, range_tuple[1]))


def parse_unit(s: str) -> Tuple[float, str]:
    """
    Parses a string containing a number and a unit suffix (e.g., "50H").

    Args:
        s (str): The string to parse.

    Returns:
        tuple: A tuple (value, unit) where value is a float and unit is a string.

    Raises:
        ValueError: If the string format is invalid.
    """
    # Matches: optional minus, digits/decimals, then letters
    match = re.match(r"([-+]?\d*\.?\d+)\s*([a-zA-Z]+)", s.strip())

    if match:
        val, unit = match.groups()
        return float(val), unit

    raise ValueError(f"Invalid format: {s}")


def parse_multi_unit(format_str: str) -> Dict[str, float]:
    """
    Parses a string containing multiple unit-value pairs (e.g., '-10h5s20l').

    Args:
        format_str (str): The string to parse.

    Returns:
        dict: A dictionary mapping unit characters (lowercase) to their float values.

    Raises:
        ValueError: If no valid components are found.
    """
    # Pattern looks for:
    # 1. An optional plus or minus [+-]?
    # 2. Digits and an optional decimal \d+\.?\d*
    # 3. The unit label [hsl] (case-insensitive)
    pattern = r"([+-]?(?:\d+\.?\d*|\.\d+))\s*(\w)"

    matches = re.findall(pattern, format_str.lower())

    if not matches:
        raise ValueError(f"Could not parse any color components from: {format_str}")

    return {unit: float(val) for val, unit in matches}


def parse_hsla_string(format_str: str) -> Dict[str, float]:
    """
    Parses an HSL modification string into a dictionary of offsets.

    Defaults to 0 for any missing component (h, s, or l).

    Args:
        format_str (str): The string to parse (e.g., "10H -5L").

    Returns:
        dict: A dictionary with keys 'h', 's', 'l' and their float values.
    """
    raw = parse_multi_unit(format_str)
    default = {
        "h": 0,
        "s": 0,
        "l": 0,
        "a": 0
    }

    default.update(raw)
    return default


def hsla_string_to_hsl_tuple(format_str: str) -> Tuple[float, float, float, float]:
    """
    Parses an HSL modification string into a tuple of (h, s, l) offsets.

    Args:
        format_str (str): The string to parse.

    Returns:
        tuple: A tuple (h, s, l) of float offsets.
    """
    raw = parse_hsla_string(format_str)
    return raw["h"], raw["s"], raw["l"], raw["a"]


def is_inside(angle: float, arc: Tuple[float, float]) -> bool:
    """
    Checks if an angle is inside a given arc (range of angles).

    Handles wrap-around cases where the arc crosses 0/360 degrees.

    Args:
        angle (float): The angle to check.
        arc (tuple): A tuple (start, end) defining the arc.

    Returns:
        bool: True if the angle is inside the arc, False otherwise.
    """
    start, end = arc

    angle %= 360
    start %= 360
    end %= 360

    if start <= end:

        return start <= angle <= end
    else:

        return angle >= start or angle <= end


def get_from_tuple(t, index, default=None):
    return t[index] if -len(t) <= index < len(t) else default


def get_random_point_with_margin(size: Tuple[int, int], margin: int = 0, default: Union[Tuple, DefaultValue, None] = None) -> Tuple[int, int]:
    if isinstance(default, DefaultValue):
        return default.value

    if isinstance(default, tuple):
        return default

    w, h = size
    x = random.randint(margin, max(margin, w - margin))
    y = random.randint(margin, max(margin, h - margin))

    return x, y
