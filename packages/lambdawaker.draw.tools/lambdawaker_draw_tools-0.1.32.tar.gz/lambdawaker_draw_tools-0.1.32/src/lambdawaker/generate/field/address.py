import os
import random

from lambdawaker.file.path.wd import path_from_root
from lambdawaker.random.selection.select_random_word_from_nested_directory import select_random_word_from_nested_directory


def generate_road_name():
    name_db = path_from_root("assets/text/address/road/name_db") + os.sep
    type_db = path_from_root("assets/text/address/road/type_db") + os.sep

    name, name_source = select_random_word_from_nested_directory(name_db)
    road_type, road_type_source = select_random_word_from_nested_directory(type_db)

    return {
        "data": f"{road_type} {name}",
        "source": [road_type_source, name_source]
    }


def generate_block_name():
    name_db = path_from_root("assets/text/address/block/name_db") + os.sep
    type_db = path_from_root("assets/text/address/block/type_db") + os.sep

    name, name_source = select_random_word_from_nested_directory(name_db)
    road_type, road_type_source = select_random_word_from_nested_directory(type_db)

    return {
        "data": f"{road_type} {name}",
        "source": [road_type_source, name_source]
    }


def generate_city_name():
    db_path = path_from_root("assets/text/address/city") + os.sep

    name, name_source = select_random_word_from_nested_directory(db_path)

    return {
        "data": name,
        "source": name_source
    }


def generate_state_name():
    db_path = path_from_root("assets/text/address/state") + os.sep

    name, name_source = select_random_word_from_nested_directory(db_path)

    return {
        "data": name,
        "source": name_source
    }


def generate_country_name():
    db_path = path_from_root("assets/text/address/country") + os.sep

    name, name_source = select_random_word_from_nested_directory(db_path)

    return {
        "data": name,
        "source": name_source
    }


def generate_address_number():
    return {
        "data": str(random.randint(1, 9999)),
        "source": "random/1-9999"
    }


def vis():
    print(generate_road_name())
    print(generate_block_name())
    print(generate_city_name())
    print(generate_state_name())
    print(generate_country_name())
    print(generate_address_number())


if __name__ == "__main__":
    vis()
