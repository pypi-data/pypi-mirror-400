from PIL import Image, ImageFilter


def draw_shadow_for_shape(shape_image, shadow_color=(0, 0, 0), shadow_opacity=128, blur_radius=5, offset=(0, 0)):
    """
    Draw a shadow for a PNG image with transparency.

    Parameters:
    shape_image (PIL.Image): The transparent PNG image containing the shape.
    shadow_color (tuple): RGB color of the shadow. Defaults to black (0, 0, 0).
    shadow_opacity (int): Opacity of the shadow (0-255). Defaults to 128.
    blur_radius (int): Radius of the Gaussian blur for the shadow. Defaults to 10.
    offset (tuple): (x, y) offset of the shadow from the original shape. Defaults to (5, 5).

    Returns:
    PIL.Image: Image with the shadow applied behind the original shape.
    """
    width, height = shape_image.size
    offset_x, offset_y = offset

    # Create a new image large enough to contain both shape and shadow
    expanded_width = width + abs(offset_x) + blur_radius * 2
    expanded_height = height + abs(offset_y) + blur_radius * 2

    result = Image.new('RGBA', (expanded_width, expanded_height), (0, 0, 0, 0))

    # Extract alpha channel from the shape
    alpha = shape_image.split()[3] if shape_image.mode == 'RGBA' else shape_image.convert('RGBA').split()[3]

    # Create shadow layer
    shadow = Image.new('RGBA', (expanded_width, expanded_height), (0, 0, 0, 0))
    shadow_with_color = Image.new('RGBA', shape_image.size, shadow_color + (shadow_opacity,))

    # Position the shadow
    shadow_x = blur_radius + max(0, offset_x)
    shadow_y = blur_radius + max(0, offset_y)
    shadow.paste(shadow_with_color, (shadow_x, shadow_y), alpha)

    # Apply blur to shadow
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

    # Paste the original shape on top
    shape_x = blur_radius + max(0, -offset_x)
    shape_y = blur_radius + max(0, -offset_y)

    result.paste(shadow, (0, 0), shadow)
    result.paste(shape_image, (shape_x, shape_y), shape_image)

    return result
