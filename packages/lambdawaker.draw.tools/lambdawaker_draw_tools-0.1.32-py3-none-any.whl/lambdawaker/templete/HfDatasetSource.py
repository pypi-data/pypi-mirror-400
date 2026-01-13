import random

from datasets import load_dataset


class HfDatasetSource:
    def __init__(self, dataset_id: str):
        self.dataset = load_dataset(dataset_id)
        self.id = dataset_id

    def __getitem__(self, item):
        path = item.split("/")
        split_name = path[0]
        split = self.dataset[split_name]
        key = path[1]

        if key == "len":
            return len(split)

        elif key == "random":
            limit = len(split)
            return split[random.randint(0, limit)]
        elif key.isdigit():
            key = int(key)
            path_size = len(path)

            if path_size == 2:
                return split[key]
            elif path_size == 3:
                field = path[2]
                data = split[key][field]
                return data

        raise ValueError(f"Unsupported data type: {path}")
