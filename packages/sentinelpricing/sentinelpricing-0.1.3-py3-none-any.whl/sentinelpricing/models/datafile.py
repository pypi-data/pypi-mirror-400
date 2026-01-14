import importlib.resources

from pathlib import Path

from abc import ABC
from typing import IO


class DataFile(ABC):
    """
    Context manager for opening a resource file from a package.

    This class abstracts the details of opening a file resource using
    importlib.resources. It supports opening the file in either text or
    binary mode, and is intended to be used with a "with" statement.

    Strictly speaking this is only necessary when using Sentinel Frameworks
    in modules that you intend to share, as it removes the need to know exactly
    where the file is stored.

    Attributes:
        path: Path to the data file in your module
            '{your_module_name}/data/file.csv'
        mode: The file mode ("t" for text or "b" for binary).
    """

    def __init__(self, path: str, mode: str = "t") -> None:
        """
        Initialize the ModuleFile context manager.

        Args:
            path: Path to the data file in your module
                '{your_module_name}/data/file.csv'
            mode: The file mode ("t" for text or "b" for binary).

        """
        self.path = Path(path)
        self.mode = mode

    def __enter__(self) -> IO:
        """
        Open the resource file and return the file object.

        The file is opened using the appropriate importlib.resources function
        based on the mode specified at initialization.

        Returns:
            A file-like object opened in the specified mode.
        """
        package_name = self.path.parts[0]
        filepath = Path(*self.path.parts[1:])
        if self.mode == "t":
            self._file = importlib.resources.open_text(
                package_name, *filepath.parts, encoding="utf-8"
            )

        if self.mode == "b":
            return importlib.resources.open_binary(
                package_name, *filepath.parts
            )

        if self._file is None:
            raise FileNotFoundError("Either Module or Path is incorrect")

        return self._file

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Close the resource file upon exiting the context.

        Args:
            exc_type: The exception type, if an exception occurred.
            exc_value: The exception value, if an exception occurred.
            traceback: The traceback, if an exception occurred.
        """
        if self._file is not None:
            self._file.close()
