from typing import Union

from PIL import Image

from lambdawaker.draw import fill as fill_module
from lambdawaker.draw import grid as grid_module
from lambdawaker.draw import waves as waves_module
from lambdawaker.draw.color.HSLuvColor import random_alpha, ColorUnion
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.random.values import Random
from lambdawaker.reflection.query import select_random_function_from_module_and_submodules


def generate_card_background_type_b(size=(800, 600), primary_color: Union[ColorUnion | Random] = Random):
    if primary_color == Random:
        primary_color = generate_hsluv_text_contrasting_color()

    width, height = size

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    background_paint_function = select_random_function_from_module_and_submodules(fill_module, "paint_random_.*")
    background_details = select_random_function_from_module_and_submodules(grid_module, "paint_random_.*")
    lines_details = select_random_function_from_module_and_submodules(waves_module, "paint_random_.*")

    draw_functions = [background_paint_function, background_details, lines_details]

    colors = [
        primary_color,
        primary_color.close_color() - random_alpha(.4, .8),
        primary_color.close_color() - random_alpha(.4, .8),
    ]

    for i, func in enumerate(draw_functions):
        func(
            img,
            primary_color=colors[i],
        )

    return img


def vis():
    card = generate_card_background_type_b()
    card.show()


if __name__ == "__main__":
    vis()
