from abc import ABC, abstractmethod


class DataProvider(ABC):
    """
    Abstract base class defining the interface for a data provider.

    A DataProvider handles low-level storage operations like reading, writing,
    listing, and deleting files.
    """

    @abstractmethod
    def pointTo(self, root_path: str):
        """
        Sets the root path for the provider.

        Args:
            root_path (str): The root directory path.
        """
        pass

    @abstractmethod
    def serve(self, relative_path: str):
        """
        Reads and returns the content of a file.

        Args:
            relative_path (str): The path to the file relative to the root.

        Returns:
            bytes: The content of the file.
        """
        pass

    @abstractmethod
    def list(self, relative_path: str):
        """
        Lists the contents of a directory.

        Args:
            relative_path (str): The path to the directory relative to the root.

        Returns:
            list: A list of file/directory names.
        """
        pass

    @abstractmethod
    def count(self, relative_path: str):
        """
        Counts the number of items in a directory.

        Args:
            relative_path (str): The path to the directory relative to the root.

        Returns:
            int: The number of items.
        """
        pass

    @abstractmethod
    def store(self, content, relative_path: str):
        """
        Writes content to a file.

        Args:
            content (Union[str, bytes]): The content to write.
            relative_path (str): The path to the file relative to the root.
        """
        pass

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        """
        Check if a file or directory exists.

        Args:
            relative_path (str): The path to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        pass

    @abstractmethod
    def info(self, relative_path: str) -> dict:
        """
        Get metadata like size and timestamps.

        Args:
            relative_path (str): The path to the file/directory.

        Returns:
            dict: A dictionary containing metadata.
        """
        pass

    @abstractmethod
    def search(self, pattern: str, relative_path: str) -> list:
        """
        Find files matching a pattern (e.g. *.csv).

        Args:
            pattern (str): The glob pattern to match.
            relative_path (str): The directory to search in.

        Returns:
            list: A list of matching file paths.
        """
        pass

    @abstractmethod
    def delete(self, relative_path: str):
        """
        Remove a file or empty directory.

        Args:
            relative_path (str): The path to remove.
        """
        pass
