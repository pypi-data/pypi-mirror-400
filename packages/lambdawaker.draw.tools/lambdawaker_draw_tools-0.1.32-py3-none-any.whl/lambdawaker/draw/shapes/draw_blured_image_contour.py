import cv2
import numpy as np
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color


def draw_contour(pil_image, color: ColorUnion, stroke_color: ColorUnion):
    color = to_hsluv_color(color)
    stroke_color = to_hsluv_color(stroke_color)

    margin = 12
    width, height = pil_image.size
    bg_color = color - "1a"

    padded_image = Image.new("RGBA", (width + 2 * margin, height + 2 * margin), bg_color.to_rgba())
    padded_image.paste(pil_image, (margin, margin))

    img_array = np.array(padded_image.convert("RGBA"))

    alpha = img_array[:, :, 3]
    _, binary = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contour_canvas = np.zeros_like(img_array)

    cv2.drawContours(contour_canvas, contours, -1, color.to_rgba(), thickness=cv2.FILLED, lineType=cv2.LINE_AA)
    cv2.drawContours(contour_canvas, contours, -1, stroke_color.to_rgba(), thickness=4, lineType=cv2.LINE_AA)

    blurred_contour = cv2.GaussianBlur(contour_canvas, (5, 5), 0)
    blurred_contour = cv2.GaussianBlur(blurred_contour, (5, 5), 0)

    new_img = Image.fromarray(blurred_contour)

    return new_img
