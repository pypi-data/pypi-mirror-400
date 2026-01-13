from abc import ABC, abstractmethod
from typing import Dict, Any


class Dataset(ABC):
    """
    Abstract base class defining the interface for a dataset.

    A Dataset provides methods to load, access, modify, and manage a collection of records.
    """

    @abstractmethod
    def load(self, root_path: str, manifest_name: str = "manifest.yaml"):
        """
        Initialize the dataset and manifest.

        Args:
            root_path (str): The root directory path of the dataset.
            manifest_name (str, optional): The name of the manifest file. Defaults to "manifest.yaml".
        """
        pass

    @abstractmethod
    def record_by_name(self, record_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific record by its ID.

        Args:
            record_id (str): The unique identifier of the record.

        Returns:
            Dict[str, Any]: A dictionary containing the record's data.
        """
        pass

    @abstractmethod
    def random(self) -> Dict[str, Any]:
        """
        Retrieve a random record from the dataset.

        Returns:
            Dict[str, Any]: A dictionary containing a random record's data.
        """
        pass

    @abstractmethod
    def insert(self, record_id: str, data: Dict[str, Any]):
        """
        Create or update a record.

        Args:
            record_id (str): The unique identifier for the new or existing record.
            data (Dict[str, Any]): The data to be stored for the record.
        """
        pass

    @abstractmethod
    def delete(self, record_id: str):
        """
        Remove a record and its associated files.

        Args:
            record_id (str): The unique identifier of the record to delete.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        Return the total number of records in the dataset.

        Returns:
            int: The count of records.
        """
        pass

    @abstractmethod
    def __getitem__(self, record_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific record by its ID using indexing syntax.

        Args:
            record_id (str): The unique identifier of the record.

        Returns:
            Dict[str, Any]: A dictionary containing the record's data.
        """
        pass
