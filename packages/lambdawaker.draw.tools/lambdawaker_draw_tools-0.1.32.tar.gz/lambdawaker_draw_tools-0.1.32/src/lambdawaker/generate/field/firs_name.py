import html
import os

from lambdawaker.file.path.wd import path_from_root
from lambdawaker.random.selection.select_random_word_from_nested_directory import select_random_word_from_nested_directory


def generate_first_name():
    db_path = path_from_root("assets/text/first_name") + os.sep

    name, source = select_random_word_from_nested_directory(
        db_path
    )

    return {
        "data": html.escape(name),
        "source": source
    }


def vis():
    print(generate_first_name())


if __name__ == "__main__":
    vis()
