import pathlib
import datetime
import fnmatch
from typing import List, Dict, Union, Any

from lambdawaker.file.path.PathResolver import resolve


class DiskProvider:
    """
    A DataProvider implementation for local disk storage.
    """

    def __init__(self):
        self.root: pathlib.Path = None

    def pointTo(self, root_path: str):
        """Sets the base directory for all operations."""
        self.root = resolve(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, relative_path: str) -> pathlib.Path:
        """Internal helper to resolve paths and prevent escaping the root."""
        if self.root is None:
            raise ValueError("Provider not initialized. Call pointTo(path) first.")

        # Joining and resolving prevents '../' attacks
        full_path = (self.root / relative_path).resolve()

        if not str(full_path).startswith(str(self.root)):
            raise PermissionError("Access denied: Path is outside the root directory.")
        return full_path

    # --- Core Methods ---

    def serve(self, relative_path: str) -> bytes:
        """Reads and returns file content as bytes."""
        path = self._get_full_path(relative_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {relative_path}")
        return path.read_bytes()

    def list(self, relative_path: str = ".") -> List[str]:
        """Lists all items in the directory (relative to root)."""
        path = self._get_full_path(relative_path)
        if not path.is_dir():
            return []
        return [str(p.relative_to(self.root)) for p in path.iterdir()]

    def count(self, relative_path: str = ".") -> int:
        """Counts items in a directory. Fails if path is a file."""
        path = self._get_full_path(relative_path)
        if not path.is_dir():
            raise ValueError(f"'{relative_path}' is not a directory.")
        return sum(1 for _ in path.iterdir())

    def store(self, content: Union[str, bytes], relative_path: str):
        """Writes content to disk, creating parent directories if needed."""
        path = self._get_full_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        mode = 'wb' if isinstance(content, bytes) else 'w'
        encoding = None if isinstance(content, bytes) else 'utf-8'

        with open(path, mode, encoding=encoding) as f:
            f.write(content)

    # --- Advanced Utility Methods ---

    def exists(self, relative_path: str) -> bool:
        """Returns True if the path exists."""
        return self._get_full_path(relative_path).exists()

    def info(self, relative_path: str) -> Dict[str, Any]:
        """Returns metadata about a file or directory."""
        path = self._get_full_path(relative_path)
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {relative_path}")

        stats = path.stat()
        return {
            "name": path.name,
            "size_bytes": stats.st_size,
            "modified": datetime.datetime.fromtimestamp(stats.st_mtime),
            "is_file": path.is_file(),
            "extension": path.suffix
        }

    def search(self, pattern: str, relative_path: str = ".") -> List[str]:
        """Finds files matching a glob pattern (e.g., '*.csv')."""
        path = self._get_full_path(relative_path)
        if not path.is_dir():
            return []

        # rglob handles recursive search
        return [str(p.relative_to(self.root)) for p in path.rglob(pattern)]

    def delete(self, relative_path: str):
        """Removes a file or directory (if empty)."""
        path = self._get_full_path(relative_path)
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink(missing_ok=True)
