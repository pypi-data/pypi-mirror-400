import os

root_dir = None


def find_root_path(start_path=None):
    # If start_path is None, use the current execution path
    if root_dir:
        return root_dir

    if start_path is None:
        start_path = os.path.dirname(__file__)

    current_path = os.path.abspath(start_path)

    while current_path != os.path.dirname(current_path):  # Until we reach the root directory
        potential_flag_file = os.path.join(current_path, 'wd')

        if os.path.isfile(potential_flag_file):
            return current_path

        current_path = os.path.dirname(current_path)  # Move one level up

    return None  # Return None if no folder with 'wd' is found


def path_from_root(*path):
    # Find the root path using the find_root_path function
    root_path = find_root_path()

    if root_path is None:
        raise FileNotFoundError("Root path with 'wd' file not found.")

    # Join the root path with the provided path
    full_path = os.path.join(root_path, *path)
    full_path = os.path.abspath(full_path)

    return full_path
