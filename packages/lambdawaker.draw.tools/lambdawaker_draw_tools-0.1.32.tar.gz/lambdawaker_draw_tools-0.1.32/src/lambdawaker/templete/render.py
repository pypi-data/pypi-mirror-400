import json
import os.path
from io import BytesIO
from types import SimpleNamespace

from PIL import Image
from jinja2 import Template

from lambdawaker.dataset.DiskDataset import DiskDataset
from lambdawaker.draw import card_background as card_background_module
from lambdawaker.draw.color.HSLuvColor import to_hsluv_color
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.file.path.ensure_directory import ensure_directory
from lambdawaker.file.path.wd import path_from_root
from lambdawaker.log.Profiler import Profiler
from lambdawaker.reflection.query import select_random_function_from_module_and_submodules
from lambdawaker.templete.PlaywrightRenderer import PlaywrightRenderer
from lambdawaker.templete.fields import field_generators
from lambdawaker.process.process_in_parrallel import process_parallel


def render_layer(page, html_content: str):
    """
    Renders HTML content to a PNG in memory, extracts bounding boxes, and specifically
    handles local image loading using Playwright's route() method.
    """

    captured_elements_data = []

    page.set_content(html_content)
    page.wait_for_selector('#view-port')

    card = page.query_selector('#view-port')
    image_bytes = card.screenshot(omit_background=True)

    elements = page.query_selector_all('*[capture="true"]')

    for i, element in enumerate(elements):
        bounding_box = element.bounding_box()

        if bounding_box:
            tag_name = element.evaluate('e => e.tagName')

            element_info = {
                "index": i,
                "tag": tag_name,
                "bounding_box": {
                    "x": bounding_box["x"],
                    "y": bounding_box["y"],
                    "width": bounding_box["width"],
                    "height": bounding_box["height"]
                },
                "source": element.get_attribute('src') if tag_name == 'IMG' else "Text Element"
            }
            captured_elements_data.append(element_info)

    return image_bytes, captured_elements_data


def render_layers(
        template_path,
        renderer,
        template_data=None,
        env=None,
        data=None
):
    valid_extensions = ['.html', '.j2']
    layers = {}

    for template in os.listdir(template_path):
        file_ext = os.path.splitext(template)[1]
        if file_ext not in valid_extensions:
            continue

        with open(os.path.join(template_path, template), 'r') as f:
            html_template = f.read()

        layer_name = os.path.splitext(template)[0]

        template = Template(html_template)

        rendered_html = template.render(
            template_data=template_data,
            gen=field_generators,
            ds=renderer.data_source_handler,
            tx={
                "str": str,
                "len": len
            },
            env=env,
            data=data
        )

        image_bytes, captured_elements_data = render_layer(
            renderer.page, rendered_html
        )

        pil_image = Image.open(BytesIO(image_bytes))

        layers[layer_name] = SimpleNamespace(
            name=layer_name,
            elements=captured_elements_data,
            image=pil_image
        )

    return layers


def render_template(template_path, renderer, env=None, data=None, cache=None):
    profiler = Profiler(verbose=False)

    cache = cache if cache is not None else {}

    profiler.start("render_template")
    profiler.start("load_template_data")

    common_data_path = os.path.join(template_path, "meta/common.json")
    if common_data_path not in cache:
        with open(common_data_path, 'r') as f:
            cache[common_data_path] = json.load(f)
    template_data = cache[common_data_path]

    meta_data_path = os.path.abspath(f"{template_path}/meta/meta.json")
    if meta_data_path not in cache:
        with open(meta_data_path, 'r') as f:
            cache[meta_data_path] = json.load(f)
    meta_data = cache[meta_data_path]
    profiler.finalize("load_template_data")

    profiler.start("render_layers")
    layers = render_layers(
        template_path,
        renderer=renderer,
        template_data=template_data,
        data=data,
        env=env
    )
    profiler.finalize("render_layers")

    profiler.start("add_background_layer")

    first_layer = layers[meta_data["order"][1]]

    profiler.start("select_background_paint_function")
    background_paint_function = select_random_function_from_module_and_submodules(card_background_module, "generate_card_background_.*")
    profiler.finalize("select_background_paint_function")

    paint_function_label = f"background_paint_function {background_paint_function.__name__}"
    profiler.start(paint_function_label)
    card_background = background_paint_function(
        first_layer.image.size,
        env["theme"]["primary_color"]
    )
    profiler.finalize(paint_function_label)

    layers["background_layer"] = SimpleNamespace(
        name="background_layer",
        elements=[],
        image=card_background
    )
    profiler.finalize("add_background_layer")
    profiler.finalize("render_template")
    return layers, meta_data


def render_record(renderer, record, record_id, cache=None):
    template_path = path_from_root("assets/templates/2016")

    primary_color = generate_hsluv_text_contrasting_color()
    text_color_hex = to_hsluv_color((0, 0, 0, 1))

    default_env = {
        "theme": {
            "primary_color": primary_color,
            "text_color": text_color_hex
        }
    }

    layers, meta_data = render_template(
        template_path,
        env=default_env,
        data={
            "id": record_id,
            "record": record
        },
        renderer=renderer,
        cache=cache
    )

    bg_layer = layers["background_layer"]

    canvas = Image.new("RGBA", bg_layer.image.size)

    for name in meta_data["order"]:
        data = layers[name]
        canvas.paste(data.image, (0, 0), data.image)

    ensure_directory("./output/")
    canvas.save(f"./output/{record_id}.png")


process_env = {}


def proces_initializer():
    person_ds = DiskDataset("lambdaWalker/ds.photo_id")
    person_ds.load("@DS/lw_person_V0.0.0")
    renderer = PlaywrightRenderer([person_ds])
    cache = {}
    global process_env

    process_env = {
        "person_ds": person_ds,
        "renderer": renderer,
        "cache": cache
    }


def render_worker(record_id, skip_existing=True):
    person_ds = process_env["person_ds"]
    renderer = process_env["renderer"]
    cache = process_env["cache"]

    if not (skip_existing and os.path.exists(f"./output/{record_id}.png")):
        record = person_ds[record_id]
        render_record(
            record_id=record_id,
            record=record,
            renderer=renderer,
            cache=cache
        )


def render_records_parallel(num_processes=None, skip_existing=True):
    temp_ds = DiskDataset("lambdaWalker/ds.photo_id")
    temp_ds.load("@DS/lw_person_V0.0.0")
    limit = len(temp_ds)
    del temp_ds

    process_parallel(
        list(range(limit)),
        render_worker,
        initializer=proces_initializer,
        kargs={"skip_existing": skip_existing},
        num_processes=num_processes
    )


if __name__ == "__main__":
    render_records_parallel(skip_existing=False)
