import os
from typing import List

from PIL import Image


class ImageSequence:
    """
    A class to represent a sequence of images from a directory.
    """

    def __init__(self, path: str):
        """
        Initialize with a path to a directory containing images.

        Args:
            path (str): The path to the directory.
        """
        if not os.path.isdir(path):
            raise ValueError(f"The path '{path}' is not a valid directory.")

        self.path = path

        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}

        self.image_files: List[str] = sorted([
            f for f in os.listdir(path)
            if os.path.splitext(f)[1].lower() in valid_extensions
        ])

    def __len__(self) -> int:
        """
        Returns the total number of valid images in the folder.

        Returns:
            int: The number of images.
        """
        return len(self.image_files)

    def __getitem__(self, index: int) -> Image.Image:
        """
        Returns the image at the specified index as a PIL Image object.

        Args:
            index (int): The index of the image to retrieve.

        Returns:
            Image.Image: The PIL Image object.
        """
        file_name = self.image_files[index]
        full_path = os.path.join(self.path, file_name)
        return Image.open(full_path)
