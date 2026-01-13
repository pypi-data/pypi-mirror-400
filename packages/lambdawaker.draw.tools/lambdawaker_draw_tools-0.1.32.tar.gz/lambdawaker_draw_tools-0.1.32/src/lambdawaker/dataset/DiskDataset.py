import pathlib
import random
import re
from typing import Dict, Any, Union, Optional

import yaml

from lambdawaker.dataset.DataProvider import DataProvider
from lambdawaker.dataset.Dataset import Dataset
from lambdawaker.dataset.DiskProvider import DiskProvider
from lambdawaker.dataset.FieldCaster import FieldCaster
from lambdawaker.dataset.Record import Record


class DiskDataset(Dataset):
    """
    A dataset implementation that stores and retrieves data from the local disk.

    This class uses a manifest file (e.g., 'manifest.yaml') to define the structure
    of the dataset, including the fields and their storage locations.
    """

    def __init__(self, dataset_id: str, provider: Optional[DataProvider] = None, read_only: bool = False):
        """
        Initializes the dataset.

        Args:
            provider (Optional[DataProvider], optional): A data provider instance.
                If no provider is given, it defaults to a DiskProvider.
        """
        self.provider = provider if provider is not None else DiskProvider()
        self.manifest = None
        self.record_ids = []
        self.read_only = read_only
        self.id = dataset_id

    def load(self, root_path: str, manifest_name: str = "manifest.yaml"):
        """
        Loads the dataset from the specified root path and manifest file.

        Args:
            root_path (str): The root directory of the dataset.
            manifest_name (str, optional): The name of the manifest file. Defaults to "manifest.yaml".
        """
        self.provider.pointTo(root_path)

        # 1. Load the YAML manifest using the provider
        raw_manifest = self.provider.serve(manifest_name)
        self.manifest = yaml.safe_load(raw_manifest)

        # 2. Synchronize the internal ID list
        self._refresh_ids()

    def _refresh_ids(self):
        """Scans the first field's directory to find valid Record IDs."""
        if not self.manifest or not self.manifest.get('fields'):
            return

        master_field = self.manifest['fields'][0]
        pattern = self.manifest.get('filename_pattern', "{id}")

        # Build a regex to extract the 'id' part from filenames
        # Escapes literals and converts {id} into a named capture group
        regex_str = re.escape(pattern).replace(r'\{id\}', r'(?P<id>.+)')
        regex = re.compile(f"^{regex_str}$")

        # List files in the directory of the primary source (e.g., 'img/')
        files = self.provider.list(master_field['source'])

        self.record_ids = []
        for f in files:
            stem = pathlib.Path(f).stem
            match = regex.match(stem)
            if match:
                self.record_ids.append(match.group('id'))

    def _find_file_for_id(self, folder: str, record_id: str) -> str:
        """Helper to find the actual filename (with extension) for an ID."""
        pattern = self.manifest.get('filename_pattern', "{id}")
        target_stem = pattern.format(id=record_id)

        for f in self.provider.list(folder):
            if pathlib.Path(f).stem == target_stem:
                return f
        raise FileNotFoundError(f"No file found for ID '{record_id}' in '{folder}'")

    def record_by_name(self, record_id: str) -> Record:
        """
        Retrieves a single record from the dataset by its ID.

        Args:
            record_id (str): The ID of the record to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the data for the requested record.
        """
        result = {"id": record_id}

        for field in self.manifest['fields']:
            name = field['name']
            folder = field['source']

            rel_path = self._find_file_for_id(folder, record_id)
            raw_data = self.provider.serve(rel_path)

            # Using the new FieldCaster
            result[name] = FieldCaster.cast(raw_data, field['type'])
        return Record(result)

    def random(self) -> Dict[str, Any]:
        """
        Retrieves a random record from the dataset.

        Returns:
            Dict[str, Any]: A dictionary containing the data for a random record.
        """
        if not self.record_ids:
            raise IndexError("Dataset is empty.")
        return self.record_by_name(random.choice(self.record_ids))

    def insert(self, record_id: str, data: Dict[str, Any]):
        """
        Inserts or updates a record in the dataset.

        Args:
            record_id (str): The ID of the record to insert or update.
            data (Dict[str, Any]): The data for the record.
        """
        if self.read_only:
            raise RuntimeError("Cannot insert into read-only dataset.")

        pattern = self.manifest.get('filename_pattern', "{id}")
        filename_base = pattern.format(id=record_id)

        for field in self.manifest['fields']:
            name = field['name']
            if name not in data: continue

            # Use FieldCaster to turn Python object into bytes
            content = FieldCaster.serialize(data[name], field['type'])

            # Determine extension (could be added to FieldCaster too)
            ext_map = {
                'json': '.json',
                'yaml': '.yaml',
                'str': '.txt',
                'int': '.txt',
                'float': '.txt',
                'xml': '.xml',
                'svgDoc': '.svg',
                'numpy': '.npy',
                'PilImage': '.png',
                'npImage': '.png'
            }
            ext = ext_map.get(field['type'], '.bin')

            path = f"{field['source']}/{filename_base}{ext}"
            self.provider.store(content, path)

        if record_id not in self.record_ids:
            self.record_ids.append(record_id)

    def delete(self, record_id: str):
        """
        Deletes a record from the dataset.

        Args:
            record_id (str): The ID of the record to delete.
        """
        if self.read_only:
            raise RuntimeError("Cannot insert into read-only dataset.")

        for field in self.manifest['fields']:
            try:
                path = self._find_file_for_id(field['source'], record_id)
                self.provider.delete(path)
            except FileNotFoundError:
                continue
        self.record_ids = [rid for rid in self.record_ids if rid != record_id]

    def __len__(self) -> int:
        """
        Returns the number of records in the dataset.

        Returns:
            int: The number of records.
        """
        return len(self.record_ids)

    def __getitem__(self, key: Union[int, str]) -> Record:
        """
        Allows accessing records using dataset[index] or dataset['record_id'].

        Args:
            key: If int, retrieves by index in the discovered record_ids.
                 If str, retrieves by the specific record ID.
        """
        if isinstance(key, int):
            if key < 0:
                key = key % len(self.record_ids)

            if key > len(self.record_ids):
                raise IndexError(f"Dataset index {key} out of range.")

            return self.record_by_name(self.record_ids[key])


        elif isinstance(key, str):
            return self.__str__getitem__(key)

        else:
            raise TypeError("Key must be an integer index or a string Record ID.")

    def __str__getitem__(self, item):
        path = item.split("/")

        split = self
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
                return split[key][field]

        raise ValueError(f"Unsupported data type: {path}")
