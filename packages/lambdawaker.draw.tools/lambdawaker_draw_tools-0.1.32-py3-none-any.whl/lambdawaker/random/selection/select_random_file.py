import os
import random


def select_random_file(path=None, extension_filter=None):
    extension_filter = extension_filter if extension_filter is not None else []
    options = [os.path.join(path, f) for f in os.listdir(path)]

    if len(extension_filter):
        options = [
            f for f in options
            if os.path.splitext(f) in extension_filter or os.path.isdir(f)
        ]

    option = random.choice(options)

    if os.path.isfile(option):
        return option

    return select_random_file(path=option)
