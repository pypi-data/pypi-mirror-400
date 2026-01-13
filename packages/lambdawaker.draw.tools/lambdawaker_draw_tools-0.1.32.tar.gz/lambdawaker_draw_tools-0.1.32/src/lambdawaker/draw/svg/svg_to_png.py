from io import BytesIO
from xml.etree import ElementTree

import cairosvg
from PIL import Image


def svg_to_png(path, size=None):
    """
    Convert an SVG file to a PNG image.

    Parameters:
    path (str): Path to the SVG file.
    size (tuple): Optional (width, height) size for the output PNG. If None, keeps original size.

    Returns:
    PIL.Image: The converted PNG image.
    """
    if size is not None:
        # Calculate scale to achieve the desired size
        svg_size = get_svg_size(path)

        target_width, target_height = size
        scale_w = target_width / svg_size[0]
        scale_h = target_height / svg_size[1]
        scale = min(scale_w, scale_h)

        png_data = cairosvg.svg2png(url=path, scale=scale)
    else:
        png_data = cairosvg.svg2png(url=path)

    return Image.open(BytesIO(png_data))


def get_svg_size(svg_path):
    """
    Get the size of an SVG file.

    Parameters:
    svg_path (str): Path to the SVG file.

    Returns:
    tuple: Width and height of the SVG.
    """
    try:
        tree = ElementTree.parse(svg_path)
        root = tree.getroot()

        # The SVG namespace
        namespace = {'svg': 'http://www.w3.org/2000/svg'}

        # Get the width and height attributes
        width = root.attrib.get('width')
        height = root.attrib.get('height')

        if width is None or height is None:
            # If width and height are not directly specified, try to get the viewBox attribute
            viewBox = root.attrib.get('viewBox')
            if viewBox:
                _, _, width, height = viewBox.split()

        # Convert width and height to float
        width = float(width)
        height = float(height)

        return width, height

    except Exception as e:
        print(f"An error occurred reading the size of {svg_path}: {e}")
        return None, None
