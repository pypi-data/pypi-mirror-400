import importlib.resources
import pickle
import os

from typing import IO, Any, Optional


class Model:
    """
    Context manager for opening a resource file from a package.

    This class abstracts the details of opening a file resource using
    importlib.resources. It supports opening the file in either text or
    binary mode, and is intended to be used with a "with" statement.

    Attributes:
        package: The package that contains the resource.
        name: The name of the resource file.
        mode: The file mode ("t" for text or "b" for binary).
    """

    _OPEN_FUNCTIONS = {
        "b": importlib.resources.open_binary,
        "t": importlib.resources.open_text,
    }

    def __init__(self, package: Any, name: str, *args, **kwargs) -> None:
        """
        Initialize the Model context manager.

        Args:
            package: The package where the resource file is located.
            name: The name of the resource file.
            mode: The mode to open the file. Accepts "text" or "t" for text
                mode, and "binary" or "b" for binary mode. Defaults to "text".

        Raises:
            ValueError: If an invalid mode is provided.
        """
        self.package = package
        self.name = name

        mode = "b"
        self._open_function = self._OPEN_FUNCTIONS[mode]
        self._file: Optional[IO] = None

    def __enter__(self) -> IO:
        """
        Open the resource file and return the file object.

        The file is opened using the appropriate importlib.resources function
        based on the mode specified at initialization.

        Returns:
            A file-like object opened in the specified mode.
        """
        # Note: The second argument "data" is assumed to be a subpackage or
        # directory within the given package where the resource is stored.
        self._file = importlib.resources.open_binary(
            self.package, os.path.join("data", self.name)
        )
        return pickle.load(self._file)

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
